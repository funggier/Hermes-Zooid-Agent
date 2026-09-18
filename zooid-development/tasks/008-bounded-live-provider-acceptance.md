# Task 008 — Bounded Live Provider Acceptance

- Task ID: `008-bounded-live-provider-acceptance`
- State: SOURCE_READY / LIVE_ACCEPTANCE_BLOCKED_BY_RUNTIME_CREDENTIALS
- Opened: 2026-09-18
- Depends on: Task 007
- Source RED commit: `d0f29ba40740ed6fca891c12cd67639ccf47e2d8`
- Source implementation: `7b60bfddfaafd543f2213160f485bf622003a72b`
- Preflight RED commit: `75da7879219f9ea0203320cbe8cecc4d6cc987b2`
- Current source-ready SHA: `e18e3e9705b3312b97a8f231924e5c8e9af2f94e`
- Authoritative Zooid workflow: `35357955959` — SUCCESS

## Why this task exists

Tasks 001–007 prove every provider-free boundary through the real Hermes worker subprocess.
The remaining minimum-usability proof is one real configured provider/model completing a bounded CogentNexus Ticket.

Target:

`CogentNexus Ticket -> Zooid Kanban -> Hermes worker -> real provider/model -> structured evidence -> parent SHA verification -> Ticket DONE`

## Acceptance design

The worker cannot self-certify the whole Ticket.

Acceptance criterion 0 is worker-owned structured evidence:

`metadata.cogentnexus_evidence[...].criterion_index = 0`

Acceptance criterion 1 is Zooid-parent-owned local verification:

`SHA-256(acceptance-result.txt) == expected SHA-256`

The worker is explicitly told not to provide criterion 1. If it attempts to do so, the runner returns `UNTRUSTED_EVIDENCE`.

## Source TDD history

### RED 1 — acceptance runner absent

Commit `d0f29ba40740ed6fca891c12cd67639ccf47e2d8`.

Zooid workflow `35357193719` failed with:

`ModuleNotFoundError: No module named 'zooid_cnx.provider_acceptance'`

### Source implementation

Commit `7b60bfddfaafd543f2213160f485bf622003a72b`.

Implemented:
- `AcceptancePlan` with disposable home/board/artifact paths;
- provider/model/profile pinning into the real Kanban task;
- `max_runtime_seconds` and `max_retries=1`;
- idempotent Project/Ticket/Step preparation;
- child `dispatch-task` mode using current Hermes `dispatch_once`;
- independent artifact SHA-256 gate;
- CLI dry-run and live-run surfaces.

Zooid workflow `35357510149` — SUCCESS.
Docker workflow `35357510176` — SUCCESS.

### RED 2 — preflight absent

Commit `75da7879219f9ea0203320cbe8cecc4d6cc987b2`.

Zooid workflow `35357830316` failed only on the new preflight contract because `PreflightStatus`/`preflight()` did not yet exist; the previous 20 tests passed.

### Preflight implementation

Commit `e18e3e9705b3312b97a8f231924e5c8e9af2f94e`.

Preflight is intentionally read-only. It:
- resolves the selected Hermes profile home;
- resolves the Hermes worker launcher argv;
- reports explicit provider/model pins or inherited-profile mode;
- does not read or return secret values;
- does not create the CogentNexus DB, Kanban DB, or artifact;
- blocks before state creation if profile/launcher resolution fails.

Zooid workflow `35357955959` — SUCCESS.

## Current status

`SOURCE_READY / LIVE_ACCEPTANCE_BLOCKED_BY_RUNTIME_CREDENTIALS`

The repository-side implementation is GREEN. A real provider result is not claimed because this GitHub/ChatGPT execution environment does not have access to the user's local Hermes provider credentials/profile runtime.

This is an evidence boundary, not a source-code failure.

## Exact live procedure on the real machine

Run from a checkout of this branch in the Hermes Python environment.

### 1. Read-only preflight using the selected Hermes profile

PowerShell example:

```powershell
$acceptHome = Join-Path $env:TEMP 'zooid-task008-live'
python -m zooid_cnx.provider_acceptance `
  --home $acceptHome `
  --acceptance-id task008-live `
  --profile default `
  --timeout 180 `
  --preflight
```

If the intended provider/model should be pinned explicitly, add:

`--provider <provider> --model <model>`

If omitted, the worker uses the selected Hermes profile's configured provider/model.

Expected preflight result:

`status = ready`

No provider request is made during preflight.

### 2. Live acceptance

```powershell
python -m zooid_cnx.provider_acceptance `
  --home $acceptHome `
  --acceptance-id task008-live `
  --profile default `
  --timeout 180
```

Or use the same explicit `--provider` / `--model` pair that passed preflight.

## Required live evidence

A PASS requires all of the following to be recorded:
- runner JSON `result.status = done`;
- provider/model actually selected;
- CogentNexus Ticket/Step IDs;
- Kanban task/run identity;
- worker completion evidence for criterion 0;
- artifact path and exact SHA-256 for criterion 1;
- final Ticket state `done`;
- dispatcher return code;
- exact repository SHA;
- whether retry/recovery occurred.

Anything less remains BLOCKED/INCOMPLETE.

## Safety

- The acceptance home is disposable and separate from the live Hermes Kanban board.
- No uninstall/reset/restart of live Hermes/OpenClaw is part of this task.
- Runtime is bounded.
- Retry budget is one.
- The artifact is local-only and harmless.
- Secret values must never be written into task reports.

## Next action

Run the read-only preflight and then the bounded live acceptance in an environment that has the intended Hermes provider credentials. Record the exact result here before changing Task 008 to DONE/GREEN.
