# Minimal CogentNexus Runtime Vertical Slice

## Purpose

Build the smallest runtime that proves Zooid can preserve a human goal across durable
machine state, execute bounded work, survive interruption, and refuse to declare success
without evidence.

The first slice deliberately uses one Project, one Ticket, ordered Steps, and one executor
at a time. Multi-agent scheduling, Group orchestration, provider routing, and autonomous
decomposition are later layers.

## Architectural decision

Hermes already has mature execution primitives in its Kanban subsystem: SQLite-backed task
state, claims, heartbeats, run history, event history, completion gates, dispatcher recovery,
and worker lifecycle handling.

Zooid therefore must not build a second scheduler that competes with Hermes. The split is:

- CogentNexus kernel owns semantic intent and durable truth:
  Project, Goal, Ticket, ordered Step, risk, uncertainty, acceptance criteria,
  Evidence, Event, Checkpoint, and recovery decision.
- An execution adapter owns dispatch:
  Hermes/Kanban first; Zooid-native scheduler later if needed.
- The adapter may execute a Step, but it cannot mark a Ticket complete without satisfying
  the CogentNexus evidence gate.

This keeps CogentNexus stable even if the underlying executor changes.

## Implemented kernel

Current package: `zooid_cnx/`

Persistence root:

`ZOOID_HOME/cogentnexus.db`

Default when `ZOOID_HOME` is absent:

`~/.zooid/cogentnexus.db`

The kernel intentionally does not fall back to `HERMES_HOME`.

### Durable records

- `projects` — durable human goal and project state.
- `tickets` — objective, acceptance criteria, risk, uncertainty, lifecycle state.
- `steps` — ordered bounded actions.
- `evidence` — artifact/test/observation receipts, optionally mapped to an acceptance criterion.
- `events` — append-only semantic transition log plus optional idempotency key.
- `checkpoints` — compact state snapshot attached to an event boundary.

SQLite foreign keys are enabled. State-changing methods use `BEGIN IMMEDIATE`.

## State model

Ticket:

`READY -> RUNNING -> DONE`

A ticket may also become `BLOCKED`.

Step:

`READY -> RUNNING -> DONE`

Interrupted work does not become READY automatically:

`RUNNING --restart/recovery--> VERIFY`

A VERIFY step must be explicitly resolved as:

- `completed` — requires evidence;
- `retry` — explicit authorization to return to READY;
- `blocked` — parks the step and ticket.

This is a safety invariant. The runtime never guesses whether an external side effect happened.

## Completion contract

Step completion requires at least one Evidence record.

Ticket completion requires:

1. at least one Step;
2. every Step is DONE;
3. every declared acceptance criterion is covered by criterion-bound Evidence.

A commit, summary, or model assertion by itself is not acceptance evidence.

## Idempotency

Mutation methods accept an optional `op_key`.

When the same operation is replayed with the same key, the prior durable result is returned
instead of applying the transition again. Reusing a key for a different transition is rejected.

This is the first replay boundary required for crash-safe orchestration and future IPC.

## Operator surface

Until Zooid owns its final launcher, the kernel is usable as a module CLI:

`python -m zooid_cnx`

Initial commands:

- `create`
- `status`
- `recover`
- `claim`
- `evidence`
- `complete-step`
- `resolve`
- `complete-ticket`

The CLI is an operator/debug surface, not the final product UI.

## TDD contract

Test file:

`tests/zooid_cnx/test_runtime.py`

The initial contract proves:

- durable Project/Ticket/Step state survives connection close/reopen;
- an interrupted RUNNING step recovers as VERIFY and is never silently replayed;
- completed recovery requires evidence;
- Ticket completion is rejected until acceptance criteria have evidence;
- idempotency keys prevent duplicate transition/event application;
- checkpoints record the latest durable phase;
- default persistence uses ZOOID_HOME even when HERMES_HOME is set.

## Next layer: Hermes/Kanban execution adapter

After this kernel is GREEN, add a narrow adapter rather than modifying Kanban semantics.

The adapter will:

1. inspect CogentNexus recovery state;
2. for EXECUTE_STEP, create/find exactly one Kanban task using a deterministic idempotency key;
3. persist the external task binding;
4. submit bounded Step context rather than the full Project history;
5. reconcile Kanban terminal state back into Step Evidence/result;
6. never automatically retry an uncertain side effect;
7. leave Ticket acceptance to the CogentNexus evidence gate.

The adapter must be replaceable. No CogentNexus table may require Hermes-specific identifiers
except through an explicit external-binding record.

## Deferred

- LLM decomposition of Goals into Steps.
- Context budgeting/compression.
- Provider router.
- Multi-session reviewer/worker topology.
- Single-model fairness/preemption scheduler.
- Project escalation and Group organization.
- Native Zooid dispatcher.
- Owned Zooid updater/release channel.

Those layers are built only after this vertical slice remains stable under restart and replay.
