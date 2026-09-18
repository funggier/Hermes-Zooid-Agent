# Task 004 — Hermes Kanban Executor Integration

- Task ID: `004-hermes-kanban-executor-integration`
- State: DONE / GREEN
- Opened: 2026-09-18
- Completed: 2026-09-18
- Depends on: Task 003
- Final tested SHA: `68c2a2a7337cd7162a98a5ac90400e11ca2abeb9`
- Authoritative Zooid workflow run: `35354752792` — SUCCESS

## Why this task existed

Task 003 proved CogentNexus could drive a generic external executor, but no real executor
implementation existed. The first production substrate should reuse Hermes Kanban instead of
building a competing scheduler because current Hermes already owns mature task/claim/heartbeat/
run-history/dispatcher mechanics.

The architectural requirement was to reuse those mechanics without making Hermes Kanban the
semantic source of truth and without writing into the live user's Hermes board.

## Goal

Implement `HermesKanbanExecutor` as the first concrete `ExecutorPort`.

Target boundary:

- CogentNexus owns Goal, Ticket, Step, risk, uncertainty, acceptance criteria, Evidence,
  semantic Events, Checkpoints, recovery and final completion.
- Hermes Kanban owns executor queue state, claim/run state and worker lifecycle.
- The adapter translates between both domains.
- Writable Kanban data remains Zooid-owned.

## Important decisions

### Zooid-owned storage

Default board path:

`ZOOID_HOME/kanban/boards/cogentnexus/kanban.db`

The adapter also exposes the worker environment required to pin:

- `HERMES_KANBAN_HOME`
- `HERMES_KANBAN_BOARD`
- `HERMES_KANBAN_DB`
- `HERMES_KANBAN_WORKSPACES_ROOT`
- `HERMES_KANBAN_ATTACHMENTS_ROOT`

to Zooid-owned paths.

### Explicit evidence

A Hermes task reaching `done` is not enough for CogentNexus acceptance.

The task body carries a completion protocol requiring structured evidence in:

`metadata.cogentnexus_evidence`

Each evidence record names its evidence kind, value, and optional acceptance-criterion index.
Prose such as "worker says done" never bypasses the CogentNexus acceptance gate.

### Idempotency stronger than native archive behavior

Hermes native `create_task` ignores archived rows when resolving its idempotency key.
CogentNexus must be more conservative because an archived executor row may still represent an
already-executed side effect.

The adapter searches all rows by deterministic operation key before creating a new task.

## TDD / failure history

### RED

Commit:

`c579a04e3576ab907a309ab2926e6660320e7176`

Zooid CI reached the new test and failed because:

`zooid_cnx.executors.hermes_kanban`

did not exist.

This is the authoritative Task 004 RED boundary.

### First implementation

Commit:

`7ae990ad3ceebbf3ea266c9ec5a72d2fab3ae699`

Implemented:

- `zooid_cnx/executors/hermes_kanban.py`
- submit/find/inspect;
- status mapping;
- Zooid worker environment;
- structured evidence extraction;
- restart-safe operation-key discovery.

### Failure 1 — whole-runtime connection coupling

Zooid workflow run:

`35354296118` — FAILURE

Root cause:

Hermes public `kanban_db_connect.connect()` performs a full application-state preflight.
That transitively imports session/provider/config modules, eventually requiring `PyYAML`.
The lightweight executor contract intentionally did not install the whole Hermes provider stack.

This was not a semantic adapter failure. It exposed an unwanted coupling boundary.

Repair:

`946aeda8e208ae9773cf2f00e3d0ceaced425a3c`

The adapter now opens its dedicated Zooid board with SQLite directly while using Hermes'
canonical schema and real Kanban domain functions. A real Hermes dispatcher/worker may still
open the same DB through the normal full-runtime connector later.

### Failure 2 — base schema versus migration pass

Zooid workflow run:

`35354683506` — FAILURE

Root cause:

Hermes `SCHEMA_SQL` intentionally represents the base schema. Current columns such as
`completion_contract` are added by the Kanban migration pass.

Repair:

`68c2a2a7337cd7162a98a5ac90400e11ca2abeb9`

The dedicated connector now executes the current Hermes migration helper after base schema
initialization.

### GREEN

Zooid workflow:

`Zooid CogentNexus Kernel / CogentNexus runtime contracts`

Run:

`35354752792`

Result: SUCCESS.

The contract suite proves:

- default Kanban writable paths are Zooid-owned;
- duplicate submit reuses one real Kanban task;
- restart finds the same task by operation key;
- real Kanban `done` maps to executor success;
- structured evidence is imported with criterion binding;
- real Kanban `blocked` maps to CogentNexus block behavior;
- CogentNexus -> real Kanban adapter -> Evidence -> Ticket DONE works end-to-end;
- a `done` task without structured evidence does not auto-accept.

## Result

PASS.

The first concrete executor now exists and is backed by current Hermes Kanban schema/domain
logic while preserving CogentNexus semantic authority and Zooid writable-state isolation.

## Follow-up

Task 005 qualifies the real Hermes dispatcher lifecycle around this board:
ready -> claim -> workspace -> spawn -> running, using an injected non-provider spawn function
first so infrastructure can be proven before any real model call.
