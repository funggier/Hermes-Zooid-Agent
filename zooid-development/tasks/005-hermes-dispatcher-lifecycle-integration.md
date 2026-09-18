# Task 005 — Hermes Dispatcher Lifecycle Integration

- Task ID: `005-hermes-dispatcher-lifecycle-integration`
- State: DONE / GREEN
- Opened: 2026-09-18
- Completed: 2026-09-18
- Depends on: Task 004
- RED commit: `2a7131b8e16fa0a53cb4e4a152894faa39997019`
- Production repair: `9aee6577c87ef509ba4f33559ab0dbe2f1d745e0`
- Final tested SHA: `e37b3d1b21e9446683b83f2eae311ff4160c46fb`
- Authoritative Zooid workflow: `35355516901` — SUCCESS

## Why this task existed

Task 004 proved that CogentNexus could create, find and reconcile a real Hermes Kanban card.
It did not prove that current Hermes dispatcher mechanics could actually consume that card.

Before any real model/provider worker is allowed, the infrastructure boundary had to prove:

`READY -> claim -> workspace -> spawn -> RUNNING -> completion evidence -> CogentNexus DONE`

without mixing provider/network failures into the result.

## Contract

The test uses:

- real CogentNexus Project/Ticket/Step state;
- real `HermesKanbanExecutor`;
- real current Hermes claim/run/workspace/PID/event bookkeeping;
- real `complete_task`;
- an injected spawn callback instead of a model process.

Only profile availability and process fingerprinting for the deliberately fake PID are isolated.

## RED

Commit:

`2a7131b8e16fa0a53cb4e4a152894faa39997019`

Workflow:

`35355192806` — FAILURE

13 existing CogentNexus tests passed. The new lifecycle contract failed immediately because
`HermesKanbanExecutor` did not yet accept an assignee.

This identified a real production gap: a dispatcher card must have explicit routing ownership.

## Production repair

Commit:

`9aee6577c87ef509ba4f33559ab0dbe2f1d745e0`

Changes:

- add optional executor `assignee`;
- pass the assignee to real Hermes `create_task`;
- persist an absolute scratch `workspace_path` immediately after card creation;
- workspace path is `<Zooid workspaces root>/<task_id>`;
- no process-global HERMES environment mutation is required.

This is important for future multi-session correctness: concurrent Zooid execution must not race
on temporary process-wide path overrides.

## Harness correction

The first post-repair run reached real dispatcher claim/workspace handling but did not report a
spawn. The injected spawn callback returns a synthetic PID (`4242`), while Hermes normally
fingerprints a real host process after spawn.

The test therefore stubs only `_process_fingerprint` for the nonexistent synthetic PID. It
does not stub claim, run creation, workspace resolution, PID persistence, events or completion.

Final harness commit:

`e37b3d1b21e9446683b83f2eae311ff4160c46fb`

## GREEN

Zooid workflow:

`35355516901` — SUCCESS.

The final contract proves:

1. CogentNexus creates the intended real Kanban card.
2. The card is READY and assigned.
3. Workspace is an absolute Zooid-owned path.
4. Real Hermes dispatcher claims exactly that card.
5. Real run identity is created.
6. The spawn callback is invoked once.
7. Worker PID bookkeeping is persisted.
8. Adapter inspection reports RUNNING.
9. Real Hermes completion records structured CogentNexus evidence.
10. ExecutionCoordinator consumes that evidence.
11. Ticket reaches DONE through the CogentNexus acceptance gate.

Docker workflow on the same tested SHA also completed successfully.

Inherited upstream CI/Nix may remain queued because this fork does not own NousResearch's
large-runner infrastructure.

## Result

PASS.

The executor plumbing up to the worker-process boundary is now proven.

## Follow-up

Task 006 creates an owned dispatcher process boundary so Zooid can run the Hermes dispatcher
with Zooid-specific environment/state without mutating the parent process environment.
