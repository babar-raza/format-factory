# /python-reduced-spec-parity-model

**Skill ID:** python-reduced-spec-parity-model
**Registry Version:** 2.0
**Track:** foss_python
**Status:** active

## Purpose

Implement a reduced-scope spec-parity model for a Python FOSS format.
"Reduced" means a documented subset of the full spec is implemented,
with `spec_qname` present and a valid exception classification for
omitted spec concepts. This is NOT a free pass to omit spec fields.

## When to Use This Instead of spec-parity-source-regeneration-and-migration

Use this skill when:
- The format spec is large and full implementation is out of scope for this sprint
- A subset of spec concepts is sufficient for the target use case
- All omitted concepts are explicitly classified and documented

Do NOT use this skill to avoid spec-parity requirements entirely.

## Required Inputs

- `format_id` — format being implemented
- `spec_qname` — the root QName from the spec that this model covers
- `reduced_scope_rationale` — documented reason for reduced scope
- `exact_source_paths` — files to modify (must be pre-approved)
- `exact_test_paths` — test files
- `ledger_entry_path` — product code ledger entry

## Mandatory Validations

1. `product_code_ledger_validator` — ledger entry must pass
2. `spec_qname_present` — at least the root `spec_qname` must be set
3. `reduced_scope_documented` — `reduced_scope_rationale` must be non-empty
4. `focused_python_tests` — all tests must pass

## Evidence Requirements

- Source diff/patch showing spec_qname fields added
- Reduced scope rationale document
- Test log
- Ledger entry JSON

## Allowed Paths

- `src/python/<format>/` (declared exact_source_paths only)
- `tests/python/<format>/` (declared exact_test_paths only)
- `reports/r90/product-code-change-ledger.json`
- `.local/evidences/<run_id>/`

## Forbidden Paths

- No edits outside `exact_source_paths` and `exact_test_paths`
- No use as a bypass to omit spec-parity requirements without documented rationale
- No Gate 11 commercial paths

## Stop Conditions

- Stop if `spec_qname` (root) is not set in the model
- Stop if `reduced_scope_rationale` is empty or missing
- Stop if any test in `exact_test_paths` fails
- Stop if `product_code_ledger_validator` exits non-zero

## Omitted Concept Classification

Each omitted spec concept must be classified as one of:
- `FOSS_REDUCED_SCOPE_V1` — within known FOSS scope reduction
- `REQUIRES_GATE_11` — needs commercial authorization
- `NOT_APPLICABLE` — spec concept not relevant to Python binding
