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
