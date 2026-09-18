# Zooid Session Handoff — Current

Updated: 2026-09-18

Repo: `funggier/Hermes-Zooid-Agent`
Branch: `agent/zooid-independence`
Canonical product token: `hermeszooid`

## User priority change

Do product independence/coexistence before installing or running live acceptance on the real machine.

Task 008 is PAUSED / SOURCE_READY.
Task 009 is ACTIVE.

## Resume order

1. `zooid-development/AGENTS.md`
2. this file
3. `coordination/ACTIVE.md`
4. `tasks/009-hermeszooid-cli-home-independence.md`
5. `coordination/STATUS.md`

## Current target

Make hermeszooid own its CLI and home selection:
- `hermeszooid`
- `HERMESZOOID_HOME`
- Windows `%LOCALAPPDATA%\hermeszooid`
- POSIX `~/.hermeszooid`

Existing `HERMES_HOME` must never choose hermeszooid product state.

## Safety

No real-machine installation yet. No force push. No live Hermes/OpenClaw lifecycle mutation.
