# Preflight — Specification Authority Layer Production Healing
Sprint ID: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-BLOCKER-PLAN-HEALING-001
Date: 2026-06-04

## Environment

- PYTHON: .local/venv/Scripts/python (Python 3.13.2)
- REPO_ROOT: C:/Users/prora/OneDrive/Documents/GitHub/format-factory
- Branch: main
- HEAD: 3a86a05295cb4b82ed40a3408b0612a90f93643c
- ZIP_PATH: $REPO_ROOT/.local/supervisor/reviews/specification-authority-layer-production-healing/declaration-review-package.zip
- DECL_PATH: $REPO_ROOT/.local/evidences/specification-authority-layer-production-healing/evidence-declaration.yaml

## Governance Reads

| File | Status |
|------|--------|
| CLAUDE.md | PRESENT |
| AGENTS.md | MISSING (caveat) |
| docs/governance/ai-authority-boundary.md | PRESENT |
| plans/master-plan.md | PRESENT |
| reports/supervisor/session-resume.md | PRESENT |
| reports/supervisor/approval-gates.md | PRESENT |
| .supervisor/policies.yaml | PRESENT |
| .supervisor/schemas/evidence-declaration.schema.json | PRESENT |
| tools/supervisor/autonomous_cycle.py | PRESENT |
| tools/supervisor/build_declaration_review_package.py | PRESENT |

## AUTONOMOUS_CONTINUE Gate

approval-gates.md read: AUTONOMOUS_CONTINUE: YES — proceeding with sprint.

## Dirty State Classification

All dirty files are pre-existing. This sprint does not modify any of them.

| Pattern | Classification |
|---------|----------------|
| .claude/commands/*.md (modified) | PRE_EXISTING_DOC_STATE — R93 work |
| .gitignore (modified) | PRE_EXISTING_DOC_STATE — R93 work |
| .supervisor/*.yaml (modified) | PRE_EXISTING_DOC_STATE — R93 work |
| plans/master-plan.md (modified) | PRE_EXISTING_DOC_STATE — R93 work |
| product-capability-matrix/poc-targets.yaml (modified) | PRE_EXISTING_DOC_STATE — R93 work |
| reports/r90/*.json (modified) | PRE_EXISTING_DOC_STATE — R90 work |
| reports/supervisor/*.md/json (modified) | PRE_EXISTING_DOC_STATE — supervisor outputs |
| src/net/fods/FodsDocument.cs (modified) | PRE_EXISTING_DOC_STATE — R93 work |
| src/net/fodt/FodtDocument.cs (modified) | PRE_EXISTING_DOC_STATE — R93 work |
| src/net/netpbm/Model/NetpbmImage.cs (modified) | PRE_EXISTING_DOC_STATE — R93 work |
| src/python/sylk/sylk_parser.py (modified) | PRE_EXISTING_DOC_STATE — R93 work |
| tools/supervisor/tri_lane_integration.py (untracked) | OTHER_RUNNING_SPRINT_DIRTY_STATE |
| memory/66-*.md (untracked) | PRE_EXISTING_DOC_STATE |

**Overall classification: ALLOWED_DIRTY_STATE**
No unsafe dirty state detected. Sprint may proceed.

## Evidence Root Labels

| Label | Path | This Sprint |
|-------|------|-------------|
| HEALING_SPRINT_EVIDENCE_ROOT | .local/evidences/specification-authority-layer-production-healing/ | WRITE HERE |
| HEALING_SPRINT_REVIEW_ROOT | .local/supervisor/reviews/specification-authority-layer-production-healing/ | ZIP GOES HERE |
| REPAIR_SPRINT_EVIDENCE_ROOT | .local/evidences/specification-authority-layer-production-healing-plan-repair/ | DO NOT WRITE |
| REPAIR_SPRINT_REVIEW_ROOT | .local/supervisor/reviews/specification-authority-layer-production-healing-plan-repair/ | DO NOT WRITE |

## Controlling Prompt

Read: reports/specification-authority-layer-production-healing-plan-repair/final-ready-to-send-execution-prompt.md
Status: PRESENT — using as execution authority
