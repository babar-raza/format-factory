# Oracle State Machines — Format Factory
# Produced by: TC-ORA-007 (jaunty-whistling-meteor investigation)
# Generated: 2026-07-08

---

## 1. Oracle Definition Status Machine

The lifecycle of an oracle package (oracle-package.yaml) for a format:

```
OBLIGATION_CREATED
    │ sample files identified, authority class assigned
    ▼
SCAFFOLDED
    │ oracle-package.yaml structure written (no valid_cases yet)
    ▼
AUTHORITY_MAPPED
    │ specification_refs + authorized_fact_refs populated
    ▼
CASES_DEFINED
    │ valid_cases (minimum 3) written with expected_model_properties
    ▼
VERIFIED
    │ oracle run passes all cases at D1+ (at least one real non-synthetic case)
    ▼
PRODUCTION_ACTIVE
    │ oracle run passes in CI, product_source_hash committed
```

**Backward transitions (invalidation)**:

| From | To | Trigger |
|---|---|---|
| VERIFIED | CASES_DEFINED | New spec section found that existing cases don't cover |
| VERIFIED | AUTHORITY_MAPPED | Authority class downgraded |
| PRODUCTION_ACTIVE | VERIFIED | product_source_hash changed (stale oracle) |
| PRODUCTION_ACTIVE | CASES_DEFINED | D1 cases dropped to D0 after Fix 1 (synthetic only) |
| Any | OBLIGATION_CREATED | Format removed from active formats list |

**Post-Fix-1 state transitions (dif, fodt, sylk)**:
```
VERIFIED → CASES_DEFINED
  Reason: All existing valid_cases are D0 after synthetic exclusion.
  Required action: Add real model property comparisons to oracle-package.yaml.
```

---

## 2. Oracle Case Status Machine

The lifecycle of a single oracle case:

```
DRAFT
    │ case_id and profile assigned, no properties defined
    ▼
VALIDATED
    │ case schema verified (has required fields, authority_ref exists in SAL)
    ▼
READY
    │ sample file exists at input_ref, sha256 verified
    ▼
RUNNING
    │ executor is executing case
    ▼
PASSED ──────────────────────► ACCEPTED
    │                           │ Depth >= D1, no deviations
    │                           │
FAILED ──────────────────────► REWORK_REQUIRED
    │                           │ Deviation found, needs oracle-package fix
    │                           │ or product fix
    │                           ▼
INCONCLUSIVE                   SUPERSEDED
    │                           (case replaced by better version)
    ▼
STALE
    (product_source_hash changed since last run)
```

**Invalidation triggers for oracle_case**:
1. `product_source_hash_changed` → STALE
2. `case_schema_not_read` (assertion: with no model_props before Fix 5) → INVALID_ORACLE
3. `synthetic_properties_only` after Fix 1 → depth drops to D0 → REWORK_REQUIRED
4. `sample_file_sha256_mismatch` → BLOCKED_MISSING_SAMPLE
5. `authority_class_blocked` → BLOCKED_MISSING_AUTHORITY

---

## 3. Format Oracle Certification Machine

The certification state for a format in the release pipeline:

```
UNCERTIFIED
    │ G1 passes (source structure verified)
    ▼
ORACLE_EVIDENCE_PRESENT
    │ G2 passes (oracle-run-summary exists, depth >= D1)
    │ (After Fix 1: depth must be real D1, not synthetic)
    │ (After Fix 2: G2 cannot pass via test-suite fallback)
    ▼
BUILD_VERIFIED  [G3 — not implemented]
    ▼
INSTALL_VERIFIED  [G4 — not implemented]
    ▼
CERTIFIED  [G5 — Gate 10 approved in format-registry.yaml]
    ▼
PRODUCTION_ACTIVE  [Gate 11 — Babar Raza sign-off only]
```

**Invalidation triggers for certification**:
1. `product_source_hash_changed` → drops from ORACLE_EVIDENCE_PRESENT to UNCERTIFIED
2. `oracle_depth_dropped_to_d0` after Fix 1 → drops from ORACLE_EVIDENCE_PRESENT to UNCERTIFIED
3. `new_invalid_cases_added_unexecuted` → WARNING only (does not block cert)
4. `spec_version_updated` → WARNING, requires oracle re-run
5. `majority_d0_fraction` after Fix 6 → V143 WARN (does not block cert but flags coverage gap)

---

## 4. Invalidation Trigger Register (minimum 15)

| ID | Trigger | Affected Artifact | Action Required |
|---|---|---|---|
| INV-001 | product_source_hash changed | oracle-run-summary.json | Re-run oracle, update summary |
| INV-002 | oracle-package.yaml content changed | oracle-run-summary.json | Re-run oracle |
| INV-003 | Sample file sha256 mismatch | oracle case | Verify sample, update sha256 in corpus_refs |
| INV-004 | New spec section identified | oracle-package.yaml | Add new cases covering the section |
| INV-005 | Fix 1 applied (synthetic exclusion) | all oracle-run-summary.json | Re-run oracle for all formats |
| INV-006 | Fix 2 applied (G2 fallback removed) | gate-check-results.json | Ensure all formats have PASS > 0 |
| INV-007 | Authority class downgraded to REJECTED | oracle case | Remove case or replace authority |
| INV-008 | Format source moved to different path | oracle-package.yaml | Update module/callable references |
| INV-009 | Spec version updated (e.g., ODF 1.4) | oracle-package.yaml authority refs | Review affected sections |
| INV-010 | SAL fact retracted | oracle-package.yaml authorized_fact_refs | Remove or replace fact reference |
| INV-011 | New case type executor registered | oracle-package.yaml | Cases previously unexecuted may now run |
| INV-012 | majority_d0_fraction > 0.5 | oracle-run-summary.json | Upgrade D0 cases to D1 |
| INV-013 | Gate 10 revoked in format-registry.yaml | gate-check-results.json | G5 fails until re-approved |
| INV-014 | Product library API changed | oracle case callable refs | Update module/callable in oracle package |
| INV-015 | Sample file no longer representative | oracle case | Replace with better sample |
| INV-016 | D3 case (LibreOffice) moves from SKIPPED to PASS | oracle-run-summary.json | Update format_depth_score |
| INV-017 | assertion: schema case upgraded to model_props | oracle case | Update to expected_model_properties |

---

## 5. Depth Level Semantics

| Level | Name | Criterion | Example |
|---|---|---|---|
| D0 | Load Only | No exception during parse. No property comparison. | `loaded: true` (synthetic) or NO_SCHEMA case |
| D1 | Model Properties | At least one non-synthetic property compared against expected value | `sheet_count == 2`, `spec_qname == "office:document"` |
| D2 | Schema Validation | External schema validates the document structure | ODF RelaxNG via lxml |
| D3 | External Tool Interop | Third-party reference implementation agrees with result | LibreOffice CSV export comparison |

**After Fix 1 (synthetic property exclusion)**:
- D1 requires at least one property where `property NOT IN {"loaded", "result_type"}`
- `ok: True`, `is_fodp: True` etc. remain D1 (real returned fields)
- `loaded: True`, `result_type: "dict"` → D0 (synthetic — oracle framework computes these)
