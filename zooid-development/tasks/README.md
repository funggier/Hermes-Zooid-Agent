# Zooid Development Task Index

This directory is the chronological, durable execution record for Zooid development.

## Numbering policy

Tasks use a monotonically increasing three-digit prefix:

`001-...`, `002-...`, `003-...`

Rules:

1. A number is never reused.
2. A task keeps its number even when it ends BLOCKED, CANCELLED, or SUPERSEDED.
3. New work receives the next number only.
4. Historical task files are not rewritten to pretend a different sequence happened.
5. Corrections are added as dated notes or follow-up tasks.
6. `coordination/ACTIVE.md` points to exactly one current numbered task.
7. `coordination/SESSION-HANDOFF.md` is the fast-entry document for a new session.

The older `prepare-development-workspace.md` predates this numbering scheme and remains
as archival planning evidence. Numbered history begins with Task 001.

## Task index

| Task | State | Purpose | Key outcome |
| --- | --- | --- | --- |
| [001](001-upstream-sync-and-planning-isolation.md) | DONE | Synchronize current Hermes and protect Zooid planning | Clean upstream `main`; Zooid planning isolated |
| [002](002-minimal-cogentnexus-durable-kernel.md) | DONE | Build first durable CogentNexus semantic kernel | Project/Ticket/Step/Evidence/recovery contract GREEN |
| [003](003-executor-neutral-execution-bridge.md) | DONE | Connect CogentNexus Steps to replaceable external executors | Durable external binding + success/failure reconciliation GREEN |
| [004](004-hermes-kanban-executor-integration.md) | ACTIVE | Use Hermes Kanban as Zooid's first real executor | In progress |

## Reading order for a new session

Read:

1. `../coordination/SESSION-HANDOFF.md`
2. `../coordination/ACTIVE.md`
3. the active task linked there
4. `../coordination/STATUS.md`
5. this index and prior numbered tasks only when historical reasoning is needed
6. `../plans/` for architectural rationale

This keeps startup context small without losing history.
