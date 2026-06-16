# Taskcard: AI-USAGE-LEDGER-AND-METRICS

**Status:** completed
**Created:** 2026-05-13

## Purpose

Ensure AI calls are logged, summarized, and auditable for every sprint that uses AI for repo-changing work. Maintain an AI usage ledger so usage patterns and costs can be reviewed.

## Scope

- Establish `.local/llm-logs/` JSONL logging convention (local only)
- Create sprint summary report template at `reports/ai/ai-usage-summary-<sprint-id>.md`
- Define required JSONL fields (per docs/ai-usage-operating-model.md)
- Create tooling or template for log generation (optional, if useful)
- Review and validate existing log format in `.local/llm-logs/` (if any)

## Non-Goals

- Building a full metrics dashboard
- Committing raw JSONL logs to repo (local only)
- Changing existing AGENTS.md §H logging rules

## Acceptance Criteria

- [ ] JSONL log format documented and consistent with AGENTS.md §H5 and docs/ai-usage-operating-model.md
- [ ] Sprint summary report template created at `reports/ai/ai-usage-summary-template.md`
- [ ] Log fields validated: timestamp, sprint_id, lane_id, model, endpoint, purpose, inputs, outputs, status, validation, secret_safety, provenance_cited
- [ ] `.local/llm-logs/` confirmed in .gitignore
- [ ] At least one example entry per sprint type (implementation, review, summarization)

## Evidence Requirements

- Template file existence
- .gitignore verification
- Example log entry reviewed

## Files Allowed

- reports/ai/ai-usage-summary-template.md (create)
- .gitignore (verify, not modify)

## Prohibited Actions

- No committing raw JSONL logs
- No adding API keys or tokens to committed files

## Validation Required

- .gitignore check for `.local/llm-logs/`
- JSONL format consistency with existing docs

## Next Dependency

- AI-VALIDATION-GATES (parallel)
- Any AI-assisted implementation sprint (uses this log format)
