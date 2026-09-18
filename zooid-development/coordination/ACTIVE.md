# Active Work

- Project state: BASELINE_REFRESH_REQUIRED
- Task state: READY
- Repository: `funggier/Hermes-Zooid-Agent`
- Working branch: `agent/zooid-independence`
- Current upstream baseline: `01382698fc32ec7740b6a204d9b7a6abeac74d33`
- Previous audit baseline: `089bb32886c8c18f7fa20182c7bf8826d6935ac5`

## Current task

Refresh the Zooid independence source map against the synchronized Hermes baseline before
applying production changes.

The roadmap remains the intended direction, but the previous targeted source audit is stale
because upstream advanced by 4,678 commits.

## Required next actions

1. Re-read the Zooid roadmap and product-independence plan.
2. Re-audit updater, storage, package/entrypoint, lifecycle, installer/Desktop identity,
   skill lifecycle and coexistence ownership in current Hermes.
3. Record moved, renamed and newly introduced code paths.
4. Update task scope and evidence before modifying production code.
5. Keep `main` clean; perform Zooid work on this branch or descendants.
