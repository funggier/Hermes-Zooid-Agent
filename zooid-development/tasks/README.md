# Zooid Development Task Index

Tasks use monotonically increasing three-digit IDs. Numbers are never reused or renumbered,
including BLOCKED, CANCELLED, or SUPERSEDED tasks.

| Task | State | Purpose | Key outcome |
| --- | --- | --- | --- |
| [001](001-upstream-sync-and-planning-isolation.md) | DONE | Sync Hermes and isolate Zooid planning | Clean upstream mirror boundary |
| [002](002-minimal-cogentnexus-durable-kernel.md) | DONE / GREEN | Durable semantic kernel | Ticket/Evidence/recovery GREEN |
| [003](003-executor-neutral-execution-bridge.md) | DONE / GREEN | Replaceable executor bridge | Durable external binding GREEN |
| [004](004-hermes-kanban-executor-integration.md) | DONE / GREEN | First real executor | Real Hermes Kanban adapter GREEN |
| [005](005-hermes-dispatcher-lifecycle-integration.md) | ACTIVE | Qualify real dispatcher lifecycle | In progress |

## New-session reading order

1. `../coordination/SESSION-HANDOFF.md`
2. `../coordination/ACTIVE.md`
3. active numbered task
4. `../coordination/STATUS.md`
5. this index
6. earlier tasks only when their rationale/evidence is needed

The older unnumbered `prepare-development-workspace.md` is archival pre-numbering material.
