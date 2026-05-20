# R37 Preflight and Lane Ownership

**Sprint:** FORMAT-FACTORY-R37-EVIDENCE-DEPTH-REPAIR-SELECTIVE-DEEPENING-AND-MATURITY-CLOSURE-001
**Date:** 2026-05-20
**Baseline:** R36 commit d51d4a4 + 3 AI-parallel commits (HEAD: 2f8e6fc)
**Run Number:** R37

## R36 Evidence-Depth Caveat

R36 (d51d4a4) is **accepted with evidence-depth caveat**: 19 of 32 metadata files in the R36 bundle contained only `placeholder: true` content. The R36 source work (registry corrections, deepening tests, alignment guards) is real and committed. The evidence-depth shortfall is in bundle metadata only.

**R37 decision: R36_EVIDENCE_DEPTH_SUPERSEDED_BY_R37** -- R37 incorporates R36 artifacts into its contract and adds the `placeholder: true` detection pattern to `validate_evidence_bundle.py` PENDING_MARKER_PATTERNS, preventing future recurrence.

## Dirty-State Classification

| Item | Classification | Action |
|------|---------------|--------|
| d5567ce (AI runner pipeline artifacts sync) | AI-parallel-out-of-scope | Preserve, do not modify |
| e5d0add (AI verification matrix sync) | AI-parallel-out-of-scope | Preserve, do not modify |
| 2f8e6fc (R35 clean runner closure test) | AI-parallel-out-of-scope | Preserve, do not modify |
| reports/ai/r35-clean-runner-closure-20260520/ | AI-parallel-out-of-scope | Untracked, ignore |
| reports/governance/r35-adversarial-review.md | AI-parallel-out-of-scope | Untracked, ignore |
| reports/verification/r35-independent-verification.md | AI-parallel-out-of-scope | Untracked, ignore |
| tools/evidence/contracts/r35-ai-*.yaml | AI-parallel-out-of-scope | Untracked, ignore |

## Lane Ownership

| Lane | Focus | Owner |
|------|-------|-------|
| 0 | Coordinator -- preflight, lane assignment | This report |
| A | R36 evidence-depth repair/supersession | R36_EVIDENCE_DEPTH_SUPERSEDED_BY_R37 |
| B | Evidence bundle quality guard hardening | test_r37_evidence_depth_guards.py (10 tests) |
| C | R36 registry/matrix/pack alignment IV | Background agent + R36 guard revalidation |
| D | Probe-format recovery decision packets | reports/r37/probe-format-recovery-decisions.md |
| E | ODS deepening | tests/python/ods/ |
| F | QOI deepening | tests/python/qoi/ |
| G | ZST deepening | tests/python/zst/ |
| H | FODS/FODT revalidation | .NET test revalidation |
| I | Matrix/registry/roadmap integration | registry/ updates |
| J | Full validation | All test suites |
| K | Reports + adversarial review + memory | reports/r37/, memory/ |
