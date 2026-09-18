# Task 009 — hermeszooid CLI and Home Independence

- Task ID: `009-hermeszooid-cli-home-independence`
- State: DONE / GREEN
- Opened: 2026-09-18
- Completed: 2026-09-18
- Canonical product token: `hermeszooid`
- RED commit: `f045c272c530d8d32571d131e4341fdf0617e2a8`
- Implementation: `cc272da4c5e345b002e632320535a5d3a5e5ebfe`
- Dispatcher migration fix: `4eabc3f333bdf4f802475d7f9fb2ad95cef20bfa`
- Lock identity fix: `8ccc789cec6d5d19f0ad0a75eb6b102db3583ca2`
- HermesZooid identity workflow commit: `71f30c93b68bfcd46c8eea08c57ba33298ca682d`
- Authoritative identity run: `35360523016` — SUCCESS

## Why this task existed

The fork still inherited Hermes package, CLI and writable-home identity. In addition, the user has a separate program/project named Zooid, so HermesZooid must not consume bare `zooid` runtime/install identity either.

## Canonical product boundary

- Distribution: `hermeszooid`
- CLI: `hermeszooid`
- Product home environment variable: `HERMESZOOID_HOME`
- Windows default: `%LOCALAPPDATA%\hermeszooid`
- POSIX default: `~/.hermeszooid`

The installed distribution exports no `hermes`, `hermes-agent`, `hermes-acp`, or `zooid` command.

`HERMES_HOME` is only a process-local compatibility variable after HermesZooid has already resolved its own home. Existing `HERMES_HOME` never chooses HermesZooid state.

`ZOOID_HOME` is ignored/removed at the HermesZooid boundary and must not choose writable product state.

## TDD history

RED `f045c272...`: `hermeszooid` package did not exist.

The contract was tightened in `a483cc09...` to forbid Hermes and Zooid CLI collisions and require distribution name `hermeszooid`.

Implementation `cc272da4...` added the `hermeszooid` launcher/identity module and migrated CogentNexus/Kanban defaults to `HERMESZOOID_HOME`.

`4eabc3f3...` repaired one child-process migration mismatch discovered by the full focused contract.

`8ccc789c...` refreshed only the local-project/self-extra identity in `uv.lock` from `hermes-agent` to `hermeszooid` without changing dependency versions.

## GREEN

HermesZooid-owned workflow:
`HermesZooid Identity / Package CLI home and lock identity`

Run `35360523016` — SUCCESS.

It proves:
- explicit `HERMESZOOID_HOME` wins;
- Windows and POSIX defaults are HermesZooid-owned;
- existing Hermes and legacy Zooid home variables do not select product state;
- runtime translation is one-way into process-local `HERMES_HOME`;
- distribution and CLI identity are `hermeszooid`;
- colliding Hermes/Zooid CLI entry points are absent;
- CogentNexus and Kanban defaults use HermesZooid home;
- `uv lock --check` is clean.

## Result

PASS.

## Follow-up

Task 010 removes the remaining internal source/package namespace `zooid_cnx` by migrating it under `hermeszooid.cnx`. Bare `zooid` is reserved for the user's separate Zooid program.
