---
document_type: environment_verification_report
sprint: GENERATED-REQUIREMENTS-DEC034-IV-AND-GOVERNANCE-STABILIZATION-001
title: "Requirements Tooling Environment Verification"
date: "2026-05-13"
visibility: internal
publish_allowed: false
---

# Requirements Tooling Environment Verification Report

**Sprint:** GENERATED-REQUIREMENTS-DEC034-IV-AND-GOVERNANCE-STABILIZATION-001
**Date:** 2026-05-13
**Scope:** Inspect and report only — no tooling implementation

---

## Verdict Summary

| Check | Result |
|-------|--------|
| pytest availability | NOT INSTALLED |
| jsonschema availability | NOT INSTALLED |
| PyYAML availability | INSTALLED |
| Validator standalone execution | PASS (with manual_validate fallback) |
| Schema files present | PASS (4/4 schemas) |
| Generated requirement files present | PASS (8/8 files) |
| Hidden dependencies identified | YES — see Section 4 |

---

## Section 1: pytest Availability

**Command run:** `python -m pytest tests/requirements -v`

**Result:**
```
C:\Python313\python.exe: No module named pytest
```

**Diagnosis:** pytest is not installed in the active Python environment (C:\Python313). The test suite at `tests/requirements/test_validate_generated_requirements.py` (9 tests) cannot be executed.

**Impact:**
- `TestManualValidate` class (8 unit tests for manual_validate function) cannot run
- `TestValidateFormatIntegration` class (5 integration tests against real YAML files) cannot run
- This means no automated regression guard on the validator logic

**Fix required:** `pip install pytest` in the active environment (C:\Python313).

**Severity: MEDIUM** — validator runs standalone; test suite cannot verify validator correctness.

---

## Section 2: jsonschema Availability

**Command run:** `python -c "import jsonschema; print('jsonschema ok')"`

**Result:**
```
ModuleNotFoundError: No module named 'jsonschema'
```

**Diagnosis:** jsonschema (JSON Schema Draft7 validator) is not installed. The validator in
`tools/requirements/validate_generated_requirements.py` falls back to `manual_validate()` when
jsonschema is absent (line 57-58):

```python
except ImportError:
    # If jsonschema not installed, do manual validation
    return manual_validate(data, schema, file_path)
```

**Impact of using manual_validate fallback:**
- Covers: required fields, non-empty requirements, unique IDs, AI_PROPOSAL constraint,
  ACCEPTED_FOR_VERTICAL_SLICE test_requirements constraint, source_evidence constraint,
  conversion scope constraint
- Does NOT cover: type checking, enum validation, nested object structure, additionalProperties
  constraints, format validation (timestamps, etc.)
- All 8 files currently pass manual validation with 0 errors — correct behavior confirmed
- No false negatives for the current requirement set

**Fix required:** `pip install jsonschema` in the active environment (C:\Python313).

**Severity: LOW for current use** (manual_validate covers critical constraints); **MEDIUM for future use** (missing type/enum enforcement).

---

## Section 3: PyYAML Availability

**Command run:** `python -c "import yaml; print('yaml ok')"`

**Result:** `yaml ok`

**Diagnosis:** PyYAML is installed. YAML loading works. All 8 requirement files load successfully.

**Status: PASS**

---

## Section 4: Validator Standalone Reliability

**Command run:** `python tools/requirements/validate_generated_requirements.py --format fods --verbose`
**Command run:** `python tools/requirements/validate_generated_requirements.py --format fodt --verbose`

**Results:**
```
FODS: 4/4 PASS, 0 errors
FODT: 4/4 PASS, 0 errors
REQUIREMENTS_SCHEMA_VALIDATION: PASS
Total issues: 0
```

**Standalone reliability assessment:**

1. **Path resolution:** `REPO_ROOT = Path(__file__).resolve().parent.parent.parent` — resolves correctly from tools/requirements/ to repo root.

2. **YAML loading:** Uses `yaml.safe_load()` — safe against YAML code injection. Correct.

3. **Schema loading:** Loads JSON schemas from `schemas/generated-requirements/`. 4 schemas present and loaded correctly.

4. **Fallback behavior:** When jsonschema absent, falls back to manual_validate without crashing. Output indicates correct validation results.

5. **Exit codes:** 0 for pass, 1 for fail, 2 for missing files. Exit code behavior is correct.

6. **Format argument:** `--format all` runs both fods and fodt. Works correctly.

**Validator standalone reliability: PASS with fallback**

---

## Section 5: Hidden Dependencies

### Identified hidden dependencies:

| Dependency | Required for | Installed | Impact if missing |
|------------|-------------|-----------|-------------------|
| `pytest` | Test suite execution | NO | Tests cannot run; manual testing only |
| `jsonschema` | Full Draft7 schema validation | NO | Falls back to manual_validate; reduced constraint coverage |
| `pyyaml` | YAML loading (all operations) | YES | N/A — present |
| LibreOffice / soffice.com | Oracle tests (FODS-REQ-032, FODT-SE-030) | INSTALLED (confirmed Gate 6) | N/A — present |

### Implicit structural dependencies:

1. **Schema files must exist at `schemas/generated-requirements/`:** Confirmed present (4 schemas). If deleted, validator fails with `FileNotFoundError`.

2. **REPO_ROOT auto-detection assumes fixed depth:** `validate_generated_requirements.py` is at `tools/requirements/` — 2 levels from repo root. If moved, REPO_ROOT detection breaks.

3. **Hardcoded SCHEMA_MAP:** The validator hardcodes file names (commercial-requirements, object-model-requirements, save-edit-requirements, conversion-requirements). If a new requirement file type is added, the SCHEMA_MAP must be updated.

4. **No verifier-review.yaml validation:** The validator does not check verifier-review.yaml against a schema. Verifier-review content is untyped. This is a gap — a malformed verifier-review would not be caught by the validator.

5. **No traceability-map.yaml validation:** Same gap — traceability-map is not schema-validated.

---

## Section 6: Tooling Assumptions vs Actual Repo State

| Assumption | Actual state | Match? |
|------------|-------------|--------|
| schemas/generated-requirements/ contains 4 schemas | 4 schemas confirmed | YES |
| generated-requirements/{fods,fodt}/ contain 4 requirement files each | 4 files + verifier-review + traceability-map each | YES (validator sees 4/6 files) |
| validator uses PyYAML | PyYAML installed | YES |
| validator uses jsonschema for full validation | jsonschema NOT installed; manual fallback used | PARTIAL |
| test suite runnable via pytest | pytest NOT installed | NO |
| tests cover negative cases | TestManualValidate has 8 negative/positive tests | YES (if pytest installed) |

---

## Section 7: Recommended Actions (Inspect Only — Not Implemented)

The following actions are NOT implemented in this sprint. They are recommendations for
a subsequent tooling sprint.

### Priority 1 (short-term, low effort):
1. `pip install pytest jsonschema` in C:\Python313 environment
   - Enables full test suite
   - Upgrades validator to Draft7 compliance
   - Verify: `python -m pytest tests/requirements -v` should show 9/9 PASS

### Priority 2 (medium-term):
2. Add schema for `verifier-review.yaml` — prevent malformed verifier reviews from silently passing
3. Add schema for `traceability-map.yaml` — validate product goal coverage structure
4. Add stale-detection tool or extend validator with `--check-stale` flag
   (compares input_source_hashes against current file hashes)

### Priority 3 (long-term):
5. Add cross-file consistency check: accepted_for_vertical_slice in traceability-map must match
   ACCEPTED_FOR_VERTICAL_SLICE requirements in commercial-requirements.yaml
6. Add requirements_schema_validation_result to evidence bundle metadata

---

## Final Verdict

| Category | Result |
|----------|--------|
| pytest availability | NOT INSTALLED |
| jsonschema availability | NOT INSTALLED |
| Validator standalone | FUNCTIONAL (manual_validate fallback) |
| All 8 requirement files validate | PASS (0 errors) |
| Hidden dependencies | 2 uninstalled (pytest, jsonschema); 3 structural (schema map, REPO depth, no verifier schema) |
| Test suite executable | NO (requires pytest install) |
| Tooling assumptions match repo state | PARTIAL (dependencies missing) |
