from dataclasses import replace

from zooid_cnx.execution import (
    ExecutionCoordinator,
    ExecutionStatus,
    ExecutorEvidence,
    ExecutorSnapshot,
    ExecutorState,
)
from zooid_cnx.store import CogentNexusStore, StepState, TicketState


class FakeExecutor:
    name = "fake"

    def __init__(self):
        self.by_key = {}
        self.by_id = {}
        self.submit_calls = 0

    def submit(self, *, operation_key, title, body):
        existing = self.by_key.get(operation_key)
        if existing is not None:
            return existing.external_id
        self.submit_calls += 1
        external_id = f"ext-{self.submit_calls}"
        snap = ExecutorSnapshot(external_id, ExecutorState.QUEUED)
        self.by_key[operation_key] = snap
        self.by_id[external_id] = snap
        return external_id

    def find(self, operation_key):
        return self.by_key.get(operation_key)

    def inspect(self, external_id):
        return self.by_id[external_id]

    def seed(self, operation_key, *, state=ExecutorState.RUNNING):
        external_id = f"seed-{len(self.by_id) + 1}"
        snap = ExecutorSnapshot(external_id, state)
        self.by_key[operation_key] = snap
        self.by_id[external_id] = snap
        return snap

    def set_state(self, external_id, state, *, summary=None, evidence=()):
        current = self.by_id[external_id]
        updated = replace(
            current,
            state=state,
            summary=summary,
            evidence=tuple(evidence),
        )
        self.by_id[external_id] = updated
        for key, value in list(self.by_key.items()):
            if value.external_id == external_id:
                self.by_key[key] = updated


def _one_step(store):
    project = store.create_project("preserve intent through execution")
    ticket = store.create_ticket(
        project.id,
        title="executor bridge",
        objective="run one bounded step through an external executor",
        acceptance_criteria=["executor result verified"],
        risk="medium",
        uncertainty="low",
    )
    step = store.add_step(ticket.id, "produce and verify the requested artifact")
    return project, ticket, step


def test_dispatch_binds_one_external_task_and_restart_never_replays(tmp_path):
    db_path = tmp_path / "cogentnexus.db"
    executor = FakeExecutor()

    with CogentNexusStore(db_path) as store:
        _project, ticket, step = _one_step(store)
        coordinator = ExecutionCoordinator(store, executor)

        dispatched = coordinator.tick(ticket.id)
        assert dispatched.status is ExecutionStatus.DISPATCHED
        assert dispatched.step_id == step.id
        assert executor.submit_calls == 1

        waiting = coordinator.tick(ticket.id)
        assert waiting.status is ExecutionStatus.WAITING_EXTERNAL
        assert executor.submit_calls == 1

        binding = store.get_external_binding(step.id)
        assert binding is not None
        assert binding.external_id == dispatched.external_id

    with CogentNexusStore(db_path) as store:
        coordinator = ExecutionCoordinator(store, executor)
        recovered = coordinator.recover(ticket.id)

        assert recovered.status is ExecutionStatus.WAITING_EXTERNAL
        assert store.get_step(step.id).state is StepState.VERIFY
        assert executor.submit_calls == 1


def test_recovery_discovers_idempotent_external_task_created_before_binding(tmp_path):
    db_path = tmp_path / "cogentnexus.db"
    executor = FakeExecutor()

    with CogentNexusStore(db_path) as store:
        _project, ticket, step = _one_step(store)
        claimed = store.claim_next_step(ticket.id, worker_id="external:fake")
        assert claimed.id == step.id

        operation_key = ExecutionCoordinator.operation_key(ticket.id, step.id)
        seeded = executor.seed(operation_key)
        assert store.get_external_binding(step.id) is None

    with CogentNexusStore(db_path) as store:
        coordinator = ExecutionCoordinator(store, executor)
        result = coordinator.recover(ticket.id)

        assert result.status is ExecutionStatus.WAITING_EXTERNAL
        binding = store.get_external_binding(step.id)
        assert binding is not None
        assert binding.external_id == seeded.external_id
        assert executor.submit_calls == 0
        assert store.get_step(step.id).state is StepState.VERIFY


def test_external_success_records_evidence_and_finishes_ticket(tmp_path):
    executor = FakeExecutor()
    with CogentNexusStore(tmp_path / "cogentnexus.db") as store:
        project, ticket, step = _one_step(store)
        coordinator = ExecutionCoordinator(store, executor)

        dispatched = coordinator.tick(ticket.id)
        executor.set_state(
            dispatched.external_id,
            ExecutorState.SUCCEEDED,
            summary="artifact exists and verification passed",
            evidence=(
                ExecutorEvidence(
                    kind="executor_result",
                    value="verified artifact receipt",
                    criterion_index=0,
                ),
            ),
        )

        result = coordinator.tick(ticket.id)

        assert result.status is ExecutionStatus.DONE
        assert store.get_step(step.id).state is StepState.DONE
        assert store.get_ticket(ticket.id).state is TicketState.DONE
        assert store.get_project(project.id).state.value == "done"
        assert len(store.list_evidence(ticket.id)) == 1


def test_external_failure_blocks_without_implicit_retry(tmp_path):
    executor = FakeExecutor()
    with CogentNexusStore(tmp_path / "cogentnexus.db") as store:
        _project, ticket, step = _one_step(store)
        coordinator = ExecutionCoordinator(store, executor)

        dispatched = coordinator.tick(ticket.id)
        executor.set_state(
            dispatched.external_id,
            ExecutorState.FAILED,
            summary="executor reported a deterministic failure",
        )

        result = coordinator.tick(ticket.id)

        assert result.status is ExecutionStatus.BLOCKED
        assert store.get_step(step.id).state is StepState.BLOCKED
        assert store.get_ticket(ticket.id).state is TicketState.BLOCKED
        assert executor.submit_calls == 1
