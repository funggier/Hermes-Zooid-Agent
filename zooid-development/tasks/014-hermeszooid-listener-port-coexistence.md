# Task 014 — HermesZooid Listener and Port Coexistence

- Task ID: `014-hermeszooid-listener-port-coexistence`
- State: ACTIVE
- Opened: 2026-09-19
- Depends on: Task 013
- Starting GREEN SHA: `496277bdeb13283c7a573675d7b678fa68e96c31`

## Why this task exists

Gateway process/service ownership is now isolated, but two independently running products can still collide if they bind the same localhost/default listener ports.

Hermes contains multiple port-binding surfaces, not one gateway port. Changing a single number would be incomplete and unsafe.

Known surfaces already identified include:
- OpenAI-compatible API server (`API_SERVER_PORT`, inherited default 8642);
- generic webhook listener (`WEBHOOK_PORT`);
- Microsoft Graph webhook (`MSGRAPH_WEBHOOK_PORT`);
- WhatsApp Cloud webhook host/port;
- WeCom callback listener (inherited default 8645);
- BlueBubbles webhook listener (inherited default 8645);
- Feishu webhook mode;
- other port-binding platform adapters routed through shared ingress/multiplexing.

## Goal

Create one authoritative HermesZooid listener-default policy and prove that a default HermesZooid runtime can coexist with a default Hermes runtime on the same host without bind collisions.

Explicit user-configured ports must still be honored. The product policy changes defaults, not operator intent.

## Required inventory before implementation

1. enumerate `PORT_BINDING_PLATFORM_VALUES` and conditional bind modes;
2. trace every default host/port constant or environment fallback used by those adapters;
3. identify which adapters share the default-profile listener under multiplexing;
4. distinguish fixed local product endpoints from external callback configuration;
5. identify Desktop/dashboard/local control endpoints outside platform adapters;
6. document all inherited Hermes default numbers before assigning HermesZooid defaults.

## Design constraints

- no bare `zooid` env names or ports;
- do not alter explicit user-supplied ports;
- centralize HermesZooid defaults instead of scattering replacement literals;
- occupied default ports must fail clearly or use a deliberately designed fallback; never silently attach to another product;
- shared-ingress semantics must remain intact;
- no claim of coexistence until two listeners are bound simultaneously in a test.

## TDD acceptance

RED first after inventory. Prove at minimum:
1. an authoritative product listener-default module exists;
2. HermesZooid API server default differs from inherited Hermes 8642;
3. every inherited fixed callback/webhook default that can bind locally is accounted for;
4. env/config explicit overrides win over product defaults;
5. two loopback API listeners using Hermes and HermesZooid defaults bind simultaneously;
6. representative shared/webhook listeners can coexist at their defaults;
7. an explicitly occupied requested port produces a clear bind failure rather than targeting/reusing Hermes;
8. no product default uses a bare Zooid namespace.

## Out of scope

- external bot-token/provider identity conflicts;
- program updater disablement;
- reset/uninstall/install-over destructive tests;
- live provider acceptance.

## Immediate next action

Build and commit a source-derived listener/port inventory, then define the RED contract from that inventory before changing defaults.
