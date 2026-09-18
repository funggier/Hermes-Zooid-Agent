# Development Status

**Project: ACTIVE**

Current active task:

[004 — Hermes Kanban Executor Integration](../tasks/004-hermes-kanban-executor-integration.md)

## Chronological milestones

| Task | State | Result |
| --- | --- | --- |
| 001 — Upstream sync and planning isolation | DONE | Clean current Hermes baseline + isolated Zooid planning |
| 002 — Minimal CogentNexus durable kernel | DONE / GREEN | Durable semantic state, evidence gate, idempotency and restart recovery |
| 003 — Executor-neutral execution bridge | DONE / GREEN | Durable external bindings and success/failure reconciliation |
| 004 — Hermes Kanban executor integration | ACTIVE | Concrete adapter not yet implemented |

## Current capabilities

- `zooid_cnx/store.py`: Project, Ticket, Step, Evidence, Events, Checkpoints.
- Zooid-owned persistence under `ZOOID_HOME`.
- Evidence-gated completion.
- Conservative `RUNNING -> VERIFY` crash recovery.
- Idempotent semantic transitions.
- `zooid_cnx/execution.py`: replaceable external executor contract.
- Durable external execution binding.
- Restart rediscovery through deterministic operation keys.
- Generic executor success/failure reconciliation.
- Zooid-owned lightweight CI on standard GitHub runners.

## Validation evidence

Minimal kernel GREEN checkpoint:

`e29010b62e08d3a78872c2bf16ce0d6428ae3b58`

Generic execution bridge implementation:

`59a55b4e6ce2d7e004d2b7f2ab5d036c7b774714`

Authoritative Zooid contract workflow:

`35352550001` — SUCCESS.

Docker workflow on the generic bridge implementation: SUCCESS.

## Current architecture boundary

CogentNexus is semantic authority.

Hermes Kanban will be the first execution substrate, not the semantic source of truth.

The next implementation must keep Kanban writable data under Zooid ownership and must not use
the live Hermes board.

## Later work

Not yet claimed as active:

- provider/router abstraction;
- autonomous Goal decomposition;
- context budgeting/compression;
- multi-session worker/reviewer topology;
- single-model scheduler/fairness/preemption;
- Project escalation / Group;
- full product identity/config/runtime separation;
- coexistence acceptance;
- Zooid-owned updater/release path.
