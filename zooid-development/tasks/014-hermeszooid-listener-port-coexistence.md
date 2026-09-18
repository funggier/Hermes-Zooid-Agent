# Task 014 — HermesZooid Listener and Port Coexistence

- Task ID: `014-hermeszooid-listener-port-coexistence`
- State: DONE / GREEN
- Opened: 2026-09-19
- Completed: 2026-09-19
- Depends on: Task 013
- Inventory commit: `d7ec3af623d27caca9df9541148044b255cec281`
- RED commit: `086c28416632bbd49dc2edafee164bbc3c234cd4`
- Production repair: `a9ecb4a1a27d9d971ac9114dad137e73c37863f2`
- Listener Port workflow: `35378978839` — SUCCESS

## Why this task existed

Even with package/process/service identities isolated, two products cannot safely coexist if their default listeners bind the same TCP ports.
Hermes has multiple independent inbound listeners, so changing one gateway port would have been incomplete.

## Source inventory

Inventory report:
`zooid-development/reports/task-014-listener-port-inventory.md`

The inventory covered all built-in `PORT_BINDING_PLATFORM_VALUES`, shared-ingress behavior, and the browser dashboard endpoint before any code change.

## RED

`086c28416632bbd49dc2edafee164bbc3c234cd4` defined a stdlib-only coexistence contract.
Workflow `35378763841` failed exactly because `hermeszooid.listener_defaults` did not yet exist.

## Production design

Added one product authority:
`hermeszooid/listener_defaults.py`

Explicit config/environment values retain their inherited precedence. Only fallback defaults changed.

Qualified HermesZooid defaults:

| Surface | Hermes | HermesZooid |
| --- | ---: | ---: |
| API server | 8642 | 18642 |
| Generic webhook | 8644 | 18644 |
| BlueBubbles | 8645 | 18645 |
| Microsoft Graph | 8646 | 18646 |
| WeCom callback | 8645 | 18647 |
| LINE | 8646 | 18648 |
| WhatsApp Cloud | 8090 | 18090 |
| SMS | 8080 | 18080 |
| Feishu webhook | 8765 | 18765 |
| Teams | 3978 | 13978 |
| Browser dashboard/serve default | 9119 | 19119 |

Every independently bindable HermesZooid fallback is unique.

Electron Desktop remains `serve --port 0`, so its private backend continues to use an OS-assigned ephemeral port.

Secondary multiplex profiles remain shared-ingress applications and do not bind their standalone fallback ports.

## GREEN

Listener Port workflow `35378978839` — SUCCESS.

Focused regressions on the same SHA:
- Gateway Identity `35378978847` — SUCCESS;
- Windows Installer Identity `35378978906` — SUCCESS;
- HermesZooid Identity `35378978926` — SUCCESS;
- Desktop Identity `35378978849` — SUCCESS;
- Bootstrap Setup Identity `35378978825` — SUCCESS;
- CogentNexus Kernel `35378978840` — SUCCESS;
- Docker `35378978899` — SUCCESS.

The coexistence contract includes real simultaneous loopback socket binds for inherited Hermes and HermesZooid API/webhook defaults.

## Result

PASS.

Default listener allocation is now separated from Hermes and internally unique.

## Follow-up

Task 015 qualifies updater ownership and upstream isolation so a HermesZooid update cannot silently switch back to NousResearch Hermes or operate on the existing Hermes installation.
