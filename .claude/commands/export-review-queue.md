---
version: "1.0"
last-updated: "2026-07-01"
phase-available: "all"
gate-required: null
created-by: FF-PLAYBOOK-SYSTEM-001
spec_qname_required: "false"
product_track: "playbook_governance"
---

# /export-review-queue

Export review queue YAML from dry-run replay report. Read-only. Writes output only to --output path.

**READ-ONLY: Review queue cannot approve gates.**

## What It Does

1. Reads a dry-run replay report
2. Extracts review queue items
3. Writes formatted YAML to the specified output path

## Usage

```bash
python tools/playbook/export_review_queue.py \
  --replay-report-path <path> \
  --output <output-path>
```

## Layer

Playbook Governance (FF-PLAYBOOK-SYSTEM-001, S-F2F-03)

## Allowed Paths

- `tools/playbook/export_review_queue.py`
- `reports/` — evidence output (write)

## Forbidden Paths

- `src/net/**` — no .NET product source mutation
- `src/python/**` — no Python product source mutation
- `plans/strategic/**` — strategic plans are read-only

## Stop Conditions

- Stop if the skill's mandatory validations cannot be completed
- Stop if the output file path is not writable

## Output Format

- Structured result written to `reports/` in YAML or JSON format
- Human-readable summary printed to stdout
- Verdict: PASS / FAIL with per-item evidence
