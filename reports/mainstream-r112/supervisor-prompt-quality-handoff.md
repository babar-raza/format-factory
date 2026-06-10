# Supervisor Prompt-Quality Handoff

## From: Mainstream R112
## To: Supervisor Stream

## Defect: D112-PQFP-01 — no_wrong_stream false positive on governance commands

### Description
The `no_wrong_stream` check in the prompt-quality validator rejects ANY Mainstream prompt that contains `tools/supervisor/` references, including mandatory governance commands like `autonomous-cycle` and `validate_product_code_ledger.py`.

### Root Cause
The check uses a simple substring match for `tools/supervisor/` without an allowlist for governance command invocations. Every Mainstream sprint must invoke `tools/supervisor/supervisor_loop.py autonomous-cycle` for evidence submission, so this check will always fail for valid Mainstream prompts.

### Fix Location
The prompt-quality validator in `tools/supervisor/autonomous_cycle.py` (or whichever module implements the `no_wrong_stream` check).

### Recommended Fix
Add an allowlist of governance command patterns that should not trigger `no_wrong_stream`:
- `tools/supervisor/supervisor_loop.py autonomous-cycle`
- `tools/supervisor/validate_product_code_ledger.py`
- `tools/supervisor/build_declaration_review_package.py`
- `.local/supervisor/selected-product-gaps.json`

Only flag `tools/supervisor/` references that describe implementation work (editing, fixing, refactoring supervisor tools).

### Evidence
- Prompt-quality result: `.local/supervisor/reviews/mainstream-r111/prompt-quality-result.json`
- Generated prompt: `.local/supervisor/reviews/mainstream-r111/combined-next-worker-prompt.md`
- Classification: `reports/mainstream-r112/prompt-quality-classification.json`

### Impact
Every valid Mainstream sprint that correctly follows CLAUDE.md will fail prompt-quality because CLAUDE.md requires invoking supervisor tools for evidence submission.
