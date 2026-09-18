# Active Work

- Project state: ACTIVE
- Active Task: `008-bounded-live-provider-acceptance`
- Task state: `SOURCE_READY / LIVE_ACCEPTANCE_BLOCKED_BY_RUNTIME_CREDENTIALS`
- Repository: `funggier/Hermes-Zooid-Agent`
- Branch: `agent/zooid-independence`
- Upstream baseline: `01382698fc32ec7740b6a204d9b7a6abeac74d33`
- Current source-ready SHA: `e18e3e9705b3312b97a8f231924e5c8e9af2f94e`
- Current GREEN Zooid workflow: `35357955959`

## Active task

[Task 008 — Bounded Live Provider Acceptance](../tasks/008-bounded-live-provider-acceptance.md)

## Immediate next action

On a real Hermes-configured machine, run Task 008 read-only preflight, then the bounded live acceptance. Do not open Task 009 until real provider evidence is recorded.

## Resume rule

Read `SESSION-HANDOFF.md` first. Next unused task ID remains 009.

## Boundaries

- no force push;
- main stays a clean upstream mirror;
- disposable Zooid acceptance state only;
- no live Hermes/OpenClaw lifecycle mutation;
- no provider PASS claim without real evidence;
- never record secret values.
