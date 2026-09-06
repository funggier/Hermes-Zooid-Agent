# Zooid Product Genesis and Independence Plan

**Project ready to start on user instruction.** The first task is READY and unassigned;
execution has not started. The user will finish CogentNexus-OpenClaw first.
Follow ACTIVE.md before using any execution steps below.

Historical audit snapshot: source 089bb32886c8c18f7fa20182c7bf8826d6935ac5; implementation and coexistence were not qualified at audit time.

Current task/status: [ACTIVE](../coordination/ACTIVE.md) and [STATUS](../coordination/STATUS.md).
Execution order: [roadmap](../roadmap.md); updater disablement is prioritized before home isolation.
Local execution: [CogentNexus-OpenClaw guide](../guides/local-development.md).
This plan records design and initial evidence, not live task ownership.

## Approved objective

Zooid — Powered by CogentNexus is an independent product derived once from Hermes.
Repository: funggier/Zooid-Agent. Product command: zooid.
Install and run alongside Hermes without sharing product-owned state or lifecycle.
Disable unused functionality first; do not remove or rewrite unused code unnecessarily.
Disable program update checks, notifications and execution against Hermes.
Retain Skills Hub and skill format compatibility where dependencies permit.
Future program updates belong to Zooid; no obligation to merge Hermes upstream.
CogentNexus execution architecture is a later phase, after independence.

## Provenance

- Fork: https://github.com/funggier/Zooid-Agent
- GitHub parent/source: NousResearch/hermes-agent (confirmed through repository API).
- Audited branch: main.
- Exact genesis candidate: 089bb32886c8c18f7fa20182c7bf8826d6935ac5.
- Declared Python project: hermes-agent, version 0.21.0.
- Root license: MIT, Copyright (c) 2025 Nous Research.
- Preserve root license and applicable third-party notices in source AND distribution.
- This is an initial targeted audit, not a claim that every source occurrence or dependency license has been reviewed.

## Verified source findings

All paths refer to the exact candidate above.

| Surface | Evidence | Independence implication |
| --- | --- | --- |
| Python package | pyproject.toml declares hermes-agent | Separate distribution and exposed CLI; audit setup.py and lockfiles together |
| Default home | hermes_constants.py: _get_platform_default_hermes_home | Windows uses LOCALAPPDATA/hermes; other platforms use ~/.hermes |
| Home resolution | hermes_constants.py: get_hermes_home and get_process_hermes_home | HERMES_HOME and context-local overrides currently select state; Zooid must not inherit Hermes state accidentally |
| Profiles | hermes_cli/profiles.py | Profile root, aliases and wrapper removal require ownership separation |
| Windows installer | scripts/install.ps1 | Defaults use Hermes home and install directories; repository URLs point to NousResearch/hermes-agent |
| Desktop package | apps/desktop/package.json | name/productName/executableName Hermes; appId com.nousresearch.hermes; hermes URL protocol; Hermes shortcuts and uninstall identity |
| Windows startup | hermes_cli/gateway_windows.py | Scheduled task names determine launcher and Startup entries; rename as a single contract |
| Process discovery | hermes_cli/gateway.py | Fleet scans include hermes-gateway and ai.hermes.gateway; changing directories alone is insufficient |
| CLI updater | hermes_cli/subcommands/update.py, hermes_cli/update_cmd.py | Explicit check and update execution routes both exist |
| Upstream sync | hermes_cli/update_cmd_git.py | Contains upstream-add and fork synchronization paths back to NousResearch |
| Desktop update | apps/desktop/electron/update-*.ts, scripts/desktop-update/, apps/bootstrap-installer/src-tauri/src/update.rs | CLI updater gating alone does not establish all-surface update disablement |
| Skills paths | tools/skills_hub.py | Skill paths resolve from product home, with .hub metadata under skills |
| Skill installation | tools/skills_hub_install.py | Install/uninstall/update use skill-root containment and quarantine; preserve these checks |
| Skill sources | hermes_cli/skills_hub.py; tools/skills_hub_* | Existing separate source routing supports preserving skill downloads independently of program updates |

## Design decisions

1. Product-owned external identifiers change; historical provenance and real dependency names do not.
2. Initial homes: Windows %LOCALAPPDATA%/Zooid; POSIX ~/.zooid. Explicit override: ZOOID_HOME.
3. A pre-existing HERMES_HOME must not select Zooid data. Do not change the user's global HERMES_HOME.
4. Internal Python module names may remain where an isolated environment prevents collisions. Avoid a repo-wide blind replacement.
5. Windows desktop identity: product/executable Zooid; application ID com.cogentnexus.zooid; URL scheme zooid. These are proposed technical identifiers, not assertions of domain/trademark ownership.
6. Package installation must use its own environment and launchers. Do not install both distributions into the same interpreter while they expose overlapping Python modules.
7. No automatic migration/import from Hermes. Explicit future copy/import is a separate operation.
8. No automatic adoption of Hermes processes, services, profiles, credentials, MCP configuration or existing channel sessions.
9. Existing external channels may conflict when two clients use the same bot token. Zooid starts without copied channel credentials; distinct configured identities are required for simultaneous polling where the provider requires it.
10. External providers such as Ollama may be shared deliberately. Zooid stop/reset/uninstall must not stop or delete a shared provider.
11. Retain upstream updater implementation dormant; all public execution and background entry points must refuse/skip before network, git, dependency mutation, backup, process stop or restart.
12. Skills download/update remains a separate allowed operation. Install copied bundles into Zooid's own skill root, including its own lockfile, quarantine, audit log and cache.
13. Skills that invoke hermes or fixed Hermes paths require review/adaptation; do not promise universal compatibility or rewrite arbitrary downloaded content silently.
14. No native CogentNexus ticket/scheduler/recovery rewrite in this phase.

## Implementation sequence and acceptance gates

### A. Home, configuration and package boundary

Files: hermes_constants.py, hermes_cli/profiles.py, pyproject.toml, setup.py, uv.lock,
CLI entry-point builders and their existing tests.

- Trace project.scripts and every home/env fallback and profile wrapper before editing.
- Add behavioral tests with distinct temporary Hermes and Zooid roots, inherited HERMES_HOME,
  and explicit ZOOID_HOME. Assert Zooid selects only its own root.
- Run the relevant files through scripts/run_tests.sh and record expected RED.
- Implement the minimal home/entry-point changes, then update affected call sites consistently.
- Test real imports and subprocess environment propagation, named profiles and alias lifecycle.
- Build/install the Python package into a separate environment; assert zooid launcher exists
  and the pre-existing Hermes launcher and distribution remain unchanged.
- Require GREEN and record the exact commit before proceeding.

### B. Lifecycle and resource ownership

Files: hermes_cli/gateway.py, hermes_cli/gateway_windows.py, gateway/status.py,
platform-specific service helpers, port/IPC configuration and corresponding tests.

- Inventory service/task/Startup names, process matchers, PID files, locks, socket/pipe names,
  desktop single-instance behavior and all listening ports using source search.
- Add negative ownership tests: a genuine Hermes process must never be selected by Zooid stop,
  restart, cleanup or fleet scanning, even with similar CLI arguments.
- Change externally shared identifiers as a group; scope discovery to installation and product identity.
- Allocate non-conflicting defaults per listener; detect explicitly occupied ports with a clear error.
  Do not invent a single gateway port as a substitute for auditing every listener.
- Run host-native Windows tests on Windows and POSIX tests on their actual hosts.
- Gate: stop/restart Zooid leaves live Hermes and any deliberately shared provider unchanged.

### C. Disable program updates, preserve skill operations

Files: hermes_cli/subcommands/update.py, hermes_cli/update_cmd*.py,
banner/version checks, TUI/web/gateway dispatchers, Desktop updater callers,
scripts/desktop-update/, bootstrap-installer update entry points.

- Trace every check/notification/execution caller; do not assume one CLI check covers Desktop.
- Write tests where network/git/subprocess update operations fail if called.
- Assert program update entry points return a clear disabled result before any such operation.
- Disable background scheduling and notification paths; retain dormant code and license/provenance.
- Assert normal skill install/update/uninstall against a local fixture still functions in Zooid home.
- Keep source URLs for legitimately downloaded third-party skills; they are not product updater URLs.
- Gate: no program updater reaches Hermes; skill fixture lifecycle succeeds without touching Hermes.

### D. Installers and Desktop identity

Files: scripts/install.ps1, POSIX installer/setup scripts, apps/desktop/package.json,
Desktop runtime identity/path resolvers, bootstrap-installer manifests,
workspace manifests/lockfiles, shortcuts/protocol/uninstall integration.

- Replace bootstrap repository targets with funggier/Zooid-Agent and use a tested release/ref.
- Audit downloaded helper scripts, repair/reinstall paths and fallback URLs as well as initial clone.
- Separate app IDs, shortcuts, protocol handlers, uninstall registration, userData and single-instance locks.
- Disable any unqualified installation surface explicitly; never ship a remaining Hermes installer as Zooid.
- Test installed commands from a new shell, not only from the development checkout.
- Gate: install both products, launch both, verify registration and data separation.

### E. Reset, uninstall and install-over

Files: actual lifecycle command owners located during source audit, installer cleanup handlers.

- Define reset data scope explicitly; reset and uninstall require the user's confirmation.
- Write sentinel files in Hermes roots and capture service/registry/launcher state.
- Exercise Zooid reset, uninstall and install-over in disposable Windows environments.
- Assert Hermes sentinels, launcher targets, processes and registrations remain intact.
- Include custom roots, profiles and junction/symlink boundary cases.
- Do not add cnx-style reset assumptions without checking existing Hermes command semantics.
- Gate: all destructive operations are limited to verified Zooid-owned resources.

### F. Qualification and release

- Keep the genesis SHA and per-step commits in the implementation report.
- Run the repo's scripts/run_tests.sh for affected Python behavior and applicable JS tests.
- Build the distributable and test it on native Windows; source-only tests are insufficient.
- Record exact candidate, OS, installer artifact hash, test commands, outcomes and unresolved issues.
- Validate coexistence with Hermes; include OpenClaw/CogentNexus-OpenClaw where available.
- Release only a candidate that passes coexistence gates. Do not claim current fork is install-ready.

## Required coexistence matrix

| Operation | Zooid expectation | Hermes expectation |
| --- | --- | --- |
| Fresh install | Own launchers, registration, home | Unchanged |
| Concurrent start | Own processes/listeners | Continues running |
| Named profile | Zooid-owned profile state | No reads/writes to Hermes profile state |
| Stop/restart | Only Zooid processes affected | Continues running |
| Program update/check | Disabled before side effects | No activity |
| Skill fixture install/update/remove | Only Zooid skills and metadata change | Skills unchanged |
| Reset | Confirmed, documented Zooid scope | All sentinels unchanged |
| Install-over | Zooid settings retained as specified | Unchanged |
| Uninstall | Only owned Zooid resources removed | Still usable |
| Shared Ollama | Connection may be used deliberately | Provider remains running |

## Current execution evidence and blocker

- GitHub connector read access and branch creation succeeded.
- Fork parent, main SHA, root instructions, tree, and targeted source files inspected.
- No production source modifications or installation tests performed.
- Direct workspace git clone did not complete; a network probe was rejected with
  "network approval was cancelled before a decision was returned".
- No escalation or access-control workaround attempted.
- GitHub API inspection/documentation remains available, but this session has not obtained
  a runnable checkout and dependency environment. A passing runtime claim is therefore unavailable.
- Continue implementation from this branch in a supported checkout/runner, using the gates above.
