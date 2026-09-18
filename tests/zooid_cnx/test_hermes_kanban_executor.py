from zooid_cnx.executors.hermes_kanban import HermesKanbanExecutor
from zooid_cnx.execution import ExecutionCoordinator, ExecutionStatus, ExecutorState
from zooid_cnx.store import CogentNexusStore


def _kanban_module():
    from hermes_cli import kanban_db as kb

    return kb


def _finish_with_cnx_evidence(
    executor: HermesKanbanExecutor,
    task_id: str,
    *,
    criterion_index: int = 0,
):
    kb = _kanban_module()
    with executor.connect_board() as conn:
        claimed = kb.claim_task(conn, task_id, claimer="zooid-test")
        assert claimed is not None
        assert claimed.current_run_id is not None
        assert kb.complete_task(
            conn,
            task_id,
            result="artifact built",
            summary="verification passed",
            metadata={
                "cogentnexus_evidence": [
                    {
                        "kind": "test",
                        "value": "pytest passed",
                        "criterion_index": criterion_index,
                        "metadata": {"source": "hermes-kanban-test"},
                    }
                ]
            },
            expected_run_id=claimed.current_run_id,
        )


def test_default_storage_and_worker_environment_are_zooid_owned(tmp_path, monkeypatch):
    zooid_home = tmp_path / "hermeszooid"
    hermes_home = tmp_path / "live-hermes"
    monkeypatch.setenv("HERMESZOOID_HOME", str(zooid_home))
    monkeypatch.setenv("HERMES_HOME", str(hermes_home))
    monkeypatch.setenv("HERMES_KANBAN_HOME", str(hermes_home / "kanban-live"))

    executor = HermesKanbanExecutor.open_default()

    expected_root = zooid_home / "kanban" / "boards" / "cogentnexus"
    assert executor.db_path == expected_root / "kanban.db"

    env = executor.worker_env()
    assert env["HERMES_KANBAN_HOME"] == str(zooid_home)
    assert env["HERMES_KANBAN_BOARD"] == "cogentnexus"
    assert env["HERMES_KANBAN_DB"] == str(expected_root / "kanban.db")
    assert env["HERMES_KANBAN_WORKSPACES_ROOT"] == str(expected_root / "workspaces")
    assert env["HERMES_KANBAN_ATTACHMENTS_ROOT"] == str(expected_root / "attachments")
    assert all(str(hermes_home) not in value for value in env.values())


def test_submit_find_and_restart_are_idempotent_on_real_kanban_db(tmp_path):
    db_path = tmp_path / "hermeszooid" / "kanban" / "boards" / "cogentnexus" / "kanban.db"
    executor = HermesKanbanExecutor(db_path=db_path)
    operation_key = "cnx:tkt_1:stp_1:execute"

    first = executor.submit(
        operation_key=operation_key,
        title="bounded step",
        body='{"acceptance_criteria":["tests pass"],"step":"run tests"}',
    )
    second = executor.submit(
        operation_key=operation_key,
        title="bounded step duplicate",
        body="must not create another card",
    )

    assert first == second
    assert db_path.is_file()

    kb = _kanban_module()
    with executor.connect_board() as conn:
        rows = conn.execute(
            "SELECT id FROM tasks WHERE idempotency_key = ?",
            (operation_key,),
        ).fetchall()
        assert [row["id"] for row in rows] == [first]
        task = kb.get_task(conn, first)
        assert task is not None
        assert task.status == "ready"
        assert task.idempotency_key == operation_key
        assert "cogentnexus_evidence" in (task.body or "")

    restarted = HermesKanbanExecutor(db_path=db_path)
    found = restarted.find(operation_key)
    assert found is not None
    assert found.external_id == first
    assert found.state is ExecutorState.QUEUED


def test_real_kanban_done_and_blocked_states_map_without_guessing(tmp_path):
    db_path = tmp_path / "board" / "kanban.db"
    executor = HermesKanbanExecutor(db_path=db_path)

    done_id = executor.submit(
        operation_key="cnx:done",
        title="done case",
        body="perform one bounded action",
    )
    _finish_with_cnx_evidence(executor, done_id)

    done = executor.inspect(done_id)
    assert done.state is ExecutorState.SUCCEEDED
    assert done.summary == "verification passed"
    assert len(done.evidence) == 1
    assert done.evidence[0].kind == "test"
    assert done.evidence[0].value == "pytest passed"
    assert done.evidence[0].criterion_index == 0
    assert done.evidence[0].metadata == {"source": "hermes-kanban-test"}

    blocked_id = executor.submit(
        operation_key="cnx:blocked",
        title="blocked case",
        body="perform another bounded action",
    )
    kb = _kanban_module()
    with executor.connect_board() as conn:
        claimed = kb.claim_task(conn, blocked_id, claimer="zooid-test")
        assert claimed is not None
        assert kb.block_task(
            conn,
            blocked_id,
            reason="provider capability unavailable",
            expected_run_id=claimed.current_run_id,
        )

    blocked = executor.inspect(blocked_id)
    assert blocked.state is ExecutorState.BLOCKED
    assert "provider capability unavailable" in (blocked.summary or "")


def test_execution_coordinator_reaches_done_through_real_kanban_adapter(tmp_path):
    cnx_db = tmp_path / "hermeszooid" / "cogentnexus.db"
    kanban_db = tmp_path / "hermeszooid" / "kanban" / "boards" / "cogentnexus" / "kanban.db"
    executor = HermesKanbanExecutor(db_path=kanban_db)

    with CogentNexusStore(cnx_db) as store:
        project = store.create_project("preserve user intent through a real executor")
        ticket = store.create_ticket(
            project.id,
            title="real kanban bridge",
            objective="execute one bounded step through Hermes Kanban",
            acceptance_criteria=["tests pass"],
            risk="medium",
            uncertainty="low",
        )
        step = store.add_step(ticket.id, "run the bounded verification")

        coordinator = ExecutionCoordinator(store, executor)
        dispatched = coordinator.tick(ticket.id)

        assert dispatched.status is ExecutionStatus.DISPATCHED
        assert dispatched.step_id == step.id
        assert dispatched.external_id is not None

        _finish_with_cnx_evidence(executor, dispatched.external_id)

        result = coordinator.tick(ticket.id)
        assert result.status is ExecutionStatus.DONE
        assert store.get_ticket(ticket.id).state.value == "done"


def test_done_without_structured_acceptance_evidence_does_not_auto_accept(tmp_path):
    cnx_db = tmp_path / "cnx.db"
    kanban_db = tmp_path / "kanban.db"
    executor = HermesKanbanExecutor(db_path=kanban_db)

    with CogentNexusStore(cnx_db) as store:
        project = store.create_project("evidence must remain explicit")
        ticket = store.create_ticket(
            project.id,
            title="no evidence shortcut",
            objective="do not treat prose success as acceptance",
            acceptance_criteria=["artifact independently verified"],
        )
        store.add_step(ticket.id, "produce artifact")

        coordinator = ExecutionCoordinator(store, executor)
        dispatched = coordinator.tick(ticket.id)

        kb = _kanban_module()
        with executor.connect_board() as conn:
            claimed = kb.claim_task(conn, dispatched.external_id, claimer="zooid-test")
            assert claimed is not None
            assert kb.complete_task(
                conn,
                dispatched.external_id,
                result="looks good",
                summary="worker says done",
                metadata={},
                expected_run_id=claimed.current_run_id,
            )

        result = coordinator.tick(ticket.id)
        assert result.status is ExecutionStatus.NEEDS_ACCEPTANCE_EVIDENCE
        assert store.get_ticket(ticket.id).state.value != "done"
