# Zooid Session Handoff — Current

Updated: 2026-09-18

Read this first when a new session resumes Zooid work.

## Repository

- Repo: `funggier/Hermes-Zooid-Agent`
- Clean upstream branch: `main`
- Zooid branch: `agent/zooid-independence`
- Hermes upstream baseline: `01382698fc32ec7740b6a204d9b7a6abeac74d33`
- Last GREEN code SHA before this documentation checkpoint:
  `68c2a2a7337cd7162a98a5ac90400e11ca2abeb9`
- PR #1 remains draft.

Always verify current GitHub HEAD and Actions before trusting cached SHA/status.

## Read order

1. `zooid-development/AGENTS.md`
2. this file
3. `zooid-development/coordination/ACTIVE.md`
4. `zooid-development/tasks/005-hermes-dispatcher-lifecycle-integration.md`
5. `zooid-development/coordination/STATUS.md`
6. task index/history only as needed

## Completed foundation

### Task 001

DONE. Fork synchronized and Zooid development layer isolated.

### Task 002

DONE / GREEN. Durable CogentNexus kernel:
Project, Ticket, Step, Evidence, Events, Checkpoints, idempotency and conservative recovery.

### Task 003

DONE / GREEN. Generic ExecutionCoordinator + replaceable ExecutorPort + durable external binding.

### Task 004

DONE / GREEN. Concrete `HermesKanbanExecutor`.

Final validation:

- SHA `68c2a2a7337cd7162a98a5ac90400e11ca2abeb9`
- Zooid workflow `35354752792` — SUCCESS

Important Task 004 decisions:

- Kanban writable state belongs under `ZOOID_HOME`.
- Hermes `done` does not imply CogentNexus acceptance.
- Evidence must arrive through `metadata.cogentnexus_evidence`.
- operation-key search is conservative across archived cards.
- dedicated Zooid board initialization uses Hermes base schema plus migration pass.

## Active work — Task 005

Prove the real dispatcher lifecycle around a CogentNexus-created Kanban card using an injected
spawn function before any provider/model call.

Target:

`READY -> claim -> Zooid workspace -> spawn -> RUNNING -> structured completion -> CogentNexus DONE`

Current Hermes exposes `dispatch_once(..., spawn_fn=...)`, making this separation possible.

## Immediate next action

Add and run the dispatcher lifecycle contract. Prefer existing Hermes mechanics and the narrowest
possible adapter changes.

## Safety boundaries

- do not use live `~/.hermes`;
- do not call a real provider yet;
- do not force push;
- do not mutate live Hermes/OpenClaw;
- do not weaken evidence gating;
- do not retry uncertain side effects automatically.

If interrupted, resume from GitHub evidence, not chat memory.
