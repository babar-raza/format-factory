# Preflight — Requirement & Capability Authority Layer Production-Blocker Healing Sprint

Sprint ID: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-PRODUCTION-BLOCKER-HEALING-001
Date: 2026-06-04

## Environment

- REPO_ROOT: C:/Users/prora/OneDrive/Documents/GitHub/format-factory (resolved via `git rev-parse --show-toplevel`)
- PYTHON: .local/venv/Scripts/python (fallback: python) → Python 3.13.2
- Branch: main
- HEAD: 3a86a05 feat(r93): context-pack, D92 defect repair, governed acceleration
- Dirty state classification: PRE_EXISTING_DOC_STATE / ALLOWED_DIRTY_STATE
  - 356 dirty entries, all pre-existing from prior R93/R92 sprint work
  - None modify `src/net/**`, `src/python/**`, `tests/net/**`, `tests/python/**`
  - This sprint adds only to `reports/requirement-capability-authority-layer-production-healing/**`,
    `docs/governance/**`, `docs/prompt-templates/**`, `.local/evidences/**`

## Governance Files Preflight Read Log

| File | Status |
|------|--------|
| CLAUDE.md | FOUND |
| AGENTS.md | MISSING (no AGENTS.md in repo root — governed by CLAUDE.md) |
| GOVERNANCE.md | MISSING (no separate GOVERNANCE.md — governance in docs/governance/) |
| plans/master-plan.md | FOUND |
| state/current-state.md | FOUND |
| reports/supervisor/session-resume.md | FOUND |
| docs/governance/product-first-operating-model.md | FOUND |
| docs/governance/four-stream-operating-model.md | FOUND |
| docs/governance/ai-authority-boundary.md | FOUND |
| product-capability-matrix/poc-targets.yaml | FOUND |
| registry/format-registry.yaml | FOUND (via registry/) |
| reports/requirement-capability-authority-layer-plan/** | MISSING (prior plan dir not yet created) |
| .supervisor/schemas/ | FOUND (11 schema files) |
| tools/supervisor/ | FOUND (47+ Python scripts) |

MISSING items are expected: AGENTS.md/GOVERNANCE.md not used in this repo; prior plan dir
does not exist yet (this sprint creates the healing output, not a prior plan dir).

## Git Snapshot at Sprint Start

See: current-git-status.txt

## Dirty State Classification

ALLOWED_DIRTY_STATE — all dirty entries are pre-existing `.supervisor/`, `reports/supervisor/`,
`.claude/commands/`, `plans/`, `tools/supervisor/` modifications from prior R93/R92 sprints.
No new dirty entries outside allowed paths will be introduced by this sprint.
