# Work Log

## 2026-09-19 — Task 013 test-first boundary
`d93d4e1bd02420acd9b46552453bbb406cee562b` defined gateway ownership tests; no Actions run was created before the next push.

## 2026-09-19 — Task 013 production repair
`6d3390f4f9281e18f7839a5d1f418f3560d43ac5` added product-owned service IDs and process-selection fencing.
Gateway run `35378010606` had 3 PASS / 1 FAIL because the static test expected an inline expression rather than equivalent local-variable semantics.

## 2026-09-19 — Task 013 DONE / GREEN
`496277bdeb13283c7a573675d7b678fa68e96c31`; Gateway Identity `35378080631` SUCCESS and all focused product regressions SUCCESS.

## 2026-09-19 — Task 014 ACTIVE
Opened listener/default-port coexistence. No default numbers will be changed until all local binders are inventoried.
