# Task 008 — Bounded Live Provider Acceptance

- Task ID: `008-bounded-live-provider-acceptance`
- State: PAUSED / SOURCE_READY
- Pause reason: product installation/runtime identity must be independent before any real-machine live acceptance
- Source-ready SHA: `e18e3e9705b3312b97a8f231924e5c8e9af2f94e`
- Zooid workflow: `35357955959` — SUCCESS

## Why paused

The source-side provider acceptance runner is GREEN, but the inherited product still exposes Hermes package/CLI/home/installer/Desktop identities.
Running the live acceptance before coexistence boundaries are qualified would prove provider execution while leaving installation collision risk unresolved.

User direction on 2026-09-18: finish product-independence/coexistence work first; install or run on the real machine only after that boundary is proven.

Task 008 remains preserved and will resume after the required independence tasks pass.
