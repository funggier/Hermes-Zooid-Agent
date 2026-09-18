# Task 015 Update Ownership Audit

- Task: `015-hermeszooid-update-ownership-upstream-isolation`
- Audit date: 2026-09-19
- Base SHA: `3bbf8743ae8a3013aa41005f87a59b60d1e2a415`
- Status: AUDIT COMPLETE / RED NOT YET COMMITTED

## Purpose

Identify every runtime update authority that could make an otherwise-isolated HermesZooid
installation mutate, fetch from, restart, or relaunch the existing Hermes product.

Upstream Hermes remains valuable as a development reference. This audit separates that development
relationship from the end-user runtime updater.

## Finding A — Runtime Git updater still treats HermesZooid as a Hermes fork

`hermes_cli/update_cmd_git.py` still defines NousResearch Hermes as the official repository:

- `https://github.com/NousResearch/hermes-agent.git`
- `git@github.com:NousResearch/hermes-agent.git`

A HermesZooid checkout at `funggier/Hermes-Zooid-Agent` is therefore classified as a fork.

The inherited runtime path can:

1. offer to add the NousResearch repo as `upstream`;
2. fetch `upstream/main`;
3. fast-forward/sync against that upstream;
4. push the synchronized result back to `origin/main --force-with-lease`.

The last operation is especially unsafe for a runtime product updater: it can rewrite the
HermesZooid product repository based on upstream Hermes.

### Required repair

Runtime updates must recognize only the HermesZooid product repository as update authority and
must never auto-add/sync/push the Hermes development upstream.

Development synchronization with NousResearch belongs in a separate developer workflow.

## Finding B — Update check path can prefer an upstream remote

`hermes_cli/update_cmd.py::_cmd_update_check` currently prefers `upstream/main` on main when an
upstream remote exists. For HermesZooid, update check and apply must be origin/product-authority
based, not development-upstream based.

### Required repair

Product update check must validate the origin and compare against HermesZooid origin only.

## Finding C — Passive banner/release checks still point at Hermes

`hermes_cli/banner.py` still contains:

- NousResearch update repository URL/canonical identity;
- GitHub compare and branch-tip requests for `nousresearch/hermes-agent`;
- release links under `NousResearch/hermes-agent/releases`;
- fallback managed checkout path `<home>/hermes-agent`.

The installed HermesZooid checkout is `<HERMESZOOID_HOME>/app`.

### Required repair

Passive checks and release links must use `funggier/Hermes-Zooid-Agent` and the product app path.

## Finding D — Electron passive update remote identity still points at Hermes

`apps/desktop/electron/update-remote.ts` still defines the official remote as
`NousResearch/hermes-agent`.

### Required repair

The canonical/HTTPS official remote used by Desktop passive checks must be HermesZooid-owned.

## Finding E — Bootstrap updater still resolves inherited install/CLI identity

Although Task 012 migrated bootstrap paths and staged setup identity,
`apps/bootstrap-installer/src-tauri/src/update.rs` still uses production assumptions including:

- `hermes_home.join("hermes-agent")`;
- venv shim `hermes.exe` / `hermes`;
- PATH fallback `hermes.exe` / `hermes`;
- child env `HERMES_HOME`.

### Required repair

Use:

- `<HERMESZOOID_HOME>/app`;
- `hermeszooid.exe` / `hermeszooid`;
- `HERMESZOOID_HOME`.

The HermesZooid launcher remains responsible for process-local inherited `HERMES_HOME` mapping.

## Finding F — Desktop staged updater helper name is stale

`apps/desktop/electron/updater-process.ts` still probes
`<home>/hermes-setup.exe` while Task 012's product helper is
`hermeszooid-setup.exe`.

### Required repair

The Desktop handoff must locate only the HermesZooid staged helper.

## Finding G — Dashboard update cleanup can still see Hermes dashboard/serve processes

`hermes_cli/dashboard_procs.py` uses broad command patterns built from:

- `hermes dashboard`
- `hermes serve`
- `hermes_cli.main dashboard/serve`

and update cleanup calls this scanner before killing/restarting stale dashboard processes.

This is a direct friendly-fire risk when Hermes and HermesZooid coexist.

### Required repair

Discovery/kill eligibility must require HermesZooid product command identity in addition to the
generic dashboard/serve syntax.

Product-owned `HERMESZOOID_HOME` should also be preferred for process-home ownership evidence.

## Finding H — Venv blocker gateway exemption is generic

`hermes_cli/_scan_venv_blockers.py::_is_pausable_gateway` accepts any command that looks like
`gateway run`. Under coexistence that can exempt an existing Hermes gateway from the blocker list
as though the HermesZooid updater owned the pause/restart responsibility.

### Required repair

The exemption must require HermesZooid product identity in addition to gateway syntax.

## Finding I — Fresh restart recovery still uses Hermes supervisor/CLI identity

`hermes_cli/update_restart_recovery.py` still contains:

- `python -m hermes_cli.main ... gateway restart`;
- `hermes-gateway*.service`;
- `hermes-serve*.service`.

`hermes_cli/update_cmd_fleet.py` similarly enumerates inherited
`hermes-gateway*` / `hermes-serve*` unit families.

Task 013 isolated gateway service names, but the updater's separate fleet recovery paths must be
brought into the same authority.

### Required repair

Update fleet/recovery must enumerate/restart only HermesZooid supervisor identities.

## Product update authority proposal

Add one stdlib-only authority:

`hermeszooid/update_identity.py`

It should define at minimum:

- repository owner/name: `funggier/Hermes-Zooid-Agent`;
- HTTPS URL: `https://github.com/funggier/Hermes-Zooid-Agent.git`;
- SSH URL: `git@github.com:funggier/Hermes-Zooid-Agent.git`;
- canonical GitHub remote: `github.com/funggier/hermes-zooid-agent`;
- release URL base;
- product app directory name: `app`;
- origin normalization/validation helpers.

Runtime update policy should be fail-closed:

- recognized HermesZooid origin -> allowed;
- NousResearch Hermes origin -> rejected;
- unknown origin -> rejected for managed product update;
- no automatic upstream addition/sync/push.

## RED contract derived from this audit

The focused contract should prove:

1. canonical update authority exists and accepts only HermesZooid origin forms;
2. NousResearch Hermes is explicitly rejected;
3. runtime updater source contains no automatic NousResearch upstream add/sync/push path;
4. update check uses product origin, not `upstream`;
5. passive banner/release metadata points only to HermesZooid;
6. Desktop update-remote constants point only to HermesZooid;
7. bootstrap updater uses `app`, `hermeszooid(.exe)`, and `HERMESZOOID_HOME`;
8. staged updater helper is `hermeszooid-setup.exe`;
9. dashboard update cleanup filters out real Hermes command lines;
10. venv gateway exemption rejects real Hermes command lines;
11. update restart recovery uses HermesZooid CLI/service identities;
12. a temporary git-origin behavior test accepts HermesZooid SSH/HTTPS forms and rejects Hermes.

## Decision boundary

No real-machine install is authorized from this audit.

After RED/GREEN updater ownership, destructive uninstall/reset/install-over coexistence still needs
its own task before installation is considered safe.
