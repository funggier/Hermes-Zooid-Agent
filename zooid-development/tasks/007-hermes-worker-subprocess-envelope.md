# Task 007 — Hermes Worker Subprocess Envelope

- Task ID: `007-hermes-worker-subprocess-envelope`
- State: ACTIVE
- Opened: 2026-09-18
- Depends on: Task 006
- Starting GREEN SHA: `0db88c097293df5182f084de32971c7abe207414`

## Why this task exists

Task 006 proves a dedicated dispatcher process can own the Zooid Kanban environment. The next
unproven boundary is the worker process created by Hermes dispatcher.

Before using a real provider/model, Zooid must prove that Hermes' real worker spawn path receives
the correct task/run/claim/workspace/board identity and cannot escape into the normal Hermes
Kanban board.

## Strategy

Use current Hermes `_default_spawn` and point `HERMES_BIN` to a test executable that does not
call any provider. The executable only records argv, cwd and selected environment fields.

This preserves the real Hermes spawn/env construction path while removing network, model,
credential and quota variables from the acceptance result.

## Contract to prove

- real Hermes worker spawn path is called;
- one child process starts;
- cwd equals the Zooid task workspace;
- worker receives the Zooid Kanban DB/board/workspaces identity;
- worker receives task id, run id and claim lock;
- worker source is tagged `kanban`;
- parent/dispatcher routing stays Zooid-owned;
- no provider API is contacted;
- worker process can exit/cleanup without corrupting task/run state.

## Dependency boundary

The lightweight Zooid CI may need small inherited Hermes runtime dependencies required merely to
import the spawn path. Add only what is demonstrated necessary; do not pull all optional provider
extras just to make this test run.

## Non-goals

- real LLM response;
- provider routing;
- user credential migration;
- final Zooid profile/config identity;
- multi-worker scheduling.

## Acceptance

Task 007 is DONE when the real Hermes worker spawn envelope is GREEN with a provider-free fake
worker executable and exact evidence is recorded here.

## Immediate next action

Write the RED worker-envelope contract against `_default_spawn` and identify the minimum
runtime imports needed by that path.
