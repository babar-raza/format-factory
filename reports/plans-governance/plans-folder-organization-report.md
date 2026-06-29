# Plans Folder Organization Report

**Mission ID:** FF-PLAN-GOV-002
**Date:** 2026-06-29
**Plan File:** plans/.claude/dapper-bouncing-scott.md

---

## Initial State

- **19 .md files** at `plans/` root
- **2 allowed:** `master-plan.md`, `master-plan-memory.md`
- **17 unauthorized:** strategic plans, healing plans, historical addenda

## Relocations (17 files)

| # | File | Destination | Method |
|---|------|-------------|--------|
| 1 | spec-to-feature-radical-correction-plan.md | plans/strategic/ | git mv |
| 2 | snoopy-juggling-seal.md | plans/strategic/ | git mv |
| 3 | capability-fact-to-feature-production-plan.md | plans/strategic/ | git mv |
| 4 | continuation-isolation-plan.md | plans/strategic/ | git mv |
| 5 | enhanced-qname-python-governed-plan.md | plans/healing/ | git mv |
| 6 | oracle-layer-hardening-addendum.md | plans/healing/ | git mv |
| 7 | oracle-backfill-wave6.md | plans/healing/ | git mv |
| 8 | product-code-healing-plan.md | plans/healing/ | git mv |
| 9 | format-factory-zero-stub-production-hardening-plan.md | plans/healing/ | git mv |
| 10 | portfolio-product-machinery-recon-and-healing-plan.md | plans/healing/ | mv (untracked) |
| 11 | csvr118-dotnet-failure-tracking-hardening.md | plans/healing/ | mv (untracked) |
| 12 | vivid-napping-kurzweil-hardening-addendum.md | plans/secondary/ | git mv |
| 13 | generic-soaring-chipmunk-hardening-addendum.md | plans/secondary/ | git mv |
| 14 | floating-stargazing-globe-hardening-addendum-20260623.md | plans/secondary/ | git mv |
| 15 | cap-fact-forensics-repair-hardening-addendum.md | plans/secondary/ | git mv |
| 16 | misty-hopping-token-hardening-addendum.md | plans/secondary/ | git mv |
| 17 | unified-multi-plan-execution.md | plans/secondary/ | git mv |

## Reference Updates

| Scope | Files Updated | Patterns Replaced |
|-------|--------------|-------------------|
| CLAUDE.md (critical) | 1 | spec-to-feature (2), snoopy (2) |
| AGENTS.md (critical) | 1 | spec-to-feature (1) |
| docs/ governance | 9 | spec-to-feature, snoopy, product-code-healing |
| plans/master-plan.md | 1 | all 17 patterns |
| plans/master-plan-memory.md | 1 | snoopy, capability-fact |
| plans/layers/ | 6 | spec-to-feature, snoopy |
| plans/.claude/ | 2 | relocated plan cross-refs |
| Relocated plan internals | 6 | cross-references between relocated plans |
| Test files | 8 | snoopy, capability-fact paths |
| Supervisor tools/config | 6 | snoopy, spec-to-feature |
| MEMORY.md | 1 | spec-to-feature (2) |
| reports/ (batch) | ~50+ | all 17 patterns (best-effort) |

## Subfolder Model

| Subfolder | Purpose | File Count |
|-----------|---------|------------|
| strategic/ | High-authority strategic/governance plans | 4 |
| healing/ | Repair, hardening, backfill plans | 7 |
| secondary/ | Historical, superseded, archived | 6 |
| .claude/ | Per-chat execution plans | existing |
| layers/ | Layer governance (exempt) | existing |
| .governance/ | Plan governance metadata (NEW) | 2 |

## Governance Infrastructure Built

1. **V90 Validator** (`governance_validators_ext2.py`): Detects unauthorized files at `plans/` root. Returns WARN for violations, PASS when clean.
2. **Plan Placement Tool** (`plan_placement.py`): `resolve_plan_destination()`, `validate_root_policy()`, `migrate_plan_locks()`.
3. **Routing Policy** (`plans/.governance/routing-policy.yaml`): Machine-readable route definitions.
4. **Path Migration Map** (`plans/.governance/path-migration-20260629.yaml`): All 17 old-to-new mappings.
5. **Rollback Script** (`.local/plans-rollback.sh`): Reverse git mv commands (not committed).

## V56 Regex Fix

V56's plan-path regex updated from `[^/\s]+\.md` to `(?:[^/\s]+/)?[^/\s]+\.md` to support subdirectory plan paths (e.g., `plans/strategic/snoopy-juggling-seal.md`).

## Test Results

| Suite | Result |
|-------|--------|
| V90 TestPlansRootPolicy (4 tests) | 4/4 PASS |
| test_plan_governance_gates.py (45 tests) | 45/45 PASS |
| test_plan_governance.py | PASS |
| test_plan_lock_machinery.py | PASS |

## Validator Results

```
V90 Run 1: PASS — plans/ root contains only master-plan.md and master-plan-memory.md
V90 Run 2: PASS — identical (idempotency confirmed)
validate_root_policy Run 1: compliant=True, violations=[]
validate_root_policy Run 2: compliant=True, violations=[] (identical)
```

## Plan Lock Migration

- 1 lock file migrated: `688d4a5de421-1a167018.json` (oracle-layer-hardening-addendum, SUPERSEDED status)

## Final Root Contents

```
plans/master-plan.md
plans/master-plan-memory.md
```

Exactly 2 files. Policy compliant.

## Idempotency Proof

Two consecutive runs of V90 and `validate_root_policy()` produced identical results with zero changes needed. The governance system is stable and idempotent.

## Verdict

**PLANS_FOLDER_CLEAN_GOVERNED_AUTOMATICALLY_ENFORCED_AND_IDEMPOTENT**
