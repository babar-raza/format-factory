# Sprint Preflight — FORMAT-FACTORY-EXPANDED-STANDING-MULTI-LANE-PRODUCT-FIRST-MEGA-TRAIN-001

## Baseline Package

- **Sprint**: FORMAT-FACTORY-STANDING-MULTI-LANE-PRODUCT-FIRST-MEGA-TRAIN-001
- **SHA-256**: 38dcb2fbb502efab7ff3c44f882719e7dc90506f879f502c1d735531def89934
- **Entries**: 81
- **Supervisor verdict**: ACCEPTED (6/6 items)
- **Git HEAD at sprint start**: e382e5fd8e65bc146c0821602cb8fb1ecfab982c

## Dirty State Classification

Working tree has uncommitted changes from prior sprints. This is EXPECTED and SAFE:
- `src/python/abw/` — ABW codec additions (edit_paragraph, export_to_json, etc.)
- `src/python/fodg/` — FODG probe_fodg
- `src/python/tsv/` — TSV write_tsv
- `src/python/ndjson/` — NDJSON new format (untracked)
- `tests/python/*/` — new tests (untracked)
- `reports/supervisor/` — supervisor-generated artifacts
- `.supervisor/` — supervisor state

No changes in forbidden paths (src/net/, registry/, AGENTS.md, GOVERNANCE.md).

## Lane Ownership

| Lane | Owner | Primary Paths |
|------|-------|--------------|
| 0 | Coordinator | reports/expanded-multilane-product-first-train/ |
| 1 | Product | src/python/abw/, src/python/gnumeric/, src/python/ndjson/, tests/python/ |
| 2 | Vertical Slice | src/python/ndjson/ (NDJSON depth) |
| 3 | Repeatability | playbooks/format-factory/ |
| 4 | Autonomy | .local/supervisor/, reports/expanded-multilane-product-first-train/autonomy/ |
| 5 | Reconciliation | reports/expanded-multilane-product-first-train/reconciliation/ |
| 6 | System Improvement | reports/expanded-multilane-product-first-train/system-improvement/ |
| 7 | Feature Coverage | reports/expanded-multilane-product-first-train/feature-coverage/ |
| 8 | New Formats | reports/expanded-multilane-product-first-train/new-formats/ |
| 9 | Pipeline Hardening | reports/expanded-multilane-product-first-train/pipeline-hardening/ |
| 10-19 | Supporting Lanes | reports/expanded-multilane-product-first-train/usable-outputs/ etc. |
| 20 | Evidence | .local/evidences/expanded-multilane-product-first-train/ |

## Forbidden Paths (No Edits)

- src/net/
- poc-targets.yaml (proposed delta only)
- registry/ (proposed delta only)
- AGENTS.md, GOVERNANCE.md

## Product Priority Confirmation

Lanes 1–2 run first and do not wait for reporting lanes.
Evidence work does not dominate.
