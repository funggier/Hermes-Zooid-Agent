# Task 011 — HermesZooid Desktop Identity Independence

- Task ID: `011-hermeszooid-desktop-identity-independence`
- State: DONE / GREEN
- Opened: 2026-09-18
- Completed: 2026-09-18
- Depends on: Task 010
- RED commit: `9c20e7e71857298115a1e68284a1b8fca3003b4d`
- GREEN commit: `494c21064f8545375a4497e363e8dd356d7ed7e8`
- Desktop Identity RED workflow: `35361896507` — FAILURE
- Desktop Identity GREEN workflow: `35362206169` — SUCCESS

## Why this task existed

Package/home and CLI installer ownership were isolated, but Electron still claimed Hermes machine identity: app ID, executable/shortcut, protocol, Desktop userData/home inputs, AUMID, and bootstrap repository/root.

## RED

Commit `9c20e7e71857298115a1e68284a1b8fca3003b4d` added a focused Desktop identity contract.

Workflow `35361896507` failed on four expected boundaries:
- desktop package still named `hermes`;
- lockfile workspace still named/linking `hermes`;
- Electron still used Hermes-owned userData/home inputs;
- bootstrap still downloaded NousResearch/Hermes installer resources.

The bare-Zooid collision guard already passed.

## Repair

Commit `494c21064f8545375a4497e363e8dd356d7ed7e8` changed OS-facing ownership:

- workspace `hermeszooid-desktop`;
- product/executable/shortcut/uninstall display `HermesZooid`;
- app ID/AUMID `com.funggier.hermeszooid`;
- protocol `hermeszooid://` (`hermeszooid-dev://` in dev);
- repository `funggier/Hermes-Zooid-Agent`;
- artifact/DMG/mac bundle identity `HermesZooid`;
- userData override `HERMESZOOID_DESKTOP_USER_DATA_DIR`;
- runtime ownership input `HERMESZOOID_HOME` only;
- Windows default `%LOCALAPPDATA%\hermeszooid`;
- POSIX default `~/.hermeszooid`;
- managed app root `<HERMESZOOID_HOME>/app`;
- bootstrap installer source moved to this repository and the product app root.

Internal inherited code may still receive an alias `HERMES_HOME = HERMESZOOID_HOME`, but Desktop never reads existing `HERMES_HOME` or `ZOOID_HOME` to select writable ownership.

## GREEN

On `494c21064f8545375a4497e363e8dd356d7ed7e8`:
- HermesZooid Desktop Identity `35362206169` — SUCCESS;
- HermesZooid Identity `35362206203` — SUCCESS;
- HermesZooid CogentNexus Kernel `35362206252` — SUCCESS;
- HermesZooid Windows Installer Identity `35362206055` — SUCCESS;
- Docker `35362206442` — SUCCESS.

## Result

PASS.

Desktop package/build/deep-link/userData/runtime-root identity no longer claims Hermes or bare Zooid resources.

## Follow-up

Task 012 isolates the separate Tauri bootstrap/setup application before lifecycle/update/service qualification.
