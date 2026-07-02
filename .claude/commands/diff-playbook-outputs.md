---
version: "1.0"
last-updated: "2026-07-01"
phase-available: "all"
gate-required: null
created-by: FF-PLAYBOOK-SYSTEM-001
spec_qname_required: "false"
product_track: "playbook_governance"
---

# /diff-playbook-outputs

Compare two dry-run replay reports. Read-only, no file writes unless --output specified. Diff output is informational only.

## What It Does

1. Loads two dry-run replay reports (report A and report B)
2. Computes structured diff of step outcomes, decision paths, and evidence
3. Reports additions, removals, and changes
4. Optionally writes diff to --output path

## Usage

```bash
python tools/playbook/diff_playbook_outputs.py \
  --report-a <path-a> \
  --report-b <path-b> \
  [--output <output-path>]
```

## Layer

Playbook Governance (FF-PLAYBOOK-SYSTEM-001, S-F2F-03)

## Allowed Paths

- `tools/playbook/diff_playbook_outputs.py`
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
