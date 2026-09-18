# Active Work

- Project state: ACTIVE
- Active Task: `006-zooid-dispatcher-process-boundary`
- Task state: ACTIVE
- Repository: `funggier/Hermes-Zooid-Agent`
- Working branch: `agent/zooid-independence`
- Upstream baseline: `01382698fc32ec7740b6a204d9b7a6abeac74d33`
- Last GREEN code SHA: `e37b3d1b21e9446683b83f2eae311ff4160c46fb`
- Last GREEN Zooid run: `35355516901`

## Active task

[Task 006 — Zooid Dispatcher Process Boundary](../tasks/006-zooid-dispatcher-process-boundary.md)

## Immediate next action

Audit current Hermes dispatcher daemon/CLI entrypoints, then write RED tests for an isolated
child process whose Kanban environment is fixed at spawn and whose parent environment is
unchanged.

## Resume rule

Read `SESSION-HANDOFF.md` first.

Next unused task ID after this task is 007.

## Boundaries

- no force push;
- keep main as clean upstream mirror;
- no live Hermes/OpenClaw mutation;
- no real provider/model call yet;
- no parent-process HERMES_KANBAN_* mutation;
- evidence gating remains authoritative.
