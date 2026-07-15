---
version: "1.0"
last-updated: "2026-07-13"
phase-available: "all"
gate-required: null
created-by: TC-007-precious-wandering-lighthouse
spec_qname_required: "false"
product_track: "governance"
---

# /certification-mutation-tester

Run mutation testing for a format and produce a kill-rate report.

## What It Does

1. Applies AST-level mutations to the format's source
2. Runs the format's test suite against each mutation
3. Reports kill rate (% mutations caught by tests)

## Usage

```bash
python tools/certification/mutation_tester.py \
  --format fods \
  --src-path src/python/fods \
  --test-path tests/python/fods \
  --output reports/certification/fods/mutation-baseline.json
```

## Required Handoff Fields

- `format_id`: The format to test (e.g. `fods`, `csv`)

## Output Contract

Writes `reports/certification/<format_id>/mutation-baseline.json`:
```json
{
  "format_id": "fods",
  "kill_rate": 0.87,
  "mutations_total": 45,
  "mutations_killed": 39,
  "verdict": "PASS | FAIL"
}
```

## Idempotency Contract

Same source + same tests → same kill rate (deterministic mutation set).
Output file is overwritten, not appended.

## Error Handling

- Missing test suite: exit 1 with `TEST_SUITE_NOT_FOUND`.
- Source parse failure: skip mutant, log `PARSE_ERROR`, continue.
- Runtime >10min: abort with `TIMEOUT` and partial results.

## Preservation Safety

AST mutations are applied to temp copies only. Source files are never permanently
modified. If temp copy fails to write, abort immediately.

## Parity Note

PARTIAL parity: command file expanded with output contract, idempotency, and
preservation safety. Full 20-dimension grading deferred to SKILL-QUALITY-004.
Repair: TC-SFE3-FU-002 (2026-07-15).
