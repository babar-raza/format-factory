# AI Usage Summary — {{SPRINT_ID}}

**Sprint:** {{SPRINT_ID}}
**Date:** {{DATE}}
**Run ID:** {{RUN_ID}}

## Usage Summary

| Metric | Value |
|--------|-------|
| Total AI calls | {{TOTAL_CALLS}} |
| Models used | {{MODELS}} |
| Purpose categories | {{PURPOSES}} |
| Total tokens (est.) | {{TOTAL_TOKENS}} |

## Call Log Summary

| # | Timestamp | Model | Purpose | Status | Validated |
|---|-----------|-------|---------|--------|-----------|
| 1 | {{TS}} | {{MODEL}} | {{PURPOSE}} | {{STATUS}} | {{VALIDATED}} |

## Validation Summary

- All AI outputs validated against source: {{YES_NO}}
- Secrets policy: no API keys or tokens in committed files
- Provenance: all AI-generated content cited in evidence declaration

## JSONL Log Location

- Local log: `.local/llm-logs/{{SPRINT_ID}}.jsonl` (not committed)
- Required fields per AGENTS.md §H5: timestamp, sprint_id, lane_id, model, endpoint, purpose, inputs, outputs, status, validation, secret_safety, provenance_cited

## Notes

{{NOTES}}
