# Zooid Session Handoff — Current

Updated: 2026-09-18

## Repository

- Repo: `funggier/Hermes-Zooid-Agent`
- Clean upstream: `main`
- Zooid branch: `agent/zooid-independence`
- Upstream baseline: `01382698fc32ec7740b6a204d9b7a6abeac74d33`
- Last GREEN code SHA before this documentation checkpoint:
  `e37b3d1b21e9446683b83f2eae311ff4160c46fb`
- PR #1: draft

Verify current GitHub HEAD/Actions before acting.

## Read order

1. `zooid-development/AGENTS.md`
2. this file
3. `coordination/ACTIVE.md`
4. `tasks/006-zooid-dispatcher-process-boundary.md`
5. `coordination/STATUS.md`
6. earlier numbered task only when rationale is needed

## Completed

001 — upstream synchronization/planning isolation — DONE.

002 — durable CogentNexus kernel — DONE / GREEN.

003 — executor-neutral bridge — DONE / GREEN.

004 — concrete Hermes Kanban executor — DONE / GREEN.

005 — real Hermes dispatcher lifecycle — DONE / GREEN.

Task 005 final proof:
- SHA `e37b3d1b21e9446683b83f2eae311ff4160c46fb`
- Zooid workflow `35355516901` — SUCCESS
- Docker SUCCESS

It proves:
CogentNexus card creation, assignment, absolute Zooid workspace, real Hermes claim/run/PID
bookkeeping, RUNNING inspection, structured completion evidence and final Ticket DONE.

## Active — Task 006

Create a dedicated dispatcher process boundary.

Reason: parent-process environment mutation would be unsafe for future concurrent Projects and
sessions. Zooid should spawn a child with fixed Kanban paths instead.

## Immediate next action

Audit current Hermes dispatcher daemon/CLI entrypoints and implement RED tests for:
parent env unchanged + child receives Zooid env + same board visible + deterministic stop/restart.

## Safety

No real provider/model call yet. No live Hermes/OpenClaw mutation. No force push.
