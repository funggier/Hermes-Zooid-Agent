# Zooid Session Handoff — Current

Updated: 2026-09-19

Repo: `funggier/Hermes-Zooid-Agent`
Branch: `agent/zooid-independence`
Canonical product token: `hermeszooid`
Bare `zooid` is reserved for the separate Zooid project.

## Completed

Tasks 009–012 are DONE/GREEN:
- package/CLI/home;
- Windows installer;
- Electron Desktop;
- Tauri bootstrap setup.

## Active

Task 013 — Gateway Service and Process Ownership.

Primary safety target: a HermesZooid stop/restart/update-style scan must never select a genuine Hermes gateway process.

## Resume order

1. `zooid-development/AGENTS.md`
2. this file
3. `coordination/ACTIVE.md`
4. `tasks/013-hermeszooid-gateway-service-process-ownership.md`
5. `coordination/STATUS.md`

## Safety

No real-machine install yet. No force push. Existing Hermes and separate Zooid resources must remain untouched.
