from pathlib import Path

from hermeszooid.cnx.executors.hermes_kanban import HermesKanbanExecutor
from hermeszooid.cnx.execution import ExecutionCoordinator, ExecutionStatus, ExecutorState
from hermeszooid.cnx.store import CogentNexusStore


def test_real_dispatcher_claims_zooid_card_and_runs_in_zooid_workspace(tmp_path, monkeypatch):
    from hermes_cli import kanban_db as kb
    from hermes_cli import kanban_db_dispatch as dispatch

    hermeszooid_home = tmp_path / "zooid"
    executor = HermesKanbanExecutor(
        db_path=hermeszooid_home / "kanban" / "boards" / "cogentnexus" / "kanban.db",
        hermeszooid_home=hermeszooid_home,
        assignee="default",
    )

    with CogentNexusStore(hermeszooid_home / "cogentnexus.db") as store:
        project = store.create_project("drive one real dispatcher lifecycle")
        ticket = store.create_ticket(
            project.id,
            title="dispatcher lifecycle",
            objective="prove claim workspace spawn running completion",
            acceptance_criteria=["dispatcher-backed verification passes"],
            risk="medium",
            uncertainty="low",
        )
        step = store.add_step(ticket.id, "run bounded dispatcher verification")

        coordinator = ExecutionCoordinator(store, executor)
        dispatched = coordinator.tick(ticket.id)

        assert dispatched.status is ExecutionStatus.DISPATCHED
        assert dispatched.external_id is not None

        with executor.connect_board() as conn:
            card = kb.get_task(conn, dispatched.external_id)
            assert card is not None
            assert card.status == "ready"
            assert card.assignee == "default"
            assert card.workspace_path is not None

            planned_workspace = Path(card.workspace_path)
            assert planned_workspace.is_absolute()
            assert planned_workspace.parent == executor.workspaces_root
            assert planned_workspace.name == card.id

            # Profile availability is outside this task's boundary. The real
            # dispatcher claim/workspace/run bookkeeping remains under test.
            monkeypatch.setattr(dispatch, "_profile_exists_fn", lambda: None)
            # fake_spawn returns a synthetic PID. Keep Hermes' durable PID
            # bookkeeping under test, but replace the host-level fingerprint
            # probe that cannot identify a nonexistent process.
            monkeypatch.setattr(
                dispatch,
                "_process_fingerprint",
                lambda pid: f"hermeszooid-test-epoch|{int(pid)}",
            )

            spawns = []

            def fake_spawn(task, workspace, *, board=None):
                spawns.append((task.id, workspace, board, task.current_run_id))
                return 4242

            result = dispatch._dispatch_once_locked(
                conn,
                spawn_fn=fake_spawn,
                max_spawn=1,
                max_in_progress=1,
                reconcile_orphans=False,
            )

            assert len(result.spawned) == 1
            assert len(spawns) == 1

            task_id, workspace, board, run_id = spawns[0]
            assert task_id == card.id
            assert board is None
            assert run_id is not None
            assert Path(workspace) == planned_workspace
            assert planned_workspace.is_dir()

            running = kb.get_task(conn, card.id)
            assert running is not None
            assert running.status == "running"
            assert running.current_run_id == run_id
            assert running.worker_pid == 4242

        snapshot = executor.inspect(dispatched.external_id)
        assert snapshot.state is ExecutorState.RUNNING

        with executor.connect_board() as conn:
            running = kb.get_task(conn, dispatched.external_id)
            assert running is not None
            assert running.current_run_id is not None
            assert kb.complete_task(
                conn,
                running.id,
                result="dispatcher lifecycle completed",
                summary="dispatcher-backed verification passed",
                metadata={
                    "cogentnexus_evidence": [
                        {
                            "kind": "dispatcher_test",
                            "value": "real claim/workspace/run bookkeeping passed",
                            "criterion_index": 0,
                            "metadata": {
                                "worker_pid": 4242,
                                "workspace": str(planned_workspace),
                            },
                        }
                    ]
                },
                expected_run_id=running.current_run_id,
            )

        final = coordinator.tick(ticket.id)
        assert final.status is ExecutionStatus.DONE
        assert store.get_ticket(ticket.id).state.value == "done"
