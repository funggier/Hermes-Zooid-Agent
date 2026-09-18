# Task 008 — Bounded Live Provider Acceptance

- Task ID: `008-bounded-live-provider-acceptance`
- State: ACTIVE
- Opened: 2026-09-18
- Depends on: Task 007
- Starting GREEN SHA: `a103575b01d169cceb9dd853cd6aad73348c8622`

## Why this task exists

Tasks 001–007 prove every provider-free boundary through the real Hermes worker subprocess.
The remaining minimum-usability proof is one real configured provider/model completing a bounded CogentNexus Ticket.

## Target

`CogentNexus Ticket -> Zooid Kanban -> Hermes worker -> real provider/model -> structured evidence -> Ticket DONE`

## Source preparation

Before any live provider call:
1. add a reusable bounded acceptance runner;
2. use a disposable Zooid acceptance home/board;
3. never mutate live Hermes Kanban routing;
4. bound runtime and retries;
5. make the requested artifact local-only and deterministic;
6. record provider/model, task/run ids, artifact evidence and final Ticket state;
7. keep the CogentNexus evidence gate authoritative.

## Live-call boundary

A real run may require credentials/configuration available only on the user machine.
If unavailable in the current execution environment, report `SOURCE_READY / LIVE_ACCEPTANCE_BLOCKED`; never infer PASS.

## Immediate next action

Implement and test the acceptance runner in dry-run/configuration mode, then attempt the bounded live provider run only where credentials are actually available.
