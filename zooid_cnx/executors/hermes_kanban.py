"""Hermes Kanban adapter for the CogentNexus executor-neutral bridge.

CogentNexus remains the semantic authority. This adapter only translates one
bounded Step into a Hermes Kanban task and translates the durable Kanban state
back into an ExecutorSnapshot.

No process-global HERMES_* environment is mutated here. A caller that launches
the Hermes dispatcher/worker may use :meth:`worker_env` to pin every writable
Kanban surface beneath Zooid-owned storage.
"""

from __future__ import annotations

import contextlib
import os
from collections.abc import Mapping
from pathlib import Path
from typing import Optional

from ..execution import ExecutorEvidence, ExecutorSnapshot, ExecutorState


_QUEUED_STATUSES = frozenset({"triage", "todo", "scheduled", "ready"})
_BLOCKED_STATUSES = frozenset({"blocked", "review"})
_FAILED_STATUSES = frozenset({"archived", "failed", "cancelled"})


class HermesKanbanExecutor:
    """Use a real Hermes Kanban SQLite board as an ExecutorPort."""

    name = "hermes-kanban"
    default_board = "cogentnexus"

    def __init__(
        self,
        *,
        db_path: Path | str,
        zooid_home: Path | str | None = None,
        board: str = default_board,
        workspaces_root: Path | str | None = None,
        attachments_root: Path | str | None = None,
    ):
        self.db_path = Path(db_path).expanduser().resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        home_value = zooid_home or os.environ.get("ZOOID_HOME") or self.db_path.parent
        self.zooid_home = Path(home_value).expanduser().resolve()
        self.board = str(board).strip() or self.default_board
        self.workspaces_root = Path(
            workspaces_root or (self.db_path.parent / "workspaces")
        ).expanduser().resolve()
        self.attachments_root = Path(
            attachments_root or (self.db_path.parent / "attachments")
        ).expanduser().resolve()

    @classmethod
    def open_default(cls) -> "HermesKanbanExecutor":
        home = Path(os.environ.get("ZOOID_HOME") or (Path.home() / ".zooid")).expanduser().resolve()
        root = home / "kanban" / "boards" / cls.default_board
        return cls(
            db_path=root / "kanban.db",
            zooid_home=home,
            board=cls.default_board,
            workspaces_root=root / "workspaces",
            attachments_root=root / "attachments",
        )

    @staticmethod
    def _modules():
        # Lazy import keeps the generic CogentNexus kernel independent from
        # Hermes implementation modules until this concrete adapter is used.
        from hermes_cli import kanban_db as kb
        from hermes_cli import kanban_db_connect as kbc

        return kb, kbc

    def worker_env(self) -> dict[str, str]:
        """Environment required to keep Hermes Kanban runtime state Zooid-owned."""
        return {
            "HERMES_KANBAN_HOME": str(self.zooid_home),
            "HERMES_KANBAN_BOARD": self.board,
            "HERMES_KANBAN_DB": str(self.db_path),
            "HERMES_KANBAN_WORKSPACES_ROOT": str(self.workspaces_root),
            "HERMES_KANBAN_ATTACHMENTS_ROOT": str(self.attachments_root),
        }

    @staticmethod
    def _completion_protocol() -> str:
        return """
## CogentNexus completion protocol

This card is one bounded execution Step. Completing the Hermes card does not
complete the CogentNexus Ticket.

When calling kanban_complete, include structured acceptance evidence in:

metadata.cogentnexus_evidence = [
  {
    "kind": "<evidence type>",
    "value": "<verifiable receipt or observation>",
    "criterion_index": <zero-based acceptance criterion index>,
    "metadata": {<optional provenance>}
  }
]

Use one entry per criterion actually proven. Do not invent evidence. If the
criterion cannot be proven, block/request review instead of claiming success.
""".strip()

    def _worker_body(self, body: str) -> str:
        body = (body or "").rstrip()
        protocol = self._completion_protocol()
        return f"{body}\n\n{protocol}\n" if body else f"{protocol}\n"

    def _find_task_id(self, operation_key: str) -> Optional[str]:
        _kb, kbc = self._modules()
        with contextlib.closing(kbc.connect(self.db_path)) as conn:
            row = conn.execute(
                """
                SELECT id
                FROM tasks
                WHERE idempotency_key = ?
                ORDER BY rowid DESC
                LIMIT 1
                """,
                (operation_key,),
            ).fetchone()
            return str(row["id"]) if row is not None else None

    def submit(self, *, operation_key: str, title: str, body: str) -> str:
        operation_key = operation_key.strip()
        title = title.strip()
        if not operation_key:
            raise ValueError("operation_key must not be empty")
        if not title:
            raise ValueError("title must not be empty")

        # Stronger than Hermes' native create_task idempotency, which ignores an
        # archived card. CogentNexus must not duplicate a possibly side-effecting
        # operation merely because an operator archived its executor record.
        existing = self._find_task_id(operation_key)
        if existing is not None:
            return existing

        kb, kbc = self._modules()
        with contextlib.closing(kbc.connect(self.db_path)) as conn:
            return kb.create_task(
                conn,
                title=title,
                body=self._worker_body(body),
                created_by="cogentnexus",
                workspace_kind="scratch",
                project_id="",
                idempotency_key=operation_key,
                completion_contract="local-only",
            )

    def find(self, operation_key: str) -> Optional[ExecutorSnapshot]:
        operation_key = operation_key.strip()
        if not operation_key:
            return None
        task_id = self._find_task_id(operation_key)
        return self.inspect(task_id) if task_id is not None else None

    @staticmethod
    def _state_for(status: str) -> ExecutorState:
        if status in _QUEUED_STATUSES:
            return ExecutorState.QUEUED
        if status == "running":
            return ExecutorState.RUNNING
        if status == "done":
            return ExecutorState.SUCCEEDED
        if status in _BLOCKED_STATUSES:
            return ExecutorState.BLOCKED
        if status in _FAILED_STATUSES:
            return ExecutorState.FAILED

        # Unknown future Hermes state is never interpreted as success.
        return ExecutorState.FAILED

    @staticmethod
    def _clean_text(value: object) -> Optional[str]:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    @classmethod
    def _evidence_from_metadata(cls, metadata: object) -> tuple[ExecutorEvidence, ...]:
        if not isinstance(metadata, Mapping):
            return ()
        raw = metadata.get("cogentnexus_evidence")
        if not isinstance(raw, (list, tuple)):
            return ()

        out: list[ExecutorEvidence] = []
        for item in raw:
            if not isinstance(item, Mapping):
                continue
            kind = cls._clean_text(item.get("kind"))
            value = cls._clean_text(item.get("value"))
            if not kind or not value:
                continue

            criterion = item.get("criterion_index")
            if criterion is not None:
                if isinstance(criterion, bool) or not isinstance(criterion, int) or criterion < 0:
                    continue

            provenance = item.get("metadata")
            if provenance is not None and not isinstance(provenance, Mapping):
                provenance = None

            out.append(
                ExecutorEvidence(
                    kind=kind,
                    value=value,
                    criterion_index=criterion,
                    metadata=dict(provenance) if isinstance(provenance, Mapping) else None,
                )
            )
        return tuple(out)

    def inspect(self, external_id: str) -> ExecutorSnapshot:
        external_id = external_id.strip()
        if not external_id:
            raise ValueError("external_id must not be empty")

        kb, kbc = self._modules()
        with contextlib.closing(kbc.connect(self.db_path)) as conn:
            task = kb.get_task(conn, external_id)
            if task is None:
                raise KeyError(f"unknown Hermes Kanban task: {external_id}")

            latest_run = kb.latest_run(conn, external_id)
            summary = (
                self._clean_text(latest_run.summary if latest_run is not None else None)
                or self._clean_text(task.result)
                or self._clean_text(task.last_failure_error)
            )
            state = self._state_for(task.status)

            if state is ExecutorState.BLOCKED and summary is None:
                summary = (
                    "Hermes Kanban task requires review"
                    if task.status == "review"
                    else "Hermes Kanban task is blocked"
                )
            elif state is ExecutorState.FAILED and summary is None:
                summary = f"Hermes Kanban task entered non-success terminal state: {task.status}"

            evidence = ()
            if state is ExecutorState.SUCCEEDED and latest_run is not None:
                evidence = self._evidence_from_metadata(latest_run.metadata)

            return ExecutorSnapshot(
                external_id=task.id,
                state=state,
                summary=summary,
                evidence=evidence,
            )
