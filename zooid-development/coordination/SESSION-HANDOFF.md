# HermesZooid Session Handoff — Current

Updated: 2026-09-18

Repo: `funggier/Hermes-Zooid-Agent`
Branch: `agent/zooid-independence`
Canonical product token: `hermeszooid`

## Critical naming rule

The user also owns a separate program/project named Zooid.
Do not use bare `zooid` as HermesZooid package, CLI, environment root, writable path, service/app identity, or future protocol.

## Completed

Task 009 DONE/GREEN.
`HermesZooid Identity` run `35360523016` SUCCESS, including `uv lock --check`.

Distribution/CLI/home are now `hermeszooid` / `HERMESZOOID_HOME` / `.hermeszooid`.

## Active

Task 010 migrates active runtime namespace `zooid_cnx` -> `hermeszooid.cnx` with no installed compatibility shim.

## Resume order

1. AGENTS.md
2. this file
3. ACTIVE.md
4. Task 010
5. STATUS.md

## Safety

No real-machine installation yet. No force push. No live Hermes/OpenClaw lifecycle mutation.
