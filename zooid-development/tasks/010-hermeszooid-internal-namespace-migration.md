# Task 010 — HermesZooid Internal Namespace Migration

- Task ID: `010-hermeszooid-internal-namespace-migration`
- State: ACTIVE
- Opened: 2026-09-18
- Depends on: Task 009

## Naming invariant

The user has a separate program/project named **Zooid**.

Therefore HermesZooid must not install or expose any bare Zooid package/runtime identity.

Reserved for the other project:
- `zooid`
- `ZOOID_HOME`
- `.zooid`
- `%LOCALAPPDATA%\zooid`
- top-level Python namespace intended to belong to Zooid.

HermesZooid canonical namespace:
- distribution/CLI/home: `hermeszooid`
- CogentNexus runtime package: `hermeszooid.cnx`

## Why this task exists

Tasks 002–008 were developed before the final product token was fixed, so source runtime still lives in top-level package `zooid_cnx` and tests/workflow paths still use that historical name.

Even though `zooid_cnx` is not currently included in installed package discovery, leaving it as the active runtime namespace creates future collision/confusion risk and makes packaging incomplete.

## TDD contract

RED first. Prove:
1. `import hermeszooid.cnx` exposes the CogentNexus runtime;
2. runtime modules import from `hermeszooid.cnx.*`;
3. `python -m hermeszooid.cnx` is the CNX operator surface;
4. active tests no longer import `zooid_cnx`;
5. installed package discovery contains the full `hermeszooid` tree;
6. top-level `zooid_cnx` package is absent after migration;
7. focused workflows use HermesZooid naming.

## Migration policy

No compatibility shim named `zooid_cnx` will be installed. This is deliberate to prevent namespace ownership ambiguity with the separate Zooid project.

Historical task/report text may mention the old namespace as evidence of what happened; historical records are not runtime resources.

## Non-goals

- Windows installer paths/services;
- Desktop app IDs/protocol/shortcuts;
- uninstall/update ownership;
- live-machine installation.

Those follow after source/package namespace is GREEN.

## Immediate next action

Add RED namespace tests, then atomically move the runtime package and update active tests/workflows/imports.
