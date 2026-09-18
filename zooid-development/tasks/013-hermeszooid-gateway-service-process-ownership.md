# Task 013 — HermesZooid Gateway Service and Process Ownership

- Task ID: `013-hermeszooid-gateway-service-process-ownership`
- State: DONE / GREEN
- Opened: 2026-09-19
- Completed: 2026-09-19
- Depends on: Task 012
- Test-first commit: `d93d4e1bd02420acd9b46552453bbb406cee562b`
- Production repair: `6d3390f4f9281e18f7839a5d1f418f3560d43ac5`
- Test semantic repair: `496277bdeb13283c7a573675d7b678fa68e96c31`
- Final Gateway Identity workflow: `35378080631` — SUCCESS

## Why this task existed

Gateway lifecycle identity was still inherited from Hermes after package/installer/Desktop/setup isolation.
That left a friendly-fire risk: broad process scans and host-global service names could make HermesZooid lifecycle operations see an existing Hermes gateway.

## Ownership invariant

A process is targetable by HermesZooid lifecycle operations only when both are true:
1. it is a valid gateway runtime command;
2. it carries HermesZooid product identity.

Existing Hermes and bare Zooid commands fail condition 2.

## Test-first boundary

`d93d4e1bd02420acd9b46552453bbb406cee562b` defined the gateway ownership contract.
GitHub Actions did not create a run for this commit before the next push, so it is recorded as a test-first boundary, not an executed RED.

## Production repair

`6d3390f4f9281e18f7839a5d1f418f3560d43ac5` added `hermeszooid/gateway_identity.py` and wired the product fence into lifecycle code.

Qualified identifiers:
- Windows Scheduled Task base: `HermesZooid_Gateway`;
- systemd base: `hermeszooid-gateway`;
- launchd base: `com.funggier.hermeszooid.gateway`;
- supervisor launchers re-enter through `python -m hermeszooid`;
- Windows CMD/VBS launchers carry `HERMESZOOID_HOME`;
- all-profile process scans require HermesZooid product identity;
- captured/replayed restart argv refuses genuine Hermes command lines.

## First implementation run

Gateway Identity run `35378010606` reached all four focused tests and failed one assertion because the test expected an inline expression while the implementation used an equivalent local variable.
That was a test-shape defect, not a production ownership defect.

## GREEN

Test semantic repair `496277bdeb13283c7a573675d7b678fa68e96c31` aligned the assertion with behavior.

Final focused evidence on the same SHA:
- Gateway Identity `35378080631` — SUCCESS;
- HermesZooid Identity `35378080992` — SUCCESS;
- Desktop Identity `35378080635` — SUCCESS;
- Windows Installer Identity `35378080666` — SUCCESS;
- Bootstrap Setup Identity `35378080702` — SUCCESS;
- CogentNexus Kernel `35378081305` — SUCCESS;
- Docker `35378081015` — SUCCESS.

## Result

PASS.

HermesZooid gateway service/process ownership is separated from existing Hermes and the separate Zooid product.

## Follow-up

Task 014 audits and separates listener/default-port ownership. No port is changed ad hoc; all port-binding adapters must be inventoried first.
