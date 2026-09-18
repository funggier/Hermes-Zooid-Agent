# Task 010 — HermesZooid Windows Installer Independence

- Task ID: `010-hermeszooid-windows-installer-independence`
- State: ACTIVE
- Opened: 2026-09-18
- Depends on: Task 009
- Starting GREEN SHA: `71f30c93b68bfcd46c8eea08c57ba33298ca682d`

## Why this task exists

Task 009 isolates Python package/CLI/home ownership, but inherited `scripts/install.ps1` still contains Hermes-owned defaults and lifecycle behavior.

Current inherited installer risks include:
- default `%LOCALAPPDATA%\hermes` root;
- `HERMES_HOME` input;
- `hermes-agent` source directory;
- upstream `NousResearch/hermes-agent` clone URLs;
- PATH launchers named `hermes` / `hermes-acp`;
- portable Git/runtime resources under Hermes paths;
- process cleanup targeting `hermes.exe` and Hermes scheduled tasks;
- user environment variables with `HERMES_*` ownership.

Those can collide with the existing Hermes installation even after Task 009.

## Canonical Windows installer ownership

- product root: `%LOCALAPPDATA%\hermeszooid`
- explicit root env: `HERMESZOOID_HOME`
- source/app directory: `%LOCALAPPDATA%\hermeszooid\app`
- PATH launcher: `hermeszooid` only
- repository: `funggier/Hermes-Zooid-Agent`
- product-owned helper/runtime resources stay under `%LOCALAPPDATA%\hermeszooid`

No installer resource may use bare `zooid`, `%LOCALAPPDATA%\zooid`, `ZOOID_HOME`, or the existing Hermes writable root.

## Safety invariant

Running any non-destructive installer introspection/test must leave existing Hermes resources unchanged.

The installer must never terminate `hermes.exe`, delete Hermes scheduled tasks, alter Hermes user env vars, or place a `hermes` launcher on PATH.

## TDD plan

RED first with a Windows-standard-runner contract that proves:
1. `-ShowResolvedPaths` ignores inherited `HERMES_HOME` and `ZOOID_HOME`;
2. default root is `%LOCALAPPDATA%\hermeszooid`;
3. default app dir is `<root>\app`;
4. explicit `HERMESZOOID_HOME` wins;
5. installer source repo points to `funggier/Hermes-Zooid-Agent`;
6. launcher set contains `hermeszooid` and no `hermes`, `hermes-agent`, `hermes-acp`, or `zooid`;
7. static lifecycle ownership test rejects Hermes process/task cleanup in HermesZooid installer;
8. no bare Zooid runtime root/env ownership remains.

## Non-goals

- Desktop productName/app ID/protocol/shortcut;
- updater ownership;
- uninstall/reset qualification;
- live machine install;
- live provider acceptance.

Those receive later numbered tasks.

## Immediate next action

Add the Windows installer RED contract and dedicated standard-runner workflow, then minimally rewrite `scripts/install.ps1` until the contract is GREEN.
