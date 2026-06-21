---
version: "1.0"
last-updated: "2026-06-18"
phase-available: "all"
gate-required: null
created-by: skill-governance-sync-plan
spec_qname_required: "false"
product_track: "foss_python_analytics"
---

# /add-analytics-function

Add one formula-based analytics function to `src/python/<format_id>/analytics.py`.
Per master plan §24.7 (BINDING), all analytics functions MUST reside in a dedicated
`analytics.py` module and MUST NOT be added to codec files, parser files, or
`neutral_model.py`. RULE-AM-001 in `validate_source_architecture.py` blocks any sprint
that places analytics functions outside `analytics.py`.

## Required Inputs

- `format_id` — target format (e.g., `toml`, `abw`, `csv`)
- `function_name` — exact Python function name following naming convention
- `formula` — arithmetic expression (used for docstring and test generation)
- `prime_used` — the prime number in the formula (must NOT already appear in `analytics.py`)
- `expected_values` — list of 3 `{sample_file, expected}` pairs referencing files in `samples/by-format/<format_id>/`

## Steps

1. **LOC pre-check (§24.7 target):** Resolve target file as `src/python/<format_id>/analytics.py`.
   If the file does not exist, it will be created (0 LOC — never at cap, proceed to Step 2).
   If it exists, read `registry/source-structure-baseline.json` and look up `baseline_loc_cap`
   for this file. If `current_loc >= baseline_loc_cap` → stop immediately with
   `BLOCKED_LOC_CAP_EXCEEDED: src/python/<format_id>/analytics.py at cap`.
   Do NOT add the function to any codec file, parser file, or `neutral_model.py` —
   those are at or over their frozen caps and are the WRONG location per §24.7.

2. **Prime collision check:** Search `analytics.py` (and the codec file where grandfathered
   functions may exist) for `prime_used`. If the prime already appears → stop with
   `BLOCKED_PRIME_COLLISION: prime <prime_used> already used in this format`.

3. **Sample file existence check:** Verify all 3 sample files exist under
   `samples/by-format/<format_id>/`. If any are missing → stop with
   `BLOCKED_MISSING_SAMPLE: <file_path>`.

4. **Implement the function:** Add the analytics function to
   `src/python/<format_id>/analytics.py`. If the file does not exist, create it with
   the standard module header (`"""Analytics functions for <format_id> format."""`).
   Add the function name to `__all__` and add the corresponding `from .analytics import
   <function_name>` export in `src/python/<format_id>/__init__.py`.

5. **Verify expected values:** Run the function against all 3 sample files and compare
   to `expected_values`. If any result does not match → stop with
   `BLOCKED_EXPECTED_VALUE_MISMATCH: <sample_file> expected=<E> got=<G>`.

6. **Create and run tests:** Create `tests/python/deepening/test_r<N>_<format>_deepening.py`
   with ≥10 test cases covering normal values, boundary inputs, and docstring assertions.
   Run `python -m pytest tests/python/deepening/test_r<N>_<format>_deepening.py -v`.
   All tests must pass. If any fail → fix the function or tests before proceeding.

7. **Write ledger entry and transcript:** Append a ledger entry to
   `reports/r90/product-code-change-ledger.json` with fields: `skill_used:
   "/add-analytics-function"`, `format_id`, `function_name`, `prime_used`,
   `changed_files`, `test_file`, `test_count`, `verdict: "PASSED"`.
   Emit a skill invocation transcript JSON to `reports/skills-r<N>/skill-transcripts/`
   with: `skill_id`, `format_id`, `function_name`, `changed_files`, `test_results`,
   `ledger_entry_id`, `verdict`.

## Allowed Paths

- `src/python/<format_id>/analytics.py` (create or extend — §24.7 MANDATORY target)
- `src/python/<format_id>/__init__.py` (add export only)
- `tests/python/deepening/test_r<N>_<format>_deepening.py` (create)
- `reports/r90/product-code-change-ledger.json` (append ledger entry)
- `reports/skills-r<N>/skill-transcripts/` (create transcript)

## Forbidden Paths

- `src/python/<format_id>/<format_id>_codec.py` (WRONG LOCATION — violates §24.7; at cap)
- `src/python/<format_id>/<format_id>_parser.py` (WRONG LOCATION — violates §24.7; at cap)
- `src/python/<format_id>/neutral_model.py` (WRONG LOCATION — violates §24.7; at cap)
- `src/net/**` (wrong track)
- `registry/format-registry.yaml` (gate authority)
- `plans/master-plan.md` (operational authority)
- `registry/source-structure-baseline.json` (frozen caps — do NOT modify)

## Stop Conditions

- `BLOCKED_LOC_CAP_EXCEEDED` — `analytics.py` exists and is at or over `baseline_loc_cap`
- `BLOCKED_PRIME_COLLISION` — `prime_used` already appears in `analytics.py` or codec file
- `BLOCKED_MISSING_SAMPLE` — one or more required sample files not found
- `BLOCKED_EXPECTED_VALUE_MISMATCH` — function output does not match `expected_values`
- `BLOCKED_SPEC_QNAME_REQUIRED` — does NOT apply to this skill (`spec_qname_required: false`);
  analytics functions are domain-specific metadata statistics with no spec QName references
- `BLOCKED_WRONG_TARGET` — any attempt to add the function to a codec/parser/neutral_model
  file must be rejected; RULE-AM-001 will block it at autonomous-cycle anyway

## Output Format

Report: `skill_id`, `format_id`, `function_name`, `prime_used`, `target_file`
(`src/python/<format_id>/analytics.py`), `changed_files`, `test_file`, `test_count`,
`ledger_entry_path`, `transcript_path`, commands run, pass/fail results for each step,
and any stop condition triggered.

## Validation

The command is complete only when ALL of the following pass:
1. Function exists in `src/python/<format_id>/analytics.py` and is exported in `__init__.py`
2. All 3 expected values match
3. `python -m pytest tests/python/deepening/test_r<N>_<format>_deepening.py -v` → 0 failures
4. Ledger entry present in `reports/r90/product-code-change-ledger.json`
5. Transcript JSON present in `reports/skills-r<N>/skill-transcripts/`

## Rollback

1. Remove the added function from `src/python/<format_id>/analytics.py`
   (if the file was created new, delete it entirely)
2. Remove the corresponding `from .analytics import <function_name>` line from `__init__.py`
3. Delete the test file `tests/python/deepening/test_r<N>_<format>_deepening.py`
4. Remove the ledger entry from `reports/r90/product-code-change-ledger.json`
5. Remove the transcript JSON from `reports/skills-r<N>/skill-transcripts/`
6. Run `python tools/supervisor/validate_product_code_ledger.py` to confirm PASS after rollback

## Transcript Requirement

After execution, emit a skill invocation transcript JSON to
`reports/skills-r<N>/skill-transcripts/` with fields: `skill_id`, `format_id`,
`function_name`, `prime_used`, `target_file`, `changed_files`, `test_results`,
`expected_values_verified`, `ledger_entry_id`, `verdict`.

## Sample Invocation

```
/add-analytics-function
# Inputs provided by execution handoff:
#   format_id: toml
#   function_name: toml_file_size_mod_307_times_1100
#   formula: file_size % 307 * 1100
#   prime_used: 307
#   expected_values:
#     - {sample_file: "samples/by-format/toml/simple.toml", expected: 12100}
#     - {sample_file: "samples/by-format/toml/nested.toml", expected: 24200}
#     - {sample_file: "samples/by-format/toml/array.toml", expected: 3300}
#   target_file: src/python/toml/analytics.py  (§24.7-compliant target)
#   ledger_entry_path: reports/r90/product-code-change-ledger.json
#   focused_test_command: python -m pytest tests/python/deepening/test_r<N>_toml_deepening.py -v
```

## Changelog

- 1.0 (2026-06-18): Initial governed command for §24.7-compliant analytics function addition.
  Target is always `analytics.py` per master plan §24.7 BINDING rule. `spec_qname_required: false`
  because analytics functions compute domain-specific metadata statistics with no spec QName refs.
