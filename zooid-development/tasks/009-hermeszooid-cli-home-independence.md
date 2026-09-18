# Task 009 — hermeszooid CLI and Home Independence

- Task ID: `009-hermeszooid-cli-home-independence`
- State: DONE / GREEN
- Opened: 2026-09-18
- Completed: 2026-09-18
- Canonical product token: `hermeszooid`
- RED commit: `f045c272c530d8d32571d131e4341fdf0617e2a8`
- Collision-hardening test commit: `a483cc0962e3f81e6ee1311e0390a697bf856d71`
- Final tested SHA: `71f30c93b68bfcd46c8eea08c57ba33298ca682d`
- HermesZooid Identity workflow: `35360523016` — SUCCESS
- Zooid CogentNexus workflow: `35360522931` — SUCCESS
- Docker: SUCCESS

## Purpose

Create a root product boundary that cannot accidentally share writable state or command names with either an existing Hermes installation or the separate Zooid project.

## Canonical identity

- Python distribution: `hermeszooid`
- CLI: `hermeszooid`
- product home variable: `HERMESZOOID_HOME`
- Windows default: `%LOCALAPPDATA%\hermeszooid`
- POSIX default: `~/.hermeszooid`

Bare `zooid` is reserved for the separate Zooid project and is not a HermesZooid runtime/install identity.

## RED

`f045c272c530d8d32571d131e4341fdf0617e2a8` failed exactly because the new `hermeszooid` package did not yet exist.

## Implementation

Added stdlib-first package `hermeszooid/` with:
- `identity.py` for product-home ownership;
- `cli.py` launcher;
- `python -m hermeszooid` entrypoint.

The launcher resolves HermesZooid ownership first, then maps the resolved home into process-local `HERMES_HOME` only for inherited Hermes internals.

One-way translation:
`HERMESZOOID_HOME/default -> process-local HERMES_HOME`

Never:
`existing HERMES_HOME -> HermesZooid product home`

`ZOOID_HOME` is removed from the translated runtime environment and is not used for writable-state selection.

Package metadata now owns the `hermeszooid` distribution and does not export `hermes`, `hermes-agent`, `hermes-acp`, or bare `zooid` console commands.

## Validation

Dedicated `HermesZooid Identity` workflow verifies:
- lockfile identity with `uv lock --check`;
- CLI/home isolation contract;
- coexistence with inherited Hermes command namespace;
- no bare Zooid product identity.

Result: PASS.

## Follow-up

Task 010 isolates the Windows installer itself: repository source, install root, launchers, user environment variables, and process/lifecycle ownership.
