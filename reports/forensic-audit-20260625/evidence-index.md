# Evidence Index

**Sprint/Run ID:** ff-archaeology-20260625
**Audit Date:** 2026-06-25
**Report Root:** `reports/forensic-audit-20260625/`

---

## Artifact Inventory

All 26 report artifacts produced by this forensic audit session.

| # | Artifact | File | Size (approx) | Status |
|---|---------|------|--------------|--------|
| 1 | Sprint Overview | sprint-overview.md | ~4 KB | COMPLETE |
| 2 | Preflight State | preflight-state.md | ~8 KB | COMPLETE |
| 3 | Source Inventory | source-inventory.md | ~12 KB | COMPLETE |
| 4 | Source Hygiene Audit | source-hygiene-audit.md | ~4 KB | COMPLETE |
| 5 | Generation Archaeology | generation-archaeology.md | ~8 KB | COMPLETE |
| 6 | Per-Product Capability Matrix | per-product-capability-matrix.yaml | ~20 KB | COMPLETE |
| 7 | Per-Product QName Compliance | per-product-qname-compliance.yaml | ~10 KB | COMPLETE |
| 8 | Source Quality Review | src-source-quality-review.md | ~6 KB | COMPLETE |
| 9 | QName Schema Audit | qname-schema-audit.md | ~6 KB | COMPLETE |
| 10 | QName Translation Standard | qname-translation-standard.md | ~5 KB | COMPLETE |
| 11 | SAL Audit | sal-audit.md | ~5 KB | COMPLETE |
| 12 | Capability Layer Audit | capability-layer-audit.md | ~5 KB | COMPLETE |
| 13 | Downstream Generation Audit | downstream-generation-audit.md | ~5 KB | COMPLETE |
| 14 | Skill Inventory and Gaps | skill-inventory-and-gaps.md | ~6 KB | COMPLETE |
| 15 | Autonomous Supervisor Audit | autonomous-supervisor-audit.md | ~5 KB | COMPLETE |
| 16 | Lane Separation and Collision Risk | lane-separation-and-collision-risk.md | ~5 KB | COMPLETE |
| 17 | Backfill Facility Design | backfill-facility-design.md | ~6 KB | COMPLETE |
| 18 | Gate 11 Readiness Review | gate11-readiness-review.md | ~5 KB | COMPLETE |
| 19 | Product Deepening Readiness Plan | product-deepening-readiness-plan.md | ~5 KB | COMPLETE |
| 20 | System Gap Matrix | system-gap-matrix.yaml | ~15 KB | COMPLETE |
| 21 | Taskcards | taskcards.yaml | ~20 KB | COMPLETE |
| 22 | Machinery Repair Plan | machinery-repair-plan.md | ~5 KB | COMPLETE |
| 23 | Product Pilot Plan | product-pilot-plan.md | ~5 KB | COMPLETE |
| 24 | Next Agent Execution Prompt | next-agent-execution-prompt.md | ~6 KB | COMPLETE |
| 25 | Evidence Index | evidence-index.md | ~3 KB | COMPLETE |
| 26 | Final Verdict | final-verdict.md | ~8 KB | COMPLETE |
| 27 | Evidence Bundle | evidence-bundle.zip | ~150 KB | COMPLETE |

---

## Key Evidence Sources Used in This Audit

The following pre-existing files were inspected by 3 parallel Explore agents to produce the findings above. These are evidence sources, not audit outputs.

### Repository State Evidence

| Evidence | Path | Key Finding |
|---------|------|-------------|
| Git HEAD | HEAD commit c6b24706 | Phase 3 TC-P3 all-green |
| Dirty file list | `git status` output | ~130 modified/untracked — current sprint artifacts |
| Master plan | `plans/master-plan.md` | Sections 1-54+ active |
| Continuation signal | `.local/supervisor/continuation-signal.json` | autonomous_continue=true, iteration 1/12 |
| Approval gates | `reports/supervisor/approval-gates.md` | AUTONOMOUS_CONTINUE: YES |

### Source Evidence

| Evidence | Path | Key Finding |
|---------|------|-------------|
| Python formats | `src/python/` (20 dirs) | 20 formats, Gen3=7, Gen4=13 |
| .NET projects | `src/net/` (10 dirs) | 10 projects, commercial+prototype+exporter |
| Source baseline | `registry/source-structure-baseline.json` | 47 known violations with write-once caps |
| QName registries | `shared/qname-registry/` (21 YAML files) | 84.5% python_file populated |

### SAL / Capability Evidence

| Evidence | Path | Key Finding |
|---------|------|-------------|
| SAL facts | `.local/spec-cache/` (22 JSONs) | 14,284 facts across all formats |
| Capability map | `reports/capability-layer/unified-capability-map.json` | 1,909 records |
| Gap ledger | `reports/capability-layer/gap-ledger.json` | 1,132 entries, 87.9% closed |
| Parity matrix | `registry/parity-matrix.yaml` | FODS PARTIAL, FODT BLOCKED |

### Governance Evidence

| Evidence | Path | Key Finding |
|---------|------|-------------|
| Governance validators | `tools/supervisor/governance_validators.py` | 50 validators, 3178 LOC |
| Skill registry | `.supervisor/skill-registry.yaml` | 37+ skills registered |
| Command files | `.claude/commands/` (37 files) | All categories present |
| Known failure ledger | `registry/known-failure-ledger.yaml` | Pre-existing failures cataloged |

### Test Evidence

| Evidence | Path | Key Finding |
|---------|------|-------------|
| Python tests | `tests/python/` | 1,447 test files |
| Supervisor tests | `tests/supervisor/` | 162 test files |
| .NET tests | `tests/net/` | 189 test files |
| Test results | `reports/supervisor/latest-review.md` | 1,609 pass, 0 fail |

---

## Audit Methodology

**Investigation method:** 3 parallel Explore subagents (one session's pre-work), each covering distinct lanes:
- **Agent 1:** Repository state, source inventory, Python source quality, generation archaeology
- **Agent 2:** SAL audit, capability layer, downstream generation, skill inventory
- **Agent 3:** Supervisor audit, governance validators, lane separation, backfill facility

**Evidence standard:** Direct file inspection only. No inference from prior MEMORY.md entries.
**Reconstruction policy:** Where findings conflicted with MEMORY.md, direct file inspection was authoritative.

---

## Canonical Reference Files for Future Audits

If re-running this audit or extending it, the following files are the ground truth:

| Concern | Ground Truth File |
|---------|-----------------|
| Format generation wave | `reports/forensic-audit-20260625/generation-archaeology.md` |
| QName compliance scores | `reports/forensic-audit-20260625/per-product-qname-compliance.yaml` |
| System gaps | `reports/forensic-audit-20260625/system-gap-matrix.yaml` |
| Repair priorities | `reports/forensic-audit-20260625/taskcards.yaml` |
| Gate 11 status | `reports/forensic-audit-20260625/gate11-readiness-review.md` |
| Overall verdict | `reports/forensic-audit-20260625/final-verdict.md` |
