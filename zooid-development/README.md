# Zooid Development Workspace

Zooid-owned planning, chronological task history, coordination state and architecture live here,
separate from the inherited Hermes source/documentation tree.

Repository: `funggier/Hermes-Zooid-Agent`
Working branch: `agent/zooid-independence`
Clean upstream branch: `main`
Upstream baseline: `01382698fc32ec7740b6a204d9b7a6abeac74d33`

## New-session start

1. `AGENTS.md`
2. `coordination/SESSION-HANDOFF.md`
3. `coordination/ACTIVE.md`
4. active numbered task
5. `coordination/STATUS.md`

## Task numbering

Tasks are monotonic: 001, 002, 003, ... .
Never reuse or renumber an old task.

Current active task:
[005 — Hermes Dispatcher Lifecycle Integration](tasks/005-hermes-dispatcher-lifecycle-integration.md)

## Architecture direction

CogentNexus owns semantic durable truth and final acceptance.

Hermes Kanban is the first execution substrate and now has a GREEN concrete adapter. Current
work is qualifying the real dispatcher lifecycle before allowing a real provider/model worker.
