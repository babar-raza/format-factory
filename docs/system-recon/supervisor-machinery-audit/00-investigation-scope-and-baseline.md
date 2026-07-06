# 00 - Investigation Scope and Baseline

## Investigation Identity

| Field | Value |
|---|---|
| Canonical Directory | `docs/system-recon/supervisor-machinery-audit/` |
| Branch | `main` |
| HEAD Commit | `6b3f6f07` |
| Date | 2026-07-06 |
| Prior Recon | `docs/system-recon/FF-DEEP-RECON-20260705-052931/` (7 files, 25 claims) |
| Platform | Windows 11 Pro 10.0.26200 |
| Shell | Git Bash |
| Investigator | Claude Opus 4.6 |

## Working-Tree State at Investigation Start

Pre-existing modified files (preserved, not touched):

- `.supervisor/skill-idempotency-proof.yaml` (M)
- `reports/acceleration-product-first/ai-usage-ledger.jsonl` (M)
- `reports/autonomous-orchestrator/next-action-generation/generation-trace.json` (M)
- `reports/concurrency/pilot-evidence/pilot-01..10-result.json` (M, 10 files)
- `reports/governance/pilots/pilot-01..12-result.json` (M, 12 files)
- `reports/superpowers-agentic-autonomy/execution-state.json` (M)
- `reports/tri-lane-integration-refresh/latest-input-selection.json` (M)
- `.runner_system_id` (untracked)
- `docs/system-recon/` (untracked — prior recon)

No files were modified, stashed, reset, or deleted during this investigation.

## Repository Scale

| Metric | Count | Method |
|---|---|---|
| Tracked files | 15,731 | `git ls-files \| wc -l` |
| `.py` files | ~4,165 | `git ls-files '*.py' \| wc -l` |
| `.cs` files | 173 | `find src/net -name '*.cs' \| wc -l` |
| `.md` files | ~4,798 | `git ls-files '*.md' \| wc -l` |

## Primary Hypothesis Under Investigation

> A prior assessment claimed that supervisor machinery is approximately 81K lines while product code is approximately 72K lines. Treat this as unverified.

## Scope

This investigation covers:

1. Whether the 81K:72K measurements are reproducible
2. Whether "machinery" and "product" were classified consistently
3. Whether the ratio reflects justified governance or accidental growth
4. Which guarantees the machinery provides
5. Which parts are duplicated, obsolete, generated, unreachable, transitional, misplaced, or overcomplicated
6. Whether consolidation would improve maintainability without weakening correctness

## What is NOT in Scope

- Execution of the consolidation plan (investigation only)
- Full test suite execution (read-only investigation)
- .NET compilation or runtime verification
- Remote service access
- Production code modification

## Classification Framework

Every relevant tracked file is classified into exactly one of 16 categories:

| # | Category | Description |
|---|---|---|
| 1 | `product_runtime` | Product libraries shipped to users (src/python/, src/net/) |
| 2 | `supervisor_orchestration` | Autonomous loop, sprint execution, continuation, repair |
| 3 | `governance_validation` | Governance validators, anti-skip, authority checks |
| 4 | `spec_acquisition` | SAL, spec normalization, QName mapping |
| 5 | `capability_planning` | Capability compilation, gap ledger, task selection |
| 6 | `source_generation` | Code generation, template expansion, libforge |
| 7 | `shared_infrastructure` | Utilities, backends, MCP bridge, control index |
| 8 | `tests` | Test files (tests/ directory) |
| 9 | `fixtures_test_data` | Sample files, test fixtures |
| 10 | `schemas_config` | JSON schemas, YAML config, registries |
| 11 | `committed_generated` | Generated files committed to version control |
| 12 | `examples` | Usage examples |
| 13 | `migration_compat` | Migration scripts, compatibility bridges |
| 14 | `executable_docs` | Documentation with executable content |
| 15 | `deprecated_archived` | Deprecated, archived, or superseded files |
| 16 | `evidence_processing` | Evidence grading, declaration, review packaging |
| 17 | `prompt_generation` | Worker prompt generation, supervisor packets |
| 18 | `state_management` | Continuation state, plan locks, ledgers |
| 19 | `ai_integration` | LLM/AI integration, embedding retrieval |
| 20 | `unknown` | Insufficient evidence to classify |

Note: Categories 16-19 were added to the original 16 because the machinery investigation revealed distinct responsibility clusters within the supervisor that warrant separate tracking.

## Excluded From LOC Counts

- Build output (`build/`, `dist/`)
- Virtual environments (`.venv/`)
- `__pycache__/` directories
- Egg-info metadata directories
- Downloaded dependencies
- `.local/` (gitignored ephemeral state)

## Measurement Method

All LOC counts use physical lines (including blanks and comments):
```
find <dir> -name "*.py" -not -path "*/__pycache__/*" -exec cat {} + | wc -l
```
This method avoids `xargs` argument-limit truncation on Windows Git Bash.

## Evidence Files

| File | Description |
|---|---|
| `evidence/metrics.json` | All LOC counts with commands and commit |
| `evidence/file-classification.csv` | Per-file category assignment |
| `evidence/component-register.csv` | Component-level classification |
| `evidence/commands-and-results.md` | All commands run during investigation |
