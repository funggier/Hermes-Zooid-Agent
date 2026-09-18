"""Bounded live-provider acceptance for the Zooid CogentNexus path."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from .dispatcher_process import ZooidDispatcherProcess
from .execution import ExecutionCoordinator, ExecutionStatus, ExecutorState
from .executors.hermes_kanban import HermesKanbanExecutor
from .store import AcceptanceError, CogentNexusStore, StepState


_SAFE_ID = re.compile(r"[A-Za-z0-9_.-]+")


class PreflightStatus(str, Enum):
    READY = "ready"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class PreflightResult:
    status: PreflightStatus
    profile_home: Optional[Path]
    provider: Optional[str]
    model: Optional[str]
    hermes_argv: tuple[str, ...]
    detail: str = ""


class AcceptanceStatus(str, Enum):
    PREPARED = "prepared"
    WAITING_EXTERNAL = "waiting_external"
    NEEDS_WORKER_EVIDENCE = "needs_worker_evidence"
    ARTIFACT_MISSING = "artifact_missing"
    ARTIFACT_MISMATCH = "artifact_mismatch"
    UNTRUSTED_EVIDENCE = "untrusted_evidence"
    BLOCKED = "blocked"
    DONE = "done"


@dataclass(frozen=True)
class AcceptancePlan:
    home: Path
    acceptance_id: str
    profile: str
    provider: Optional[str]
    model: Optional[str]
    timeout_seconds: int
    expected_text: str
    expected_sha256: str
    board: str
    cnx_db: Path
    kanban_db: Path
    artifact_path: Path
    state_dir: Path

    @classmethod
    def create(
        cls,
        *,
        home: Path | str,
        acceptance_id: str,
        profile: str = "default",
        provider: str | None = None,
        model: str | None = None,
        timeout_seconds: int = 180,
        expected_text: str = "ZOOID-LIVE-ACCEPTANCE\n",
    ) -> "AcceptancePlan":
        home_path = Path(home).expanduser().resolve()
        clean_id = str(acceptance_id).strip()
        if not clean_id or not _SAFE_ID.fullmatch(clean_id):
            raise ValueError("acceptance_id must contain only letters, digits, dot, underscore, or dash")
        clean_profile = str(profile).strip()
        if not clean_profile:
            raise ValueError("profile must not be empty")
        clean_provider = str(provider).strip() if provider is not None else None
        clean_provider = clean_provider or None
        clean_model = str(model).strip() if model is not None else None
        clean_model = clean_model or None
        if clean_provider and not clean_model:
            raise ValueError("provider requires an explicit model")
        timeout = int(timeout_seconds)
        if timeout <= 0:
            raise ValueError("timeout_seconds must be > 0")
        expected = str(expected_text)
        digest = hashlib.sha256(expected.encode("utf-8")).hexdigest()
        board = "cogentnexus-acceptance"
        root = home_path / "kanban" / "boards" / board
        artifact = home_path / "artifacts" / clean_id / "acceptance-result.txt"
        return cls(
            home=home_path,
            acceptance_id=clean_id,
            profile=clean_profile,
            provider=clean_provider,
            model=clean_model,
            timeout_seconds=timeout,
            expected_text=expected,
            expected_sha256=digest,
            board=board,
            cnx_db=home_path / "cogentnexus.db",
            kanban_db=root / "kanban.db",
            artifact_path=artifact,
            state_dir=home_path / "dispatcher",
        )


@dataclass(frozen=True)
class PreparedAcceptance:
    project_id: str
    ticket_id: str
    step_id: str
    external_id: str


@dataclass(frozen=True)
class AcceptanceResult:
    status: AcceptanceStatus
    ticket_id: str
    external_id: str
    artifact_sha256: Optional[str] = None
    detail: Optional[str] = None
    dispatcher_returncode: Optional[int] = None


class LiveProviderAcceptance:
    """Prepare, dispatch, and independently verify one bounded live task."""

    def __init__(self, plan: AcceptancePlan):
        self.plan = plan
        self.executor = HermesKanbanExecutor(
            db_path=plan.kanban_db,
            zooid_home=plan.home,
            board=plan.board,
            assignee=plan.profile,
            model_override=plan.model,
            provider_override=plan.provider,
            max_runtime_seconds=plan.timeout_seconds,
            max_retries=1,
        )

    def open_store(self) -> CogentNexusStore:
        return CogentNexusStore(self.plan.cnx_db)

    def preflight(self) -> PreflightResult:
        """Read-only runtime resolution before creating acceptance state.

        This deliberately does not inspect or return secret values. Provider
        authentication is proven only by the later live worker execution.
        """
        try:
            from hermes_cli.profiles import resolve_profile_env

            profile_home = Path(
                resolve_profile_env(self.plan.profile)
            ).expanduser().resolve()
            if not profile_home.exists():
                return PreflightResult(
                    PreflightStatus.BLOCKED,
                    None,
                    self.plan.provider,
                    self.plan.model,
                    (),
                    f"profile home does not exist: {profile_home}",
                )
        except Exception as exc:
            return PreflightResult(
                PreflightStatus.BLOCKED,
                None,
                self.plan.provider,
                self.plan.model,
                (),
                f"profile resolution failed: {exc}",
            )

        try:
            from hermes_cli.kanban_db_dispatch import _resolve_hermes_argv

            hermes_argv = tuple(str(part) for part in _resolve_hermes_argv())
        except Exception as exc:
            return PreflightResult(
                PreflightStatus.BLOCKED,
                profile_home,
                self.plan.provider,
                self.plan.model,
                (),
                f"Hermes worker launcher resolution failed: {exc}",
            )

        if not hermes_argv:
            return PreflightResult(
                PreflightStatus.BLOCKED,
                profile_home,
                self.plan.provider,
                self.plan.model,
                (),
                "Hermes worker launcher resolved to an empty argv",
            )

        runtime = (
            f"explicit provider={self.plan.provider!r}, model={self.plan.model!r}"
            if self.plan.provider or self.plan.model
            else "provider/model inherited from selected Hermes profile"
        )
        return PreflightResult(
            PreflightStatus.READY,
            profile_home,
            self.plan.provider,
            self.plan.model,
            hermes_argv,
            f"{runtime}; credentials are intentionally not read or exposed by preflight",
        )

    def _step_description(self) -> str:
        return (
            "Create the local acceptance artifact at "
            f"{self.plan.artifact_path} with EXACT UTF-8 content "
            f"{self.plan.expected_text!r}. Read it back before reporting success. "
            "When completing the Kanban task, provide structured "
            "metadata.cogentnexus_evidence with exactly one worker-owned item: "
            "kind='worker_completion', a truthful value, criterion_index=0. "
            "Do not provide evidence for criterion_index=1; that criterion is "
            "reserved for independent Zooid parent SHA-256 verification."
        )

    def prepare(self) -> PreparedAcceptance:
        self.plan.home.mkdir(parents=True, exist_ok=True)
        self.plan.artifact_path.parent.mkdir(parents=True, exist_ok=True)

        prefix = f"live-acceptance:{self.plan.acceptance_id}"
        with self.open_store() as store:
            project = store.create_project(
                "Prove one bounded real provider execution through Zooid CogentNexus.",
                op_key=f"{prefix}:project",
            )
            ticket = store.create_ticket(
                project.id,
                title="bounded live provider acceptance",
                objective="Run one harmless provider-backed worker and verify its local artifact.",
                acceptance_criteria=[
                    "worker supplied structured completion evidence",
                    f"local artifact sha256 equals {self.plan.expected_sha256}",
                ],
                risk="low",
                uncertainty="medium",
                op_key=f"{prefix}:ticket",
            )
            step = store.add_step(
                ticket.id,
                self._step_description(),
                op_key=f"{prefix}:step",
            )
            coordinator = ExecutionCoordinator(store, self.executor)
            result = coordinator.tick(ticket.id)
            binding = store.get_external_binding(step.id)
            external_id = result.external_id or (binding.external_id if binding else None)
            if not external_id:
                raise RuntimeError(f"acceptance preparation did not produce an external task: {result}")

        # Pin the task workspace to the artifact directory so relative worker
        # tools and TERMINAL_CWD remain inside the disposable acceptance home.
        from hermes_cli import kanban_db_workspace as kbw

        with self.executor.connect_board() as conn:
            kbw.set_workspace_path(conn, external_id, str(self.plan.artifact_path.parent))

        return PreparedAcceptance(project.id, ticket.id, step.id, external_id)

    def child_env(self) -> dict[str, str]:
        process = ZooidDispatcherProcess(self.executor, state_dir=self.plan.state_dir)
        env = process.child_env()
        env["ZOOID_HOME"] = str(self.plan.home)
        return env

    def dispatch_command(self, prepared: PreparedAcceptance) -> list[str]:
        return [
            sys.executable,
            "-m",
            "zooid_cnx.dispatcher_child",
            "--mode",
            "dispatch-task",
            "--db",
            str(self.plan.kanban_db),
            "--board",
            self.plan.board,
            "--ready-file",
            str(self.plan.state_dir / "live-dispatch.json"),
            "--interval",
            "0.5",
            "--task-id",
            prepared.external_id,
            "--timeout",
            str(self.plan.timeout_seconds),
        ]

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def reconcile(self, prepared: PreparedAcceptance) -> AcceptanceResult:
        snapshot = self.executor.inspect(prepared.external_id)
        if snapshot.state is ExecutorState.SUCCEEDED:
            if any(item.criterion_index == 1 for item in snapshot.evidence):
                return AcceptanceResult(
                    AcceptanceStatus.UNTRUSTED_EVIDENCE,
                    prepared.ticket_id,
                    prepared.external_id,
                    detail="worker attempted to satisfy parent-owned local verification criterion",
                )

        with self.open_store() as store:
            coordinator = ExecutionCoordinator(store, self.executor)
            bridge = coordinator.tick(prepared.ticket_id)

            if bridge.status is ExecutionStatus.BLOCKED:
                return AcceptanceResult(
                    AcceptanceStatus.BLOCKED,
                    prepared.ticket_id,
                    prepared.external_id,
                    detail=bridge.detail,
                )
            if bridge.status in {
                ExecutionStatus.DISPATCHED,
                ExecutionStatus.WAITING_EXTERNAL,
                ExecutionStatus.NEEDS_VERIFICATION,
                ExecutionStatus.STEP_COMPLETED,
            }:
                return AcceptanceResult(
                    AcceptanceStatus.WAITING_EXTERNAL,
                    prepared.ticket_id,
                    prepared.external_id,
                    detail=bridge.detail,
                )

            step = store.get_step(prepared.step_id)
            if step.state is not StepState.DONE:
                return AcceptanceResult(
                    AcceptanceStatus.NEEDS_WORKER_EVIDENCE,
                    prepared.ticket_id,
                    prepared.external_id,
                    detail=bridge.detail,
                )

            if not self.plan.artifact_path.is_file():
                return AcceptanceResult(
                    AcceptanceStatus.ARTIFACT_MISSING,
                    prepared.ticket_id,
                    prepared.external_id,
                    detail=str(self.plan.artifact_path),
                )

            actual = self._sha256(self.plan.artifact_path)
            if actual != self.plan.expected_sha256:
                return AcceptanceResult(
                    AcceptanceStatus.ARTIFACT_MISMATCH,
                    prepared.ticket_id,
                    prepared.external_id,
                    artifact_sha256=actual,
                    detail=f"expected {self.plan.expected_sha256}",
                )

            store.record_evidence(
                prepared.ticket_id,
                prepared.step_id,
                kind="local_artifact_sha256",
                value=actual,
                criterion_index=1,
                metadata={"path": str(self.plan.artifact_path), "verified_by": "zooid-parent"},
                op_key=f"live-acceptance:{self.plan.acceptance_id}:local-artifact",
            )
            try:
                store.complete_ticket(
                    prepared.ticket_id,
                    summary="bounded live provider acceptance verified locally",
                    op_key=f"live-acceptance:{self.plan.acceptance_id}:complete-ticket",
                )
            except AcceptanceError as exc:
                return AcceptanceResult(
                    AcceptanceStatus.NEEDS_WORKER_EVIDENCE,
                    prepared.ticket_id,
                    prepared.external_id,
                    artifact_sha256=actual,
                    detail=str(exc),
                )

            return AcceptanceResult(
                AcceptanceStatus.DONE,
                prepared.ticket_id,
                prepared.external_id,
                artifact_sha256=actual,
            )

    def run_live(self, prepared: PreparedAcceptance) -> AcceptanceResult:
        completed = subprocess.run(
            self.dispatch_command(prepared),
            env=self.child_env(),
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=self.plan.timeout_seconds + 60,
            check=False,
        )
        result = self.reconcile(prepared)
        return AcceptanceResult(
            status=result.status,
            ticket_id=result.ticket_id,
            external_id=result.external_id,
            artifact_sha256=result.artifact_sha256,
            detail=result.detail or (completed.stderr.strip() or None),
            dispatcher_returncode=completed.returncode,
        )

    def describe(self) -> dict[str, Any]:
        return {
            "acceptance_id": self.plan.acceptance_id,
            "home": str(self.plan.home),
            "cnx_db": str(self.plan.cnx_db),
            "kanban_db": str(self.plan.kanban_db),
            "board": self.plan.board,
            "artifact_path": str(self.plan.artifact_path),
            "expected_sha256": self.plan.expected_sha256,
            "profile": self.plan.profile,
            "provider": self.plan.provider,
            "model": self.plan.model,
            "timeout_seconds": self.plan.timeout_seconds,
        }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m zooid_cnx.provider_acceptance")
    parser.add_argument("--home", required=True)
    parser.add_argument("--acceptance-id", required=True)
    parser.add_argument("--profile", default="default")
    parser.add_argument("--provider")
    parser.add_argument("--model")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--expected-text", default="ZOOID-LIVE-ACCEPTANCE\n")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--preflight", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    plan = AcceptancePlan.create(
        home=args.home,
        acceptance_id=args.acceptance_id,
        profile=args.profile,
        provider=args.provider,
        model=args.model,
        timeout_seconds=args.timeout,
        expected_text=args.expected_text,
    )
    runner = LiveProviderAcceptance(plan)
    if args.dry_run:
        print(json.dumps(runner.describe(), indent=2, sort_keys=True))
        return 0
    if args.preflight:
        result = runner.preflight()
        payload = asdict(result)
        payload["status"] = result.status.value
        if result.profile_home is not None:
            payload["profile_home"] = str(result.profile_home)
        payload["hermes_argv"] = list(result.hermes_argv)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0 if result.status is PreflightStatus.READY else 2

    preflight = runner.preflight()
    if preflight.status is not PreflightStatus.READY:
        payload = asdict(preflight)
        payload["status"] = preflight.status.value
        payload["profile_home"] = (
            str(preflight.profile_home) if preflight.profile_home is not None else None
        )
        payload["hermes_argv"] = list(preflight.hermes_argv)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 2

    prepared = runner.prepare()
    result = runner.run_live(prepared)
    payload = {**runner.describe(), "prepared": asdict(prepared), "result": asdict(result)}
    payload["result"]["status"] = result.status.value
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if result.status is AcceptanceStatus.DONE else 2


if __name__ == "__main__":
    raise SystemExit(main())
