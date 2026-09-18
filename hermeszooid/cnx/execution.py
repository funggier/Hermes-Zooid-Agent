"""Executor-neutral bridge from CogentNexus semantic state to bounded work."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Optional, Protocol, Sequence

from .store import (
    AcceptanceError,
    CogentNexusStore,
    ExternalBinding,
    RecoveryAction,
    Step,
    StepState,
    Ticket,
    TicketState,
)


class ExecutorState(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class ExecutorEvidence:
    kind: str
    value: str
    criterion_index: Optional[int] = None
    metadata: Optional[Mapping[str, object]] = None


@dataclass(frozen=True)
class ExecutorSnapshot:
    external_id: str
    state: ExecutorState
    summary: Optional[str] = None
    evidence: Sequence[ExecutorEvidence] = ()


class ExecutorPort(Protocol):
    name: str

    def submit(self, *, operation_key: str, title: str, body: str) -> str:
        ...

    def find(self, operation_key: str) -> Optional[ExecutorSnapshot]:
        ...

    def inspect(self, external_id: str) -> ExecutorSnapshot:
        ...


class ExecutionStatus(str, Enum):
    DISPATCHED = "dispatched"
    WAITING_EXTERNAL = "waiting_external"
    STEP_COMPLETED = "step_completed"
    NEEDS_VERIFICATION = "needs_verification"
    NEEDS_ACCEPTANCE_EVIDENCE = "needs_acceptance_evidence"
    BLOCKED = "blocked"
    DONE = "done"


@dataclass(frozen=True)
class ExecutionResult:
    status: ExecutionStatus
    ticket_id: str
    step_id: Optional[str] = None
    external_id: Optional[str] = None
    detail: Optional[str] = None


class ExecutionCoordinator:
    """Drive one Ticket through an idempotent external executor.

    The coordinator deliberately keeps the executor replaceable. CogentNexus
    remains authoritative for intent, acceptance, evidence, and recovery.
    """

    def __init__(self, store: CogentNexusStore, executor: ExecutorPort):
        self.store = store
        self.executor = executor
        self._owned_running_steps: set[str] = set()

    @staticmethod
    def operation_key(ticket_id: str, step_id: str) -> str:
        return f"cnx:{ticket_id}:{step_id}:execute"

    def _step_body(self, ticket: Ticket, step: Step) -> str:
        payload = {
            "ticket_id": ticket.id,
            "objective": ticket.objective,
            "step_id": step.id,
            "step": step.description,
            "risk": ticket.risk,
            "uncertainty": ticket.uncertainty,
            "acceptance_criteria": list(ticket.acceptance_criteria),
            "contract": (
                "Perform only this bounded step. Return explicit evidence. "
                "Do not declare the CogentNexus ticket complete."
            ),
        }
        return json.dumps(payload, ensure_ascii=False, sort_keys=True)

    def _discover_binding(self, ticket: Ticket, step: Step) -> Optional[ExternalBinding]:
        binding = self.store.get_external_binding(step.id)
        if binding is not None:
            if binding.executor != self.executor.name:
                raise RuntimeError(
                    f"step {step.id} belongs to executor {binding.executor!r}, "
                    f"not {self.executor.name!r}"
                )
            return binding

        operation_key = self.operation_key(ticket.id, step.id)
        snapshot = self.executor.find(operation_key)
        if snapshot is None:
            return None
        return self.store.bind_external(
            step.id,
            executor=self.executor.name,
            operation_key=operation_key,
            external_id=snapshot.external_id,
        )

    def dispatch_next(self, ticket_id: str) -> ExecutionResult:
        ticket = self.store.get_ticket(ticket_id)
        if ticket.state is TicketState.DONE:
            return ExecutionResult(ExecutionStatus.DONE, ticket_id)
        if ticket.state is TicketState.BLOCKED:
            return ExecutionResult(ExecutionStatus.BLOCKED, ticket_id)

        step = self.store.claim_next_step(
            ticket_id,
            worker_id=f"external:{self.executor.name}",
        )
        if step is None:
            return ExecutionResult(
                ExecutionStatus.NEEDS_VERIFICATION,
                ticket_id,
                detail="no claimable step; inspect active or acceptance state",
            )

        operation_key = self.operation_key(ticket.id, step.id)
        snapshot = self.executor.find(operation_key)
        if snapshot is None:
            external_id = self.executor.submit(
                operation_key=operation_key,
                title=step.description,
                body=self._step_body(ticket, step),
            )
        else:
            external_id = snapshot.external_id

        binding = self.store.bind_external(
            step.id,
            executor=self.executor.name,
            operation_key=operation_key,
            external_id=external_id,
        )
        self._owned_running_steps.add(step.id)
        return ExecutionResult(
            ExecutionStatus.DISPATCHED,
            ticket_id,
            step.id,
            binding.external_id,
        )

    def _apply_snapshot(
        self,
        ticket: Ticket,
        step: Step,
        binding: ExternalBinding,
    ) -> ExecutionResult:
        snapshot = self.executor.inspect(binding.external_id)
        if snapshot.external_id != binding.external_id:
            raise RuntimeError("executor returned a snapshot for the wrong external id")

        if snapshot.state in {ExecutorState.QUEUED, ExecutorState.RUNNING}:
            return ExecutionResult(
                ExecutionStatus.WAITING_EXTERNAL,
                ticket.id,
                step.id,
                binding.external_id,
            )

        if snapshot.state in {ExecutorState.FAILED, ExecutorState.BLOCKED}:
            reason = snapshot.summary or f"external executor reported {snapshot.state.value}"
            self.store.block_step(
                step.id,
                reason=reason,
                op_key=f"{binding.operation_key}:block",
            )
            self._owned_running_steps.discard(step.id)
            return ExecutionResult(
                ExecutionStatus.BLOCKED,
                ticket.id,
                step.id,
                binding.external_id,
                reason,
            )

        if snapshot.state is not ExecutorState.SUCCEEDED:
            return ExecutionResult(
                ExecutionStatus.NEEDS_VERIFICATION,
                ticket.id,
                step.id,
                binding.external_id,
                f"unrecognized external state: {snapshot.state}",
            )

        evidence = tuple(snapshot.evidence)
        if not evidence:
            return ExecutionResult(
                ExecutionStatus.NEEDS_ACCEPTANCE_EVIDENCE,
                ticket.id,
                step.id,
                binding.external_id,
                "executor reported success without evidence",
            )

        for index, item in enumerate(evidence):
            self.store.record_evidence(
                ticket.id,
                step.id,
                kind=item.kind,
                value=item.value,
                criterion_index=item.criterion_index,
                metadata=item.metadata,
                op_key=f"{binding.operation_key}:evidence:{index}",
            )

        self.store.complete_step(
            step.id,
            summary=snapshot.summary or "external executor completed",
            op_key=f"{binding.operation_key}:complete-step",
        )
        self._owned_running_steps.discard(step.id)

        remaining = [
            item
            for item in self.store.list_steps(ticket.id)
            if item.state is not StepState.DONE
        ]
        if remaining:
            return ExecutionResult(
                ExecutionStatus.STEP_COMPLETED,
                ticket.id,
                step.id,
                binding.external_id,
            )

        try:
            self.store.complete_ticket(
                ticket.id,
                summary=snapshot.summary or "all bounded steps completed",
                op_key=f"{ticket.id}:complete-ticket",
            )
        except AcceptanceError as exc:
            return ExecutionResult(
                ExecutionStatus.NEEDS_ACCEPTANCE_EVIDENCE,
                ticket.id,
                step.id,
                binding.external_id,
                str(exc),
            )

        return ExecutionResult(
            ExecutionStatus.DONE,
            ticket.id,
            step.id,
            binding.external_id,
        )

    def recover(self, ticket_id: str) -> ExecutionResult:
        recovery = self.store.recover_ticket(ticket_id)
        if recovery.action is RecoveryAction.DONE:
            return ExecutionResult(ExecutionStatus.DONE, ticket_id)
        if recovery.action is RecoveryAction.BLOCKED:
            return ExecutionResult(
                ExecutionStatus.BLOCKED,
                ticket_id,
                recovery.step_id,
            )
        if recovery.action is RecoveryAction.COLLECT_ACCEPTANCE_EVIDENCE:
            return ExecutionResult(
                ExecutionStatus.NEEDS_ACCEPTANCE_EVIDENCE,
                ticket_id,
                detail=recovery.detail,
            )
        if recovery.action is RecoveryAction.COMPLETE_TICKET:
            try:
                self.store.complete_ticket(ticket_id)
            except AcceptanceError as exc:
                return ExecutionResult(
                    ExecutionStatus.NEEDS_ACCEPTANCE_EVIDENCE,
                    ticket_id,
                    detail=str(exc),
                )
            return ExecutionResult(ExecutionStatus.DONE, ticket_id)
        if recovery.action is RecoveryAction.EXECUTE_STEP:
            return self.dispatch_next(ticket_id)

        step = self.store.get_step(recovery.step_id)
        ticket = self.store.get_ticket(ticket_id)
        binding = self._discover_binding(ticket, step)
        if binding is None:
            return ExecutionResult(
                ExecutionStatus.NEEDS_VERIFICATION,
                ticket_id,
                step.id,
                detail=(
                    "interrupted step has no durable binding and the executor "
                    "cannot prove an idempotent external task exists"
                ),
            )
        return self._apply_snapshot(ticket, step, binding)

    def tick(self, ticket_id: str) -> ExecutionResult:
        ticket = self.store.get_ticket(ticket_id)
        if ticket.state is TicketState.DONE:
            return ExecutionResult(ExecutionStatus.DONE, ticket_id)
        if ticket.state is TicketState.BLOCKED:
            return ExecutionResult(ExecutionStatus.BLOCKED, ticket_id)

        active = next(
            (
                step
                for step in self.store.list_steps(ticket_id)
                if step.state in {StepState.RUNNING, StepState.VERIFY}
            ),
            None,
        )
        if active is not None:
            if active.state is StepState.RUNNING and active.id not in self._owned_running_steps:
                return self.recover(ticket_id)
            binding = self._discover_binding(ticket, active)
            if binding is None:
                return ExecutionResult(
                    ExecutionStatus.NEEDS_VERIFICATION,
                    ticket_id,
                    active.id,
                    detail="active step has no proven external execution",
                )
            return self._apply_snapshot(ticket, active, binding)

        ready = any(step.state is StepState.READY for step in self.store.list_steps(ticket_id))
        if ready:
            return self.dispatch_next(ticket_id)

        try:
            self.store.complete_ticket(ticket_id)
        except AcceptanceError as exc:
            return ExecutionResult(
                ExecutionStatus.NEEDS_ACCEPTANCE_EVIDENCE,
                ticket_id,
                detail=str(exc),
            )
        return ExecutionResult(ExecutionStatus.DONE, ticket_id)
