# Task 001 — Upstream Sync and Planning Isolation

- Task ID: `001-upstream-sync-and-planning-isolation`
- State: DONE
- Date: 2026-09-18
- Repository: `funggier/Hermes-Zooid-Agent`
- Working branch: `agent/zooid-independence`

## Why this task existed

The fork had fallen behind Hermes upstream while Zooid-specific planning lived in paths that
could collide with upstream-owned documentation. Continuing development on that base would
increase merge risk and make later upstream synchronization unnecessarily difficult.

The project also needed a durable rule separating inherited Hermes code from Zooid-owned
planning and future product changes.

## Starting state

- Fork `main`: `089bb32886c8c18f7fa20182c7bf8826d6935ac5`
- Upstream: `NousResearch/hermes-agent/main`
- Current upstream selected: `01382698fc32ec7740b6a204d9b7a6abeac74d33`
- Upstream advance from old fork baseline: 4,678 commits
- Existing Zooid planning head before synchronization:
  `d51582fe064cd2a6b438d0d95d994529c0509e3e`

## Decisions

1. Keep fork `main` as a clean mirror of Hermes upstream.
2. Never put Zooid planning changes directly on clean `main`.
3. Keep Zooid work on `agent/zooid-independence` or descendant branches.
4. Move Zooid planning/coordination into top-level `zooid-development/`.
5. Do not modify root Hermes `AGENTS.md` merely to carry Zooid planning.
6. Preserve historical planning in Git instead of rewriting history.

## Work completed

- Fast-forwarded fork `main` to `01382698fc32ec7740b6a204d9b7a6abeac74d33`.
- No force push was used.
- Merged the updated upstream baseline into the Zooid branch while preserving old Zooid history.
- Isolated Zooid documents beneath `zooid-development/`.
- Added Zooid-specific `AGENTS.md` and upstream baseline documentation.
- Updated PR #1 to reflect the new baseline and preservation strategy.

## Evidence

- Upstream/Zooid merge checkpoint:
  `3d56d79d4354f9b46e2dbe572338fca2ed1086a1`
- Upstream baseline:
  `01382698fc32ec7740b6a204d9b7a6abeac74d33`
- Baseline CI, Nix and Docker were observed PASS before production CogentNexus work began.

## Result

PASS.

The repository now has a clean synchronization boundary:

`main = Hermes upstream mirror`

`agent/zooid-independence = Zooid product/development line`

This task established the repository structure required for safe long-term Zooid development.

## Follow-up

Task 002 builds the smallest durable CogentNexus runtime on top of this clean baseline.
