# 12 — Proof Chain Gaps Register

**Baseline commit:** dd909cf3a
**Evidence:** IPYNB and ORA trace analysis + system-wide architecture inspection

## Systematic Gaps (affect ALL formats)

### Gap 1: No Live Test Execution in Reconciliation
- **Edge:** Evidence → Reconciliation
- **Producer:** Implementation evidence files (historical PASS records)
- **Consumer:** contract_reconciler.py
- **What's missing:** The reconciler never executes test selectors. It checks file existence and historical transcript results.
- **Impact:** A test can fail without evidence being invalidated or reconciliation detecting it
- **Affected formats:** All 6 (ipynb, ora, nrrd, xliff, safetensors, ubl)
- **Status:** PROVEN

### Gap 2: No Source Hash Tracking in Evidence
- **Edge:** Source → Evidence
- **What's missing:** Evidence records do not store the SHA-256 of the source file they cover. When source changes, evidence is not invalidated.
- **Impact:** Source code can change arbitrarily without triggering evidence re-validation
- **Status:** PROVEN (reconciler input_digests hash the evidence FILE, not the source files the evidence covers)

### Gap 3: No Evidence-to-Certification Derivation
- **Edge:** Reconciliation → Certification
- **What's missing:** Certification is a manually-set YAML string, not computed from evidence. The reconciler explicitly outputs `promotion_effect: none` and `proof_strength: supporting_nonpromoting`.
- **Impact:** Certification cannot regress automatically. Manual label persists indefinitely.
- **Status:** PROVEN (false certification exploit)

### Gap 4: No Invalidation on Corpus/Fixture Changes
- **Edge:** Test fixtures → Evidence
- **What's missing:** When corpus files change (hashes drift), evidence citing those tests is not invalidated.
- **Impact:** IPYNB has 3 active corpus hash disagreements + 2 quarantine corpus disagreements while evidence still claims PASS
- **Status:** PROVEN (known IPYNB failures)

### Gap 5: No CI Installation of FF6 Packages
- **Edge:** CI → Package testing
- **What's missing:** CI runs `pip install -e ".[dev]"` only. None of the 6 gen-2 FF6 packages are installed. Tests run against source tree, not installed wheel.
- **Impact:** Package metadata errors (like ORA's wrong namespace) are never caught in CI
- **Status:** PROVEN (ci.yml grep shows no gen-2 installations)

### Gap 6: No Automated Namespace Validation
- **Edge:** product-goal.yaml → actual package
- **What's missing:** No test or validator checks that declared import_namespace matches actual installed namespace
- **Impact:** ORA declares format_factory.openraster but actual namespace is format_factory.ora — undetected
- **Status:** PROVEN (ORA trace)

## Format-Specific Gaps

### IPYNB
- Gap 7: timeout test failure not detected (test_timeout_preserves_partial_output_from_completed_cells)
- Gap 8: corpus hash drift (3 active + 2 quarantine + 1 license hash)
- Gap 9: Cells returned as dicts after round-trip, not typed objects

### ORA
- Gap 10: Double namespace mismatch (distribution + import_namespace)
- Gap 11: production_program.py has phantom source_package_id="openraster" pointing to nonexistent directory
- Gap 12: test_production_program.py asserts phantom path (line 941)
- Gap 13: 1 unresolved obligation despite other formats being CERTIFIED with 0 unresolved

### UBL
- Gap 14: Obligation count mismatch: 194 (product-goal.yaml canonical_obligations) vs 195 (obligation register/goal_driver)

## Root Cause Classification

All systematic gaps share one root cause: **evidence is a frozen snapshot, not a live computation.** The system records what was true at a point in time and never re-validates. The reconciler is designed to check structural completeness (do files exist? do symbols exist?) not runtime correctness (do tests pass?).

The false certification vulnerability is a second root cause: **certification is declared, not derived.** The promotion label in controller-state.yaml is the sole certification authority, and no automated mechanism can demote it.
