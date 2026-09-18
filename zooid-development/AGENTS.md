# Zooid Development Instructions

This directory belongs to **Zooid — Powered by CogentNexus** and is deliberately separated
from the inherited Hermes source/documentation tree.

## Resume order

Before selecting or continuing Zooid work, read:

1. `README.md`
2. `coordination/SESSION-HANDOFF.md`
3. `coordination/ACTIVE.md`
4. the active numbered task linked there
5. `coordination/STATUS.md`

Read older numbered tasks only when their rationale/evidence is needed.

## Task-history invariant

All execution work uses monotonically increasing three-digit task IDs under `tasks/`:

`001`, `002`, `003`, ...

Never reuse, reorder, or renumber an existing task. BLOCKED/CANCELLED/SUPERSEDED tasks retain
their numbers. New work always receives the next number.

Every task file should capture at least:

- why the task exists;
- starting state and dependencies;
- intended outcome;
- important architecture/safety decisions;
- work completed;
- evidence and exact commits/workflows where available;
- failures/blockers and what they mean;
- current state;
- acceptance criteria;
- next action or follow-up task.

When a task changes materially, update its file and coordination state in the same development
sequence so a new session can resume from GitHub alone.

## Repository boundary

Keep fork `main` as a clean mirror of `NousResearch/hermes-agent/main`.
Zooid-specific source changes, planning, reports, identity work and release work belong on
Zooid branches. Never force-update upstream history.

Use root and area `AGENTS.md` files from synchronized Hermes for inherited engineering rules.

Zooid is intended to own installation, runtime, configuration, storage, lifecycle resources and
its future update path. Compatible Hermes skills/execution primitives may be reused, but Zooid
must own writable product state and must not depend on a shared writable Hermes home.

Preserve licenses, copyright notices, attribution and third-party obligations.

Do not stop/reset/uninstall/mutate live Hermes, OpenClaw, CogentNexus-OpenClaw or shared provider
runtimes unless a later numbered acceptance task explicitly scopes that operation.

## HermesZooid naming isolation

The user has a separate Zooid program. Bare `zooid` is reserved for that project.
HermesZooid product/runtime resources must use `hermeszooid` / `HERMESZOOID_*` naming.
Historical documentation may retain old names as evidence, but new writable/runtime/package identities must not use bare Zooid naming.
