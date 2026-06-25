# Recommended Review Sequence
# Format Factory — Expert Manual System Review
# Phase 10 output — Generated: 2026-06-25

## Optimal Review Order

This sequence is designed to discover systemic issues before product issues,
and to review the most critical products before thinner ones.

### Step 1: Authority Layer Baseline (30 min)

Read these files first to establish ground truth before looking at source:
1. `registry/format-registry.yaml` — what formats are registered and at what gate
2. `registry/parity-matrix.yaml` — what spec parity claims have been made
3. `product-capability-matrix/poc-targets.yaml` — what PASS/FAIL claims exist
4. `shared/qname-registry/*.yaml` — what spec_qname mappings are registered

**Purpose:** Form a baseline of what is CLAIMED before reading what EXISTS.

---

### Step 2: System Gap Assessment (45 min)

Assess the autonomous machinery before reviewing products, because system gaps cause product gaps:
1. `reports/capability-layer/gap-ledger.json` — what gaps are tracked and with what categories
2. `.supervisor/skill-registry.yaml` — what skills govern product work
3. `.local/spec-cache/` — which formats have SAL facts
4. `tools/supervisor/governance_validators.py` — what validators enforce quality

**Key question:** Can the system detect and govern the product gaps I'm about to find?

---

### Step 3: .NET Commercial Products (2 hours)

Review in commercial priority order:
1. FODS — Gate 11 approved; expected HIGH
2. FODT — Gate 11 approved; expected HIGH
3. NetPBM — Commercial candidate; expected MEDIUM-HIGH
4. CSV — Thin; expected LOW-MEDIUM
5. TSV — Thin; expected LOW-MEDIUM
6. NDJSON — Thin; expected LOW-MEDIUM
7. ZST — CRITICAL GAP; expected VERY LOW
8. HTML/Markdown/TXT — Utilities; assess as non-format-products

---

### Step 4: Python FOSS Products (3 hours)

Review in richness order:
1. FODS — Most complete; expected PY-4
2. FODT — Most complete; expected PY-4
3. GNUMERIC, SYLK, TOML, NDJSON — Full parsers; expected PY-3
4. ODS, ODT, ABW — With writers; expected PY-3
5. PBM/PGM/PPM — Image formats with writers; expected PY-3
6. QOI, ZST — Special cases; expected PY-3
7. XCF — Parse-only (acceptable); expected PY-2
8. DIF, TSV, CSV — Thin parsers; expected PY-2-3
9. FODG — Large codec; expected PY-3
10. FODP — CRITICAL: no write_fodp; expected PY-2

---

### Step 5: Evidence and Authority Reconciliation (1 hour)

Compare source findings to authority claims:
1. List all PASS claims in poc-targets.yaml for reviewed products
2. Cross-check each PASS against source findings
3. Flag discrepancies (e.g., FodsOdsExporter PROTOTYPE vs PASS)
4. Assess parity-matrix claims against SAL facts

---

### Step 6: Problem Matrix Compilation (30 min)

For each confirmed gap:
1. Classify as system gap or product gap
2. Assign severity, confidence, status
3. Identify system component that must be healed first
4. Enter into confirmed-problems.json

---

### Step 7: Solution Matrix (30 min)

For each confirmed problem:
1. Define system healing step (if applicable)
2. Define product fix
3. Define test strategy
4. Define recurrence prevention
5. Assign to sprint or owner lane

---

### Step 8: Risk Register (15 min)

For each proposed fix:
1. Assess risk of the fix (could it break other products?)
2. Assess rollback strategy
3. Assign risk level (LOW/MEDIUM/HIGH)

---

### Total Time Estimate: ~8 hours for complete review
