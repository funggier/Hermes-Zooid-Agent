# Active Work

- Project state: ACTIVE
- Active Task: `005-hermes-dispatcher-lifecycle-integration`
- Task state: ACTIVE
- Repository: `funggier/Hermes-Zooid-Agent`
- Working branch: `agent/zooid-independence`
- Hermes upstream baseline: `01382698fc32ec7740b6a204d9b7a6abeac74d33`
- Last GREEN code SHA: `68c2a2a7337cd7162a98a5ac90400e11ca2abeb9`
- Last GREEN Zooid workflow run: `35354752792`

## Active task

[Task 005 — Hermes Dispatcher Lifecycle Integration](../tasks/005-hermes-dispatcher-lifecycle-integration.md)

## Immediate next action

Add an isolated dispatcher lifecycle test using current Hermes dispatcher mechanics and an
injected spawn function. Prove ready -> claim -> Zooid workspace -> running -> evidence -> DONE
before any real provider/model worker is launched.

## Resume rule

Read [SESSION-HANDOFF.md](SESSION-HANDOFF.md) first in a new session.

The next new task number after Task 005 is 006. Never reuse prior numbers.

## Boundaries

- no force push;
- keep `main` as clean upstream mirror;
- no live Hermes/OpenClaw lifecycle mutation;
- no live provider call yet;
- no process-global path mutation as a production design;
- no implicit side-effect replay;
- GitHub repository/actions are authoritative.
