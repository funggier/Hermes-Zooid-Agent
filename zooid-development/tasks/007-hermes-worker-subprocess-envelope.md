# Task 007 — Hermes Worker Subprocess Envelope

- Task ID: `007-hermes-worker-subprocess-envelope`
- State: DONE / GREEN
- Opened: 2026-09-18
- Completed: 2026-09-18
- Depends on: Task 006
- RED commit: `d4e7fc78a13886dffd5748d938365ef02e578b9e`
- Final tested SHA: `a103575b01d169cceb9dd853cd6aad73348c8622`
- Zooid workflow: `35356697706` — SUCCESS
- Docker: SUCCESS

## Purpose

Qualify Hermes real `_default_spawn` worker boundary without invoking a provider/model.

## RED

`d4e7fc78a13886dffd5748d938365ef02e578b9e` reached the real spawn path and failed because `PyYAML` was absent from the lightweight Zooid workflow.
This dependency comes from Hermes core (`agent.secret_scope -> utils`) and is not a provider extra.

## Repair

`a103575b01d169cceb9dd853cd6aad73348c8622` added pinned core dependency `pyyaml==6.0.3` to the focused Zooid workflow.

## GREEN evidence

Workflow `35356697706` passed and proves:
- a real OS child is launched by Hermes `_default_spawn`;
- cwd is the Zooid task workspace;
- task id, run id and claim lock are passed;
- Zooid Kanban DB, board and workspaces are pinned;
- worker source is `kanban` and profile is explicit;
- expected Hermes worker argv is built;
- no provider/model override is injected;
- fake worker exit does not silently mark the task complete.

## Result

PASS.

## Follow-up

Task 008 prepares and attempts one bounded live provider/model acceptance through the same Zooid-owned path.
