# Task 011 — HermesZooid Desktop Identity Independence

- Task ID: `011-hermeszooid-desktop-identity-independence`
- State: ACTIVE
- Opened: 2026-09-18
- Depends on: Task 010
- Starting GREEN SHA: `14dae17beb6cb0aaa5f0988fb85224c8191426bd`

## Why this task exists

The Windows CLI installer is now isolated, but the inherited Electron Desktop still identifies itself to the OS as Hermes.

Current collision surfaces include:
- npm workspace name `hermes`;
- product/executable/shortcut/uninstall display `Hermes`;
- app ID `com.nousresearch.hermes`;
- deep-link scheme `hermes://`;
- Desktop home resolver reading `HERMES_HOME` and `%LOCALAPPDATA%\hermes`;
- Desktop userData override `HERMES_DESKTOP_USER_DATA_DIR`;
- bootstrap root `<HermesHome>/hermes-agent`;
- bootstrap download source `NousResearch/hermes-agent`;
- Windows AppUserModelID `com.nousresearch.hermes`.

Any one of these can cause side-by-side Desktop installations to share state, handlers, shortcuts, notifications, or update/bootstrap resources.

## Canonical Desktop identity

- npm workspace package: `hermeszooid-desktop`;
- display/product/executable: `HermesZooid`;
- app ID / Windows AUMID: `com.funggier.hermeszooid`;
- protocol: `hermeszooid://`;
- repository: `funggier/Hermes-Zooid-Agent`;
- Desktop userData override: `HERMESZOOID_DESKTOP_USER_DATA_DIR`;
- runtime root input: `HERMESZOOID_HOME`;
- Windows runtime root default: `%LOCALAPPDATA%\hermeszooid`;
- POSIX runtime root default: `~/.hermeszooid`;
- managed app root: `<HERMESZOOID_HOME>/app`.

Bare `zooid` remains reserved for the separate Zooid project.

## Ownership invariant

HermesZooid Desktop must never select writable state from:
- `HERMES_HOME`;
- `HERMES_DESKTOP_USER_DATA_DIR`;
- `ZOOID_HOME`;
- `%LOCALAPPDATA%\hermes`;
- `%LOCALAPPDATA%\zooid`;
- `~/.hermes` or `~/.zooid`.

Inherited Hermes backend modules may receive a process-local `HERMES_HOME` translated from the already-resolved HermesZooid root, but that variable is never an ownership input.

## TDD plan

RED first. Prove:
1. package/build identity is HermesZooid and package-lock agrees;
2. app ID/AUMID is `com.funggier.hermeszooid`;
3. executable, shortcut, uninstall display and artifacts use `HermesZooid`;
4. only `hermeszooid` deep-link scheme is registered;
5. Desktop home resolver uses only HermesZooid inputs/defaults;
6. Desktop userData override is HermesZooid-owned;
7. managed app root is `<home>/app`, not `hermes-agent`;
8. bootstrap installer source is this repository, not NousResearch upstream;
9. bootstrap subprocess passes `HERMESZOOID_HOME`, not an ownership-level `HERMES_HOME`;
10. existing Hermes and bare Zooid Desktop identifiers remain untouched.

## Non-goals

- full updater ownership;
- uninstall/reset end-to-end qualification;
- scheduled gateway/task naming outside Desktop;
- live-machine installation;
- Task 008 provider acceptance.

These are later numbered tasks.

## Immediate next action

Add a dedicated Desktop identity RED contract, then minimally repair package metadata and Desktop machine/runtime ownership until GREEN.
