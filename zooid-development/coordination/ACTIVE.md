# Active Work

- Project state: ACTIVE
- Task ID: cnx-minimal-runtime-vertical-slice
- Task state: VALIDATION
- Repository: `funggier/Hermes-Zooid-Agent`
- Working branch: `agent/zooid-independence`
- Current upstream baseline: `01382698fc32ec7740b6a204d9b7a6abeac74d33`
- RED contract commit: `3e4d180defc3d3ecac0a1626f78f18204f5ad460`
- Implementation commit: `e63610eab12a7c8cb2f12dd9f373bcb9fa492d97`

## Current task

Validate the first durable CogentNexus vertical slice.

Implemented scope:

- Zooid-owned SQLite persistence under `ZOOID_HOME`;
- Project / Ticket / ordered Step state;
- risk, uncertainty and acceptance criteria;
- Evidence and acceptance gate;
- append-only semantic events;
- durable checkpoints;
- optional idempotency keys;
- conservative restart recovery: RUNNING -> VERIFY, never implicit replay;
- module CLI through `python -m zooid_cnx`.

Design: [minimal-cogentnexus-runtime](../plans/minimal-cogentnexus-runtime.md)

## Validation state

- Baseline CI before production work: PASS.
- Docker workflow on implementation commit: PASS.
- Full CI / Nix on implementation commit: RUNNING at this checkpoint.
- Local checkout is unavailable in the current ChatGPT container because public DNS for github.com
  is unavailable; this is an environment limitation, not repository evidence.
- GitHub Actions remains authoritative.

## Next actions

1. Finish GitHub CI validation for the implementation commit.
2. Repair any failing contract/lint without widening scope.
3. When GREEN, checkpoint the minimal kernel as the first executable CogentNexus milestone.
4. Open the next task for the Hermes/Kanban execution adapter.
5. Continue the broader product-independence audit in parallel only where the adapter needs it.

Keep fork `main` clean; Zooid implementation remains on this branch or descendants.
