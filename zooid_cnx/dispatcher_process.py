"""Parent-side process boundary for the Zooid Kanban dispatcher host."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Mapping, Optional

from .executors.hermes_kanban import HermesKanbanExecutor


_WORKER_IDENTITY_KEYS = (
    "HERMES_KANBAN_TASK",
    "HERMES_KANBAN_RUN_ID",
    "HERMES_KANBAN_CLAIM_LOCK",
    "HERMES_KANBAN_WORKSPACE",
    "HERMES_KANBAN_BRANCH",
    "HERMES_KANBAN_GOAL_MODE",
    "HERMES_KANBAN_GOAL_MAX_TURNS",
)


class ZooidDispatcherProcess:
    """Own one child process whose Kanban routing is fixed at spawn time.

    This class never mutates the parent process environment. The child gets
    an explicit copy, which is the concurrency-safe boundary required before
    Zooid can host more than one Project/dispatcher in the same parent.
    """

    def __init__(
        self,
        executor: HermesKanbanExecutor,
        *,
        state_dir: Path | str,
        probe_interval: float = 0.25,
        python_executable: str | None = None,
    ):
        self.executor = executor
        self.state_dir = Path(state_dir).expanduser().resolve()
        self.ready_file = self.state_dir / "dispatcher-ready.json"
        self.probe_interval = max(float(probe_interval), 0.01)
        self.python_executable = python_executable or sys.executable
        self._process: Optional[subprocess.Popen] = None

    @property
    def process(self) -> Optional[subprocess.Popen]:
        return self._process

    def child_env(
        self,
        base_env: Mapping[str, str] | None = None,
    ) -> dict[str, str]:
        env = dict(os.environ if base_env is None else base_env)
        for key in _WORKER_IDENTITY_KEYS:
            env.pop(key, None)

        env["ZOOID_HOME"] = str(self.executor.zooid_home)
        env.update(self.executor.worker_env())
        env["PYTHONUNBUFFERED"] = "1"
        return env

    def probe_command(self) -> list[str]:
        return [
            self.python_executable,
            "-m",
            "zooid_cnx.dispatcher_child",
            "--mode",
            "probe",
            "--db",
            str(self.executor.db_path),
            "--board",
            self.executor.board,
            "--ready-file",
            str(self.ready_file),
            "--interval",
            str(self.probe_interval),
        ]

    def start_probe(self) -> subprocess.Popen:
        if self._process is not None and self._process.poll() is None:
            raise RuntimeError("dispatcher child is already running")

        self.state_dir.mkdir(parents=True, exist_ok=True)
        try:
            self.ready_file.unlink()
        except FileNotFoundError:
            pass

        self._process = subprocess.Popen(
            self.probe_command(),
            env=self.child_env(),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        return self._process

    def wait_ready(self, *, timeout: float = 10.0) -> dict[str, Any]:
        deadline = time.monotonic() + max(float(timeout), 0.0)
        last_error: Exception | None = None
        while time.monotonic() <= deadline:
            proc = self._process
            if proc is None:
                raise RuntimeError("dispatcher child has not been started")
            if proc.poll() is not None:
                raise RuntimeError(
                    f"dispatcher child exited before ready receipt (code={proc.returncode})"
                )

            try:
                payload = json.loads(self.ready_file.read_text(encoding="utf-8"))
                if isinstance(payload, dict) and payload.get("pid") == proc.pid:
                    return payload
            except (FileNotFoundError, json.JSONDecodeError, OSError) as exc:
                last_error = exc
            time.sleep(0.02)

        detail = f": {last_error}" if last_error is not None else ""
        raise TimeoutError(
            f"dispatcher child did not become ready within {timeout}s{detail}"
        )

    def stop(self, *, timeout: float = 10.0) -> Optional[int]:
        proc = self._process
        if proc is None:
            return None
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=max(float(timeout), 0.01))
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=max(float(timeout), 0.01))
        self._process = None
        return proc.returncode
