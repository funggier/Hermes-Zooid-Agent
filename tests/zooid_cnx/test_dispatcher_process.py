import json
import os
from pathlib import Path

from zooid_cnx.dispatcher_process import ZooidDispatcherProcess
from zooid_cnx.executors.hermes_kanban import HermesKanbanExecutor


def test_dispatcher_child_has_isolated_env_same_board_and_restart_stability(tmp_path, monkeypatch):
    zooid_home = tmp_path / "hermeszooid"
    parent_sentinel = str(tmp_path / "parent-must-not-change.db")
    monkeypatch.setenv("HERMES_KANBAN_DB", parent_sentinel)
    monkeypatch.setenv("HERMES_KANBAN_BOARD", "parent-board")

    executor = HermesKanbanExecutor(
        db_path=zooid_home / "kanban" / "boards" / "cogentnexus" / "kanban.db",
        zooid_home=zooid_home,
        board="cogentnexus",
        assignee="default",
    )
    task_id = executor.submit(
        operation_key="cnx:task006:probe",
        title="dispatcher process boundary",
        body="prove child process isolation",
    )

    process = ZooidDispatcherProcess(
        executor,
        state_dir=zooid_home / "dispatcher",
        probe_interval=0.05,
    )

    expected_env = executor.worker_env()

    first = process.start_probe()
    try:
        ready = process.wait_ready(timeout=10)
        assert ready["pid"] == first.pid
        assert Path(ready["db_path"]) == executor.db_path
        assert ready["board"] == executor.board
        assert task_id in ready["task_ids"]
        assert ready["environment"] == {
            "HERMES_KANBAN_HOME": expected_env["HERMES_KANBAN_HOME"],
            "HERMES_KANBAN_BOARD": expected_env["HERMES_KANBAN_BOARD"],
            "HERMES_KANBAN_DB": expected_env["HERMES_KANBAN_DB"],
            "HERMES_KANBAN_WORKSPACES_ROOT": expected_env["HERMES_KANBAN_WORKSPACES_ROOT"],
            "HERMES_KANBAN_ATTACHMENTS_ROOT": expected_env["HERMES_KANBAN_ATTACHMENTS_ROOT"],
        }

        # The parent process remains untouched. Isolation comes from Popen(env=...),
        # never from temporarily rewriting process-global routing variables.
        assert os.environ["HERMES_KANBAN_DB"] == parent_sentinel
        assert os.environ["HERMES_KANBAN_BOARD"] == "parent-board"
    finally:
        process.stop(timeout=5)

    assert first.poll() is not None

    # A restart must reopen the same durable board, not create a new routing identity.
    second = process.start_probe()
    try:
        ready2 = process.wait_ready(timeout=10)
        assert Path(ready2["db_path"]) == executor.db_path
        assert ready2["board"] == "cogentnexus"
        assert task_id in ready2["task_ids"]
        assert json.loads(process.ready_file.read_text(encoding="utf-8"))["pid"] == second.pid
    finally:
        process.stop(timeout=5)

    assert second.poll() is not None


def test_dispatcher_child_env_scrubs_worker_identity_without_mutating_parent(tmp_path, monkeypatch):
    zooid_home = tmp_path / "hermeszooid"
    executor = HermesKanbanExecutor(
        db_path=zooid_home / "kanban" / "boards" / "cogentnexus" / "kanban.db",
        zooid_home=zooid_home,
    )
    for key, value in {
        "HERMES_KANBAN_TASK": "parent-task",
        "HERMES_KANBAN_RUN_ID": "99",
        "HERMES_KANBAN_CLAIM_LOCK": "parent-lock",
        "HERMES_KANBAN_WORKSPACE": "/parent/workspace",
        "HERMES_KANBAN_BRANCH": "parent-branch",
        "HERMES_KANBAN_GOAL_MODE": "1",
        "HERMES_KANBAN_GOAL_MAX_TURNS": "12",
    }.items():
        monkeypatch.setenv(key, value)

    process = ZooidDispatcherProcess(executor, state_dir=zooid_home / "dispatcher")
    child_env = process.child_env()

    for key in (
        "HERMES_KANBAN_TASK",
        "HERMES_KANBAN_RUN_ID",
        "HERMES_KANBAN_CLAIM_LOCK",
        "HERMES_KANBAN_WORKSPACE",
        "HERMES_KANBAN_BRANCH",
        "HERMES_KANBAN_GOAL_MODE",
        "HERMES_KANBAN_GOAL_MAX_TURNS",
    ):
        assert key not in child_env
        assert key in os.environ

    assert child_env["HERMESZOOID_HOME"] == str(zooid_home.resolve())
    assert child_env["HERMES_KANBAN_DB"] == str(executor.db_path)
