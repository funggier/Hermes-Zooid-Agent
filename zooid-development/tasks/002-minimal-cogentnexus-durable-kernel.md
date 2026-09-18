# Task 002 — Minimal CogentNexus Durable Kernel

- Task ID: `002-minimal-cogentnexus-durable-kernel`
- State: DONE
- Date: 2026-09-18
- Depends on: Task 001

## Why this task existed

Zooid should not begin with multi-agent orchestration, Group topology, or a large scheduler.
The first requirement is a small system that can preserve a human objective across process
restarts and determine completion from evidence rather than model assertion.

The minimal proof target was:

`Goal -> Ticket -> Step -> Evidence -> Checkpoint -> Recovery -> DONE`

using one executor at a time.

## Architectural intent

CogentNexus owns semantic truth:

- Project / Goal
- Ticket
- ordered Step
- risk and uncertainty
- acceptance criteria
- Evidence
- Event
- Checkpoint
- recovery decision

Execution machinery remains replaceable.

## Safety invariant

If a process stops while a Step is RUNNING, restart must not assume the side effect did or
did not happen.

Therefore:

`RUNNING -> VERIFY`

Recovery must explicitly decide:

- completed, with evidence;
- retry, explicitly authorized;
- blocked.

There is no implicit replay.

## Work completed

Created `zooid_cnx/` with:

- SQLite durable store;
- Project, Ticket and Step state;
- Evidence records;
- append-only semantic Events;
- Checkpoints;
- idempotency keys;
- evidence-gated Step and Ticket completion;
- conservative restart recovery;
- temporary operator CLI through `python -m zooid_cnx`.

Default persistence:

`ZOOID_HOME/cogentnexus.db`

with fallback to:

`~/.zooid/cogentnexus.db`

It intentionally does **not** fall back to `HERMES_HOME`.

## TDD history

Initial contract commit:

`3e4d180defc3d3ecac0a1626f78f18204f5ad460`

Implementation commit:

`e63610eab12a7c8cb2f12dd9f373bcb9fa492d97`

A first lightweight Zooid CI attempt failed before exercising the kernel because the root
Hermes pytest `conftest.py` imported dependencies not installed in the isolated job.
That was a test-environment coupling problem, not a kernel failure.

The Zooid workflow was then isolated from inherited Hermes fixtures.

GREEN validation checkpoint:

`e29010b62e08d3a78872c2bf16ce0d6428ae3b58`

Workflow:

`Zooid CogentNexus Kernel / Minimal runtime contract`

Result: SUCCESS.

## What the contract proves

- durable state survives close/reopen;
- RUNNING work becomes VERIFY after interruption;
- interrupted work is never silently replayed;
- completion requires evidence;
- acceptance criteria require criterion-bound evidence;
- repeated mutation with the same operation key does not duplicate transitions/events;
- checkpoints preserve the latest durable phase;
- CogentNexus persistence remains in Zooid-owned storage.

## Result

PASS.

The first executable CogentNexus semantic kernel exists and is independently testable.

## Follow-up

Task 003 adds a replaceable external execution bridge without binding the semantic kernel to
Hermes-specific task identifiers.
