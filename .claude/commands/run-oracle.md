---
version: "1.0"
last-updated: "2026-06-26"
phase-available: "all"
gate-required: null
created-by: TC-LA-010
spec_qname_required: "false"
product_track: "oracle_execution"
---

# /run-oracle

Execute the Format Factory product conformance oracle for one or more formats.

The oracle compares product behavior against authoritative reference implementations
(LibreOffice for ODF formats, Python stdlib for CSV/TSV/NDJSON/ZST) and emits
PASS/FAIL verdicts per case.

## Prerequisites

1. **Oracle package must exist** — `oracle/formats/<format_id>/oracle-package.yaml` must be present
2. **Samples must exist** — `samples/by-format/<format_id>/` must have the referenced corpus files
3. **Product must be importable** — the format's Python library must be importable from `src/python/` or installed

## Handoff Fields (required in execution context)

| Field | Description |
|---|---|
| `format_id` | Lowercase format identifier (e.g. `csv`, `tsv`, `ndjson`, `zst`) |
| `profile` | Optional — filter to a specific oracle profile (e.g. `PARSE_VALIDITY`) |
| `case_id` | Optional — run a single case only |

## Execution Command

```bash
# Run all cases for a format
python tools/oracle/execute_oracle.py --format <format_id>

# Run a specific profile
python tools/oracle/execute_oracle.py --format <format_id> --profile PARSE_VALIDITY

# Run a specific case
python tools/oracle/execute_oracle.py --format <format_id> --case <case_id>
```

## Supported Formats (as of 2026-06-26)

| Format | Oracle Package | Reference Authority | Cases |
|---|---|---|---|
| csv | oracle/formats/csv/oracle-package.yaml | RFC 4180 | 5/5 PASS |
| zst | oracle/formats/zst/oracle-package.yaml | RFC 8878 + facebook/zstd | 6/6 PASS |
| fods | oracle/formats/fods/oracle-package.yaml | LibreOffice | 7/8 PASS |
| tsv | oracle/formats/tsv/oracle-package.yaml | Python stdlib csv (excel-tab) | 4/4 PASS |
| ndjson | oracle/formats/ndjson/oracle-package.yaml | Python stdlib json | 4/4 PASS |

## Output

- Verdict files written to `.local/oracle/<format_id>/verdicts/` (gitignored)
- Run summary written to `oracle/formats/<format_id>/reports/oracle-run-summary.json` (committed)

## Mandatory Validations (post-execution)

- **oracle_all_pass**: After execution, `oracle-run-summary.json` must show `verdict: ALL_PASS`
  or `verdict: PARTIAL_PASS` with documented tolerated failures
- **no_blocked_missing_authority**: No cases may have `result: BLOCKED_MISSING_AUTHORITY`
  unless the authority gap is documented in the oracle package's `authority_summary`
- **verdict_file_exists**: At least one verdict file must exist in `.local/oracle/<format_id>/verdicts/`

## SAL Integration Note

For stdlib-backed formats (CSV, TSV, NDJSON, ZST), oracle authorized_fact_refs must
reference FACT-IDs from `sal-facts-latest.json`. As of 2026-06-26, 14,441 facts are
present. Use `/ingest-spec-sal` to add facts for formats with zero spec_facts.

## Adding Oracle Support for a New Format

1. Create `oracle/formats/<format_id>/oracle-package.yaml` — use tsv or ndjson as template
2. Add `execute_<format_id>_valid_case()` to `tools/oracle/execute_oracle.py`
3. Wire in the format dispatch block (lines ~1000+ of execute_oracle.py)
4. Add `authorized_fact_refs` pointing to FACT-IDs from sal-facts-latest.json
5. Run this skill to verify ALL_PASS or PARTIAL_PASS

## Required Inputs

- `format_id` — format identifier from the format registry

## Allowed Paths

- `tools/oracle/execute_oracle.py`
- `oracle/formats/`
- `reports/` — evidence output (write)

## Forbidden Paths

- `src/**` — no product source mutation during oracle execution
- `plans/strategic/**` — strategic plans are read-only

## Stop Conditions

- Stop if the skill's mandatory validations cannot be completed
- Stop if any required input field is missing or invalid

## Output Format

- Structured result written to `reports/` in YAML or JSON format
- Human-readable summary printed to stdout
- Verdict: PASS / FAIL with per-item evidence
