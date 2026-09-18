# Zooid Development Workspace

This directory is the Zooid-owned planning, coordination, task history and architecture layer,
kept separate from the inherited Hermes source/documentation tree.

**Repository:** `funggier/Hermes-Zooid-Agent`
**Working branch:** `agent/zooid-independence`
**Upstream source:** `NousResearch/hermes-agent`
**Synchronized upstream baseline:** `01382698fc32ec7740b6a204d9b7a6abeac74d33`

Fork `main` is kept as a clean upstream mirror. Zooid-specific product work belongs on Zooid
branches.

## New-session start here

1. [AGENTS.md](AGENTS.md)
2. [coordination/SESSION-HANDOFF.md](coordination/SESSION-HANDOFF.md)
3. [coordination/ACTIVE.md](coordination/ACTIVE.md)
4. the numbered active task linked by ACTIVE
5. [coordination/STATUS.md](coordination/STATUS.md)
6. [tasks/README.md](tasks/README.md) when historical sequence is needed

## Durable task history

Development tasks are numbered monotonically:

`001`, `002`, `003`, ...

Numbers are never reused, including for BLOCKED/CANCELLED/SUPERSEDED work.

This makes repository state sufficient to reconstruct what happened, why it happened, what
evidence existed, where work stopped and what should happen next without depending on chat
history.

## Current architecture direction

CogentNexus owns semantic durable truth.

Hermes/Kanban is being reused as the first execution substrate rather than duplicating its
mature queue/claim/heartbeat/worker mechanics.

See:

- [minimal CogentNexus runtime](plans/minimal-cogentnexus-runtime.md)
- [Task 004 — Hermes Kanban Executor Integration](tasks/004-hermes-kanban-executor-integration.md)

Git history remains authoritative for earlier snapshots.
