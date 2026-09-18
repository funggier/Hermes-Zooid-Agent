# Zooid Session Handoff — Current

Updated: 2026-09-18

Repo: `funggier/Hermes-Zooid-Agent`
Branch: `agent/zooid-independence`
Clean upstream: `main`
Upstream baseline: `01382698fc32ec7740b6a204d9b7a6abeac74d33`

Last GREEN code before this documentation checkpoint:
`0db88c097293df5182f084de32971c7abe207414`

Zooid workflow:
`35356146655` — SUCCESS.

## Resume order

1. AGENTS.md
2. this file
3. ACTIVE.md
4. Task 007
5. STATUS.md
6. older tasks only when needed

## Completed chain

001 sync/isolation — GREEN
002 durable kernel — GREEN
003 generic execution bridge — GREEN
004 real Kanban executor — GREEN
005 dispatcher lifecycle — GREEN
006 dispatcher process boundary — GREEN

Task 006 proves child routing is fixed at Popen environment creation, parent routing is unchanged,
worker identity is scrubbed, and restart sees the same durable board.

## Active

Task 007 qualifies Hermes' real worker subprocess envelope with a fake executable, before any
provider/model request.

## Safety

No real provider yet. No live Hermes/OpenClaw mutation. No force push.
