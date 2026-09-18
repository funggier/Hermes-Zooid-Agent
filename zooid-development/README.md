# Zooid Development Workspace

This directory is the Zooid-owned development and planning layer kept separate from the
Hermes upstream source tree.

**Repository:** `funggier/Hermes-Zooid-Agent`
**Working branch:** `agent/zooid-independence`
**Upstream source:** `NousResearch/hermes-agent`
**Current synchronized upstream baseline:** `01382698fc32ec7740b6a204d9b7a6abeac74d33`

The fork's `main` branch is intentionally kept as a clean upstream mirror. Zooid-specific
planning, coordination, reports, and product changes belong on Zooid branches.

## Start here

1. Read [AGENTS.md](AGENTS.md).
2. Read [UPSTREAM-BASELINE.md](UPSTREAM-BASELINE.md).
3. Read [coordination/ACTIVE.md](coordination/ACTIVE.md) and [coordination/STATUS.md](coordination/STATUS.md).
4. Read the active architecture plan:
   [minimal CogentNexus runtime](plans/minimal-cogentnexus-runtime.md).
5. Use [roadmap.md](roadmap.md) as the broader durable development direction.
6. Treat [plans/product-independence.md](plans/product-independence.md) as historical audit
   evidence and refresh source ownership when an active task reaches that surface.

## Current architecture direction

CogentNexus semantic state is being built as a Zooid-owned durable kernel.
Hermes/Kanban will be used as the first execution substrate where appropriate rather than
duplicating its mature claim/heartbeat/worker scheduler.

Git history remains authoritative for the original September 6 planning snapshot.
