# Task 014 Listener and Port Inventory

- Task: `014-hermeszooid-listener-port-coexistence`
- Inventory date: 2026-09-19
- Source branch: `agent/zooid-independence`
- Inventory base SHA: `844433054cfa41fdaf9ceb055a15419aa2c7f542`
- Status: SOURCE INVENTORY COMPLETE / IMPLEMENTATION NOT STARTED

## Purpose

Identify every product-local TCP listener that can collide when Hermes and HermesZooid run on the
same host. No port is changed in this report.

The inventory is derived from the actual adapter registry and adapter constructors, not from
documentation examples.

## Port-binding registry

`gateway/config.py` declares these built-in port-binding platform values:

- `webhook`
- `api_server`
- `msgraph_webhook`
- `feishu` — binds only in `connection_mode=webhook`
- `wecom_callback`
- `bluebubbles`
- `sms`
- `whatsapp_cloud`
- `line`
- `teams`

`api_server` and `webhook` are also the default-profile shared-listener mirrors. Named profiles
do not bind their own TCP sockets in shared-listener mode; their adapter applications are forwarded
under `/p/<profile>/...`.

For the remaining port-binding adapters, `shared_ingress.bind_listener()` also suppresses the
secondary profile's own bind and publishes its application through the default listener.

Default-profile adapters still own their normal standalone ports.

## Inherited Hermes standalone defaults

| Surface | Source | Host default | Port default | Override |
| --- | --- | --- | ---: | --- |
| API server | `gateway/platforms/api_server.py` | `127.0.0.1` | 8642 | config / `API_SERVER_PORT` |
| Generic webhook | `gateway/platforms/webhook.py` | dual-stack/all interfaces | 8644 | config / `WEBHOOK_PORT` |
| Microsoft Graph webhook | `gateway/platforms/msgraph_webhook.py` | dual-stack/all interfaces | 8646 | config / `MSGRAPH_WEBHOOK_PORT` |
| WhatsApp Cloud webhook | `gateway/platforms/whatsapp_cloud.py` | dual-stack/all interfaces | 8090 | config / `WHATSAPP_CLOUD_WEBHOOK_PORT` |
| BlueBubbles webhook | `gateway/platforms/bluebubbles.py` | `127.0.0.1` | 8645 | config / `BLUEBUBBLES_WEBHOOK_PORT` |
| Feishu webhook mode | `plugins/platforms/feishu/adapter.py` | `127.0.0.1` | 8765 | config / `FEISHU_WEBHOOK_PORT` |
| WeCom callback | `plugins/platforms/wecom/callback_adapter.py` | dual-stack/all interfaces | 8645 | config / `WECOM_CALLBACK_PORT` |
| Twilio SMS webhook | `plugins/platforms/sms/adapter.py` | `127.0.0.1` | 8080 | `SMS_WEBHOOK_PORT` |
| LINE webhook | `plugins/platforms/line/adapter.py` | dual-stack/all interfaces | 8646 | config / `LINE_PORT` |
| Microsoft Teams webhook | `plugins/platforms/teams/adapter.py` | dual-stack/all interfaces | 3978 | config / `TEAMS_PORT` |

### Other local product endpoint

`hermes dashboard` / `hermes serve` uses:

- host `127.0.0.1`
- default port `9119`

Source: `hermes_cli/subcommands/dashboard.py`.

The Electron Desktop backend is different: it invokes `serve --host 127.0.0.1 --port 0`, so the OS
assigns an ephemeral port. That path has no fixed-port coexistence collision by default.

### Non-TCP gateway coordination

`gateway/control_socket.py` uses a filesystem Unix socket or Windows named pipe scoped by the
product home. It is not a TCP port and Task 009's independent HermesZooid home already separates
that resource from Hermes.

## Collision classes

### Class A — direct default collision with existing Hermes

If both products enable the same surface with inherited defaults, the second bind can fail on every
fixed port above.

This is true even when process/service identity is perfectly separated.

### Class B — duplicate inherited defaults inside one product

Some adapters intentionally share the same inherited number but are separate standalone listeners:

- 8645: BlueBubbles + WeCom callback
- 8646: Microsoft Graph + LINE

If both are enabled simultaneously in a default profile, they can already conflict unless one is
served through shared ingress or explicitly reconfigured.

HermesZooid should not preserve this ambiguous default topology.

### Class C — explicit operator configuration

An explicit config/env port is operator intent and must win over the product default.

HermesZooid must not silently rewrite an explicit value just to avoid a collision. If the requested
port is occupied, startup must report a clear bind/configuration error.

## Candidate HermesZooid default policy

Use one deterministic product transform for inherited fixed TCP defaults:

`HermesZooid default = inherited Hermes default + 10000`

Candidate mapping:

| Surface | Hermes inherited | HermesZooid candidate |
| --- | ---: | ---: |
| API server | 8642 | 18642 |
| Generic webhook | 8644 | 18644 |
| Microsoft Graph webhook | 8646 | 18646 |
| WhatsApp Cloud | 8090 | 18090 |
| BlueBubbles | 8645 | 18645 |
| Feishu webhook | 8765 | 18765 |
| WeCom callback | 8645 | 18645 |
| SMS | 8080 | 18080 |
| LINE | 8646 | 18646 |
| Teams | 3978 | 13978 |
| Dashboard / browser serve | 9119 | 19119 |

### Important refinement

A simple +10000 transform solves Hermes-vs-HermesZooid collision, but it does NOT solve duplicate
defaults inside HermesZooid itself:

- BlueBubbles and WeCom would both become 18645.
- Microsoft Graph and LINE would both become 18646.

Therefore the production policy must allocate a UNIQUE HermesZooid default per independently
bindable standalone surface.

The transform is useful as a base range, not sufficient as the final allocation.

## Proposed unique HermesZooid allocation

Keep recognizable values near the +10000 base while making every independently bindable surface
unique:

| Surface | Proposed HermesZooid default |
| --- | ---: |
| API server | 18642 |
| Generic webhook | 18644 |
| BlueBubbles | 18645 |
| Microsoft Graph | 18646 |
| WeCom callback | 18647 |
| LINE | 18648 |
| WhatsApp Cloud | 18090 |
| SMS | 18080 |
| Feishu webhook | 18765 |
| Teams | 13978 |
| Dashboard / browser serve | 19119 |

These are product defaults only. Secondary shared-ingress adapters do not bind their standalone
default when routed through the default listener.

## Architecture recommendation

Create one stdlib-only authority, for example:

`hermeszooid/listener_defaults.py`

It should own named constants/mapping rather than scattering HermesZooid literals through inherited
adapter files.

Inherited adapters should obtain a product-aware default through a small helper while preserving
their existing explicit config/env precedence.

The default authority should be import-light and must not depend on provider/plugin initialization.

## Required RED contract derived from this inventory

1. every registered built-in port binder is present in the product allocation inventory;
2. each independently bindable HermesZooid default is unique;
3. none equals the corresponding inherited Hermes default;
4. dashboard default is product-owned;
5. explicit config/env values beat the product default;
6. API server Hermes default and HermesZooid default can bind simultaneously on loopback;
7. representative webhook listeners can bind simultaneously on their two product defaults;
8. an explicit occupied port fails clearly instead of auto-attaching or silently changing;
9. secondary shared-ingress mode still performs no TCP bind;
10. Desktop `serve --port 0` remains auto-assigned and is not forced onto the dashboard fixed port.

## Decision boundary

No real-machine installation is authorized from this inventory alone.

Task 014 proceeds to RED tests, then minimal product-default implementation, then GREEN coexistence
binding tests.
