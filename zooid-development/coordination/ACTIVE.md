# Active Work

- Project state: ACTIVE
- Active Task: `004-hermes-kanban-executor-integration`
- Task state: ACTIVE
- Repository: `funggier/Hermes-Zooid-Agent`
- Working branch: `agent/zooid-independence`
- Current upstream baseline: `01382698fc32ec7740b6a204d9b7a6abeac74d33`
- Last GREEN production-code checkpoint:
  `59a55b4e6ce2d7e004d2b7f2ab5d036c7b774714`

## Active task

[Task 004 — Hermes Kanban Executor Integration](../tasks/004-hermes-kanban-executor-integration.md)

Goal: bind the GREEN generic CogentNexus execution bridge to current Hermes Kanban while keeping
Zooid writable state isolated from live Hermes.

## Immediate next action

Write RED adapter tests against a temporary real Hermes Kanban DB, then implement the minimum
`HermesKanbanExecutor` needed to make the contract GREEN.

Do not launch a real provider worker until the source-level adapter is GREEN.

## Resume rule

For a new session, read [SESSION-HANDOFF.md](SESSION-HANDOFF.md) first.

Task numbering is monotonic. The next new task after this one is 005; never reuse an old number.

## Boundaries

- no force push;
- keep `main` a clean upstream mirror;
- no live Hermes/OpenClaw lifecycle mutation during this source-level task;
- no implicit replay of uncertain side effects;
- GitHub repository/actions are authoritative.
