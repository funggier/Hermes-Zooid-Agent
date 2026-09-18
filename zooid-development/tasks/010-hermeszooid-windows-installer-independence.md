# Task 010 — HermesZooid Windows Installer Independence

- Task ID: `010-hermeszooid-windows-installer-independence`
- State: DONE / GREEN
- Opened: 2026-09-18
- Completed: 2026-09-18
- Depends on: Task 009
- RED commit: `8f0eddfa151b2511a792212f7e647fd845c893b5`
- Production repair: `08ad934fb2777c1eee411df5ca4e28905e45d82a`
- Current namespace-clean GREEN SHA: `14dae17beb6cb0aaa5f0988fb85224c8191426bd`
- Windows Installer workflow on current HEAD: `35361401981` — SUCCESS

## Why this task existed

Task 009 separated distribution, CLI, and product home, but the inherited Windows installer still owned Hermes paths, launchers, repository URLs, persistent environment variables, and lifecycle targets.

That could collide with an existing Hermes installation even though the Python runtime itself was isolated.

## RED

Commit `8f0eddfa151b2511a792212f7e647fd845c893b5` added two independent contracts:

1. static installer ownership;
2. real `install.ps1 -ShowResolvedPaths` behavior on `windows-latest`.

The Windows RED proved the inherited installer did not expose/resolve `hermeszooid_home` and still followed Hermes ownership.

## Repair

Commit `08ad934fb2777c1eee411df5ca4e28905e45d82a` changed machine-owning installer resources to HermesZooid:

- root `%LOCALAPPDATA%\hermeszooid`;
- root env `HERMESZOOID_HOME`;
- app dir `<root>\app`;
- repository `funggier/Hermes-Zooid-Agent`;
- PATH launcher `hermeszooid` only;
- persistent helper env `HERMESZOOID_GIT_BASH_PATH`;
- no persistent `HERMES_HOME` or `ZOOID_HOME` writes;
- lifecycle target `hermeszooid.exe` / `HermesZooid_Gateway`, never existing Hermes resources;
- inherited `HERMES_HOME` / `HERMES_GIT_BASH_PATH` are process-local compatibility translations only.

## GREEN

Dedicated `HermesZooid Windows Installer Identity` workflow passed both:

- Installer ownership static contract;
- Windows resolved paths contract.

On current namespace-clean HEAD `14dae17beb6cb0aaa5f0988fb85224c8191426bd`, workflow `35361401981` is SUCCESS.

The same HEAD also has:
- HermesZooid Identity `35361402036` — SUCCESS;
- HermesZooid CogentNexus Kernel `35361402094` — SUCCESS;
- Docker `35361401966` — SUCCESS.

## Result

PASS.

Windows CLI installer ownership is isolated from both existing Hermes and the separate Zooid project.

## Follow-up

Task 011 isolates Desktop OS identity, userData/runtime home, deep-link protocol, bootstrap root/repository, shortcut/uninstall identity, and AppUserModelID.
