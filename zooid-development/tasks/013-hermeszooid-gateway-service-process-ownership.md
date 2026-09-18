# Task 013 — HermesZooid Gateway Service and Process Ownership

- Task ID: `013-hermeszooid-gateway-service-process-ownership`
- State: ACTIVE
- Opened: 2026-09-19
- Depends on: Task 012
- Starting GREEN SHA: `427c426fd1e47f0d5568d82f5c809e68b3268db1`

## Why this task exists

Package, installer, Desktop and setup identity are isolated, but inherited gateway lifecycle code still contains host-global Hermes identifiers and broad process matching.

Observed collision surfaces include:
- Windows Scheduled Task base `Hermes_Gateway`;
- Windows gateway launcher invoking `python -m hermes_cli.main`;
- generated gateway wrappers writing `HERMES_HOME` directly;
- systemd service base `hermes-gateway`;
- launchd label `ai.hermes.gateway`;
- whole-fleet scans using `hermes-gateway*` and `ai.hermes.gateway*`;
- fallback process scans that recognize generic `gateway run` command lines and can therefore see a genuine Hermes process;
- restart argv rebuilt with `-m hermes_cli.main`.

These are dangerous because `hermeszooid gateway stop/restart --all` must never select, terminate, protect-as-self, or respawn the user's existing Hermes gateway.

## Canonical gateway identity

- Windows Scheduled Task base: `HermesZooid_Gateway`;
- systemd base: `hermeszooid-gateway`;
- launchd base: `com.funggier.hermeszooid.gateway`;
- generated launcher command: `python -m hermeszooid ... gateway run`;
- generated launcher product home: `HERMESZOOID_HOME`;
- process-selection marker: HermesZooid product command identity, not generic Hermes gateway syntax.

## Ownership invariant

A command line is targetable by HermesZooid lifecycle operations only when BOTH conditions hold:
1. it is a valid gateway runtime command;
2. it belongs to HermesZooid product identity.

`hermes gateway run`, `python -m hermes_cli.main gateway run`, and bare `zooid` processes must not satisfy condition 2.

## TDD contract

RED first. Prove:
1. a stdlib-only HermesZooid gateway identity authority exists;
2. it recognizes `hermeszooid` / `python -m hermeszooid` and rejects Hermes/bare Zooid command lines;
3. Windows task name/description are HermesZooid-owned;
4. generated Windows CMD/VBS launchers carry `HERMESZOOID_HOME` and invoke `-m hermeszooid`, not `-m hermes_cli.main`;
5. elevated Windows gateway commands re-enter through `-m hermeszooid`;
6. systemd base/fleet glob are `hermeszooid-gateway*`;
7. launchd base/fleet scan are `com.funggier.hermeszooid.gateway*`;
8. fallback `_scan_gateway_pids` excludes a real Hermes command even under `all_profiles=True`;
9. `_capture_gateway_argv` refuses a Hermes command line so force-kill/restart cannot replay it;
10. HermesZooid restart argv is rebuilt through `-m hermeszooid`.

## Out of scope

- listener/default port allocation;
- shared external bot-token policy;
- updater disablement;
- reset/uninstall/install-over destructive qualification.

Those become later numbered tasks so each safety boundary can be proven independently.

## Immediate next action

Commit RED gateway identity/process-selection contracts and a focused standard-runner workflow, then minimally repair gateway lifecycle ownership until GREEN.
