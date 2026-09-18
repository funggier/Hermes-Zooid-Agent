"""Child entrypoint for the Zooid-owned dispatcher process boundary."""

from __future__ import annotations

import argparse
import json
import os
import signal
import threading
import time
from pathlib import Path
from typing import Any

from .executors.hermes_kanban import HermesKanbanExecutor


_ENV_KEYS = (
    "HERMES_KANBAN_HOME",
    "HERMES_KANBAN_BOARD",
    "HERMES_KANBAN_DB",
    "HERMES_KANBAN_WORKSPACES_ROOT",
    "HERMES_KANBAN_ATTACHMENTS_ROOT",
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m zooid_cnx.dispatcher_child")
    parser.add_argument("--mode", choices=("probe", "dispatch-task"), required=True)
    parser.add_argument("--db", required=True)
    parser.add_argument("--board", required=True)
    parser.add_argument("--ready-file", required=True)
    parser.add_argument("--interval", type=float, default=0.25)
    parser.add_argument("--task-id")
    parser.add_argument("--timeout", type=float, default=300.0)
    return parser


def _validate_process_identity(db_path: Path, board: str) -> None:
    env_db = (os.environ.get("HERMES_KANBAN_DB") or "").strip()
    env_board = (os.environ.get("HERMES_KANBAN_BOARD") or "").strip()
    hermeszooid_home = (os.environ.get("HERMESZOOID_HOME") or "").strip()

    if not hermeszooid_home:
        raise RuntimeError("dispatcher child requires HERMESZOOID_HOME")
    if not env_db:
        raise RuntimeError("dispatcher child requires HERMES_KANBAN_DB")
    if Path(env_db).expanduser().resolve() != db_path:
        raise RuntimeError("dispatcher child DB argv/env mismatch")
    if env_board != board:
        raise RuntimeError("dispatcher child board argv/env mismatch")

    for key in (
        "HERMES_KANBAN_TASK",
        "HERMES_KANBAN_RUN_ID",
        "HERMES_KANBAN_CLAIM_LOCK",
        "HERMES_KANBAN_WORKSPACE",
    ):
        if os.environ.get(key):
            raise RuntimeError(f"dispatcher child inherited worker identity: {key}")


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )
    os.replace(temp, path)


def _snapshot(
    executor: HermesKanbanExecutor,
    *,
    started_at: float,
) -> dict[str, Any]:
    with executor.connect_board() as conn:
        task_ids = [
            str(row["id"])
            for row in conn.execute(
                "SELECT id FROM tasks ORDER BY created_at ASC, id ASC"
            ).fetchall()
        ]
    return {
        "pid": os.getpid(),
        "started_at": started_at,
        "observed_at": time.time(),
        "db_path": str(executor.db_path),
        "board": executor.board,
        "task_ids": task_ids,
        "environment": {key: os.environ.get(key, "") for key in _ENV_KEYS},
    }


def _dispatch_task(
    *,
    db_path: Path,
    board: str,
    task_id: str,
    ready_file: Path,
    interval: float,
    timeout: float,
) -> int:
    """Run current Hermes dispatcher ticks until one bounded task is terminal."""
    if not task_id:
        raise ValueError("dispatch-task mode requires --task-id")
    if timeout <= 0:
        raise ValueError("timeout must be > 0")

    from hermes_cli import kanban_db as kb
    from hermes_cli import kanban_db_connect as kbc
    from hermes_cli import kanban_db_dispatch as kbd

    terminal = {"done", "blocked", "review", "archived"}
    started_at = time.time()
    deadline = time.monotonic() + timeout
    last_spawned = []

    while True:
        with kbc.connect_closing(db_path) as conn:
            task = kb.get_task(conn, task_id)
            if task is None:
                raise KeyError(f"unknown Kanban task: {task_id}")

            if task.status not in terminal:
                result = kbd.dispatch_once(
                    conn,
                    max_spawn=1,
                    failure_limit=1,
                    board=board,
                )
                last_spawned = list(result.spawned)
                task = kb.get_task(conn, task_id)
                if task is None:
                    raise KeyError(f"Kanban task disappeared: {task_id}")

            payload = {
                "pid": os.getpid(),
                "mode": "dispatch-task",
                "started_at": started_at,
                "observed_at": time.time(),
                "db_path": str(db_path),
                "board": board,
                "task_id": task_id,
                "task_status": task.status,
                "worker_pid": task.worker_pid,
                "current_run_id": task.current_run_id,
                "spawned": last_spawned,
                "environment": {key: os.environ.get(key, "") for key in _ENV_KEYS},
            }
            _atomic_json(ready_file, payload)

            if task.status in terminal:
                return 0 if task.status == "done" else 2

        if time.monotonic() >= deadline:
            return 124
        time.sleep(max(interval, 0.05))


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    db_path = Path(args.db).expanduser().resolve()
    board = str(args.board).strip()
    ready_file = Path(args.ready_file).expanduser().resolve()
    interval = max(float(args.interval), 0.01)

    _validate_process_identity(db_path, board)

    if args.mode == "dispatch-task":
        return _dispatch_task(
            db_path=db_path,
            board=board,
            task_id=str(args.task_id or "").strip(),
            ready_file=ready_file,
            interval=interval,
            timeout=float(args.timeout),
        )

    executor = HermesKanbanExecutor(
        db_path=db_path,
        hermeszooid_home=Path(os.environ["HERMESZOOID_HOME"]),
        board=board,
    )

    stop = threading.Event()

    def _handle_signal(_signum, _frame) -> None:
        stop.set()

    for sig_name in ("SIGTERM", "SIGINT"):
        sig = getattr(signal, sig_name, None)
        if sig is not None:
            try:
                signal.signal(sig, _handle_signal)
            except (ValueError, OSError):
                pass

    started_at = time.time()
    _atomic_json(ready_file, _snapshot(executor, started_at=started_at))

    while not stop.wait(interval):
        _atomic_json(ready_file, _snapshot(executor, started_at=started_at))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
