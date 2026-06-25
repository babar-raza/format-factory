# Format Factory — Generation Archaeology & Forensic Audit
## Sprint Overview

**Sprint/Run ID:** ff-archaeology-20260625
**Date:** 2026-06-25
**Auditor:** Claude Sonnet 4.6 (claude-sonnet-4-6)
**Report Root:** `reports/forensic-audit-20260625/`
**Investigation Method:** 3 parallel Explore agents + preflight Bash inspection

---

## Core Question

> **Is Format Factory currently able to convert specifications into professional, repeatable,
> qname/spec-hierarchy-aligned, testable, maintainable .NET and Python format libraries?
> Or is it still generating product-shaped prototypes from weak machinery?**

---

## Verdict

**READY_AFTER_TARGETED_MACHINERY_REPAIRS**

The system is substantially built and operational. The machinery (SAL, capability layer,
governance validators, skills, supervisor) works. Source quality is high for 13/20 Python
formats (Gen4). Gate 11 sub-gate is APPROVED for FODS and FODT. But 5 targeted repairs
are required before the answer becomes unambiguously YES.

---

## Scope of Investigation

| Lane | Subject | Status |
|------|---------|--------|
| A | Repository / State / Evidence | COMPLETE |
| B | Source Inventory (20 Python + 10 .NET) | COMPLETE |
| C | QName / Spec Hierarchy Compliance | COMPLETE |
| D | Product Source Quality | COMPLETE |
| E | SAL (Spec Abstraction Layer) | COMPLETE |
| F | Capability Layer | COMPLETE |
| G | Downstream Product Generation | COMPLETE |
| H | Skills Inventory | COMPLETE |
| I | Autonomous Supervisor | COMPLETE |
| J | Backfill / Migration Facility | COMPLETE |
| K | Product Deepening Readiness | COMPLETE |

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| Python formats | 20 |
| .NET projects | 10 |
| SAL facts | 14,284 |
| Capability records | 1,909 |
| Governance validators | 50 |
| Gap ledger entries | 1,132 (87.9% closed) |
| Governance tests passing | 1,609 |
| QName coverage | 84.5% |
| Gen4 Python formats | 13 / 20 |
| Gen3 Python formats | 7 / 20 |
| Gen1/Gen2 formats | 0 (all upgraded) |
| Gate 11 sub-gate approved | FODS, FODT |

---

## Artifact Index

| # | File | Contents |
|---|------|----------|
| 1 | sprint-overview.md | This file |
| 2 | preflight-state.md | Branch, HEAD, dirty files, existing plans, ledgers |
| 3 | source-inventory.md | Complete product listing, file trees, test counts |
| 4 | source-hygiene-audit.md | Build artifacts, stale files, duplicates |
| 5 | generation-archaeology.md | Wave classification, epochs, what produced each layer |
| 6 | per-product-capability-matrix.yaml | Full 30-column matrix for 30 products |
| 7 | per-product-qname-compliance.yaml | QName coverage per format |
| 8 | src-source-quality-review.md | Python + .NET quality analysis |
| 9 | qname-schema-audit.md | QName compliance deep-dive |
| 10 | qname-translation-standard.md | Required standard with codebase examples |
| 11 | sal-audit.md | SAL facts, seeding, consumption, chain status |
| 12 | capability-layer-audit.md | 1,909 records, SAL integration proof |
| 13 | downstream-generation-audit.md | Spec-to-code pipeline, where malformed src enters |
| 14 | skill-inventory-and-gaps.md | 37 commands, enforcement, gaps |
| 15 | autonomous-supervisor-audit.md | GREEN state, 50 validators, known gaps |
| 16 | lane-separation-and-collision-risk.md | Machinery vs product lanes, GOV_BLOCK |
| 17 | backfill-facility-design.md | Current state, design for automated backfill |
| 18 | gate11-readiness-review.md | FODS/FODT status, criteria scores |
| 19 | product-deepening-readiness-plan.md | What to fix first, what is safe to continue |
| 20 | system-gap-matrix.yaml | 14 gaps, all columns |
| 21 | taskcards.yaml | 25+ taskcards across 14 groups |
| 22 | machinery-repair-plan.md | Immediate / short / medium / long-term |
| 23 | product-pilot-plan.md | FODS, FODT, ZST, NDJSON pilots |
| 24 | next-agent-execution-prompt.md | Ready-to-use follow-on sprint prompt |
| 25 | evidence-index.md | All artifact paths |
| 26 | final-verdict.md | Full verdict + 21 self-check answers |
| 27 | evidence-bundle.zip | ZIP of all 26 artifacts |

---

## What Was Intentionally NOT Done

- No src/ files were modified
- No domain model classes created (separate sprint)
- No capability compiler integration (separate sprint)
- No Gate 11 packet preparation (separate sprint)
- No product deepening
- No test execution (investigation only)
- No governance sprint closeout (this is an investigation, not a product sprint)

---

## Investigation Methodology

1. Launched 3 parallel Explore agents (no modification access):
   - **Agent 1:** Source inventory, .NET + Python structure, generation wave detection
   - **Agent 2:** Machinery layer — SAL, capability, skills, supervisor, gap ledger
   - **Agent 3:** QName compliance, backfill readiness, Gate 11 status, test quality

2. Synthesized findings into this 27-artifact report bundle

3. All findings are evidence-backed (direct source inspection, not summaries or assumptions)
