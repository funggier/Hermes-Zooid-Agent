# Task 003 — Executor-Neutral Execution Bridge

- Task ID: `003-executor-neutral-execution-bridge`
- State: DONE
- Date: 2026-09-18
- Depends on: Task 002

## Why this task existed

A durable Ticket model alone cannot perform real work. CogentNexus needs to hand a bounded
Step to an executor while keeping semantic ownership inside CogentNexus.

The bridge must also remain replaceable so Hermes/Kanban can be the first executor without
becoming a permanent architectural dependency.

## Required contract

The bridge must:

1. claim one CogentNexus Step;
2. derive a deterministic external operation key;
3. create or discover exactly one external task;
4. persist the external binding;
5. survive a crash between external creation and local binding;
6. reconcile executor success into Evidence;
7. allow Ticket completion only through the CogentNexus acceptance gate;
8. turn deterministic external failure into BLOCKED;
9. never automatically retry uncertain side effects.

## RED

Contract commit:

`7b14546e916003546024279a45b9c4ba130fac1d`

Zooid-owned CI executed the contract and failed during collection because
`zooid_cnx.execution` did not yet exist.

This is the authoritative RED for this task.

## Implementation

Implementation commit:

`59a55b4e6ce2d7e004d2b7f2ab5d036c7b774714`

Added:

- executor-neutral `ExecutorPort`;
- `ExecutionCoordinator`;
- deterministic operation key:
  `cnx:<ticket_id>:<step_id>:execute`;
- durable `executor_bindings`;
- reconciliation of queued/running/succeeded/failed/blocked states;
- Evidence import from external executor results;
- Ticket finalization through existing CogentNexus acceptance logic;
- explicit block transition.

## Recovery behavior

When restart finds an interrupted Step:

- CogentNexus changes RUNNING to VERIFY;
- the coordinator checks the durable external binding;
- if the binding is absent, it searches the executor by deterministic operation key;
- if the executor can prove an external task already exists, the binding is reconstructed;
- otherwise it stops at NEEDS_VERIFICATION instead of creating another task.

## GREEN

Zooid workflow:

`Zooid CogentNexus Kernel / CogentNexus runtime contracts`

Run ID:

`35352550001`

Result: SUCCESS.

Docker workflow on the implementation commit also completed successfully.

The inherited upstream full CI/Nix jobs use large NousResearch-specific runner labels and may
remain queued on the fork; they are not substituted for the Zooid-owned contract workflow.

## Result

PASS.

CogentNexus can now drive a generic external executor while preserving durable, evidence-gated
semantic state.

## Follow-up

Task 004 binds the generic `ExecutorPort` to the real Hermes Kanban execution substrate,
using Zooid-owned Kanban storage.
