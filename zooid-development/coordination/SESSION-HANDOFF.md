# Zooid Session Handoff — Current

Updated: 2026-09-18

Repo: `funggier/Hermes-Zooid-Agent`
Branch: `agent/zooid-independence`
Clean upstream: `main`
Upstream baseline: `01382698fc32ec7740b6a204d9b7a6abeac74d33`

Current source-ready SHA before this documentation checkpoint:
`e18e3e9705b3312b97a8f231924e5c8e9af2f94e`

Zooid workflow:
`35357955959` — SUCCESS.

## Resume order

1. `zooid-development/AGENTS.md`
2. this file
3. `coordination/ACTIVE.md`
4. `tasks/008-bounded-live-provider-acceptance.md`
5. `coordination/STATUS.md`

## Completed chain

Tasks 001–007 are DONE/GREEN.

Task 008 source is GREEN and includes:
- bounded acceptance runner;
- disposable Zooid home/board;
- provider/model/runtime pinning;
- real child dispatcher mode;
- worker structured-evidence gate;
- independent parent SHA-256 gate;
- read-only profile/launcher preflight.

## Active boundary

Task 008 is `SOURCE_READY / LIVE_ACCEPTANCE_BLOCKED_BY_RUNTIME_CREDENTIALS`.

No real provider PASS is recorded. The current execution environment cannot access the user's local Hermes credentialed profile runtime.

## Immediate continuation

On the real machine:
1. run the exact `--preflight` command documented in Task 008;
2. if status is `ready`, run the same acceptance without `--preflight`;
3. save the JSON result;
4. record provider/model, IDs, artifact SHA, Ticket state, retry/recovery and exact SHA in Task 008;
5. only then mark Task 008 DONE/GREEN and open Task 009.

## Safety

Do not expose credentials in reports. Use only the disposable acceptance home. Do not mutate live Hermes/OpenClaw lifecycle. No force push.
