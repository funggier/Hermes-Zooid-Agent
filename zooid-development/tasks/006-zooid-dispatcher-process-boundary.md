# Task 006 — Zooid Dispatcher Process Boundary

- Task ID: `006-zooid-dispatcher-process-boundary`
- State: ACTIVE
- Opened: 2026-09-18
- Depends on: Task 005
- Starting GREEN SHA: `e37b3d1b21e9446683b83f2eae311ff4160c46fb`

## Why this task exists

Task 005 proves Hermes dispatcher mechanics work with a Zooid-created card, but the test invokes
the dispatcher inside the same Python process.

A real Zooid runtime must avoid changing process-global `HERMES_KANBAN_*` variables around
individual calls. That would become a race as soon as more than one Project/session/dispatcher
exists in the same process.

The correct ownership boundary is a dedicated dispatcher process whose environment is fixed at
process creation.

## Goal

Create a Zooid-owned process boundary around current Hermes dispatcher mechanics.

Parent Zooid process:

- owns CogentNexus semantic state;
- creates the dedicated Kanban board;
- builds the dispatcher environment;
- starts/stops the dispatcher process;
- never mutates its own HERMES_KANBAN_* environment to route work.

Dispatcher child:

- receives immutable Zooid-owned Kanban paths in its environment;
- opens only the Zooid board;
- uses current Hermes dispatcher mechanics;
- later may launch real Hermes workers.

## Target topology

```text
Zooid / CogentNexus parent
        |
        | subprocess env
        v
Zooid dispatcher child
        |
        | Hermes Kanban dispatcher
        v
Zooid-owned kanban.db
        |
        v
worker process boundary
```

## Initial contract

Before launching a real provider/model, prove:

1. parent environment remains unchanged;
2. child receives exactly the paths returned by `HermesKanbanExecutor.worker_env()`;
3. child can open the same Zooid Kanban DB;
4. child observes the intended board/card;
5. child lifecycle can be started and stopped deterministically;
6. no live Hermes board/config is touched;
7. restart uses the same durable board.

## Design constraints

- Do not implement another scheduler.
- Reuse current Hermes dispatcher.
- No temporary parent-process HERMES_KANBAN_* mutation.
- Child process environment must be explicit.
- Child termination must be bounded and observable.
- Board/database identity must be durable across restart.
- Provider/model execution is still outside this task's acceptance boundary.

## Expected code direction

A small Zooid-owned runtime layer, for example:

- `zooid_cnx/dispatcher_process.py` — parent-side lifecycle/process contract;
- `zooid_cnx/dispatcher_child.py` — child entrypoint.

Exact names may change if implementation evidence gives a better boundary.

The child should be narrow: it is not a second scheduler, only a process host for Hermes'
existing dispatcher.

## TDD

Write RED tests first for:

- environment isolation;
- deterministic argv/environment;
- process start/stop;
- same-board visibility;
- restart stability.

Then implement the minimum process boundary required for GREEN.

## Acceptance

Task 006 is DONE when a standard GitHub runner proves the process boundary without a real
provider/model and exact evidence is recorded here.

## Immediate next action

Audit existing Hermes daemon/CLI entrypoints for reusable dispatcher functions, then define the
RED process-boundary contract.
