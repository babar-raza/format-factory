# Autonomous Machinery Layer Review Plan
# Format Factory — Expert Manual System Review
# Phase 5 output — Generated: 2026-06-25

## Layers Under Review

1. Supervisor Infrastructure
2. Skills Layer
3. Specification Authority Layer (SAL)
4. Gap Ledger and Capability Authority
5. Evidence System
6. Governance Validators
7. Format Registry and Authority Registries

---

## 1. Supervisor Infrastructure

**Files:** `tools/supervisor/autonomous_cycle.py` (2,406 LOC), `check_continuation.py`, `sprint_executor.py`, `grade_declared_work.py`

**Maturity target:** L4 (enforced in pipeline)
**Current maturity:** L3 (implemented and tested; some LOC violations)

### Review Questions

1. **LOC violation (self-referential):** `autonomous_cycle.py` is at 2,406 LOC — above its own LOC cap. The system that enforces LOC caps on source files itself violates them. Does any validator catch this?

2. **LLM grader dependency:** `grade_declared_work.py` requires `GPT_OSS_ENDPOINT` or `PROFESSIONALIZE_BASE_URL`. Without these env vars, spec-parity items get `DEFERRED_WITH_REASON`. This silent degradation is the most dangerous system risk.

3. **Circuit breaker:** The zero-task circuit breaker was added in 2026-06-24. Is it wired correctly? Does it actually stop runaway loops?

4. **SIGNAL-UNIFY-001 bug fix:** `latest_dir` undefined bug was fixed 2026-06-25. Verify the fix is in source.

5. **Dispatcher reality:** Most dispatchers in `autonomous_cycle.py` are LOGISTICS_STUBs. Only `dispatch_recompute` is REAL_EXECUTION. This means many "sprint modes" are actually no-ops.

### Layer Check Rubric

| Check | Status |
|-------|--------|
| LOC cap on autonomous_cycle.py | VIOLATED (2406 LOC, known) |
| LOC cap on governance_validators.py | VIOLATED (3181 LOC, known) |
| LLM grader available | UNKNOWN (depends on env vars) |
| Circuit breaker wired | YES (added 2026-06-24) |
| SIGNAL-UNIFY-001 fixed | YES (fixed 2026-06-25) |
| Dispatcher reality | LOGISTICS_STUBs (most modes are no-ops) |

---

## 2. Skills Layer

**File:** `.supervisor/skill-registry.yaml` (65 skills)

**Maturity target:** L4 (enforced in pipeline)
**Current maturity:** L2 (implemented but advisory)

### Review Questions

1. How many skills have empty `implementation_paths: []`? These are prompt-only, not code-enforced.
2. Which skills are marked `deprecated` but still in the registry?
3. `ci_transcript_verification` is backlog — how are skill transcripts verified today?
4. `add-analytics-function` was suspended — is the skill still `deprecated` in registry?

### Known Issues

| Issue | Status |
|-------|--------|
| `add-analytics-function` deprecated | Still in registry (known) |
| `ci_transcript_verification` | Backlog — not enforced in CI |
| Empty implementation_paths | Several skills (prompt-only) |
| `capability_compiler` | Backlog |
| `ci_transcript_verification` | Backlog |

---

## 3. Specification Authority Layer (SAL)

**Location:** `.local/spec-cache/`

**Maturity target:** L4 (enforced for all formats)
**Current maturity:** L4 for FODS/FODT; L0 for 10 formats

### Review Questions

1. Which formats have spec facts in `.local/spec-cache/`?
2. For formats with CHAIN_BROKEN_AT_SAL: what would it take to build a SAL extractor?
3. Without spec facts, how does the system verify spec parity for CSV, SYLK, TOML, etc.?

### Known Chain Status

| Format | SAL Chain | Facts |
|--------|-----------|-------|
| FODS | CHAIN_INTACT | 4,988 |
| FODT | CHAIN_INTACT | 4,936 |
| ODS | CHAIN_INTACT | (from qname registry) |
| ODT | CHAIN_INTACT | (from qname registry) |
| ABW | CHAIN_BROKEN_AT_SAL | 0 |
| CSV | CHAIN_BROKEN_AT_SAL | 0 |
| DIF | CHAIN_BROKEN_AT_SAL | 0 |
| GNUMERIC | CHAIN_BROKEN_AT_SAL | 0 |
| NDJSON | CHAIN_BROKEN_AT_SAL | 0 |
| SYLK | CHAIN_BROKEN_AT_SAL | 0 |
| TOML | CHAIN_BROKEN_AT_SAL | 0 |
| TSV | CHAIN_BROKEN_AT_SAL | 0 |
| XCF | CHAIN_BROKEN_AT_SAL | 0 |
| ZST | CHAIN_BROKEN_AT_SAL | 0 |

---

## 4. Gap Ledger and Capability Authority

**File:** `reports/capability-layer/gap-ledger.json`

**Maturity target:** L3 (meaningful categories enabling routing)
**Current maturity:** L1 (data exists, taxonomy broken)

### CRITICAL ISSUE

1,131 of 1,132 gaps have `category: "unknown"`. The gap generation pipeline does not populate the category field.

**Consequence:** Gap routing, prioritization, and category-based filtering are all broken.
The capability routing system has no input to route on.

### Review Questions

1. Which pipeline step is supposed to set `category`? `gap_ledger_to_work_items.py`?
2. Is the `category` field defined in the gap ledger schema?
3. What would it take to retroactively classify the 1,131 unknown gaps?

---

## 5. Evidence System

**Location:** `.local/evidences/`

**Maturity target:** L4 (evidence quality enforced with physical output verification)
**Current maturity:** L3 (evidence bundles generated; quality grading LLM-dependent)

### Known Issues

| Issue | Severity |
|-------|---------|
| LLM grader requires external API keys | HIGH |
| `evidence_quality_zero` is warning-only | MEDIUM |
| No persistent proof of physical output files | MEDIUM |
| Adoption compliance not fully wired | LOW |

---

## 6. Governance Validators

**File:** `tools/supervisor/governance_validators.py` (3,181 LOC, 50 validators)

**Maturity target:** L5 (all gates enforced with physical output)
**Current maturity:** L4 (enforced in pipeline; LOC cap self-violation)

### Self-Referential LOC Violation

`governance_validators.py` enforces LOC caps on source files. It is itself at 3,181 LOC — a known violation of the same caps it enforces. The system acknowledges this via `known_violations` in the baseline.

### Validators Of Note

| Validator | Status |
|-----------|--------|
| V35 (LOC cap) | Active — enforced |
| V42 (deepening suspension) | Active — rejects arithmetic-only rotation |
| V44 (import inspection) | Fixed (was constant-WARN stub) |
| V48 (architecture_only stub gate) | Active — added 2026-06-21 |
| V53 (spec_qname compliance) | Active — blocks items without spec_qname |

---

## 7. Format Registry and Authority Registries

**Files:** `registry/format-registry.yaml`, `registry/parity-matrix.yaml`, `shared/qname-registry/`

**Maturity target:** L4 (authoritative and enforced)
**Current maturity:** L3-L4 (authoritative; parity-matrix partially advisory)

### Known Issues

| Issue | Severity |
|-------|---------|
| parity-matrix.yaml is advisory (self-declared) | MEDIUM |
| HTML/Markdown/TXT listed as format products | MEDIUM |
| poc-targets.yaml PASS claims unverified for some items | HIGH |

---

## Layer Maturity Summary

| Layer | Current Maturity | Target | Key Gap |
|-------|-----------------|--------|---------|
| Supervisor | L3 | L4 | LLM grader dependency; LOC violations |
| Skills | L2 | L4 | No CI enforcement; empty implementation_paths |
| SAL | L4 (ODF) / L0 (10 formats) | L4 all | CHAIN_BROKEN for 10 formats |
| Gap Ledger | L1 | L3 | 99.9% unknown category |
| Evidence | L3 | L4 | LLM grader; evidence_quality_zero advisory only |
| Governance | L4 | L5 | LOC self-violation; no physical output verification |
| Registries | L3-L4 | L4 | parity-matrix advisory; PASS claims unverified |
