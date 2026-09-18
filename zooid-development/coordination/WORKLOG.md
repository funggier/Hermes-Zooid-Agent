# Work Log

เพิ่มรายการตามลำดับเวลา UTC; ไม่ลบผลล้มเหลวเดิม
แต่ละรายการบอก task, การเปลี่ยนแปลง, หลักฐาน, ผล และ next action
commit ที่บรรจุรายการเป็น checkpoint ของเอกสาร; tested SHA ต้องระบุแยกเสมอ

## Genesis audit

- Date: 2026-09-06 UTC
- Task: product-genesis-audit
- Source: `089bb32886c8c18f7fa20182c7bf8826d6935ac5`
- Result: targeted fork/license/home/installer/Desktop/updater/skills inspection
- Limitation: no production changes or runtime tests; source ownership later became stale

## Development coordination documents

- Date: 2026-09-06 UTC
- Task: document-development-workflow
- Evidence: PR #1 and Git history
- Result: roadmap, naming, local guide, task/report templates, acceptance and coordination prepared

## User resume / continuous execution

- Date: 2026-09-18 UTC
- Decision: user authorized Zooid development to proceed continuously toward a working
  CogentNexus execution model.
- Boundary: source/repository work may proceed without per-step approval; live destructive
  lifecycle operations remain separately scoped.

## Upstream synchronization and planning isolation

- Date: 2026-09-18 UTC
- Task: synchronize-current-hermes
- Old fork main: `089bb32886c8c18f7fa20182c7bf8826d6935ac5`
- New upstream main: `01382698fc32ec7740b6a204d9b7a6abeac74d33`
- Advance: 4,678 commits
- Method: fast-forward, no force push
- Zooid branch checkpoint: `3d56d79d4354f9b46e2dbe572338fca2ed1086a1`
- Result: fork main is clean upstream mirror; Zooid planning isolated in `zooid-development/`
- Validation: baseline CI, Nix and Docker PASS

## Minimal CogentNexus runtime — RED

- Date: 2026-09-18 UTC
- Task: cnx-minimal-runtime-vertical-slice
- Commit: `3e4d180defc3d3ecac0a1626f78f18204f5ad460`
- Change: add tests defining persistence, evidence, idempotency and restart-recovery contract
- Important invariant: interrupted RUNNING work must recover as VERIFY, never implicit retry
- Result: RED boundary published before implementation; authoritative CI started from GitHub

## Minimal CogentNexus runtime — implementation

- Date: 2026-09-18 UTC
- Task: cnx-minimal-runtime-vertical-slice
- Commit: `e63610eab12a7c8cb2f12dd9f373bcb9fa492d97`
- Change: add `zooid_cnx` durable kernel and module CLI
- Persistence: `ZOOID_HOME/cogentnexus.db`; no HERMES_HOME fallback
- Data: Project, Ticket, Step, Evidence, Event, Checkpoint
- Semantics: acceptance evidence gate, replay idempotency, explicit interrupted-step resolution
- Validation at this checkpoint: Docker PASS; full CI/Nix still running
- Next: obtain GREEN, then build a narrow Hermes/Kanban execution adapter
