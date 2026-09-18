# Task 012 — HermesZooid Bootstrap Setup Identity Independence

- Task ID: `012-hermeszooid-bootstrap-setup-identity`
- State: DONE / GREEN
- Opened: 2026-09-18
- Completed: 2026-09-18
- Depends on: Task 011
- RED commit: `fd8ec87c2bbae9332cf88ff7d32dd9b0ee3b4697`
- Production repair: `427c426fd1e47f0d5568d82f5c809e68b3268db1`
- Bootstrap Setup Identity workflow: `35363272722` — SUCCESS

## Purpose

Separate the Tauri bootstrap/setup application from inherited Hermes and bare Zooid machine identity before any real-machine installation.

## Qualified identity

- setup product/window: `HermesZooid Setup`;
- Tauri identifier: `com.funggier.hermeszooid.setup`;
- binary: `HermesZooid-Setup`;
- Windows assembly: `Funggier.HermesZooid.Setup`;
- product root input: `HERMESZOOID_HOME`;
- staged helper: `hermeszooid-setup`;
- development source env: `HERMESZOOID_SETUP_DEV_REPO_ROOT`;
- raw installer source: `funggier/Hermes-Zooid-Agent`.

## TDD evidence

RED `fd8ec87c2bbae9332cf88ff7d32dd9b0ee3b4697` defined the bootstrap machine-identity contract.

Production repair `427c426fd1e47f0d5568d82f5c809e68b3268db1` changed Tauri/Cargo/manifest/home/helper/source identity to HermesZooid ownership.

Dedicated workflow `35363272722` passed the full bootstrap identity contract.

Same HEAD regression evidence:
- Desktop Identity `35363272731` — SUCCESS;
- CogentNexus `35363272609` — SUCCESS;
- HermesZooid Identity `35363272711` — SUCCESS;
- Windows Installer `35363272816` — SUCCESS;
- Docker `35363272677` — SUCCESS.

## Result

PASS.

Real-machine installation remains blocked because gateway/service/process ownership, listener defaults, updater and destructive lifecycle fences are not yet all qualified.

## Follow-up

Task 013 qualifies gateway service names, launcher process identity, and stop/restart process-selection fences. Listener/port allocation is deliberately audited separately after process ownership is GREEN.
