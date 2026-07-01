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
