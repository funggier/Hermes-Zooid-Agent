# Upstream Synchronization Baseline

Date: 2026-09-18

- Fork: `funggier/Hermes-Zooid-Agent`
- Upstream: `NousResearch/hermes-agent`
- Fork `main` before synchronization: `089bb32886c8c18f7fa20182c7bf8826d6935ac5`
- Upstream `main` synchronized baseline: `01382698fc32ec7740b6a204d9b7a6abeac74d33`
- Upstream advance: **4,678 commits**
- Update method: fast-forward only; no force update.
- Previous Zooid planning head: `d51582fe064cd2a6b438d0d95d994529c0509e3e`

The latest stable release observed during synchronization was
**Hermes Agent v0.21.3 (v2026.9.14)**, published 2026-09-14.
The synchronized `main` commit is newer than that release tag.

## Preservation strategy

Fork `main` remains a clean Hermes mirror. Zooid planning is isolated under
`zooid-development/`, while original planning history remains reachable through Git history.

Because the prior targeted source audit used the September 6 baseline, production changes
must begin with a refreshed audit against the synchronized September 18 source tree.
