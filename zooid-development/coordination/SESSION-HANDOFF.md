# Zooid Session Handoff — Current

Updated: 2026-09-18

This is the first file to read when a new ChatGPT/Hermes/Codex session must resume Zooid work.

## Repository

- Repo: `funggier/Hermes-Zooid-Agent`
- Clean upstream branch: `main`
- Zooid working branch: `agent/zooid-independence`
- Hermes upstream baseline: `01382698fc32ec7740b6a204d9b7a6abeac74d33`
- Current production-code checkpoint before this documentation update:
  `59a55b4e6ce2d7e004d2b7f2ab5d036c7b774714`
- PR: #1, draft

Always verify GitHub current branch HEAD before relying on the SHA above.

## Read order

1. `zooid-development/AGENTS.md`
2. this file
3. `zooid-development/coordination/ACTIVE.md`
4. active numbered task:
   `zooid-development/tasks/004-hermes-kanban-executor-integration.md`
5. `zooid-development/coordination/STATUS.md`
6. `zooid-development/tasks/README.md`
7. architecture plan only as needed:
   `zooid-development/plans/minimal-cogentnexus-runtime.md`

Do not load every historical task unless its rationale is needed.

## What already works

### Task 001 — repository baseline

DONE.

Fork main was fast-forwarded to current Hermes baseline and Zooid planning was isolated under
`zooid-development/`.

### Task 002 — durable CogentNexus kernel

DONE and GREEN.

Code:

`zooid_cnx/store.py`

Provides Project, Ticket, Step, Evidence, semantic Events, Checkpoints, idempotency and
conservative recovery.

Critical invariant:

`RUNNING -> VERIFY` after interruption; no implicit side-effect replay.

### Task 003 — executor-neutral bridge

DONE and GREEN.

Code:

`zooid_cnx/execution.py`

Provides `ExecutorPort`, `ExecutionCoordinator`, durable external bindings and reconciliation.

Authoritative Zooid workflow run for this contract:

`35352550001` — SUCCESS.

## What is being done now

Task 004 — Hermes Kanban Executor Integration.

Goal: implement the first real executor using current Hermes Kanban while storing its writable
board state under Zooid ownership.

Key discovery:

Hermes already supports task `idempotency_key` and pins a worker to a DB through
`HERMES_KANBAN_DB`.

This means Zooid should reuse Kanban dispatch/heartbeat/run mechanics rather than duplicate them.

## Immediate next action

Create RED tests for a concrete Hermes Kanban adapter using a temporary isolated Kanban DB.

Then implement the minimum adapter that can:

- submit by deterministic CogentNexus operation key;
- find/reuse the same task;
- inspect status;
- surface completed result/evidence;
- preserve blocked state;
- work through the generic `ExecutionCoordinator`.

Do not launch a real provider worker until this source-level adapter contract is GREEN.

## Current safety boundaries

- Do not force-push.
- Keep `main` clean as upstream mirror.
- Do not write to live `~/.hermes` state.
- Do not stop/reset/uninstall live Hermes/OpenClaw/CogentNexus-OpenClaw for this task.
- Do not infer that external side effects are safe to replay.
- Keep CogentNexus semantic completion evidence-gated.
- Preserve attribution/licenses.

## Validation note

Zooid now owns a lightweight workflow:

`.github/workflows/zooid-cnx.yml`

It runs CogentNexus contracts on standard GitHub runners.

Inherited upstream CI includes NousResearch large-runner labels such as
`ubuntu-latest-96-core` and `windows-latest-32-core`, which may remain queued in this fork.
Do not confuse that infrastructure limitation with Zooid contract failure.

## If interrupted again

Do not reconstruct state from chat memory first.

Read this file, ACTIVE, Task 004 and current GitHub Actions. Continue from the last exact
repository evidence and append the outcome to the numbered task/worklog.
