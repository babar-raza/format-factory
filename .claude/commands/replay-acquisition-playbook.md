---
version: "1.0"
last-updated: "2026-07-01"
phase-available: "all"
gate-required: null
created-by: FF-PLAYBOOK-SYSTEM-001
spec_qname_required: "false"
product_track: "playbook_governance"
---

# /replay-acquisition-playbook

Dry-run replay of YAML acquisition playbook. Modes: validate, dry-run, explain, export-review-queue. Informational only. Does not approve gates.

**WARNING: Replay does NOT approve gates and does NOT satisfy DEC-034. Apply mode is NOT implemented.**

## What It Does

1. Loads and validates the acquisition playbook
2. Replays steps in dry-run mode (no file writes, no side effects)
3. Explains step logic and decision points
4. Exports review queue for human inspection

## Usage

```bash
python tools/playbook/replay_acquisition_playbook.py \
  --playbook-path <path> \
  --mode dry-run | validate | explain | export-review-queue
```

## Layer

Playbook Governance (FF-PLAYBOOK-SYSTEM-001, S-F2F-03)

## Allowed Paths

- `tools/playbook/replay_acquisition_playbook.py`
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
