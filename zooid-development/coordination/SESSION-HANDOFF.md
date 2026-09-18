# Zooid Session Handoff — Current

Updated: 2026-09-19

Repo: `funggier/Hermes-Zooid-Agent`
Branch: `agent/zooid-independence`
Canonical product token: `hermeszooid`
Bare `zooid` is reserved for the separate Zooid project.

## Completed

Tasks 009–014 are DONE/GREEN:
- package/CLI/home;
- Windows installer;
- Desktop;
- bootstrap setup;
- gateway service/process ownership;
- fixed listener/default-port coexistence.

Latest qualified SHA before this docs checkpoint: `a9ecb4a1a27d9d971ac9114dad137e73c37863f2`.

## Active

Task 015 — Update Ownership and Upstream Isolation.

Primary safety target: `hermeszooid update` must never fetch/replace from NousResearch Hermes by default or clean/restart the existing Hermes installation.

## Resume order

1. `zooid-development/AGENTS.md`
2. this file
3. `coordination/ACTIVE.md`
4. `tasks/015-hermeszooid-update-ownership-upstream-isolation.md`
5. `coordination/STATUS.md`

## Safety

No real-machine install yet. No force push. Existing Hermes and separate Zooid resources must remain untouched.
