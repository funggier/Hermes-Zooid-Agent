import json

import pytest

from hermeszooid.cnx.store import (
    AcceptanceError,
    CogentNexusStore,
    RecoveryAction,
    StepState,
    TicketState,
)


def _make_ticket(store):
    project = store.create_project(
        goal="Deliver one durable CogentNexus vertical slice",
        op_key="project:create",
    )
    ticket = store.create_ticket(
        project.id,
        title="Minimal runtime",
        objective="Persist work, recover safely, and complete only with evidence",
        acceptance_criteria=["artifact exists", "verification passes"],
        risk="medium",
        uncertainty="low",
        op_key="ticket:create",
    )
    first = store.add_step(ticket.id, "implement artifact", op_key="step:1")
    second = store.add_step(ticket.id, "verify artifact", op_key="step:2")
    return project, ticket, first, second


def test_ticket_lifecycle_persists_and_recovers_without_replay(tmp_path, monkeypatch):
    hermeszooid_home = tmp_path / "hermeszooid"
    hermes_home = tmp_path / "hermes"
    monkeypatch.setenv("HERMESZOOID_HOME", str(hermeszooid_home))
    monkeypatch.setenv("HERMES_HOME", str(hermes_home))

    with CogentNexusStore.open_default() as store:
        project, ticket, first, second = _make_ticket(store)

        claimed = store.claim_next_step(ticket.id, worker_id="worker-a", op_key="claim:1")
        assert claimed.id == first.id
        assert claimed.state is StepState.RUNNING

        store.record_evidence(
            ticket.id,
            first.id,
            kind="artifact",
            value="src/hermeszooid.cnx/store.py",
            criterion_index=0,
            op_key="evidence:1",
        )
        store.complete_step(first.id, summary="artifact created", op_key="complete:1")

        interrupted = store.claim_next_step(ticket.id, worker_id="worker-a", op_key="claim:2")
        assert interrupted.id == second.id
        assert interrupted.state is StepState.RUNNING

    # A crash/restart must never infer that the running side effect is safe to repeat.
    with CogentNexusStore.open_default() as store:
        recovery = store.recover_ticket(ticket.id, op_key="recover:1")
        assert recovery.action is RecoveryAction.VERIFY_INTERRUPTED_STEP
        assert recovery.step_id == second.id
        assert store.get_step(second.id).state is StepState.VERIFY

        store.resolve_interrupted_step(
            second.id,
            resolution="completed",
            summary="verification had completed before the crash",
            evidence={
                "kind": "test",
                "value": "pytest: passed",
                "criterion_index": 1,
            },
            op_key="resolve:2",
        )
        done = store.complete_ticket(ticket.id, summary="vertical slice accepted", op_key="ticket:done")
        assert done.state is TicketState.DONE

        events = store.list_events(ticket.id)
        kinds = [row["kind"] for row in events]
        assert kinds[0] == "ticket_created"
        assert "recovery_requires_verification" in kinds
        assert kinds[-1] == "ticket_completed"

        latest = store.latest_checkpoint(ticket.id)
        assert latest["phase"] == "ticket_done"
        assert json.loads(latest["state_json"])["ticket_state"] == "done"

    assert (hermeszooid_home / "cogentnexus.db").is_file()
    assert not (hermes_home / "cogentnexus.db").exists()


def test_idempotency_key_prevents_duplicate_transition_and_event(tmp_path):
    db_path = tmp_path / "cnx.db"
    with CogentNexusStore(db_path) as store:
        _project, ticket, first, _second = _make_ticket(store)

        one = store.claim_next_step(ticket.id, worker_id="worker-a", op_key="same-claim")
        two = store.claim_next_step(ticket.id, worker_id="worker-a", op_key="same-claim")
        assert one.id == two.id == first.id

        claimed_events = [
            event for event in store.list_events(ticket.id)
            if event["kind"] == "step_claimed"
        ]
        assert len(claimed_events) == 1


def test_ticket_completion_requires_acceptance_evidence(tmp_path):
    with CogentNexusStore(tmp_path / "cnx.db") as store:
        project = store.create_project("goal")
        ticket = store.create_ticket(
            project.id,
            title="evidence gate",
            objective="prove completion gate",
            acceptance_criteria=["tests pass"],
        )
        step = store.add_step(ticket.id, "run tests")
        store.claim_next_step(ticket.id, worker_id="worker")
        store.record_evidence(ticket.id, step.id, kind="note", value="worked")
        store.complete_step(step.id, summary="done")

        with pytest.raises(AcceptanceError, match="criterion 0"):
            store.complete_ticket(ticket.id)

        store.record_evidence(
            ticket.id,
            step.id,
            kind="test",
            value="pytest: passed",
            criterion_index=0,
        )
        assert store.complete_ticket(ticket.id).state is TicketState.DONE


def test_recovery_of_running_step_is_idempotent_and_never_requeues(tmp_path):
    with CogentNexusStore(tmp_path / "cnx.db") as store:
        _project, ticket, first, _second = _make_ticket(store)
        store.claim_next_step(ticket.id, worker_id="worker")

        first_recovery = store.recover_ticket(ticket.id, op_key="recover")
        second_recovery = store.recover_ticket(ticket.id, op_key="recover")

        assert first_recovery == second_recovery
        assert first_recovery.action is RecoveryAction.VERIFY_INTERRUPTED_STEP
        assert store.get_step(first.id).state is StepState.VERIFY
        assert store.claim_next_step(ticket.id, worker_id="other") is None
