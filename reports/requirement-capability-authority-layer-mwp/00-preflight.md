# Preflight — Requirement & Capability Authority Layer MWP Sprint

Sprint ID: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-MWP-001
Date: 2026-06-04

## Environment

- REPO_ROOT: C:/Users/prora/OneDrive/Documents/GitHub/format-factory
- PYTHON: python (fallback) → Python 3.13.2
- Branch: main
- HEAD: 3a86a05 feat(r93): context-pack, D92 defect repair, governed acceleration

## Dirty State Classification

**ALLOWED_MWP_DIRTY_STATE + PRE_EXISTING_SUPERVISOR_WIP**

- 356 pre-existing dirty entries from R93/R92 sprints: .claude/commands/, .supervisor/, reports/supervisor/, plans/, tools/supervisor/ — all pre-existing, not modified by this sprint
- Tri-lane files: `??` untracked (not modified): tri_lane_integration.py, validate_tri_lane_contract.py, test_tri_lane_integration_fabric.py, test_tri_lane_integration_refresh_readiness.py — classified PRE_EXISTING_SUPERVISOR_WIP; will not be touched

## Design Import Gate Result

ALL 14 required design input files PRESENT (see design-import-gate.json)

## Closeout Hygiene Import

- reports/requirement-capability-authority-layer-production-healing/review-package-proof.md: PRESENT (created in healing sprint)
- docs/prompt-templates/requirement-capability-authority-layer-template.md: PRESENT
No repair needed.

## Scope

All new files go to:
- requirements-authority/**
- tools/requirements_authority/**
- tests/supervisor/test_requirement_capability_*.py
- reports/requirement-capability-authority-layer-mwp/**
- .local/evidences/requirement-capability-authority-layer-mwp/**
- .local/supervisor/reviews/requirement-capability-authority-layer-mwp/**
- docs/governance/requirement-capability-authority-layer.md (updates only)
- docs/prompt-templates/*.md (updates only)

Forbidden (no modifications): src/net/**, src/python/**, tests/net/**, tests/python/**, poc-targets.yaml (direct write), registry/format-registry.yaml (direct write)
