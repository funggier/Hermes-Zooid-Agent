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
    parser.add_argument("--mode", choices=("probe",), required=True)
    parser.add_argument("--db", required=True)
    parser.add_argument("--board", required=True)
    parser.add_argument("--ready-file", required=True)
    parser.add_argument("--interval", type=float, default=0.25)
    return parser


def _validate_process_identity(db_path: Path, board: str) -> None:
    env_db = (os.environ.get("HERMES_KANBAN_DB") or "").strip()
    env_board = (os.environ.get("HERMES_KANBAN_BOARD") or "").strip()
    zooid_home = (os.environ.get("ZOOID_HOME") or "").strip()

    if not zooid_home:
        raise RuntimeError("dispatcher child requires ZOOID_HOME")
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


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    db_path = Path(args.db).expanduser().resolve()
    board = str(args.board).strip()
    ready_file = Path(args.ready_file).expanduser().resolve()
    interval = max(float(args.interval), 0.01)

    _validate_process_identity(db_path, board)

    executor = HermesKanbanExecutor(
        db_path=db_path,
        zooid_home=Path(os.environ["ZOOID_HOME"]),
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
