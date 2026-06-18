# Product Deepening Sprint Declaration Template

**Purpose:** Reference template for evidence-declaration.yaml files produced during
product deepening sprints (analytics function addition). Includes all governance fields
required by validators 1–5 and V13 (spec_fact_refs).

**Added:** 2026-06-17 (TC-GV-001 — governance validator debt triage)

---

## Required Fields per Work Item (PRODUCT_SOURCE type)

Every `planned_work_items` entry with `item_type: PRODUCT_SOURCE` must include:

| Field | Required By | Value for Product Deepening |
|---|---|---|
| `item_type` | V1, V2, V3, V13 | `PRODUCT_SOURCE` |
| `execution_method` | V1 | `AGENT_GOVERNED_DIRECT_EXECUTION` |
| `claim_classification` | V5 | `GOVERNED_BUT_NOT_REPLAYED` |
| `idempotency_key` | V3 | SHA256 of `"{sprint_id}-{item_id}"`, 64 hex chars |
| `source_diff_paths` | V2 | List of changed source file paths |
| `exception_classification` | V13 | See table below |

### `exception_classification` values for analytics functions

Analytics functions (e.g., `xcf_file_size_mod_7_plus_...`) are NOT spec-QName backed.
They must carry one of these exemptions to pass the `spec_fact_refs` validator (V13):

| Value | Use When |
|---|---|
| `legacy_backfill` | Function added BEFORE 2026-06-07 (SAL enforcement date). 2-sprint grace. |
| `fallback_authority_approved` | Function added AFTER 2026-06-07. Requires written rationale in item. |

For `fallback_authority_approved`, add `rationale` field:
```yaml
exception_classification: fallback_authority_approved
rationale: >
  Analytics function — derives statistical properties from parsed file content,
  not from spec structural elements. Not covered by spec QName framework.
  Approved per product policy exception for analytics-only deepening.
```

---

## MANDATORY: source_diff_paths Must Include Codec/Analytics Files

**RULE (enforced by TC-DECL-001 — effective immediately):**

If a sprint adds analytics functions to format `{format}`, the `source_diff_paths` list
MUST include at least one of:
- `src/python/{format}/{format}_codec.py`
- `src/python/{format}/{format}_parser.py`
- `src/python/{format}/analytics.py`

Adding analytics functions to a codec file IS a structural mutation and MUST be declared.
Declarations that omit the codec/analytics file from `source_diff_paths` are INCOMPLETE.

**After analytics separation is complete** for a format, `source_diff_paths` should
reference `analytics.py`, not the codec file. The codec file should only appear in
`source_diff_paths` if parser/core logic was also changed.

---

## Complete Item Template

```yaml
planned_work_items:
  - item_id: SPRINT333-FODG-001
    title: "Add fodg_file_size_mod_11_times_3_plus_shape_count_times_900_plus_text_count_times_700"
    status: completed
    item_type: PRODUCT_SOURCE
    execution_method: AGENT_GOVERNED_DIRECT_EXECUTION
    claim_classification: GOVERNED_BUT_NOT_REPLAYED
    # Compute: import hashlib; hashlib.sha256(b"sprint333-SPRINT333-FODG-001").hexdigest()
    idempotency_key: "<64-char sha256 hex>"
    # REQUIRED: Must include the codec or analytics file where functions land.
    # Adding functions to a codec IS a structural mutation — always declare it.
    source_diff_paths:
      - src/python/fodg/fodg_codec.py   # or analytics.py once analytics separation is done
      - src/python/fodg/__init__.py
    exception_classification: legacy_backfill
    state_machine_start: DISCOVERED
    state_machine_target: GOVERNANCE_ACCEPTED
    evidence_paths:
      - .local/evidences/sprint333-fodg-deepening-20260617/evidence-declaration.yaml
    tests_supporting:
      - tests/python/fodg/test_r638_fodg_sprint333_deepening.py
    acceptance_criteria: Function added, exported, 10 tests pass

  - item_id: SPRINT333-FODG-002
    title: "Add fodg_file_size_mod_7_times_50_plus_shape_count_times_800_plus_text_count_times_500"
    status: completed
    item_type: PRODUCT_SOURCE
    execution_method: AGENT_GOVERNED_DIRECT_EXECUTION
    claim_classification: GOVERNED_BUT_NOT_REPLAYED
    idempotency_key: "<64-char sha256 hex>"
    source_diff_paths:
      - src/python/fodg/fodg_codec.py
      - src/python/fodg/__init__.py
    exception_classification: legacy_backfill
    state_machine_start: DISCOVERED
    state_machine_target: GOVERNANCE_ACCEPTED
    evidence_paths:
      - .local/evidences/sprint333-fodg-deepening-20260617/evidence-declaration.yaml
    tests_supporting:
      - tests/python/fodg/test_r638_fodg_sprint333_deepening.py
    acceptance_criteria: Function added, exported, 10 tests pass
```

---

## Idempotency Key Generation

```python
import hashlib
sprint_id = "sprint333-fodg-deepening-20260617"
item_id = "SPRINT333-FODG-001"
key = hashlib.sha256(f"{sprint_id}-{item_id}".encode()).hexdigest()
# key is a 64-char hex string
```

---

## Governance Validator Reference

| Validator | Field Checked | Blocks Sprint? |
|---|---|---|
| V1 `execution_method_required` | `execution_method` in PRODUCT_SOURCE items | Yes |
| V2 `source_diff_required` | `source_diff_paths` in PRODUCT_SOURCE items | Yes |
| V3 `idempotency_key_required` | `idempotency_key` (64-char hex) in PRODUCT_SOURCE items | Yes |
| V4 `replay_recipe_required` | Only for `REPLAYABLE_*` claims — not needed for `GOVERNED_BUT_NOT_REPLAYED` | No |
| V5 `claim_classification` | `claim_classification` valid value | Yes |
| V13 `spec_fact_refs` | `spec_fact_refs` FACT-* IDs OR valid `exception_classification` | Yes (for PRODUCT_SOURCE) |
| V35 `monolith_detection` | Changed source files LOC vs baseline | Yes (regressions) |
| `validate_source_architecture` | Proactive AST scan — analytics in codec, `__init__.py` size, LOC cap | Yes (new violations) |

**IMPORTANT:** `validate_source_architecture` proactively scans ALL Python files in `src/python/`,
not just `source_diff_paths`. But declaring codec mutations in `source_diff_paths` is still
required so that `validate_monolith_detection` in `governance_validators.py` also runs on them.

---

## Historic Validator Failures (pre-TC-GV-001)

The following validators were failing on every sprint because declarations lacked these fields:

| Validator | Failures | Fix |
|---|---|---|
| `execution_method_required_validator_failed` | 122x | Add `execution_method: AGENT_GOVERNED_DIRECT_EXECUTION` |
| `spec_fact_refs_validator_failed` | 166x | Add `exception_classification: legacy_backfill` |
| `source_diff_required_validator_failed` | 80x | Add `source_diff_paths: [...]` |
| `idempotency_key_required_validator_failed` | 54x | Add `idempotency_key: <sha256>` |
| `claim_classification_validator_failed` | 7x | Add `claim_classification: GOVERNED_BUT_NOT_REPLAYED` |

Starting from the next sprint using this template, these failures should be eliminated.
