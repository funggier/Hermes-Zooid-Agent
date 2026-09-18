# Task 006 — Zooid Dispatcher Process Boundary

- Task ID: `006-zooid-dispatcher-process-boundary`
- State: DONE / GREEN
- Opened: 2026-09-18
- Completed: 2026-09-18
- Depends on: Task 005
- RED commit: `eb02d3a804048ad8b0640349e81f06995a70c1bb`
- Implementation commit: `0db88c097293df5182f084de32971c7abe207414`
- Authoritative Zooid workflow: `35356146655` — SUCCESS

## Why this task existed

Task 005 proved Hermes dispatcher mechanics in-process, but a real Zooid runtime cannot safely
route different boards by temporarily changing process-global HERMES_KANBAN_* variables.

That design would race as soon as more than one Project/session exists in the same parent
process.

## Decision

The durable boundary is a dedicated child process.

Parent Zooid:

- owns CogentNexus semantic state;
- constructs an explicit child environment;
- never mutates its own Kanban routing environment.

Dispatcher child:

- receives immutable Zooid-owned Kanban paths at process creation;
- validates argv/environment identity before opening the board;
- opens the same durable Zooid board;
- emits an atomic ready receipt;
- can be terminated and restarted without changing board identity.

## RED

Commit:

`eb02d3a804048ad8b0640349e81f06995a70c1bb`

The Zooid workflow failed during collection because `zooid_cnx.dispatcher_process` did not yet
exist. This is the authoritative RED boundary.

## Implementation

Commit:

`0db88c097293df5182f084de32971c7abe207414`

Added:

- `zooid_cnx/dispatcher_process.py`
- `zooid_cnx/dispatcher_child.py`

The parent process builds a copied environment, scrubs worker-specific Kanban identity, pins
ZOOID_HOME and all Zooid Kanban paths, then uses Popen(env=...) without changing os.environ.

The child fails closed if DB/board argv disagree with its environment.

Ready state is written atomically to:

`<state_dir>/dispatcher-ready.json`

and includes PID, DB path, board, task IDs and the observed Kanban environment.

## GREEN

Workflow:

`35356146655` — SUCCESS.

The contract proves:

- parent HERMES_KANBAN_DB/HERMES_KANBAN_BOARD remain unchanged;
- child receives Zooid routing;
- inherited worker identity is removed from child env;
- child sees the same durable card;
- stop is bounded;
- restart sees the same board/task again.

## Result

PASS.

Zooid now has a concurrency-safe process boundary for hosting dispatcher work without routing via
parent-process global mutation.

## Follow-up

Task 007 qualifies the worker subprocess envelope used by Hermes dispatcher before any real
provider/model request is allowed.
