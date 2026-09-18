import json
import os
import stat
import time
from pathlib import Path

from hermeszooid.cnx.executors.hermes_kanban import HermesKanbanExecutor


def _write_fake_hermes(path: Path, receipt: Path) -> None:
    script = f"""#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

payload = {{
    "argv": sys.argv[1:],
    "cwd": os.getcwd(),
    "environment": {{
        key: os.environ.get(key)
        for key in (
            "HERMES_KANBAN_TASK",
            "HERMES_KANBAN_RUN_ID",
            "HERMES_KANBAN_CLAIM_LOCK",
            "HERMES_KANBAN_WORKSPACE",
            "HERMES_KANBAN_BRANCH",
            "HERMES_KANBAN_DB",
            "HERMES_KANBAN_BOARD",
            "HERMES_KANBAN_WORKSPACES_ROOT",
            "HERMES_SESSION_SOURCE",
            "HERMES_PROFILE",
            "TERMINAL_CWD",
            "HERMES_DELEGATED_CHILD_CONTEXT",
        )
    }},
}}
Path({str(receipt)!r}).write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
"""
    path.write_text(script, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _wait_receipt(path: Path, timeout: float = 10.0) -> dict:
    deadline = time.monotonic() + timeout
    last_error = None
    while time.monotonic() < deadline:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError, OSError) as exc:
            last_error = exc
            time.sleep(0.02)
    raise TimeoutError(f"fake Hermes worker did not write receipt: {last_error}")


def test_real_default_spawn_pins_zooid_worker_envelope_without_provider(tmp_path, monkeypatch):
    from hermes_cli import kanban_db as kb
    from hermes_cli.kanban_db_dispatch import _default_spawn

    hermeszooid_home = tmp_path / "zooid"
    executor = HermesKanbanExecutor(
        db_path=hermeszooid_home / "kanban" / "boards" / "cogentnexus" / "kanban.db",
        hermeszooid_home=hermeszooid_home,
        board="cogentnexus",
        assignee="default",
    )

    task_id = executor.submit(
        operation_key="cnx:task007:worker-envelope",
        title="worker subprocess envelope",
        body="record the real Hermes worker launch envelope",
    )

    with executor.connect_board() as conn:
        claimed = kb.claim_task(conn, task_id, claimer="task007-test")
        assert claimed is not None
        assert claimed.current_run_id is not None
        assert claimed.claim_lock
        workspace = Path(claimed.workspace_path)
        workspace.mkdir(parents=True, exist_ok=True)
        claimed = kb.get_task(conn, task_id)
        assert claimed is not None

    receipt = tmp_path / "worker-envelope.json"
    fake_hermes = tmp_path / "fake-hermes"
    _write_fake_hermes(fake_hermes, receipt)

    # Route the real spawn path to the deterministic executable while keeping
    # every Kanban surface on the dedicated Zooid board.
    monkeypatch.setenv("HERMES_BIN", str(fake_hermes))
    for key, value in executor.worker_env().items():
        monkeypatch.setenv(key, value)
    monkeypatch.setenv("ZOOID_HOME", str(hermeszooid_home))

    pid = _default_spawn(claimed, str(workspace), board=executor.board)
    assert isinstance(pid, int) and pid > 0

    payload = _wait_receipt(receipt)
    try:
        waited_pid, status = os.waitpid(pid, 0)
        assert waited_pid == pid
        assert os.waitstatus_to_exitcode(status) == 0
    except ChildProcessError:
        # Some Python/platform combinations may reap a very short-lived child
        # before the explicit wait. The durable receipt is still authoritative.
        pass

    env = payload["environment"]
    assert Path(payload["cwd"]) == workspace.resolve()
    assert env["HERMES_KANBAN_TASK"] == task_id
    assert env["HERMES_KANBAN_RUN_ID"] == str(claimed.current_run_id)
    assert env["HERMES_KANBAN_CLAIM_LOCK"] == claimed.claim_lock
    assert Path(env["HERMES_KANBAN_WORKSPACE"]) == workspace.resolve()
    assert Path(env["HERMES_KANBAN_DB"]) == executor.db_path
    assert env["HERMES_KANBAN_BOARD"] == executor.board
    assert Path(env["HERMES_KANBAN_WORKSPACES_ROOT"]) == executor.workspaces_root
    assert env["HERMES_SESSION_SOURCE"] == "kanban"
    assert env["HERMES_PROFILE"] == "default"
    assert Path(env["TERMINAL_CWD"]) == workspace.resolve()
    assert env["HERMES_DELEGATED_CHILD_CONTEXT"] is None

    argv = payload["argv"]
    assert argv[:3] == ["-p", "default", "--cli"]
    assert "--accept-hooks" in argv
    assert argv[-3:] == ["chat", "-q", f"work kanban task {task_id}"]
    assert "--provider" not in argv
    assert "-m" not in argv

    # The fake worker exiting does not rewrite the Kanban lifecycle by itself;
    # dispatcher reconciliation remains the owner of crash/retry semantics.
    with executor.connect_board() as conn:
        after = kb.get_task(conn, task_id)
        assert after is not None
        assert after.status == "running"
        assert after.current_run_id == claimed.current_run_id
        assert after.claim_lock == claimed.claim_lock
