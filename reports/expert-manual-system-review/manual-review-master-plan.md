# Manual Review Master Plan
# Format Factory — Expert Manual System Review
# Phase 10 output — Generated: 2026-06-25
# Sprint: FORMAT-FACTORY-EXPERT-MANUAL-SYSTEM-REVIEW-PLAN-001

## Executive Summary

This document is the master output of the expert manual system review sprint.
It consolidates findings from all 11 phases and defines the recommended healing path.

**Review verdict:** `EXPERT_MANUAL_SYSTEM_REVIEW_PLAN_READY`

**Key finding:** Format Factory has two strong commercial products (FODS, FODT) ready for NuGet publication
after known gap remediation, and a solid foundation of 19 Python FOSS packages at PY-3 level.
However, three system gaps block confident governed product repair:
1. Gap ledger taxonomy is broken (99.9% unknown category)
2. SAL chain is broken for 10 of 20 Python formats
3. LLM evidence grader requires external API keys (silent degradation)

These system gaps must be healed BEFORE systematic product improvement can be trusted as governed.

---

## System Health Summary

| Layer | Current Level | Target | Gap |
|-------|--------------|--------|-----|
| .NET Products (FODS/FODT) | L4 (strong) | L5 | Pub. credentials |
| .NET Products (CSV/TSV/NDJSON) | L2 (thin) | L3 | Edit API + tests |
| .NET Products (ZST) | L1 (probe only) | L3 | No decompression |
| Python FOSS (FODS/FODT) | L4 (strong) | L5 | Pub. credentials |
| Python FOSS (most others) | L3 (functional) | L4 | Installed workflow |
| Python FOSS (FODP) | L2 (read-only) | L3 | No write_fodp |
| Supervisor | L3 | L4 | LLM grader; LOC |
| Skills | L2 | L4 | CI enforcement |
| SAL | L4/L0 mix | L4 all | 10 CHAIN_BROKEN |
| Gap Ledger | L1 | L3 | Taxonomy broken |
| Evidence | L3 | L4 | Grader dependency |
| Governance | L4 | L5 | LOC self-violation |

---

## Problem Summary (18 Problems Identified)

### CRITICAL (Fix Immediately — Block Product Trust)

| ID | Summary | Owner |
|----|---------|-------|
| PROB-001 | ZST .NET: no decompression — not a product | dotnet_commercial |
| PROB-009 | Gap ledger: 99.9% unknown category | system |

### HIGH (Fix Before NuGet/PyPI Publication)

| ID | Summary | Owner |
|----|---------|-------|
| PROB-002 | FODS PDF: Latin-1 only | dotnet_commercial |
| PROB-003 | FODT: no table traversal in public model | dotnet_commercial |
| PROB-010 | SAL chain broken for 10 formats | system |
| PROB-011 | LLM grader dependency; silent degradation | system |
| PROB-013 | FodsOdsExporter: PROTOTYPE vs. PASS in poc-targets | evidence |

### MEDIUM (Fix in Regular Sprints)

| ID | Summary | Owner |
|----|---------|-------|
| PROB-004 | HTML/Markdown/TXT counted as format products | governance |
| PROB-005 | CSV .NET: no edit API | dotnet_commercial |
| PROB-006 | FODP Python: no write_fodp | python_foss |
| PROB-012 | autonomous_cycle.py + governance_validators.py LOC violations | system |
| PROB-014 | Analytics masquerade rename (deferred) | python_foss |
| PROB-015 | Skills with empty implementation_paths | skills |
| PROB-016 | FodsOdsExporter PROTOTYPE comment (overlaps PROB-013) | dotnet_commercial |
| PROB-017 | ci_transcript_verification backlog | skills |

### LOW (Or Corrected)

| ID | Summary | Status |
|----|---------|--------|
| PROB-007 | ODS Python no writer | CLOSED_CORRECTED — write_ods() confirmed |
| PROB-008 | PBM/PGM/PPM no writers | CLOSED_CORRECTED — write_* confirmed |
| PROB-018 | ZST Python analytics ratio | LOW — analytics-heavy but functional |

---

## System-First Healing Sequence

```
Phase 1 (System): Fix gap ledger taxonomy (PROB-009)
  → Enables: gap routing, prioritization, category-based filtering

Phase 2 (System): Extend SAL chain for 10 broken formats (PROB-010)
  → Enables: spec-parity grading for CSV, SYLK, TOML, etc.

Phase 3 (System): Resolve LLM grader dependency (PROB-011)
  → Enables: reliable evidence quality grades

Phase 4 (Authority): Fix poc-targets discrepancies (PROB-013)
  → Enables: accurate commercial readiness claims

Phase 5 (Product): ZST .NET decompression (PROB-001)
  → Governed by healed gap ledger

Phase 6 (Product): FODS PDF Unicode (PROB-002)
  → Governed by healed gap ledger

Phase 7 (Product): FODT table model (PROB-003)
  → Governed by healed gap ledger

Phase 8 (Product): FODP write_fodp (PROB-006)
  → Governed by healed gap ledger

Phase 9 (Product): CSV edit API (PROB-005)
  → Governed by healed gap ledger

Phase 10 (Registry): HTML/Markdown/TXT reclassification (PROB-004)
  → Metadata fix; no source changes needed
```

---

## Commercial Publication Readiness

### FODS .NET (FormatFactory.Fods)

- Score: 3.79/5 (APPROACHING_SCOPED_COMMERCIAL_READY)
- Blocking gaps: ODS exporter PROTOTYPE vs. PASS (PROB-013)
- Scoped ready: If scope excludes ODS exporter and non-Latin PDF content
- Gate 11: G11-G approved by Babar Raza; awaiting NuGet publication credentials

### FODT .NET (FormatFactory.Fodt)

- Score: 3.67/5 (APPROACHING_SCOPED_COMMERCIAL_READY)
- Blocking gaps: No table traversal (PROB-003); Latin-1 PDF only (PROB-002)
- Scoped ready: If scope excludes table-containing documents and non-Latin PDF content
- Gate 11: G11-G approved by Babar Raza; awaiting NuGet publication credentials

### Python FOSS (FODS, FODT packages)

- Level: PY-4 (approaching PY-5)
- Blocking gaps: No per-format README; no standalone installation proof page
- Ready for PyPI scoped release with documentation disclaimer

---

## Next Sprint Recommendation

**Recommended next sprint:** `ff-expert-review-system-healing-001`

Sprint goal: Heal system gaps PROB-009 and PROB-011 before any product work.

Sprint scope:
1. Fix gap_ledger_to_work_items.py to populate category field from gap content
2. Re-run gap ledger generation; verify categories are meaningful
3. Add local evidence grader fallback (or document limitation formally)
4. Verify autonomous_cycle.py circuit breaker is correctly wired
5. Update session-resume.md with system healing status

Sprint constraints:
- Same as this sprint: no Gate 11 changes, no publication
- Source changes ONLY in tools/supervisor/ and reports/
- No changes to src/ products yet

After system healing sprint: execute product fixes through healed gap ledger paths.

---

## Files Created in This Sprint

See `final-plan-mode-summary.md` for complete file list with status.
