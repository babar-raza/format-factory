---
version: "2.0"
last-updated: "2026-06-24"
phase-available: "all"
gate-required: null
created-by: skill-governance-sync-plan
spec_qname_required: "true"
overflow_split_allowed: "false"
product_track: "foss_python_spec_domain"
---

# /add-analytics-function

## STATUS: SUSPENDED (2026-06-18)

The arithmetic analytics rotation (mod/times functions) is **SUSPENDED**.
Do NOT add new `{format}_*_mod_*_times_*` functions.

This skill may ONLY be used for **spec-backed domain analytics** — functions computing
meaningful document metrics grounded in a spec element (page count, shape density, etc.).
Arithmetic-only formulas are permanently prohibited.

---

Add one spec-backed analytics function to a spec-owned domain module
at `src/python/<format_id>/<spec_domain_module>.py`.

All analytics functions MUST reside in a spec-owned domain module with a `spec_qname`
attribute. MUST NOT be added to codec files, parser files, `neutral_model.py`, or any
file named `analytics.py`, `*_analytics.py`, `*_analytics_extra.py`, `*_extra.py`, or
`*_misc.py`. V50 (MODULE-NAME-001) blocks any sprint that creates or modifies these
forbidden file patterns.

## Prerequisites (ALL required before any work)

1. **Gap-ledger entry MUST exist** — `reports/capability-layer/gap-ledger.json` must have a
   `GAP-*` entry for this capability. No gap entry = no analytics function.
2. **Spec fact reference MUST exist** — function must trace to a `FACT-<FORMAT>-*` entry
   in `.local/sal-output/sal-facts-latest.json`. Declare `spec_fact_ref` in function docstring.
3. **Target module must be spec-owned** — target file MUST have a `spec_qname` module-level
   attribute. Target file MUST NOT match any forbidden pattern (see below).
4. **LOC cap must not be exceeded** — RULE-AM-003 blocks if target file is at `baseline_loc_cap`.

## Forbidden Target Files (MODULE-NAME-001 — HARD BLOCK)

The following file patterns are PERMANENTLY FORBIDDEN as targets:

- `analytics.py` — generic analytics bucket (V50 blocks)
- `*_analytics.py` — format-prefixed analytics bucket (V50 blocks)
- `*_analytics_extra.py` — overflow bucket (V50 blocks)
- `*_extra.py` — generic bucket (V50 blocks)
- `*_misc.py` — convenience grouping (V50 blocks)
- `*_codec.py` — codec/parser file (wrong location, at cap)
- `*_parser.py` — parser file (wrong location, at cap)
- `neutral_model.py` — model file (wrong location, at cap)

**When a domain module reaches `baseline_loc_cap`: STOP.**
Do NOT create an overflow file. Create a spec-level segregation taskcard instead.
Overflow splits are FORBIDDEN. `overflow_split_allowed: false`.

## Required Inputs

- `format_id` — target format (e.g., `toml`, `abw`, `csv`)
- `function_name` — exact Python function name following naming convention
- `target_module` — path to spec-owned domain module (e.g., `config_document.py`)
- `spec_fact_ref` — FACT-* reference from sal-facts-latest.json (REQUIRED)
- `gap_ledger_ref` — GAP-* reference from gap-ledger.json (REQUIRED)
- `formula` — computation description (used for docstring and test generation)
- `expected_values` — list of 3 `{sample_file, expected}` pairs referencing files in `samples/by-format/<format_id>/`

## Steps

1. **Target validation:** Resolve target file as `src/python/<format_id>/<target_module>`.
   Verify the file has a `spec_qname` module-level attribute. If the file does not exist,
   create it with `spec_qname`, `spec_fact_ref`, and `namespace_uri` attributes.
   If `target_module` matches any forbidden pattern → stop with `BLOCKED_FORBIDDEN_TARGET`.
   If `current_loc >= baseline_loc_cap` → stop with `BLOCKED_LOC_CAP_EXCEEDED`.

2. **Prime collision check:** Search the target domain module (and the codec file where
   grandfathered functions may exist) for `prime_used`. If the prime already appears → stop
   with `BLOCKED_PRIME_COLLISION: prime <prime_used> already used in this format`.

3. **Sample file existence check:** Verify all 3 sample files exist under
   `samples/by-format/<format_id>/`. If any are missing → stop with
   `BLOCKED_MISSING_SAMPLE: <file_path>`.

4. **Implement the function:** Add the analytics function to
   `src/python/<format_id>/<target_module>`. Add the function name to `__all__` (if present)
   and ensure re-export via the consumer file's `from .<target_module> import *` block.

5. **Verify expected values:** Run the function against all 3 sample files and compare
   to `expected_values`. If any result does not match → stop with
   `BLOCKED_EXPECTED_VALUE_MISMATCH: <sample_file> expected=<E> got=<G>`.

6. **Create and run tests:** Create `tests/python/deepening/test_r<N>_<format>_deepening.py`
   with ≥10 test cases covering normal values, boundary inputs, and docstring assertions.
   Run `.venv/Scripts/pytest tests/python/deepening/test_r<N>_<format>_deepening.py -v`.
   All tests must pass. If any fail → fix the function or tests before proceeding.

7. **Write ledger entry and transcript:** Append a ledger entry to
   `reports/r90/product-code-change-ledger.json` with fields: `skill_used:
   "/add-analytics-function"`, `format_id`, `function_name`, `prime_used`,
   `changed_files`, `test_file`, `test_count`, `verdict: "PASSED"`.
   Emit a skill invocation transcript JSON to `reports/skills-r<N>/skill-transcripts/`
   with: `skill_id`, `format_id`, `function_name`, `changed_files`, `test_results`,
   `ledger_entry_id`, `verdict`.

## Allowed Paths

- `src/python/<format_id>/<spec_domain_module>.py` (extend — must have `spec_qname`)
- `src/python/<format_id>/__init__.py` (add export only)
- `tests/python/deepening/test_r<N>_<format>_deepening.py` (create)
- `reports/r90/product-code-change-ledger.json` (append ledger entry)
- `reports/skills-r<N>/skill-transcripts/` (create transcript)

## Forbidden Paths

- `src/python/<format_id>/analytics.py` (FORBIDDEN — V50 blocks)
- `src/python/<format_id>/<format_id>_analytics.py` (FORBIDDEN — V50 blocks)
- `src/python/<format_id>/<format_id>_analytics_extra.py` (FORBIDDEN — V50 blocks)
- `src/python/<format_id>/<format_id>_codec.py` (WRONG LOCATION — at cap)
- `src/python/<format_id>/<format_id>_parser.py` (WRONG LOCATION — at cap)
- `src/python/<format_id>/neutral_model.py` (WRONG LOCATION — at cap)
- `src/net/**` (wrong track)
- `registry/format-registry.yaml` (gate authority)
- `plans/master-plan.md` (operational authority)
- `registry/source-structure-baseline.json` (frozen caps — do NOT modify)

## Stop Conditions

- `BLOCKED_FORBIDDEN_TARGET` — target file matches a forbidden module name pattern
- `BLOCKED_NO_SPEC_QNAME` — target file does not have `spec_qname` attribute
- `BLOCKED_LOC_CAP_EXCEEDED` — target file is at or over `baseline_loc_cap`
- `BLOCKED_PRIME_COLLISION` — `prime_used` already appears in target or codec file
- `BLOCKED_MISSING_SAMPLE` — one or more required sample files not found
- `BLOCKED_EXPECTED_VALUE_MISMATCH` — function output does not match `expected_values`
- `BLOCKED_WRONG_TARGET` — any attempt to add the function to a codec/parser/neutral_model

## Output Format

Report: `skill_id`, `format_id`, `function_name`, `prime_used`, `target_file`
(`src/python/<format_id>/<spec_domain_module>.py`), `changed_files`, `test_file`,
`test_count`, `ledger_entry_path`, `transcript_path`, commands run, pass/fail results
for each step, and any stop condition triggered.

## Validation

The command is complete only when ALL of the following pass:
1. Function exists in spec-owned domain module with `spec_qname` and is exported
2. All 3 expected values match
3. `.venv/Scripts/pytest tests/python/deepening/test_r<N>_<format>_deepening.py -v` → 0 failures
4. Ledger entry present in `reports/r90/product-code-change-ledger.json`
5. Transcript JSON present in `reports/skills-r<N>/skill-transcripts/`

## Rollback

1. Remove the added function from the target domain module
   (if the file was created new, delete it entirely)
2. Remove the corresponding export from `__init__.py`
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
#   function_name: toml_nested_table_depth
#   formula: max depth of nested TOML tables
#   spec_fact_ref: FACT-TOML-042
#   gap_ledger_ref: GAP-TOML-DEPTH-001
#   expected_values:
#     - {sample_file: "samples/by-format/toml/simple.toml", expected: 1}
#     - {sample_file: "samples/by-format/toml/nested.toml", expected: 3}
#     - {sample_file: "samples/by-format/toml/array.toml", expected: 2}
#   target_module: config_document.py  (spec-owned domain module with spec_qname)
#   ledger_entry_path: reports/r90/product-code-change-ledger.json
#   focused_test_command: .venv/Scripts/pytest tests/python/deepening/test_r<N>_toml_deepening.py -v
```

## Changelog

- 1.0 (2026-06-18): Initial governed command for §24.7-compliant analytics function addition.
- 1.1 (2026-06-22): Added SUSPENDED status, spec_qname_required, overflow_split_allowed.
- 2.0 (2026-06-24): **BREAKING** — Removed `analytics.py` as mandatory target. All references
  to `analytics.py` replaced with spec-owned domain module. Forbidden targets now include
  `analytics.py`, `*_analytics.py`, `*_analytics_extra.py`, `*_extra.py`, `*_misc.py`.
  `product_track` changed from `foss_python_analytics` to `foss_python_spec_domain`.
  Sample invocation updated to use `config_document.py` instead of `analytics.py`.
  Added `BLOCKED_FORBIDDEN_TARGET` and `BLOCKED_NO_SPEC_QNAME` stop conditions.
