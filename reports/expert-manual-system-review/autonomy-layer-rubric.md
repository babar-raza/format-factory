# Autonomy Layer Rubric
# Format Factory — Expert Manual System Review
# Phase 9 output — Generated: 2026-06-25

## Overview

The autonomy layer is the machinery that produces, validates, and governs Format Factory products.
This rubric assesses each layer component on the L0–L5 maturity scale
and on 7 system-healing readiness dimensions.

---

## Maturity Scale (L0–L5)

| Level | Meaning |
|-------|---------|
| L0 | Not present — documented intent only |
| L1 | Documented only — no implementation |
| L2 | Implemented but advisory — can be overridden |
| L3 | Implemented and tested — works but not enforced in pipeline |
| L4 | Enforced in pipeline — blocks sprint continuation if violated |
| L5 | Proven end-to-end with physical output verification |

---

## Layer Assessments

### Supervisor Infrastructure

| Sub-component | Maturity | Issues |
|--------------|---------|--------|
| autonomous_cycle.py | L3 | 2406 LOC violation; dispatcher stubs |
| check_continuation.py | L3 | Complex branching; session isolation |
| sprint_executor.py | L3 | Many modes; some logistics-only |
| grade_declared_work.py | L2-L3 | LLM grader dependency |
| stop_reason_adjudicator.py | L2 | Advisory only |

**Target:** L4 for autonomous_cycle.py, check_continuation.py, grade_declared_work.py

---

### Skills Layer

| Sub-component | Maturity | Issues |
|--------------|---------|--------|
| skill-registry.yaml | L2 | Several empty implementation_paths |
| slash commands | L2 | Command files exist; CI not verified |
| ci_transcript_verification | L0 | Backlog — not implemented |
| Skill enforcement | L2 | Prompt-only for many skills |

**Target:** L4 for all active skills with implementation_paths

---

### SAL (Specification Authority Layer)

| Format Group | Maturity | Facts |
|-------------|---------|-------|
| FODS / FODT (ODF) | L4 | 4,988 / 4,936 facts |
| ODF image formats | L4 | Present |
| CSV, SYLK, TOML, NDJSON, etc. | L0 | CHAIN_BROKEN_AT_SAL |

**Target:** L4 for all 20 formats (requires SAL extractor for 10 broken formats)

---

### Gap Ledger

| Aspect | Maturity | Issue |
|--------|---------|-------|
| Gap data | L1 | 1,132 gaps exist |
| Gap taxonomy | L0 | 1,131 "unknown" category — routing broken |
| Gap routing | L0 | Cannot route by category |

**Target:** L3 (meaningful categories; routing enabled)

---

### Evidence System

| Sub-component | Maturity | Issue |
|--------------|---------|-------|
| Evidence bundle generation | L3 | Generated consistently |
| Evidence quality grading | L2 | LLM-dependent; DEFERRED when unavailable |
| Physical output verification | L1 | Not verified in CI |
| Evidence quality_zero blocking | L1 | Warning only; not blocking |

**Target:** L4 (evidence quality grading always produces a grade; physical outputs verified)

---

### Governance Validators

| Sub-component | Maturity | Issue |
|--------------|---------|-------|
| V35 (LOC cap) | L4 | Active and enforced |
| V42 (deepening suspension) | L4 | Active and enforced |
| V48 (architecture_only stub gate) | L4 | Active and enforced |
| V53 (spec_qname compliance) | L4 | Active and enforced |
| governance_validators.py LOC | VIOLATED | 3,181 LOC — violates own cap |
| autonomous_cycle.py LOC | VIOLATED | 2,406 LOC — violates own cap |

**Target:** L4 maintained; L5 for physical output verification

---

## System-Healing Readiness Dimensions (0–5 each)

1. **Gap detection** — Does the system detect this class of product defect?
2. **Root-cause traceability** — Can we trace product defect → system cause?
3. **Healing path clarity** — Is the system repair path defined and actionable?
4. **Rerunability** — Can we rerun the healed system to regenerate/revalidate the product?
5. **Product heal through system** — Does product improve when system is healed?
6. **Recurrence prevention** — Is a gate, validator, or test added to prevent recurrence?
7. **Evidence that system improved product** — Is there a physical proof artifact?

### System-Healing Scorecard

| Problem | Gap Detection | Root Cause | Healing Path | Rerun | Product Heal | Prevention | Evidence |
|---------|--------------|-----------|-------------|-------|-------------|------------|---------|
| PROB-009 (gap taxonomy) | 4 | 4 | 3 | 4 | 3 | 2 | 2 |
| PROB-010 (SAL broken) | 3 | 4 | 2 | 3 | 2 | 2 | 1 |
| PROB-011 (LLM grader) | 4 | 4 | 3 | 3 | 3 | 2 | 2 |
| PROB-001 (ZST no decomp) | 2 | 4 | 4 | 4 | 4 | 3 | 2 |
| PROB-002 (PDF Latin-1) | 2 | 4 | 3 | 3 | 4 | 2 | 2 |

**Key insight:** Gap detection scores are low for product problems (PROB-001, PROB-002)
because the gap ledger does not track them with meaningful categories.
This confirms that PROB-009 (gap taxonomy) must be fixed first.
