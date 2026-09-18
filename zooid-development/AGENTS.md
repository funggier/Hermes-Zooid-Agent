# Zooid Development Instructions

This directory belongs to **Zooid — Powered by CogentNexus** and is deliberately separated
from the inherited Hermes source/documentation tree.

Read `README.md`, `UPSTREAM-BASELINE.md`, `coordination/ACTIVE.md`, and
`coordination/STATUS.md` before selecting Zooid work.

Keep fork `main` as a clean mirror of `NousResearch/hermes-agent/main`.
Zooid-specific source changes, planning, reports, identity work and release work belong on
Zooid branches. Never force-update upstream history.

The independence roadmap remains durable direction, but source paths and ownership from the
September 6 audit are historical until revalidated against the current upstream baseline.
Use root and area `AGENTS.md` files from the synchronized Hermes tree for inherited
engineering rules.

Zooid is intended to have independent installation, runtime, configuration, storage,
lifecycle resources and future update path. Compatible skills may be reused, but Zooid must
own its writable skill state and must not depend on a shared writable Hermes home.

Preserve licenses, copyright notices, attribution and third-party obligations.
Do not stop/reset/uninstall/mutate live Hermes, OpenClaw, CogentNexus-OpenClaw or shared
provider runtimes unless a later acceptance task explicitly scopes that operation.
