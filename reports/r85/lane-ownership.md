# R85 Lane Ownership

Sprint: FORMAT-FACTORY-R85-POC-DIRECTION-LOCAL-SUPERVISOR-AUTONOMOUS-PRODUCT-FACTORY-MEGA-TRAIN-001
Date: 2026-05-31

## Coordinator Lane (Claude Code)

Coordinator owns shared authority files. Writes only after lane-local evidence passes.

Owned files:
- state/current-state.md
- state/current-state.json
- registry/format-registry.yaml (read-only in R85 — no new format gates)
- plans/master-plan.md (Section 38+ POC direction update)
- memory/00-index.md
- .supervisor/project-memory.md
- .supervisor/policies.yaml
- reports/r85/final-verdict.md
- R85 evidence contract
- final supervisor review package
- product-capability-matrix/poc-targets.yaml

## GROUP 1 — Direction correction

| Train | Owner | Primary output |
|-------|-------|----------------|
| A | Coordinator | memory/27-r85-product-factory-direction.md, reports/r85/current-direction-correction.md |
| B | Coordinator | product-capability-matrix/poc-targets.yaml, reports/r85/poc-target-matrix.md |

## GROUP 2 — Local supervisor adoption

| Train | Owner | Primary output |
|-------|-------|----------------|
| C | Coordinator | reports/r85/local-supervisor-plan-verification.md, reports/r85/supervisor-loop-smoke.md |
| D | Coordinator | .supervisor/policies.yaml update, reports/r85/product-direction-supervisor-policy.md |
| E | Coordinator | .supervisor/policies.yaml approval gate update, reports/r85/approval-gate-classifier-product-update.md |
| F | Coordinator | tests/supervisor/test_r85_taskmaster_ruflo_alignment.py, reports/r85/taskmaster-ruflo-product-alignment.md |

## GROUP 3 — Reproducibility

| Train | Owner | Primary output |
|-------|-------|----------------|
| G | Coordinator | reports/r85/fods-reproducible-product-path.md |
| H | Coordinator | docs/format-family-playbooks/, reports/r85/format-family-repeatability-templates.md |

## GROUP 4 — Commercial POC

| Train | Owner | Primary output |
|-------|-------|----------------|
| I | Coordinator | tests/net/fods updates, reports/r85/fods-commercial-dotnet-product-slice.md |
| J | Coordinator | tests/net/fodt updates, reports/r85/fodt-commercial-dotnet-product-slice.md |
| K | Coordinator | src/net/netpbm/ (new), tests/net/netpbm/ (new), reports/r85/third-commercial-product-selection.md |

## GROUP 5 — Reduced/FOSS

| Train | Owner | Primary output |
|-------|-------|----------------|
| L | Coordinator | reports/r85/zst-reduced-foss-product-finish.md |
| M | Coordinator | src/python/pbm/pbm_to_pgm.py (new cross-family export), reports/r85/netpbm-reduced-foss-product.md |
| N | Coordinator | reports/r85/sylk-or-dif-reduced-foss-product.md |

## GROUP 6 — Dogfooding

| Train | Owner | Primary output |
|-------|-------|----------------|
| O | Coordinator | docs/export/dogfood-export-strategy.md, reports/r85/dogfood-export-map.md |
| P | Coordinator | tests/python/netpbm/test_r85_pbm_to_pgm_dogfood.py, reports/r85/first-dogfooded-export-slice.md |

## GROUP 7-8 — Packages, Examples, AI, Automation

| Train | Owner | Primary output |
|-------|-------|----------------|
| Q | Coordinator | reports/r85/installed-package-review-package-proof.md |
| R | Coordinator | examples/python/ updates, reports/r85/examples-docs-poc-baseline.md |
| S | Coordinator | reports/r85/ai-assisted-poc-gap-extraction.md |
| T | Coordinator | reports/r85/supervisor-autonomous-next-sprint-proof.md |

## GROUP 9 — State, IV, Closure

| Train | Owner | Primary output |
|-------|-------|----------------|
| U | Coordinator | state/ updates, reports/r85/state-registry-memory-master-plan-sync.md |
| V | Coordinator | reports/r85/final-adversarial-independent-verification.md |

## Hard prohibitions (applies to all lanes)
- No git push
- No PyPI/NuGet upload
- No Gate 8 or Gate 11 approval
- No commercial_product_ready=true
- No MCP activation
- No destructive git operations
