# Task 012 — HermesZooid Bootstrap Setup Identity Independence

- Task ID: `012-hermeszooid-bootstrap-setup-identity`
- State: ACTIVE
- Opened: 2026-09-18
- Depends on: Task 011
- Starting GREEN SHA: `494c21064f8545375a4497e363e8dd356d7ed7e8`

## Why this task exists

HermesZooid Desktop is now OS-unique, but the separate Tauri bootstrap installer still presents and persists inherited Hermes identity.

Current collision surfaces include:
- Tauri product `Hermes`;
- identifier `com.nousresearch.hermes.setup`;
- binary `Hermes-Setup`;
- Windows manifest identity `NousResearch.Hermes.Setup`;
- root input `HERMES_HOME`;
- Windows root `%LOCALAPPDATA%\hermes`;
- POSIX root `~/.hermes`;
- staged installer helper `hermes-setup.exe`;
- dev-source env `HERMES_SETUP_DEV_REPO_ROOT`;
- raw installer download from `NousResearch/hermes-agent`.

## Canonical setup identity

- product/window/bundle name: `HermesZooid Setup`;
- Tauri identifier: `com.funggier.hermeszooid.setup`;
- binary: `HermesZooid-Setup`;
- Windows assembly identity: `Funggier.HermesZooid.Setup`;
- product root input: `HERMESZOOID_HOME`;
- staged helper: `hermeszooid-setup.exe` (or no extension off Windows);
- dev source env: `HERMESZOOID_SETUP_DEV_REPO_ROOT`;
- raw installer source: `funggier/Hermes-Zooid-Agent`.

## Ownership invariant

The setup app must not select writable state from `HERMES_HOME`, `ZOOID_HOME`, `%LOCALAPPDATA%\hermes`, `%LOCALAPPDATA%\zooid`, `~/.hermes`, or `~/.zooid`.

## Scope

This task covers setup-app product identity, setup-home selection, helper name, and installer-script source.

The updater command path, gateway scheduled-task/service identity, default ports, and uninstall/reset fences are deliberately deferred to Tasks 013–014 so their runtime behavior can be tested independently.

## TDD plan

RED first. Prove:
1. Tauri package/bundle/window identifier is HermesZooid-owned;
2. Cargo package/bin/lib identifiers do not claim Hermes executable names;
3. Windows application manifest identity is HermesZooid-owned;
4. setup home resolves only `HERMESZOOID_HOME` or HermesZooid defaults;
5. staged helper is `hermeszooid-setup`;
6. setup log-level env is HermesZooid-owned;
7. dev-source env is HermesZooid-owned;
8. raw install script comes from `funggier/Hermes-Zooid-Agent`;
9. no bare Zooid machine root or helper identity is introduced.

## Immediate next action

Add a focused bootstrap-setup RED contract and repair the Tauri/Rust identity/home/source boundary until GREEN.
