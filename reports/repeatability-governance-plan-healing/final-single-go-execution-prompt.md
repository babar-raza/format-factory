# Format Factory — Final Single-Go Execution Prompt
# Sprint: FORMAT-FACTORY-GOVERNANCE-REPEATABILITY-IDEMPOTENCY-CONTRACTS-001
# Plan file: C:\Users\prora\.claude\plans\humming-sauteeing-crown.md
# Date: 2026-06-08
# Status: EXECUTED — this file documents the execution prompt used

## MANDATORY FIRST ACTIONS (do not skip any)
1. Read reports/supervisor/session-resume.md
2. Read reports/supervisor/approval-gates.md
3. Read C:\Users\prora\.claude\plans\humming-sauteeing-crown.md IN FULL
4. Read AGENTS.md -- especially sections AE1, AE2, AD5, P1-P4

## STRICT SCOPE: GOVERNANCE LAYER ONLY
This sprint MUST NOT:
- Implement product source features
- Improve autonomous execution level
- Build queue dispatch infrastructure
- Call Qwen, ChatGPT, or any LLM for code generation
- Run product implementation pilots
- Implement the 10 validators (plan only)
- Use git checkout --, git reset, git restore, git clean, or git stash
- Commit or push code

## PHASE 0 -- Environment Discovery (before any writes)
Run each in order; record results in adaptation-log.md:

1. Python discovery:
   a. Try: python tools/supervisor/supervisor_loop.py --help
   b. If fail: try .local/venv/Scripts/python tools/supervisor/supervisor_loop.py --help
   c. If fail: try .local/venv/bin/python tools/supervisor/supervisor_loop.py --help
   d. Record: PYTHON_CMD = whichever worked
   Record: git status --short (baseline)

2. Test command discovery:
   a. Check if pytest is on PATH: pytest --version
   b. If not: try PYTHON_CMD -m pytest --version
   c. Try: .local/venv/Scripts/python -m pytest --version
   d. Record: PYTEST_CMD = whichever worked

3. Verify .local/evidences/autonomous-execution-spine/evidence-declaration.yaml exists
4. Verify .supervisor/project-memory.md exists
5. Check for external MEMORY.md (optional, do not fail if absent)

## PHASE 1 -- Create Directories
- mkdir reports/repeatability-governance-plan-healing/
- mkdir docs/governance/
- mkdir schemas/governance/
- mkdir taskcards/governance-repeatability/
- mkdir .local/attribution/gnumeric/ .local/attribution/tsv/ .local/attribution/abw/ .local/attribution/ndjson/

## PHASE 2 -- Preflight Review Doc
Write reports/repeatability-governance-plan-healing/preflight-repo-workflow-review.md

## PHASE 3 -- Write Governance Contracts
GR-TC-002: docs/governance/execution-method-taxonomy.md + schemas/governance/execution-method-taxonomy.schema.json
GR-TC-003: docs/governance/repeatability-contract.md
GR-TC-004: docs/governance/idempotency-contract.md
GR-TC-005: schemas/governance/product-mutation-evidence.schema.json
GR-TC-007: docs/governance/product-mutation-taskcard-state-machine.md + schemas/governance/product-mutation-taskcard-state-machine.schema.json
Additional: docs/governance/legacy-manual-backfill-policy.md

## PHASE 4 -- Write Governance Taskcards
Write taskcards/governance-repeatability/GR-TC-001.yaml through GR-TC-010.yaml

## PHASE 5 -- Legacy Backfill (sidecar-first)
Step 5a: Read source files (confirm function locations)
Step 5b: Compute 4 idempotency SHA-256 keys
Step 5c: Write 4 sidecar attribution files in .local/attribution/
Step 5d: Source comments -- SKIP (sidecar-only is sufficient)
Step 5e: Correct .supervisor/project-memory.md autonomous-execution-spine entry
Step 5f: Update .local/evidences/autonomous-execution-spine/evidence-declaration.yaml (add fields only)

## PHASE 6 -- Write Report Docs
GR-TC-001: plan-quality-review.md + healed-plan.md
GR-TC-008: validator-hardening-plan.md
GR-TC-009: autonomy-boundary-handoff.md
GR-TC-010: final-single-go-execution-prompt.md (this file)

## PHASE 7 -- State Ledger, Ownership Matrix, Adaptation Log
Write file-ownership-matrix.md, state-ledger-template.jsonl, state-ledger.jsonl, adaptation-log.md

## PHASE 8 -- Verification Run
1. git status --short (no unauthorized source logic changes)
2. Verify JSON schemas parse: python -c "import json; json.load(open(...))"
3. Verify taskcard YAMLs parse: python -c "import yaml; yaml.safe_load(open(...))"
4. Verify sidecar YAMLs parse
5. Verify state-ledger.jsonl has 10 rows

## PHASE 9 -- Evidence Declaration
run_id: governance-repeatability-contracts-001
Write: .local/evidences/governance-repeatability-contracts-001/evidence-declaration.yaml
Validate: python tools/supervisor/supervisor_loop.py validate-declaration --declaration ...

## PHASE 10 -- Evidence Bundle
Build: python tools/supervisor/build_declaration_review_package.py --declaration ...
Print absolute ZIP path
Run: python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration ...

## STOP CONDITIONS
- JSON/YAML schema fails syntax check: fix before continuing
- git diff shows logic changes in src/python/: STOP and report
- autonomous-cycle exit 3: fix declaration before bundle
- Do not commit, push, or approve gates
