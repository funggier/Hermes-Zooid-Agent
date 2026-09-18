import os
from pathlib import Path

from zooid_cnx.provider_acceptance import (
    AcceptancePlan,
    AcceptanceStatus,
    LiveProviderAcceptance,
)


def _plan(tmp_path):
    return AcceptancePlan.create(
        home=tmp_path / "acceptance-home",
        acceptance_id="task008-test",
        profile="default",
        provider="openai",
        model="gpt-test",
        timeout_seconds=90,
        expected_text="ZOOID-TASK-008-ACCEPTED\n",
    )


def test_prepare_pins_provider_model_runtime_and_disposable_storage(tmp_path):
    from hermes_cli import kanban_db as kb

    plan = _plan(tmp_path)
    runner = LiveProviderAcceptance(plan)
    prepared = runner.prepare()

    assert plan.cnx_db.is_relative_to(plan.home)
    assert plan.kanban_db.is_relative_to(plan.home)
    assert plan.artifact_path.is_relative_to(plan.home)

    with runner.executor.connect_board() as conn:
        task = kb.get_task(conn, prepared.external_id)
        assert task is not None
        assert task.assignee == "default"
        assert task.provider_override == "openai"
        assert task.model_override == "gpt-test"
        assert task.max_runtime_seconds == 90
        assert task.max_retries == 1
        assert Path(task.workspace_path).is_relative_to(plan.home)
        assert str(plan.artifact_path) in (task.body or "")
        assert "criterion_index" in (task.body or "")

    with runner.open_store() as store:
        ticket = store.get_ticket(prepared.ticket_id)
        assert len(ticket.acceptance_criteria) == 2
        assert "worker" in ticket.acceptance_criteria[0].lower()
        assert plan.expected_sha256 in ticket.acceptance_criteria[1]


def test_dispatch_child_env_and_command_do_not_mutate_parent(tmp_path, monkeypatch):
    plan = _plan(tmp_path)
    runner = LiveProviderAcceptance(plan)
    prepared = runner.prepare()

    monkeypatch.setenv("HERMES_KANBAN_DB", "/parent/not-hermeszooid.db")
    monkeypatch.setenv("HERMES_KANBAN_BOARD", "parent-board")

    child_env = runner.child_env()
    command = runner.dispatch_command(prepared)

    assert os.environ["HERMES_KANBAN_DB"] == "/parent/not-hermeszooid.db"
    assert os.environ["HERMES_KANBAN_BOARD"] == "parent-board"
    assert child_env["HERMES_KANBAN_DB"] == str(plan.kanban_db)
    assert child_env["HERMES_KANBAN_BOARD"] == plan.board
    assert child_env["HERMESZOOID_HOME"] == str(plan.home)
    assert "--mode" in command and "dispatch-task" in command
    assert "--task-id" in command and prepared.external_id in command
    assert "--timeout" in command and str(plan.timeout_seconds) in command


def test_worker_evidence_alone_cannot_finish_without_local_artifact_hash(tmp_path):
    from hermes_cli import kanban_db as kb

    plan = _plan(tmp_path)
    runner = LiveProviderAcceptance(plan)
    prepared = runner.prepare()

    with runner.executor.connect_board() as conn:
        claimed = kb.claim_task(conn, prepared.external_id, claimer="task008-test")
        assert claimed is not None
        assert kb.complete_task(
            conn,
            prepared.external_id,
            result="worker reports success",
            summary="worker wrote acceptance artifact",
            metadata={
                "cogentnexus_evidence": [
                    {
                        "kind": "worker_completion",
                        "value": "worker reports artifact created",
                        "criterion_index": 0,
                    }
                ]
            },
            expected_run_id=claimed.current_run_id,
        )

    missing = runner.reconcile(prepared)
    assert missing.status is AcceptanceStatus.ARTIFACT_MISSING
    with runner.open_store() as store:
        assert store.get_ticket(prepared.ticket_id).state.value != "done"

    plan.artifact_path.parent.mkdir(parents=True, exist_ok=True)
    plan.artifact_path.write_text(plan.expected_text, encoding="utf-8")

    done = runner.reconcile(prepared)
    assert done.status is AcceptanceStatus.DONE
    assert done.artifact_sha256 == plan.expected_sha256
    with runner.open_store() as store:
        assert store.get_ticket(prepared.ticket_id).state.value == "done"
        evidence = store.list_evidence(prepared.ticket_id)
        assert {item.criterion_index for item in evidence} == {0, 1}


def test_preflight_is_read_only_and_reports_explicit_runtime(tmp_path, monkeypatch):
    from zooid_cnx.provider_acceptance import PreflightStatus

    hermes_home = tmp_path / "hermes-profile"
    hermes_home.mkdir()
    monkeypatch.setenv("HERMES_HOME", str(hermes_home))
    monkeypatch.setenv("OPENAI_API_KEY", "must-never-be-returned")

    plan = _plan(tmp_path)
    runner = LiveProviderAcceptance(plan)
    result = runner.preflight()

    assert result.status is PreflightStatus.READY
    assert result.profile_home == hermes_home.resolve()
    assert result.provider == "openai"
    assert result.model == "gpt-test"
    assert result.hermes_argv
    assert not plan.cnx_db.exists()
    assert not plan.kanban_db.exists()
    assert not plan.artifact_path.exists()
    assert "must-never-be-returned" not in repr(result)


def test_preflight_blocks_missing_named_profile_without_writing_state(tmp_path, monkeypatch):
    from zooid_cnx.provider_acceptance import PreflightStatus

    hermes_home = tmp_path / "hermes-root"
    hermes_home.mkdir()
    monkeypatch.setenv("HERMES_HOME", str(hermes_home))

    plan = AcceptancePlan.create(
        home=tmp_path / "acceptance-home",
        acceptance_id="task008-missing-profile",
        profile="definitely-missing-profile",
        provider="openai",
        model="gpt-test",
        timeout_seconds=90,
    )
    runner = LiveProviderAcceptance(plan)
    result = runner.preflight()

    assert result.status is PreflightStatus.BLOCKED
    assert "profile" in result.detail.lower()
    assert result.profile_home is None
    assert not plan.cnx_db.exists()
    assert not plan.kanban_db.exists()
