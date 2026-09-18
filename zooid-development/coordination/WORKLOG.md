# Work Log

Append entries chronologically. Do not erase failed attempts. Numbered task files are the
durable detailed history; this file is the compact timeline.

## 2026-09-06 — Genesis audit

- Historical pre-numbering work.
- Source: `089bb32886c8c18f7fa20182c7bf8826d6935ac5`
- Result: initial fork/license/home/installer/Desktop/updater/skills inspection.
- Limitation: source ownership later became stale.

## 2026-09-18 — Task 001 DONE

- Synced fork `main` to Hermes upstream `01382698fc32ec7740b6a204d9b7a6abeac74d33`.
- Advance: 4,678 commits.
- No force push.
- Isolated Zooid planning under `zooid-development/`.
- Established clean-main / Zooid-branch policy.
- Detail: `../tasks/001-upstream-sync-and-planning-isolation.md`

## 2026-09-18 — Task 002 DONE / GREEN

- Built `zooid_cnx` durable CogentNexus semantic kernel.
- Added Project/Ticket/Step/Evidence/Event/Checkpoint/idempotency/recovery.
- Persistence uses `ZOOID_HOME`, not HERMES_HOME fallback.
- Conservative crash invariant: `RUNNING -> VERIFY`, no implicit replay.
- GREEN checkpoint: `e29010b62e08d3a78872c2bf16ce0d6428ae3b58`.
- Detail: `../tasks/002-minimal-cogentnexus-durable-kernel.md`

## 2026-09-18 — Task 003 DONE / GREEN

- RED: `7b14546e916003546024279a45b9c4ba130fac1d`.
- Implementation: `59a55b4e6ce2d7e004d2b7f2ab5d036c7b774714`.
- Added executor-neutral bridge and durable external bindings.
- Zooid workflow run `35352550001`: SUCCESS.
- Detail: `../tasks/003-executor-neutral-execution-bridge.md`

## 2026-09-18 — Task 004 ACTIVE

- Goal: concrete Hermes Kanban executor using Zooid-owned writable Kanban state.
- Confirmed current Hermes has task idempotency keys and `HERMES_KANBAN_DB` pinning.
- Adapter RED/implementation not yet committed.
- Immediate next action: write isolated real-Kanban adapter tests.
- Detail: `../tasks/004-hermes-kanban-executor-integration.md`

## 2026-09-18 — Coordination numbering introduced

- User requested durable chronological task history so an emergency new session can resume by
  reading GitHub rather than relying on conversation context.
- Numbered historical tasks 001–003 were reconstructed from existing repository evidence.
- Task 004 is the first active task under the explicit monotonic numbering policy.
- Added `SESSION-HANDOFF.md` as the fast resume entry point.
