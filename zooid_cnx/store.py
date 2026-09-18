"""Durable CogentNexus state machine.

This kernel intentionally does not execute arbitrary side effects. It owns the
semantic state, evidence gate, idempotency boundary, checkpoints, and recovery
decision. An executor (Hermes/Kanban today, Zooid-native later) claims the next
step and performs the action.

The critical recovery invariant is conservative: a step found RUNNING after a
restart is moved to VERIFY, never back to READY automatically. The caller must
establish reality before choosing completed/retry/blocked.
"""

from __future__ import annotations

import contextlib
import json
import os
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Iterator, Mapping, Optional


class CogentNexusError(RuntimeError):
    """Base runtime error."""


class AcceptanceError(CogentNexusError):
    """Completion was attempted without sufficient evidence."""


class StateTransitionError(CogentNexusError):
    """A state transition violates the durable runtime contract."""


class ProjectState(str, Enum):
    ACTIVE = "active"
    DONE = "done"


class TicketState(str, Enum):
    READY = "ready"
    RUNNING = "running"
    BLOCKED = "blocked"
    DONE = "done"


class StepState(str, Enum):
    READY = "ready"
    RUNNING = "running"
    VERIFY = "verify"
    BLOCKED = "blocked"
    DONE = "done"


class RecoveryAction(str, Enum):
    EXECUTE_STEP = "execute_step"
    VERIFY_INTERRUPTED_STEP = "verify_interrupted_step"
    COLLECT_ACCEPTANCE_EVIDENCE = "collect_acceptance_evidence"
    COMPLETE_TICKET = "complete_ticket"
    BLOCKED = "blocked"
    DONE = "done"


@dataclass(frozen=True)
class Project:
    id: str
    goal: str
    state: ProjectState
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class Ticket:
    id: str
    project_id: str
    title: str
    objective: str
    acceptance_criteria: tuple[str, ...]
    state: TicketState
    risk: str
    uncertainty: str
    created_at: str
    updated_at: str
    completed_at: Optional[str]


@dataclass(frozen=True)
class Step:
    id: str
    ticket_id: str
    position: int
    description: str
    state: StepState
    worker_id: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]
    summary: Optional[str]


@dataclass(frozen=True)
class Evidence:
    id: str
    ticket_id: str
    step_id: str
    kind: str
    value: str
    criterion_index: Optional[int]
    metadata: Mapping[str, Any]
    created_at: str


@dataclass(frozen=True)
class RecoveryResult:
    action: RecoveryAction
    ticket_id: str
    step_id: Optional[str] = None
    detail: Optional[str] = None


_SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    goal TEXT NOT NULL,
    state TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tickets (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    objective TEXT NOT NULL,
    acceptance_json TEXT NOT NULL,
    state TEXT NOT NULL,
    risk TEXT NOT NULL,
    uncertainty TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    completed_at TEXT
);

CREATE TABLE IF NOT EXISTS steps (
    id TEXT PRIMARY KEY,
    ticket_id TEXT NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    position INTEGER NOT NULL,
    description TEXT NOT NULL,
    state TEXT NOT NULL,
    worker_id TEXT,
    started_at TEXT,
    completed_at TEXT,
    summary TEXT,
    UNIQUE(ticket_id, position)
);

CREATE TABLE IF NOT EXISTS evidence (
    id TEXT PRIMARY KEY,
    ticket_id TEXT NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    step_id TEXT NOT NULL REFERENCES steps(id) ON DELETE CASCADE,
    kind TEXT NOT NULL,
    value TEXT NOT NULL,
    criterion_index INTEGER,
    metadata_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    aggregate_type TEXT NOT NULL,
    aggregate_id TEXT NOT NULL,
    ticket_id TEXT,
    kind TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    op_key TEXT UNIQUE,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_cnx_events_ticket_seq
    ON events(ticket_id, seq);

CREATE TABLE IF NOT EXISTS checkpoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id TEXT NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    step_id TEXT REFERENCES steps(id) ON DELETE SET NULL,
    phase TEXT NOT NULL,
    state_json TEXT NOT NULL,
    event_seq INTEGER NOT NULL REFERENCES events(seq),
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_cnx_checkpoints_ticket
    ON checkpoints(ticket_id, id);
"""


class CogentNexusStore:
    """SQLite-backed semantic kernel."""

    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path).expanduser().resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, timeout=5.0, isolation_level=None)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("PRAGMA busy_timeout = 5000")
        with contextlib.suppress(sqlite3.DatabaseError):
            self.conn.execute("PRAGMA journal_mode = WAL")
        self.conn.executescript(_SCHEMA)
        self.conn.execute("PRAGMA user_version = 1")

    @classmethod
    def open_default(cls) -> "CogentNexusStore":
        home = Path(os.environ.get("ZOOID_HOME") or (Path.home() / ".zooid"))
        return cls(home / "cogentnexus.db")

    def __enter__(self) -> "CogentNexusStore":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def close(self) -> None:
        self.conn.close()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _new_id(prefix: str) -> str:
        return f"{prefix}_{uuid.uuid4().hex}"

    @staticmethod
    def _json(value: Any) -> str:
        return json.dumps(value, sort_keys=True, separators=(",", ":"))

    @contextlib.contextmanager
    def _txn(self) -> Iterator[sqlite3.Connection]:
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            yield self.conn
        except Exception:
            with contextlib.suppress(sqlite3.Error):
                self.conn.execute("ROLLBACK")
            raise
        else:
            self.conn.execute("COMMIT")

    def _event_for_op(self, op_key: Optional[str], expected_kind: str) -> Optional[sqlite3.Row]:
        if not op_key:
            return None
        row = self.conn.execute("SELECT * FROM events WHERE op_key = ?", (op_key,)).fetchone()
        if row is not None and row["kind"] != expected_kind:
            raise StateTransitionError(
                f"idempotency key {op_key!r} already belongs to {row['kind']!r}"
            )
        return row

    def _record_event(
        self,
        *,
        aggregate_type: str,
        aggregate_id: str,
        ticket_id: Optional[str],
        kind: str,
        payload: Mapping[str, Any],
        op_key: Optional[str],
    ) -> int:
        cur = self.conn.execute(
            """
            INSERT INTO events(
                aggregate_type, aggregate_id, ticket_id, kind,
                payload_json, op_key, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                aggregate_type,
                aggregate_id,
                ticket_id,
                kind,
                self._json(dict(payload)),
                op_key,
                self._now(),
            ),
        )
        return int(cur.lastrowid)

    def _checkpoint(
        self,
        ticket_id: str,
        *,
        step_id: Optional[str],
        phase: str,
        event_seq: int,
    ) -> None:
        ticket = self.get_ticket(ticket_id)
        step = self.get_step(step_id) if step_id else None
        state = {
            "ticket_state": ticket.state.value,
            "step_id": step.id if step else None,
            "step_state": step.state.value if step else None,
        }
        self.conn.execute(
            """
            INSERT INTO checkpoints(
                ticket_id, step_id, phase, state_json, event_seq, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (ticket_id, step_id, phase, self._json(state), event_seq, self._now()),
        )

    @staticmethod
    def _event_payload(row: sqlite3.Row) -> dict[str, Any]:
        return json.loads(row["payload_json"])

    def create_project(self, goal: str, *, op_key: Optional[str] = None) -> Project:
        goal = goal.strip()
        if not goal:
            raise ValueError("goal must not be empty")
        with self._txn():
            prior = self._event_for_op(op_key, "project_created")
            if prior is not None:
                return self.get_project(self._event_payload(prior)["project_id"])
            project_id = self._new_id("prj")
            now = self._now()
            self.conn.execute(
                "INSERT INTO projects(id, goal, state, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (project_id, goal, ProjectState.ACTIVE.value, now, now),
            )
            self._record_event(
                aggregate_type="project",
                aggregate_id=project_id,
                ticket_id=None,
                kind="project_created",
                payload={"project_id": project_id},
                op_key=op_key,
            )
            return self.get_project(project_id)

    def create_ticket(
        self,
        project_id: str,
        *,
        title: str,
        objective: str,
        acceptance_criteria: list[str] | tuple[str, ...],
        risk: str = "unknown",
        uncertainty: str = "unknown",
        op_key: Optional[str] = None,
    ) -> Ticket:
        title = title.strip()
        objective = objective.strip()
        criteria = tuple(str(item).strip() for item in acceptance_criteria if str(item).strip())
        if not title or not objective:
            raise ValueError("title and objective must not be empty")
        with self._txn():
            prior = self._event_for_op(op_key, "ticket_created")
            if prior is not None:
                return self.get_ticket(self._event_payload(prior)["ticket_id"])
            self.get_project(project_id)
            ticket_id = self._new_id("tkt")
            now = self._now()
            self.conn.execute(
                """
                INSERT INTO tickets(
                    id, project_id, title, objective, acceptance_json, state,
                    risk, uncertainty, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ticket_id,
                    project_id,
                    title,
                    objective,
                    self._json(criteria),
                    TicketState.READY.value,
                    str(risk),
                    str(uncertainty),
                    now,
                    now,
                ),
            )
            seq = self._record_event(
                aggregate_type="ticket",
                aggregate_id=ticket_id,
                ticket_id=ticket_id,
                kind="ticket_created",
                payload={"ticket_id": ticket_id, "project_id": project_id},
                op_key=op_key,
            )
            self._checkpoint(ticket_id, step_id=None, phase="ticket_created", event_seq=seq)
            return self.get_ticket(ticket_id)

    def add_step(self, ticket_id: str, description: str, *, op_key: Optional[str] = None) -> Step:
        description = description.strip()
        if not description:
            raise ValueError("description must not be empty")
        with self._txn():
            prior = self._event_for_op(op_key, "step_added")
            if prior is not None:
                return self.get_step(self._event_payload(prior)["step_id"])
            ticket = self.get_ticket(ticket_id)
            if ticket.state is TicketState.DONE:
                raise StateTransitionError("cannot add a step to a completed ticket")
            row = self.conn.execute(
                "SELECT COALESCE(MAX(position), 0) + 1 FROM steps WHERE ticket_id = ?",
                (ticket_id,),
            ).fetchone()
            position = int(row[0])
            step_id = self._new_id("stp")
            self.conn.execute(
                "INSERT INTO steps(id, ticket_id, position, description, state) VALUES (?, ?, ?, ?, ?)",
                (step_id, ticket_id, position, description, StepState.READY.value),
            )
            seq = self._record_event(
                aggregate_type="step",
                aggregate_id=step_id,
                ticket_id=ticket_id,
                kind="step_added",
                payload={"ticket_id": ticket_id, "step_id": step_id, "position": position},
                op_key=op_key,
            )
            self._checkpoint(ticket_id, step_id=step_id, phase="step_ready", event_seq=seq)
            return self.get_step(step_id)

    def claim_next_step(
        self,
        ticket_id: str,
        *,
        worker_id: str,
        op_key: Optional[str] = None,
    ) -> Optional[Step]:
        worker_id = worker_id.strip()
        if not worker_id:
            raise ValueError("worker_id must not be empty")
        with self._txn():
            prior = self._event_for_op(op_key, "step_claimed")
            if prior is not None:
                return self.get_step(self._event_payload(prior)["step_id"])
            ticket = self.get_ticket(ticket_id)
            if ticket.state in {TicketState.BLOCKED, TicketState.DONE}:
                return None
            active = self.conn.execute(
                """
                SELECT id FROM steps
                WHERE ticket_id = ? AND state IN (?, ?)
                ORDER BY position LIMIT 1
                """,
                (ticket_id, StepState.RUNNING.value, StepState.VERIFY.value),
            ).fetchone()
            if active is not None:
                return None
            row = self.conn.execute(
                """
                SELECT id FROM steps
                WHERE ticket_id = ? AND state = ?
                ORDER BY position LIMIT 1
                """,
                (ticket_id, StepState.READY.value),
            ).fetchone()
            if row is None:
                return None
            step_id = str(row["id"])
            now = self._now()
            self.conn.execute(
                """
                UPDATE steps
                SET state = ?, worker_id = ?, started_at = ?, completed_at = NULL
                WHERE id = ?
                """,
                (StepState.RUNNING.value, worker_id, now, step_id),
            )
            self.conn.execute(
                "UPDATE tickets SET state = ?, updated_at = ? WHERE id = ?",
                (TicketState.RUNNING.value, now, ticket_id),
            )
            seq = self._record_event(
                aggregate_type="step",
                aggregate_id=step_id,
                ticket_id=ticket_id,
                kind="step_claimed",
                payload={"ticket_id": ticket_id, "step_id": step_id, "worker_id": worker_id},
                op_key=op_key,
            )
            self._checkpoint(ticket_id, step_id=step_id, phase="step_running", event_seq=seq)
            return self.get_step(step_id)

    def _validate_criterion(self, ticket: Ticket, criterion_index: Optional[int]) -> None:
        if criterion_index is None:
            return
        if criterion_index < 0 or criterion_index >= len(ticket.acceptance_criteria):
            raise ValueError(f"criterion_index out of range: {criterion_index}")

    def _insert_evidence(
        self,
        *,
        ticket: Ticket,
        step: Step,
        kind: str,
        value: str,
        criterion_index: Optional[int],
        metadata: Optional[Mapping[str, Any]],
        op_key: Optional[str],
    ) -> Evidence:
        if not kind or not value:
            raise ValueError("evidence kind and value must not be empty")
        prior = self._event_for_op(op_key, "evidence_recorded")
        if prior is not None:
            return self.get_evidence(self._event_payload(prior)["evidence_id"])
        self._validate_criterion(ticket, criterion_index)
        evidence_id = self._new_id("evd")
        now = self._now()
        self.conn.execute(
            """
            INSERT INTO evidence(
                id, ticket_id, step_id, kind, value, criterion_index,
                metadata_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                evidence_id,
                ticket.id,
                step.id,
                kind,
                value,
                criterion_index,
                self._json(dict(metadata or {})),
                now,
            ),
        )
        seq = self._record_event(
            aggregate_type="evidence",
            aggregate_id=evidence_id,
            ticket_id=ticket.id,
            kind="evidence_recorded",
            payload={
                "evidence_id": evidence_id,
                "step_id": step.id,
                "criterion_index": criterion_index,
                "kind": kind,
            },
            op_key=op_key,
        )
        self._checkpoint(ticket.id, step_id=step.id, phase="evidence_recorded", event_seq=seq)
        return self.get_evidence(evidence_id)

    def record_evidence(
        self,
        ticket_id: str,
        step_id: str,
        *,
        kind: str,
        value: str,
        criterion_index: Optional[int] = None,
        metadata: Optional[Mapping[str, Any]] = None,
        op_key: Optional[str] = None,
    ) -> Evidence:
        kind = kind.strip()
        value = value.strip()
        if not kind or not value:
            raise ValueError("evidence kind and value must not be empty")
        with self._txn():
            ticket = self.get_ticket(ticket_id)
            step = self.get_step(step_id)
            if step.ticket_id != ticket_id:
                raise StateTransitionError("step does not belong to ticket")
            return self._insert_evidence(
                ticket=ticket,
                step=step,
                kind=kind,
                value=value,
                criterion_index=criterion_index,
                metadata=metadata,
                op_key=op_key,
            )

    def complete_step(
        self,
        step_id: str,
        *,
        summary: str = "",
        op_key: Optional[str] = None,
    ) -> Step:
        with self._txn():
            prior = self._event_for_op(op_key, "step_completed")
            if prior is not None:
                return self.get_step(self._event_payload(prior)["step_id"])
            step = self.get_step(step_id)
            if step.state not in {StepState.RUNNING, StepState.VERIFY}:
                raise StateTransitionError(f"step {step_id} is {step.state.value}, not completable")
            count = self.conn.execute(
                "SELECT COUNT(*) FROM evidence WHERE step_id = ?",
                (step_id,),
            ).fetchone()[0]
            if not count:
                raise AcceptanceError("step completion requires at least one evidence record")
            now = self._now()
            self.conn.execute(
                "UPDATE steps SET state = ?, completed_at = ?, summary = ? WHERE id = ?",
                (StepState.DONE.value, now, summary or None, step_id),
            )
            seq = self._record_event(
                aggregate_type="step",
                aggregate_id=step_id,
                ticket_id=step.ticket_id,
                kind="step_completed",
                payload={"step_id": step_id, "summary": summary},
                op_key=op_key,
            )
            self._checkpoint(step.ticket_id, step_id=step_id, phase="step_done", event_seq=seq)
            return self.get_step(step_id)

    def _missing_acceptance_criteria(self, ticket: Ticket) -> list[int]:
        if not ticket.acceptance_criteria:
            return []
        covered = {
            int(row[0])
            for row in self.conn.execute(
                """
                SELECT DISTINCT criterion_index FROM evidence
                WHERE ticket_id = ? AND criterion_index IS NOT NULL
                """,
                (ticket.id,),
            )
        }
        return [i for i in range(len(ticket.acceptance_criteria)) if i not in covered]

    def complete_ticket(
        self,
        ticket_id: str,
        *,
        summary: str = "",
        op_key: Optional[str] = None,
    ) -> Ticket:
        with self._txn():
            prior = self._event_for_op(op_key, "ticket_completed")
            if prior is not None:
                return self.get_ticket(self._event_payload(prior)["ticket_id"])
            ticket = self.get_ticket(ticket_id)
            if ticket.state is TicketState.DONE:
                return ticket
            rows = self.conn.execute(
                "SELECT state FROM steps WHERE ticket_id = ? ORDER BY position",
                (ticket_id,),
            ).fetchall()
            if not rows:
                raise AcceptanceError("ticket completion requires at least one step")
            not_done = [row["state"] for row in rows if row["state"] != StepState.DONE.value]
            if not_done:
                raise AcceptanceError(f"ticket has unfinished steps: {', '.join(not_done)}")
            missing = self._missing_acceptance_criteria(ticket)
            if missing:
                raise AcceptanceError(f"missing acceptance evidence for criterion {missing[0]}")
            now = self._now()
            self.conn.execute(
                "UPDATE tickets SET state = ?, updated_at = ?, completed_at = ? WHERE id = ?",
                (TicketState.DONE.value, now, now, ticket_id),
            )
            seq = self._record_event(
                aggregate_type="ticket",
                aggregate_id=ticket_id,
                ticket_id=ticket_id,
                kind="ticket_completed",
                payload={"ticket_id": ticket_id, "summary": summary},
                op_key=op_key,
            )
            self._checkpoint(ticket_id, step_id=None, phase="ticket_done", event_seq=seq)
            project_id = ticket.project_id
            unfinished = self.conn.execute(
                "SELECT COUNT(*) FROM tickets WHERE project_id = ? AND state != ?",
                (project_id, TicketState.DONE.value),
            ).fetchone()[0]
            if not unfinished:
                self.conn.execute(
                    "UPDATE projects SET state = ?, updated_at = ? WHERE id = ?",
                    (ProjectState.DONE.value, now, project_id),
                )
            return self.get_ticket(ticket_id)

    def recover_ticket(
        self,
        ticket_id: str,
        *,
        op_key: Optional[str] = None,
    ) -> RecoveryResult:
        with self._txn():
            if op_key:
                prior = self.conn.execute(
                    "SELECT * FROM events WHERE op_key = ?",
                    (op_key,),
                ).fetchone()
                if prior is not None:
                    if not prior["kind"].startswith("recovery_"):
                        raise StateTransitionError(
                            f"idempotency key {op_key!r} already belongs to {prior['kind']!r}"
                        )
                    payload = self._event_payload(prior)
                    return RecoveryResult(
                        RecoveryAction(payload["action"]),
                        ticket_id,
                        payload.get("step_id"),
                        payload.get("detail"),
                    )

            ticket = self.get_ticket(ticket_id)
            if ticket.state is TicketState.DONE:
                return self._record_recovery(
                    ticket,
                    RecoveryResult(RecoveryAction.DONE, ticket_id),
                    kind="recovery_done",
                    op_key=op_key,
                )

            verify = self.conn.execute(
                "SELECT id FROM steps WHERE ticket_id = ? AND state = ? ORDER BY position LIMIT 1",
                (ticket_id, StepState.VERIFY.value),
            ).fetchone()
            if verify is not None:
                return self._record_recovery(
                    ticket,
                    RecoveryResult(
                        RecoveryAction.VERIFY_INTERRUPTED_STEP,
                        ticket_id,
                        str(verify["id"]),
                        "step outcome is uncertain; verify reality before retry",
                    ),
                    kind="recovery_requires_verification",
                    op_key=op_key,
                )

            running = self.conn.execute(
                "SELECT id FROM steps WHERE ticket_id = ? AND state = ? ORDER BY position LIMIT 1",
                (ticket_id, StepState.RUNNING.value),
            ).fetchone()
            if running is not None:
                step_id = str(running["id"])
                self.conn.execute(
                    "UPDATE steps SET state = ? WHERE id = ?",
                    (StepState.VERIFY.value, step_id),
                )
                return self._record_recovery(
                    ticket,
                    RecoveryResult(
                        RecoveryAction.VERIFY_INTERRUPTED_STEP,
                        ticket_id,
                        step_id,
                        "interrupted running step moved to VERIFY; no automatic replay",
                    ),
                    kind="recovery_requires_verification",
                    op_key=op_key,
                )

            blocked = self.conn.execute(
                "SELECT id FROM steps WHERE ticket_id = ? AND state = ? ORDER BY position LIMIT 1",
                (ticket_id, StepState.BLOCKED.value),
            ).fetchone()
            if ticket.state is TicketState.BLOCKED or blocked is not None:
                return self._record_recovery(
                    ticket,
                    RecoveryResult(
                        RecoveryAction.BLOCKED,
                        ticket_id,
                        str(blocked["id"]) if blocked else None,
                    ),
                    kind="recovery_blocked",
                    op_key=op_key,
                )

            ready = self.conn.execute(
                "SELECT id FROM steps WHERE ticket_id = ? AND state = ? ORDER BY position LIMIT 1",
                (ticket_id, StepState.READY.value),
            ).fetchone()
            if ready is not None:
                return self._record_recovery(
                    ticket,
                    RecoveryResult(RecoveryAction.EXECUTE_STEP, ticket_id, str(ready["id"])),
                    kind="recovery_ready",
                    op_key=op_key,
                )

            missing = self._missing_acceptance_criteria(ticket)
            if missing:
                return self._record_recovery(
                    ticket,
                    RecoveryResult(
                        RecoveryAction.COLLECT_ACCEPTANCE_EVIDENCE,
                        ticket_id,
                        detail=f"criterion {missing[0]} lacks evidence",
                    ),
                    kind="recovery_acceptance_evidence",
                    op_key=op_key,
                )
            return self._record_recovery(
                ticket,
                RecoveryResult(RecoveryAction.COMPLETE_TICKET, ticket_id),
                kind="recovery_complete_ticket",
                op_key=op_key,
            )

    def _record_recovery(
        self,
        ticket: Ticket,
        result: RecoveryResult,
        *,
        kind: str,
        op_key: Optional[str],
    ) -> RecoveryResult:
        seq = self._record_event(
            aggregate_type="ticket",
            aggregate_id=ticket.id,
            ticket_id=ticket.id,
            kind=kind,
            payload={
                "action": result.action.value,
                "step_id": result.step_id,
                "detail": result.detail,
            },
            op_key=op_key,
        )
        phase = (
            "recovery_verify"
            if result.action is RecoveryAction.VERIFY_INTERRUPTED_STEP
            else f"recovery_{result.action.value}"
        )
        self._checkpoint(ticket.id, step_id=result.step_id, phase=phase, event_seq=seq)
        return result

    def resolve_interrupted_step(
        self,
        step_id: str,
        *,
        resolution: str,
        summary: str = "",
        evidence: Optional[Mapping[str, Any]] = None,
        op_key: Optional[str] = None,
    ) -> Step:
        resolution = resolution.strip().lower()
        if resolution not in {"completed", "retry", "blocked"}:
            raise ValueError("resolution must be completed, retry, or blocked")
        expected_kind = {
            "completed": "step_verified_completed",
            "retry": "step_retry_authorized",
            "blocked": "step_blocked",
        }[resolution]
        with self._txn():
            prior = self._event_for_op(op_key, expected_kind)
            if prior is not None:
                return self.get_step(self._event_payload(prior)["step_id"])
            step = self.get_step(step_id)
            if step.state is not StepState.VERIFY:
                raise StateTransitionError("only a VERIFY step can be resolved after recovery")
            ticket = self.get_ticket(step.ticket_id)
            now = self._now()

            if resolution == "completed":
                if not evidence:
                    raise AcceptanceError("completed recovery resolution requires evidence")
                self._insert_evidence(
                    ticket=ticket,
                    step=step,
                    kind=str(evidence.get("kind", "")).strip(),
                    value=str(evidence.get("value", "")).strip(),
                    criterion_index=evidence.get("criterion_index"),
                    metadata=evidence.get("metadata") if isinstance(evidence.get("metadata"), Mapping) else None,
                    op_key=None,
                )
                self.conn.execute(
                    "UPDATE steps SET state = ?, completed_at = ?, summary = ? WHERE id = ?",
                    (StepState.DONE.value, now, summary or None, step_id),
                )
                phase = "step_verified_done"
            elif resolution == "retry":
                self.conn.execute(
                    """
                    UPDATE steps SET state = ?, worker_id = NULL, started_at = NULL,
                        completed_at = NULL, summary = ?
                    WHERE id = ?
                    """,
                    (StepState.READY.value, summary or None, step_id),
                )
                phase = "step_retry_ready"
            else:
                self.conn.execute(
                    "UPDATE steps SET state = ?, summary = ? WHERE id = ?",
                    (StepState.BLOCKED.value, summary or None, step_id),
                )
                self.conn.execute(
                    "UPDATE tickets SET state = ?, updated_at = ? WHERE id = ?",
                    (TicketState.BLOCKED.value, now, step.ticket_id),
                )
                phase = "step_blocked"

            seq = self._record_event(
                aggregate_type="step",
                aggregate_id=step_id,
                ticket_id=step.ticket_id,
                kind=expected_kind,
                payload={"step_id": step_id, "resolution": resolution, "summary": summary},
                op_key=op_key,
            )
            self._checkpoint(step.ticket_id, step_id=step_id, phase=phase, event_seq=seq)
            return self.get_step(step_id)

    def get_project(self, project_id: str) -> Project:
        row = self.conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        if row is None:
            raise KeyError(f"unknown project: {project_id}")
        return Project(
            id=row["id"],
            goal=row["goal"],
            state=ProjectState(row["state"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def get_ticket(self, ticket_id: str) -> Ticket:
        row = self.conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        if row is None:
            raise KeyError(f"unknown ticket: {ticket_id}")
        return Ticket(
            id=row["id"],
            project_id=row["project_id"],
            title=row["title"],
            objective=row["objective"],
            acceptance_criteria=tuple(json.loads(row["acceptance_json"])),
            state=TicketState(row["state"]),
            risk=row["risk"],
            uncertainty=row["uncertainty"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            completed_at=row["completed_at"],
        )

    def get_step(self, step_id: str) -> Step:
        row = self.conn.execute("SELECT * FROM steps WHERE id = ?", (step_id,)).fetchone()
        if row is None:
            raise KeyError(f"unknown step: {step_id}")
        return Step(
            id=row["id"],
            ticket_id=row["ticket_id"],
            position=int(row["position"]),
            description=row["description"],
            state=StepState(row["state"]),
            worker_id=row["worker_id"],
            started_at=row["started_at"],
            completed_at=row["completed_at"],
            summary=row["summary"],
        )

    def get_evidence(self, evidence_id: str) -> Evidence:
        row = self.conn.execute("SELECT * FROM evidence WHERE id = ?", (evidence_id,)).fetchone()
        if row is None:
            raise KeyError(f"unknown evidence: {evidence_id}")
        return Evidence(
            id=row["id"],
            ticket_id=row["ticket_id"],
            step_id=row["step_id"],
            kind=row["kind"],
            value=row["value"],
            criterion_index=row["criterion_index"],
            metadata=json.loads(row["metadata_json"]),
            created_at=row["created_at"],
        )

    def list_steps(self, ticket_id: str) -> list[Step]:
        rows = self.conn.execute(
            "SELECT id FROM steps WHERE ticket_id = ? ORDER BY position",
            (ticket_id,),
        ).fetchall()
        return [self.get_step(str(row["id"])) for row in rows]

    def list_evidence(self, ticket_id: str) -> list[Evidence]:
        rows = self.conn.execute(
            "SELECT id FROM evidence WHERE ticket_id = ? ORDER BY created_at, id",
            (ticket_id,),
        ).fetchall()
        return [self.get_evidence(str(row["id"])) for row in rows]

    def list_events(self, ticket_id: str) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT * FROM events WHERE ticket_id = ? ORDER BY seq",
            (ticket_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    def latest_checkpoint(self, ticket_id: str) -> dict[str, Any]:
        row = self.conn.execute(
            "SELECT * FROM checkpoints WHERE ticket_id = ? ORDER BY id DESC LIMIT 1",
            (ticket_id,),
        ).fetchone()
        if row is None:
            raise KeyError(f"ticket has no checkpoint: {ticket_id}")
        return dict(row)
