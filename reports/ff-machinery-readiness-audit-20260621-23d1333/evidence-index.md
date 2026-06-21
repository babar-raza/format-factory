# Evidence Index
# Sprint ID: ff-machinery-readiness-audit-20260621-23d1333

## Artifact Files Created

| # | File | Description |
|---|------|-------------|
| 1 | sprint-overview.md | Sprint purpose, verdict summary, evidence sources |
| 2 | preflight-state.md | Branch, HEAD, dirty files, supervisor state, directory layout |
| 3 | qname-schema-audit.md | QName design vs reality, what exists, what doesn't, enforcement gaps |
| 4 | per-product-qname-compliance.yaml | Per-product compliance matrix (8 products) |
| 5 | src-source-quality-review.md | Source quality ratings and issues per product |
| 6 | skill-inventory-and-gaps.md | 40+ skills inventoried, 5 critical gaps found |
| 7 | sal-audit.md | Two broken pipelines, 78 real facts stranded, test confirmation |
| 8 | capability-layer-audit.md | 3,166 capabilities, 932 gaps, disconnection from SAL |
| 9 | downstream-layer-audit.md | Feature planning, code gen, source quality enforcement, export layer |
| 10 | autonomous-supervisor-audit.md | Continuation state, plan lock, lane separation, Gate 11 stop |
| 11 | lane-separation-and-collision-risk.md | Lane boundaries, shared files, collision risk matrix |
| 12 | backfill-facility-design.md | 4-phase backfill design, tooling spec, compatibility strategy |
| 13 | gate11-readiness-review.md | FODS/FODT/ZST Gate 11 status and requirements |
| 14 | product-deepening-readiness-plan.md | Go/No-Go gates, pilot sequence, export proof |
| 15 | system-gap-matrix.yaml | 11 gaps (3 blocker, 6 high, 1 medium, 1 advisory) |
| 16 | taskcards.yaml | 8 taskcards across 6 groups |
| 17 | machinery-repair-plan.md | P0-P4 repair sequence with time estimates |
| 18 | downstream-layer-audit.md | (covered above) |
| 19 | next-agent-execution-prompt.md | Exact next execution prompt for agent |
| 20 | evidence-index.md | This file |
| 21 | final-verdict.md | Final verdict with self-check answers |

## Key Evidence Cited (from existing repo files)

| Evidence | Location | Finding |
|----------|----------|---------|
| SAL test failure | tests/specification-authority-layer/ | FODS facts NOT in sal-facts-latest.json |
| QName inventory | reports/specification-authority-layer-mwp/qname-ontology/canonical-class-inventory.yaml | ALL classes not_implemented or facade_exists_no_canonical |
| Migration plan | reports/specification-authority-layer-mwp/qname-ontology/migration-plan.yaml | ALL phases not_started |
| Plan lock | .local/supervisor/active-plan-lock.json | IN_PROGRESS, session 45da76b0e59c |
| FODS test failures | tests/python/fods/ | 31 ImportError collection failures |
| Continuation signal | .local/supervisor/continuation-signal.json | MANUALLY RESET (owner: reset_track_signal) |
| GAP ledger | reports/capability-layer/gap-ledger.json | 932 entries, severity: ? |
| Capability map | reports/capability-layer/unified-capability-map.json | 3,166 entries |
| Gate 11 FODS | reports/gate11/fods-gate11-readiness-packet.md | G11-G APPROVED, needs final sign-off |
| XCF analytics | src/python/xcf/xcf_analytics.py | 5725 LOC monolith |
| FODS .NET | src/net/fods/FodsDocument.cs | 1293 LOC, working, format-prefixed not qname |
| SAL plan | plans/snoopy-juggling-seal.md | Two broken pipelines, forensic analysis |
| Spec cache | .local/spec-cache/fods/1.3/workbench/verified-facts-review.yaml | 78 verified FODS facts |
| Skill registry | .supervisor/skill-registry.yaml | qname_ontology_generator.py referenced but missing |

## Test Evidence

| Test | Result | Evidence |
|------|--------|---------|
| SAL tests | 1 FAILED, 1 PASSED | "No FODS facts in sal-facts-latest.json" |
| Governance validator tests | 41/46 PASSED, 5 FAILED (known) | ModuleNotFoundError pre-existing |
| FODS Python tests | 31 ImportError collection failures | fods_value_variance etc. not found |
| FODT Python tests | Not run in this audit (new small suite) | — |
| FODS .NET tests | Not run (no dotnet runner available in this audit) | 547 from poc-targets.yaml |
