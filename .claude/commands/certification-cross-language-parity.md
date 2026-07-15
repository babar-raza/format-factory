---
version: "1.0"
last-updated: "2026-07-13"
phase-available: "all"
gate-required: null
created-by: TC-007-precious-wandering-lighthouse
spec_qname_required: "false"
product_track: "governance"
---

# /certification-cross-language-parity

Check cross-language (Python/dotnet) API parity for a certified format.

## What It Does

1. Reads Python and .NET API contract reports for the format
2. Compares function signatures, return types, and parameter names
3. Produces a parity report with PASS/PARTIAL/FAIL per contract

## Usage

```bash
python tools/certification/cross_language_parity_checker.py \
  --format fods \
  --output reports/certification/fods/cross-language-parity.json
```

## Required Handoff Fields

- `format_id`: The format to check (e.g. `fods`, `csv`)

## Output Contract

Writes `reports/certification/<format_id>/cross-language-parity.json`:
```json
{
  "format_id": "fods",
  "verdict": "PASS | PARTIAL | FAIL",
  "functions": [{"name": "load_fods", "python_sig": "...", "dotnet_sig": "...", "match": true}]
}
```

## Idempotency Contract

Same API contract inputs → same parity report. Output file is overwritten, not appended.

## Error Handling

- Missing Python or .NET report: records `"verdict": "MISSING_INPUT"` in output.
- Format not certified: exit 1 with `FORMAT_NOT_CERTIFIED`.

## Parity Note

PARTIAL parity: command file expanded with output contract and idempotency.
Full 20-dimension quality grading deferred to SKILL-QUALITY-004.
Repair: TC-SFE3-FU-002 (2026-07-15).
