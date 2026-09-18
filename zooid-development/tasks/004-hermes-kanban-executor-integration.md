# Task 004 — Hermes Kanban Executor Integration

- Task ID: `004-hermes-kanban-executor-integration`
- State: ACTIVE
- Opened: 2026-09-18
- Depends on: Task 003
- Current branch: `agent/zooid-independence`
- Starting code HEAD: `59a55b4e6ce2d7e004d2b7f2ab5d036c7b774714`

## Goal

Make the first real CogentNexus execution path use Hermes Kanban as the executor while keeping
CogentNexus semantic state and Zooid writable runtime state independent from live Hermes.

Target flow:

`CogentNexus Ticket -> Step -> ExecutionCoordinator -> HermesKanbanExecutor -> Kanban task -> Hermes worker -> result/evidence -> CogentNexus acceptance -> next Step/DONE`

## Why Hermes Kanban

Current Hermes already contains mature execution primitives:

- SQLite Kanban state;
- task idempotency keys;
- claim fencing;
- worker heartbeat;
- task run history;
- event history;
- dispatcher crash/stale recovery;
- completion fencing;
- bounded worker context;
- worker lifecycle handling.

Reimplementing those mechanisms inside CogentNexus would create competing schedulers and more
failure modes.

CogentNexus should reuse execution mechanics but retain semantic ownership.

## Important discovery

Hermes supports pinning Kanban storage through `HERMES_KANBAN_DB`.

Therefore Zooid can place its execution board beneath `ZOOID_HOME`, rather than writing to
the user's normal `~/.hermes/kanban.db`.

This is the intended first coexistence boundary.

## Ownership boundary

CogentNexus owns:

- Project / Goal;
- Ticket / Step;
- risk / uncertainty;
- acceptance criteria;
- Evidence;
- semantic Events / Checkpoints;
- external binding;
- final completion decision.

Hermes Kanban owns:

- dispatch queue mechanics;
- claim / heartbeat;
- worker process lifecycle;
- task run state;
- bounded execution context;
- raw executor result.

The adapter translates between the two. It must not make Hermes Kanban the source of truth for
CogentNexus completion.

## Planned implementation

Create a narrow adapter, expected under a Zooid-owned module such as:

`zooid_cnx/executors/hermes_kanban.py`

The exact path may change if current source constraints require it; record any change here.

Adapter responsibilities:

- initialize/open a Zooid-owned Kanban DB;
- submit a Kanban task using the CogentNexus deterministic operation key as Hermes'
  `idempotency_key`;
- locate an existing task by that key after restart;
- inspect task status and latest closed run;
- map Kanban states into `ExecutorState`;
- extract bounded summary/result/metadata into `ExecutorEvidence`;
- never silently resubmit an ambiguous task;
- keep external task identifiers only in the generic binding layer.

## Storage target

Provisional:

`ZOOID_HOME/kanban/boards/cogentnexus/kanban.db`

or another Zooid-owned path chosen after exact current Hermes path behavior is verified.

No test or adapter should use the live user's Hermes board.

## Test strategy

### Adapter contract

Use a temporary real Hermes Kanban SQLite DB and real current Kanban functions.

Prove:

- submit creates one task;
- same operation key discovers/reuses the same task;
- status mapping is deterministic;
- DONE result/summary becomes executor evidence;
- BLOCKED remains blocked;
- restart can rediscover a task before a CogentNexus binding was persisted;
- temporary board path stays outside HERMES_HOME.

### Integration contract

Connect:

CogentNexus store + ExecutionCoordinator + HermesKanbanExecutor

without launching a real provider/model first.

Only after source-level integration is GREEN should a later bounded acceptance step launch a
real Hermes worker/dispatcher.

## Non-goals for this task

- final Zooid launcher/installer;
- provider router;
- autonomous Goal decomposition;
- multiple reviewer/worker sessions;
- Group orchestration;
- live destructive Hermes lifecycle changes;
- full Zooid updater;
- release.

## Current progress

Completed before opening:

- targeted audit of current Hermes Kanban `create_task`, `get_task`, `list_runs`,
  dispatcher, workspace behavior and DB pinning;
- confirmed task-level `idempotency_key` support;
- confirmed worker receives `HERMES_KANBAN_DB`;
- confirmed current generic execution bridge is GREEN.

Not yet completed:

- concrete `HermesKanbanExecutor`;
- adapter-specific RED contract;
- adapter GREEN;
- real worker acceptance.

## Acceptance

Task 004 is DONE only when:

1. the real Hermes Kanban adapter satisfies `ExecutorPort`;
2. tests use an isolated Zooid-owned/temp Kanban DB;
3. duplicate dispatch is prevented across restart;
4. result/evidence reconciliation passes;
5. failure/block state mapping passes;
6. generic CogentNexus contracts remain GREEN;
7. no live Hermes board/config/runtime was modified;
8. evidence and exact tested SHA are recorded here and in STATUS/WORKLOG.

## Next action

Write the adapter RED contract first, then implement the minimum adapter required to turn it GREEN.
