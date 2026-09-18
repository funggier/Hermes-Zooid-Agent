# Task 015 — HermesZooid Update Ownership and Upstream Isolation

- Task ID: `015-hermeszooid-update-ownership-upstream-isolation`
- State: ACTIVE
- Opened: 2026-09-19
- Depends on: Task 014
- Starting GREEN SHA: `a9ecb4a1a27d9d971ac9114dad137e73c37863f2`

## Why this task exists

Installation/runtime identity can be perfectly isolated and still become unsafe if `hermeszooid update` fetches the Hermes upstream, rewrites the wrong checkout, restarts broad Hermes processes, or uses Hermes-owned release/update channels.

The fork was intentionally created from Hermes but must become update-owned by HermesZooid.

## Safety invariants

1. HermesZooid update operations may mutate only the HermesZooid checkout/home/runtime.
2. Default update remote/repository must be `funggier/Hermes-Zooid-Agent`, never `NousResearch/hermes-agent`.
3. Upstream Hermes may remain a read-only development reference, but never the runtime update authority.
4. Update subprocesses must re-enter through `hermeszooid` product identity.
5. Process/dashboard/gateway cleanup during update must target HermesZooid-owned processes only.
6. Existing Hermes installation, Git checkout, services, tasks, profiles, env vars and running processes must remain unchanged.
7. Bare Zooid project identity must never be used.

## Audit targets

- `hermes_cli/subcommands/update.py` and update command dispatch;
- update/managed-uv/source checkout helpers;
- Git remote validation and branch/tag resolution;
- dashboard/gateway stale-process cleanup invoked by update;
- release/version source and update-check URL/channel;
- Desktop update hooks if they call CLI update;
- post-update restart argv;
- any hard-coded `NousResearch/hermes-agent`, `hermes update`, or Hermes-owned remote assumptions.

## TDD plan

RED after source audit. Prove:
1. one HermesZooid update authority exposes canonical repo/remote identity;
2. a checkout whose origin is the real Hermes repo is rejected for managed HermesZooid update;
3. HermesZooid repo origin is accepted;
4. update command/restart subprocesses use `hermeszooid` identity;
5. dashboard/gateway process cleanup cannot target existing Hermes commands;
6. release/update metadata does not switch the runtime back to upstream Hermes;
7. a simulated update in an isolated temp checkout changes only that checkout and its HermesZooid home.

## Out of scope

- destructive uninstall/reset/install-over acceptance;
- real-machine installation;
- live provider acceptance;
- changing how upstream Hermes is periodically imported into development branches.

## Immediate next action

Audit every update authority/source/restart path, write a durable report, then commit RED ownership tests before changing updater behavior.
