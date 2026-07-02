---
version: "1.0"
last-updated: "2026-07-01"
phase-available: "all"
gate-required: null
created-by: FF-PLAYBOOK-SYSTEM-001
spec_qname_required: "false"
product_track: "playbook_governance"
---

# /validate-playbook

Validate YAML acquisition playbook or review queue against its JSON Schema. Read-only, no file writes, no apply mode. PASS is not gate approval.

**READ-ONLY: PASS does NOT approve gates. Evidence aid only.**

## What It Does

1. Loads the YAML playbook or review queue file
2. Validates against the JSON Schema
3. Reports schema violations with field-level detail
4. Exits 0 on PASS, 1 on FAIL, 2 on error

## Usage

```bash
python tools/playbook/validate_playbook.py --playbook-path <path>
```

## Layer

Playbook Governance (FF-PLAYBOOK-SYSTEM-001)

## Allowed Paths

- `tools/playbook/validate_playbook.py`
- `reports/` — evidence output (write)

## Forbidden Paths

- `src/net/**` — no .NET product source mutation
- `src/python/**` — no Python product source mutation
- `plans/strategic/**` — strategic plans are read-only

## Stop Conditions

- Stop if the skill's mandatory validations cannot be completed
- Stop if any required input field is missing or invalid

## Output Format

- PASS / FAIL / PARTIAL verdict printed to stdout
- Per-item findings list with skill_id, issue, and severity
- Report file at `reports/` with structured YAML findings
