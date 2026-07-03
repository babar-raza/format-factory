---
version: "1.5"
last-updated: "2026-07-03"
phase-available: "3+"
gate-required: null
generated_by: claude
visibility: generated
---

# /add-python-object-model-feature

Add a new object-model feature to a Python FOSS product (fods, fodt, pbm, pgm, ppm, sylk, zst).

## MANDATORY PRE-CHECK: File-Type and Wildcard Prohibition

**Before Step 0:**
1. Read the first 30 lines of every target source file.
2. If the file has NO `class` definitions and contains only functions — it is NOT a domain model file. STOP: `BLOCKED_ANALYTICS_FILE_TARGETED`. Object-model features must go in a file with proper class definitions.
3. Wildcard imports (`from .X import *`) are PROHIBITED in all product source files. Do not add code that depends on wildcards being present. If found, register as a gap instead.
4. After implementation: verify `__all__` in `<format>/__init__.py` explicitly lists all new public names. No wildcard re-exports.

---

## Step 0 — Knowledge Registry Lookup (MANDATORY, before any code)

Before modifying or creating any Python domain model class:

1. Read `.supervisor/knowledge/registry.yaml` — locate `stable_semantic_key: python_domain_model_class` (KC-PYTHON-001)
2. Read `.supervisor/knowledge/contracts/python-domain-model.yaml`
3. Verify `status: VERIFIED_CURRENT`. If STALE: run `.venv/Scripts/python .supervisor/knowledge/validate_knowledge_contracts.py --contract KC-PYTHON-001` and update contract before proceeding.
4. Read `.supervisor/knowledge/examples/python-domain-model-canonical.py`
5. Follow the contract structure exactly. Do NOT infer structure by inspecting other implementations.

If contract is missing or status is `CONTRADICTED`: add an entry to `.supervisor/knowledge/gaps.yaml` (following KG-001 template), investigate authority, write/repair contract, then resume this skill.

## Usage

```
/add-python-object-model-feature
```

## What This Skill Does

1. **Pre-flight**: Reads `.supervisor/skill-registry.yaml` and `reports/r90/product-code-change-ledger.json`
2. **Plan**: Determines the target Python module and feature to add
3. **Implement**: Adds the feature to `src/python/<format>/` following existing patterns
4. **Test**: Creates a test in `tests/python/<format>/test_r<run>_<feature>.py`
5. **Ledger**: Adds a `GOVERNED_PRODUCT_CHANGE` entry to `reports/r90/product-code-change-ledger.json`
6. **Verify**: Runs `python -m pytest tests/python/<format>/test_r<run>_<feature>.py -v`

## Mandatory QName Requirements

Because `spec_qname_required: true` for this skill, the execution handoff MUST include:
- `spec_qname`: the ODF/format QName of the element being modeled (e.g. `"table:table-cell"`)
- `spec_fact_ref`: the FACT-{FORMAT}-* identifier from `.local/sal-output/sal-facts-latest.json`
- At least one `spec_fact_refs` entry linking the feature to a format specification fact. Example:

```yaml
spec_fact_refs:
  - PPM-FACT-001   # Netpbm §2.1 — P6 binary header
```

If no `spec_fact_refs` are provided, stop with `BLOCKED_SPEC_QNAME_REQUIRED`.
Spec facts are produced by `tools/specification-authority-layer/sal_master_runner.py` and stored
in `.local/sal-output/sal-facts-latest.json`. Verify the cited QName exists in that file.

## Constraints

- One feature at a time
- Must add or modify Python source in `src/python/`
- Must create at least 4 new test functions
- Must add ledger entry with SHA-256 before and after
- No direct src edits without this skill or explicit execution handoff

## Evidence Required

- Source file path
- Pre-change SHA-256
- Post-change SHA-256
- Test file path
- Test count and pass result
- Ledger entry ID

## Ledger Entry Format

```json
{
  "entry_id": "R<N>-GOVERNED-PYTHON-<FORMAT>-<FEATURE>-001",
  "sprint": "R<N>",
  "classification": "GOVERNED_PRODUCT_CHANGE",
  "skill_used": "/add-python-object-model-feature",
  "source_files": [{"path": "src/python/<format>/...", "sha256_before": "...", "sha256_after": "..."}],
  "tests_added": ["tests/python/<format>/test_r<n>_<feature>.py"],
  "test_count": <n>,
  "description": "<feature> added to <format>"
}
```

## Allowed Paths

- `src/python/<format>/` (source)
- `tests/python/<format>/` (tests)

## Forbidden Paths

- `src/net/**` (wrong track)
- `registry/format-registry.yaml` (gate authority)
- `plans/master-plan.md` (operational authority)
- `product-capability-matrix/poc-targets.yaml` (use /update-capability-matrix)

## Rollback

1. Revert source changes in `src/python/<format>/`
2. Remove test file `tests/python/<format>/test_r<n>_<feature>.py`
3. Remove the ledger entry from `reports/r90/product-code-change-ledger.json`
4. Re-run `python tools/supervisor/validate_product_code_ledger.py` to confirm PASS

## Validation

Complete only when ledger validation and focused Python tests pass (4+ tests, 0 failures).

## Transcript Requirement

After execution, emit a skill invocation transcript JSON to `reports/skills-r<N>/skill-transcripts/`
with: skill_id, format_id, feature_name, changed_files, test_results, ledger_entry_id, verdict.

## Sample Invocation

```
/add-python-object-model-feature
# Inputs:
#   format_id: ppm
#   feature_name: grayscale_conversion
#   exact_source_paths: [src/python/ppm/ppm_grayscale.py]
#   exact_test_paths: [tests/python/ppm/test_r94_ppm_grayscale_conversion.py]
#   ledger_entry_path: reports/r90/product-code-change-ledger.json
```

## Changelog

- 1.0 (2026-06-02): Initial version
- 1.1 (2026-06-03): Added frontmatter, allowed/forbidden paths, rollback, changelog (Skills R99)
- 1.2 (2026-06-03): Added validation, transcript requirement, sample invocation (Skills R101).
- 1.3 (2026-06-21): Renamed "Spec-Literal Requirements" → "Mandatory QName Requirements"; added spec_qname and spec_fact_ref as explicit required handoff fields (TC-SKILL-HARDEN-001).
- 1.4 (2026-06-24): Added Step 0 knowledge registry lookup (hidden-puzzling-rain).
