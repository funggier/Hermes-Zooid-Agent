# Task 009 — hermeszooid CLI and Home Independence

- Task ID: `009-hermeszooid-cli-home-independence`
- State: ACTIVE
- Opened: 2026-09-18
- Depends on: Task 007
- Task 008: PAUSED / SOURCE_READY
- Canonical product token: `hermeszooid`

## Why this task exists

The inherited repository still exposes the Hermes product identity:
- Python distribution: `hermes-agent`;
- CLI scripts: `hermes`, `hermes-agent`, `hermes-acp`;
- runtime root selected by `HERMES_HOME` or Hermes platform defaults;
- Windows installer defaults under `%LOCALAPPDATA%\hermes`.

Those surfaces can collide with an existing Hermes installation even though the CogentNexus/Kanban test runtime is already isolated.

Before installing on a real machine, hermeszooid needs an explicit product boundary that cannot accidentally select the user's Hermes home.

## Canonical identity for this project

- Product/technical token: `hermeszooid`
- CLI: `hermeszooid`
- Product home environment variable: `HERMESZOOID_HOME`
- Windows default product home: `%LOCALAPPDATA%\hermeszooid`
- POSIX default product home: `~/.hermeszooid`

`HERMES_HOME` is inherited-Hermes implementation detail only. It must never be accepted as the input that chooses hermeszooid's product home.

## Compatibility strategy

The fork still reuses large parts of Hermes internally. The hermeszooid launcher may set a process-local `HERMES_HOME` to the already-resolved hermeszooid home before importing inherited Hermes runtime code.

This translation is one-way:

`HERMESZOOID_HOME/default hermeszooid path -> process-local HERMES_HOME for inherited code`

Never:

`existing HERMES_HOME -> hermeszooid product home`

The parent shell/environment must not be rewritten persistently.

## TDD contract

RED first. Prove:
1. explicit `HERMESZOOID_HOME` wins;
2. default Windows home resolves to `%LOCALAPPDATA%\hermeszooid`;
3. existing `HERMES_HOME` is ignored when choosing hermeszooid home;
4. POSIX default is `~/.hermeszooid`;
5. child/runtime environment maps resolved home into process-local `HERMES_HOME` without mutating the input environment;
6. `hermeszooid` CLI entry exists;
7. `python -m hermeszooid` reaches the same isolated launcher boundary;
8. current CogentNexus default storage migrates to `HERMESZOOID_HOME` rather than `ZOOID_HOME`.

## Non-goals

- Windows installer rewrite;
- Desktop app ID/productName/protocol rewrite;
- uninstall/reset/update ownership;
- real-machine installation;
- live provider acceptance.

Those receive later numbered tasks after this root boundary is GREEN.

## Acceptance

Task 009 is DONE only when the focused Zooid workflow proves all identity/home contracts and no test requires reading the real Hermes home.

## Immediate next action

Commit the RED identity/home contract, then add the minimum `hermeszooid` launcher/identity module and migrate CogentNexus default-home selection to it.
