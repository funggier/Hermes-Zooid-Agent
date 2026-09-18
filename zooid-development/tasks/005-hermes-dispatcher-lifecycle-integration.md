# Task 005 — Hermes Dispatcher Lifecycle Integration

- Task ID: `005-hermes-dispatcher-lifecycle-integration`
- State: ACTIVE
- Opened: 2026-09-18
- Depends on: Task 004
- Starting GREEN SHA: `68c2a2a7337cd7162a98a5ac90400e11ca2abeb9`

## Why this task exists

Task 004 proved that CogentNexus can create and reconcile a real Hermes Kanban card, but it did
not prove the dispatcher side of the lifecycle.

Before allowing a real provider/model worker, Zooid must verify that a card created by
CogentNexus can be consumed by current Hermes dispatcher mechanics without escaping Zooid-owned
storage.

The next proof boundary is:

`READY -> claim -> workspace -> spawn callback -> RUNNING`

using the real current Kanban dispatcher and an injected spawn function that does not launch a
provider.

## Goal

Qualify one complete infrastructure-only lifecycle:

1. CogentNexus creates Ticket/Step.
2. ExecutionCoordinator dispatches it to HermesKanbanExecutor.
3. Real Hermes dispatcher claims the Kanban card.
4. Workspace resolves beneath Zooid-owned storage.
5. Dispatcher calls the injected spawn function exactly once.
6. PID/run/claim state is durably visible.
7. HermesKanbanExecutor reports RUNNING.
8. Simulated worker completion with structured evidence returns through CogentNexus to DONE.

## Why use an injected spawn function first

Current Hermes `dispatch_once` supports `spawn_fn`.

This lets the project test dispatcher queue/claim/workspace/run bookkeeping separately from:

- provider credentials;
- model availability;
- quotas;
- network;
- real worker subprocess behavior.

A failure here is therefore an execution-plumbing problem, not a provider problem.

## Safety / architecture constraints

- Never point the test at live `~/.hermes`.
- Workspace must be under Zooid-owned/temp storage.
- Do not mutate process-global HERMES environment as a production API.
- Do not introduce a second scheduler.
- Do not interpret dispatcher spawn as semantic completion.
- CogentNexus acceptance remains evidence-gated.
- Real provider execution is deferred until this lifecycle is GREEN.

## Planned validation

Use:

- real `HermesKanbanExecutor`;
- real Hermes Kanban domain functions;
- real dispatcher claim/workspace/run logic;
- injected spawn callback only.

The test should record:

- task ID;
- assignee;
- resolved workspace;
- board identity;
- synthetic PID;
- Kanban status/current_run_id/worker_pid;
- CogentNexus external binding;
- final evidence and Ticket status.

## Expected implementation impact

Prefer no new scheduler code.

Small adapter changes are allowed only if needed to make storage/workspace ownership explicit and
restart-safe.

If current Hermes public dispatcher API cannot be used without hidden global path resolution,
record the exact reason and add the narrowest safe Zooid integration layer instead of mutating
global environment.

## Acceptance

Task 005 is DONE when:

1. one real dispatcher lifecycle test is GREEN;
2. the dispatcher claims exactly the intended CogentNexus-created card;
3. exactly one spawn callback occurs;
4. workspace resolves under Zooid-owned/temp storage;
5. task becomes RUNNING with durable run identity;
6. adapter inspection reports RUNNING;
7. structured completion evidence flows back to CogentNexus DONE;
8. no live Hermes board/profile/provider was modified;
9. exact SHA/run evidence is recorded here and in coordination files.

## Immediate next action

Add the dispatcher lifecycle contract and run it against the current Hermes implementation.
