# Skills R101 Wave 0 — Preflight Report

Sprint: FORMAT-FACTORY-SKILLS-R101-GOVERNED-EXECUTION-MULTI-WAVE-SKILL-FACTORY-CAMPAIGN-001
Generated: 2026-06-03

## Skill Registry State

- Registry: `.supervisor/skill-registry.yaml` (r98-governed-skills-expanded)
- Status: active_fail_closed
- Total skills: 20 (13 active, 7 draft)
- Global controls: source_edits_require_explicit_handoff=true, exact_path_scope_required=true

## Registry Validation

- Tool: `tools/supervisor/validate_skill_registry.py --json`
- Result: **PASS** — 13 READY, 5 DRAFT, 2 new DRAFT (validate-product-code-ledger, validate-skill-transcript)
- 5 warnings: draft command files not found (expected)

## Command Files State

- Directory: `.claude/commands/`
- Total files: 19 (18 skill commands + 1 _readme)
- Validator: `tools/supervisor/validate_claude_commands.py` (NEW — Train C)
- Baseline result: **FAIL** — 7 passing, 11 failing
- Common gaps: allowed_paths (8), forbidden_paths (8), rollback (11), transcript_requirement (17), sample_invocation (11)

## Ledger Validation

- Tool: `tools/supervisor/validate_product_code_ledger.py --ledger reports/r90/product-code-change-ledger.json`
- Result: **PASS**

## Existing Validator Tests

- `tests/python/supervisor/` — 37 tests, all passing
- NEW: `test_validate_claude_commands.py` — 12 tests, all passing

## Quota Baseline

| Quota | Target | Baseline | Gap |
|---|---|---|---|
| Skills audited | 18+ | 20 | MET |
| Skills hardened | 10+ | 0 | 10+ needed |
| Validators | 5 | 3 existing + 1 new | 1 more needed |
| Transcripts | 10+ | 0 | 10+ needed |
| Anti-bypass demos | 2+ | 0 | 2+ needed |
