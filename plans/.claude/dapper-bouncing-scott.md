# Plans Folder Cleanup, Governance, and Permanent Structure Control

## Context

The `plans/` directory root contains 19 .md files, but policy requires only 2 (`master-plan.md` and `master-plan-memory.md`). The other 17 files are strategic plans, hardening addenda, healing plans, and historical artifacts that belong in subfolders. This plan reorganizes the folder, updates all references, builds a governance validator (V90), creates a plan-placement tool, and proves idempotency.

**Mission ID:** `FF-PLAN-GOV-002`

---

## Wave 0: Inventory & Baseline

### TC-PG2-001: Capture baseline snapshot
- Record current `plans/` tree (19 root files, 5 subfolders)
- Record git HEAD revision
- Capture list of all root files with sizes

**Root files to relocate (17):**

| # | File | Destination | Category |
|---|------|-------------|----------|
| 1 | `spec-to-feature-radical-correction-plan.md` | `plans/strategic/` | strategic |
| 2 | `snoopy-juggling-seal.md` | `plans/strategic/` | strategic |
| 3 | `capability-fact-to-feature-production-plan.md` | `plans/strategic/` | strategic |
| 4 | `continuation-isolation-plan.md` | `plans/strategic/` | strategic |
| 5 | `enhanced-qname-python-governed-plan.md` | `plans/healing/` | healing |
| 6 | `oracle-layer-hardening-addendum.md` | `plans/healing/` | healing |
| 7 | `oracle-backfill-wave6.md` | `plans/healing/` | healing |
| 8 | `product-code-healing-plan.md` | `plans/healing/` | healing |
| 9 | `format-factory-zero-stub-production-hardening-plan.md` | `plans/healing/` | healing |
| 10 | `portfolio-product-machinery-recon-and-healing-plan.md` | `plans/healing/` | healing |
| 11 | `csvr118-dotnet-failure-tracking-hardening.md` | `plans/healing/` | healing |
| 12 | `vivid-napping-kurzweil-hardening-addendum.md` | `plans/secondary/` | historical |
| 13 | `generic-soaring-chipmunk-hardening-addendum.md` | `plans/secondary/` | historical |
| 14 | `floating-stargazing-globe-hardening-addendum-20260623.md` | `plans/secondary/` | historical |
| 15 | `cap-fact-forensics-repair-hardening-addendum.md` | `plans/secondary/` | historical |
| 16 | `misty-hopping-token-hardening-addendum.md` | `plans/secondary/` | historical |
| 17 | `unified-multi-plan-execution.md` | `plans/secondary/` | historical |

**Subfolder model:**

| Subfolder | Purpose | Accepted Types |
|-----------|---------|----------------|
| `strategic/` | NEW - high-authority strategic/governance plans | strategic, governance, forensic |
| `healing/` | existing - repair, hardening, backfill plans | healing, hardening, backfill |
| `secondary/` | existing - historical, superseded, archived | historical, superseded, addenda |
| `.claude/` | existing - per-chat execution plans | per_chat |
| `layers/` | existing - layer governance (exempt from relocation) | layer_definition, layer_registry |
| `from_chat/` | existing - imported plans placeholder | imported |
| `.governance/` | NEW - plan governance metadata | migration_map, routing_policy |

---

## Wave 0.5: Pre-Flight Safety Checks (MUST PASS before any mutation)

### TC-PG2-001b: Pre-flight gate

Run these checks before ANY file move. If any check fails, STOP and diagnose.

**Check 1 — No IN_PROGRESS locks for target files:**
```bash
# Verify no active locks reference any of the 17 files being moved
grep -rl "spec-to-feature\|snoopy\|capability-fact\|continuation-isolation\|enhanced-qname\|oracle-layer-hardening\|oracle-backfill\|product-code-healing\|format-factory-zero\|portfolio-product\|csvr118\|vivid-napping\|generic-soaring\|floating-stargazing\|cap-fact-forensics\|misty-hopping\|unified-multi" .local/supervisor/plan-locks/ 2>/dev/null || echo "CLEAN: no lock references"
```
Status: **Pre-verified CLEAN** — no locks reference any of these plans.

**Check 2 — All 17 source files exist:**
```bash
for f in spec-to-feature-radical-correction-plan.md snoopy-juggling-seal.md capability-fact-to-feature-production-plan.md continuation-isolation-plan.md enhanced-qname-python-governed-plan.md oracle-layer-hardening-addendum.md oracle-backfill-wave6.md product-code-healing-plan.md format-factory-zero-stub-production-hardening-plan.md portfolio-product-machinery-recon-and-healing-plan.md csvr118-dotnet-failure-tracking-hardening.md vivid-napping-kurzweil-hardening-addendum.md generic-soaring-chipmunk-hardening-addendum.md floating-stargazing-globe-hardening-addendum-20260623.md cap-fact-forensics-repair-hardening-addendum.md misty-hopping-token-hardening-addendum.md unified-multi-plan-execution.md; do
  [ -f "plans/$f" ] || echo "MISSING: plans/$f"
done
```

**Check 3 — Destination folders exist or can be created:**
```bash
[ -d "plans/healing" ] && echo "OK: healing/" || echo "MISSING: healing/"
[ -d "plans/secondary" ] && echo "OK: secondary/" || echo "MISSING: secondary/"
```

**Check 4 — No filename collisions at destinations:**
```bash
for f in enhanced-qname-python-governed-plan.md oracle-layer-hardening-addendum.md oracle-backfill-wave6.md product-code-healing-plan.md format-factory-zero-stub-production-hardening-plan.md portfolio-product-machinery-recon-and-healing-plan.md csvr118-dotnet-failure-tracking-hardening.md; do
  [ -f "plans/healing/$f" ] && echo "COLLISION: plans/healing/$f"
done
for f in vivid-napping-kurzweil-hardening-addendum.md generic-soaring-chipmunk-hardening-addendum.md floating-stargazing-globe-hardening-addendum-20260623.md cap-fact-forensics-repair-hardening-addendum.md misty-hopping-token-hardening-addendum.md unified-multi-plan-execution.md; do
  [ -f "plans/secondary/$f" ] && echo "COLLISION: plans/secondary/$f"
done
```

**Check 5 — Git working tree allows git mv (no unmerged files):**
```bash
git status --porcelain plans/ | grep "^U" && echo "BLOCKED: unmerged files in plans/" || echo "OK: no unmerged files"
```

**All 5 checks must echo OK/CLEAN before proceeding to Wave 1.**

### TC-PG2-001c: Generate rollback script

Before any moves, generate a reverse-migration script stored at `.local/plans-rollback.sh`:
```bash
#!/bin/bash
# Auto-generated rollback for FF-PLAN-GOV-002
# Run this to undo all git mv operations
git mv plans/strategic/spec-to-feature-radical-correction-plan.md plans/
git mv plans/strategic/snoopy-juggling-seal.md plans/
# ... (all 17 reverse moves)
# Then revert reference changes:
# git checkout HEAD -- CLAUDE.md AGENTS.md docs/ tools/supervisor/plan_identity.py ...
```

This script is NOT committed — it lives in `.local/` for emergency rollback only.

---

## Wave 1: File Moves

### TC-PG2-002: Move files with git mv

```bash
mkdir -p plans/strategic plans/.governance

# Strategic (4 files)
git mv plans/spec-to-feature-radical-correction-plan.md plans/strategic/
git mv plans/snoopy-juggling-seal.md plans/strategic/
git mv plans/capability-fact-to-feature-production-plan.md plans/strategic/
git mv plans/continuation-isolation-plan.md plans/strategic/

# Healing (7 files - folder exists)
git mv plans/enhanced-qname-python-governed-plan.md plans/healing/
git mv plans/oracle-layer-hardening-addendum.md plans/healing/
git mv plans/oracle-backfill-wave6.md plans/healing/
git mv plans/product-code-healing-plan.md plans/healing/
git mv plans/format-factory-zero-stub-production-hardening-plan.md plans/healing/
git mv plans/portfolio-product-machinery-recon-and-healing-plan.md plans/healing/
git mv plans/csvr118-dotnet-failure-tracking-hardening.md plans/healing/

# Secondary (6 files - folder exists)
git mv plans/vivid-napping-kurzweil-hardening-addendum.md plans/secondary/
git mv plans/generic-soaring-chipmunk-hardening-addendum.md plans/secondary/
git mv plans/floating-stargazing-globe-hardening-addendum-20260623.md plans/secondary/
git mv plans/cap-fact-forensics-repair-hardening-addendum.md plans/secondary/
git mv plans/misty-hopping-token-hardening-addendum.md plans/secondary/
git mv plans/unified-multi-plan-execution.md plans/secondary/
```

### TC-PG2-002b: Wave 1 verification gate

After all git mv commands, verify before proceeding:
```bash
# Exactly 2 .md files at root
count=$(ls plans/*.md 2>/dev/null | wc -l)
[ "$count" -eq 2 ] && echo "PASS: $count root files" || echo "FAIL: $count root files (expected 2)"

# All 17 files landed in correct destinations
[ -f "plans/strategic/spec-to-feature-radical-correction-plan.md" ] && echo "OK" || echo "MISSING"
[ -f "plans/strategic/snoopy-juggling-seal.md" ] && echo "OK" || echo "MISSING"
[ -f "plans/strategic/capability-fact-to-feature-production-plan.md" ] && echo "OK" || echo "MISSING"
[ -f "plans/strategic/continuation-isolation-plan.md" ] && echo "OK" || echo "MISSING"
# ... (spot-check 2-3 from each destination group)

# Git status shows renames (not deletes+adds)
git diff --cached --name-status | head -20
# Should show "R100" (rename) entries
```

**If any file is missing or git shows delete+add instead of rename, STOP and investigate before reference updates.**

---

## Wave 2: Reference Updates (Critical — Runtime-Affecting)

### TC-PG2-003: Update CLAUDE.md (2 occurrences of spec-to-feature, 2 of snoopy)

Files: [CLAUDE.md](CLAUDE.md)

| Pattern | Replacement |
|---------|------------|
| `plans/spec-to-feature-radical-correction-plan.md` | `plans/strategic/spec-to-feature-radical-correction-plan.md` |
| `plans/snoopy-juggling-seal.md` | `plans/strategic/snoopy-juggling-seal.md` |

### TC-PG2-004: Update AGENTS.md (1 occurrence of spec-to-feature)

Files: [AGENTS.md](AGENTS.md)

### TC-PG2-005: Update docs/ governance files (~12 occurrences across 8 files)

Files:
- [docs/spec-to-feature-correction-plan-summary.md](docs/spec-to-feature-correction-plan-summary.md)
- [docs/python-foss/spec-to-source-chain-contract.md](docs/python-foss/spec-to-source-chain-contract.md)
- [docs/governance/dotnet-library-standard.md](docs/governance/dotnet-library-standard.md)
- [docs/governance/cross-language-semantic-standard.md](docs/governance/cross-language-semantic-standard.md)
- [docs/governance/production-code-governance-rules.yaml](docs/governance/production-code-governance-rules.yaml)
- [docs/governance/production-code-governance-standard.md](docs/governance/production-code-governance-standard.md)
- [docs/governance/python-library-standard.md](docs/governance/python-library-standard.md)
- [docs/governance/plan-identity-schema.md](docs/governance/plan-identity-schema.md)

### TC-PG2-006: Update supervisor tools & config

Files:
- [tools/supervisor/plan_identity.py](tools/supervisor/plan_identity.py) — comment-only update for snoopy path
- [.governance/capabilities/registry.yaml](.governance/capabilities/registry.yaml) — snoopy reference
- [.supervisor/skill-registry.yaml](.supervisor/skill-registry.yaml) — snoopy reference
- [.supervisor/taskcard-skill-backfill.yaml](.supervisor/taskcard-skill-backfill.yaml) — spec-to-feature reference
- [.claude/commands/sal-pipeline-heal.md](.claude/commands/sal-pipeline-heal.md) — 5 snoopy references

Note: `governance_validators_ext.py` V56 uses filename-substring matching (`"snoopy-juggling-seal.md" in path_norm`) — **no runtime change needed**. The docstring comment on line 102 references the old path — update as cosmetic fix only.

### TC-PG2-006b: Verify V56 still works after move

V56 in [tools/supervisor/governance_validators_ext.py:195](tools/supervisor/governance_validators_ext.py#L195) checks `"snoopy-juggling-seal.md" in path_norm` (substring match). This is path-agnostic and safe. After all moves, run:
```bash
.venv/Scripts/pytest tests/supervisor/test_governance_validators.py -k "V56 or snoopy" -v
```
If V56 tests reference full paths (not substrings), update them too.

### TC-PG2-007: Update MEMORY.md

File: [C:\Users\prora\.claude\projects\c--Users-prora-OneDrive-Documents-GitHub-format-factory\memory\MEMORY.md](C:\Users\prora\.claude\projects\c--Users-prora-OneDrive-Documents-GitHub-format-factory\memory\MEMORY.md)

Update the "Always Follow spec-to-feature" section path reference.

### TC-PG2-007b: Wave 2 verification gate — critical references

After updating all critical files, verify BEFORE touching non-critical files:
```bash
# CLAUDE.md must have new paths
grep -c "plans/strategic/spec-to-feature" CLAUDE.md  # expect 2
grep -c "plans/strategic/snoopy" CLAUDE.md            # expect 2
# Must NOT have old root paths for moved files
grep -c "plans/spec-to-feature-radical-correction-plan\.md" CLAUDE.md  # expect 0
grep -c "plans/snoopy-juggling-seal\.md" CLAUDE.md                     # expect 0

# AGENTS.md must have new path
grep "plans/strategic/spec-to-feature" AGENTS.md  # expect 1 hit

# docs/ governance — spot check
grep "plans/strategic/spec-to-feature" docs/spec-to-feature-correction-plan-summary.md  # expect 1
```

**STOP if CLAUDE.md still contains old root paths. This is the highest-risk reference.**

---

## Wave 3: Reference Updates (Non-Critical — Plans, Reports, Tests)

### TC-PG2-008: Update master-plan.md references

File: [plans/master-plan.md](plans/master-plan.md)
- ~1 spec-to-feature reference
- ~12 snoopy references
- ~5 other relocated plan references
- ~2 continuation-isolation references
- ~1 capability-fact reference

### TC-PG2-009: Update master-plan-memory.md

File: [plans/master-plan-memory.md](plans/master-plan-memory.md)
- ~1 snoopy reference
- ~1 capability-fact reference

### TC-PG2-010: Update plans/layers/ references

Files:
- [plans/layers/plan-prompt-authority-layer.md](plans/layers/plan-prompt-authority-layer.md) — 3 spec-to-feature, 1 snoopy
- [plans/layers/feature-compilation-layer.md](plans/layers/feature-compilation-layer.md) — 2 spec-to-feature
- [plans/layers/master.md](plans/layers/master.md) — 1 spec-to-feature
- [plans/layers/specification-authority-layer.md](plans/layers/specification-authority-layer.md) — 4 snoopy
- [plans/layers/decision-register.yaml](plans/layers/decision-register.yaml) — 1 spec-to-feature
- [plans/layers/task-register.yaml](plans/layers/task-register.yaml) — 1 spec-to-feature

### TC-PG2-011: Update per-chat plan references

Files:
- [plans/.claude/precious-launching-pebble.md](plans/.claude/precious-launching-pebble.md) — 2 relocated plan refs
- [plans/.claude/distributed-growing-cerf.md](plans/.claude/distributed-growing-cerf.md) — 1 spec-to-feature, 1 snoopy

### TC-PG2-012: Update cross-referencing plan files

Files within relocated plans that reference other relocated plans:
- `plans/healing/oracle-layer-hardening-addendum.md` — 3 self-references (update internal paths)
- `plans/strategic/capability-fact-to-feature-production-plan.md` — 7 self/cross-references
- `plans/secondary/cap-fact-forensics-repair-hardening-addendum.md` — 1 capability-fact reference
- `plans/secondary/vivid-napping-kurzweil-hardening-addendum.md` — 4 self-references
- `plans/secondary/floating-stargazing-globe-hardening-addendum-20260623.md` — 2 self-references
- `plans/strategic/continuation-isolation-plan.md` — 1 spec-to-feature reference

### TC-PG2-013: Update test files

Files:
- [tests/supervisor/test_plan_governance.py](tests/supervisor/test_plan_governance.py) — 6 snoopy references
- [tests/supervisor/test_plan_lock_machinery.py](tests/supervisor/test_plan_lock_machinery.py) — 2 snoopy references
- [tests/supervisor/test_plan_governance_gates.py](tests/supervisor/test_plan_governance_gates.py) — 1 snoopy reference
- [tests/specification-authority-layer/test_plan_readiness_verdict.py](tests/specification-authority-layer/test_plan_readiness_verdict.py) — 1 snoopy reference
- [tests/specification-authority-layer/test_gap_int_002_product_source_fact_refs.py](tests/specification-authority-layer/test_gap_int_002_product_source_fact_refs.py) — 1 snoopy reference
- [tests/supervisor/test_tc_prod_closure_proof_001.py](tests/supervisor/test_tc_prod_closure_proof_001.py) — 1 capability-fact reference
- [tests/supervisor/test_tc_finding021_status_filter.py](tests/supervisor/test_tc_finding021_status_filter.py) — 1 capability-fact reference
- [tests/supervisor/test_tc_c1_extend_behavioral.py](tests/supervisor/test_tc_c1_extend_behavioral.py) — 1 capability-fact reference

### TC-PG2-014: Update report files (batch — historical, non-blocking)

~50+ report files under `reports/` reference old paths. Use batch grep+sed approach:
- Search for each old path pattern
- Replace with new path
- Skip immutable evidence files (`.local/evidences/`)

Historical reports are best-effort — update where found but do not block on missed references.

### TC-PG2-014b: Wave 3 verification gate — comprehensive stale-path sweep

Run a comprehensive sweep across ALL file types (not just .py/.yaml):
```bash
# Build alternation pattern for all 17 moved filenames (anchored to plans/ root)
# This catches any remaining stale root-path references in critical files
for pattern in \
  "plans/spec-to-feature-radical-correction-plan\\.md" \
  "plans/snoopy-juggling-seal\\.md" \
  "plans/capability-fact-to-feature-production-plan\\.md" \
  "plans/continuation-isolation-plan\\.md" \
  "plans/enhanced-qname-python-governed-plan\\.md" \
  "plans/oracle-layer-hardening-addendum\\.md" \
  "plans/oracle-backfill-wave6\\.md" \
  "plans/product-code-healing-plan\\.md"; do
  hits=$(grep -rn "$pattern" --include="*.py" --include="*.yaml" --include="*.md" \
    CLAUDE.md AGENTS.md docs/ tools/ tests/ plans/layers/ plans/.claude/ .claude/ .supervisor/ .governance/ 2>/dev/null | wc -l)
  [ "$hits" -gt 0 ] && echo "STALE ($hits): $pattern"
done
```

**Acceptable residual:** `reports/` directory may retain old paths in historical snapshots. All other directories must be clean.

### TC-PG2-014c: Run test suite before governance infrastructure

Run the full plan-related test suite BEFORE building new infrastructure. This catches reference breakage early.
```bash
.venv/Scripts/pytest tests/supervisor/test_plan_governance.py tests/supervisor/test_plan_lock_machinery.py tests/supervisor/test_plan_governance_gates.py tests/specification-authority-layer/ -v --tb=short
```

**If tests fail due to stale path references, fix them NOW before proceeding to Wave 4.**

---

## Wave 4: Governance Infrastructure

### TC-PG2-015: Create path migration map

File: `plans/.governance/path-migration-20260629.yaml`

```yaml
migration_date: "2026-06-29"
mission_id: "FF-PLAN-GOV-002"
migrations:
  - old: "plans/spec-to-feature-radical-correction-plan.md"
    new: "plans/strategic/spec-to-feature-radical-correction-plan.md"
    category: strategic
  # ... (all 17 entries)
```

### TC-PG2-016: Create plan routing policy

File: `plans/.governance/routing-policy.yaml`

```yaml
root_allowed:
  - master-plan.md
  - master-plan-memory.md

routes:
  strategic:
    folder: plans/strategic/
    types: [strategic, governance, forensic]
  healing:
    folder: plans/healing/
    types: [healing, hardening, backfill, repair]
  secondary:
    folder: plans/secondary/
    types: [historical, superseded, archived, addendum]
  per_chat:
    folder: plans/.claude/
    types: [per_chat, execution]
  layer:
    folder: plans/layers/
    types: [layer_definition, layer_registry]
```

### TC-PG2-017: Create plan placement tool

File: [tools/supervisor/plan_placement.py](tools/supervisor/plan_placement.py) (~80 LOC)

Functions:
- `resolve_plan_destination(filename, plan_type) -> str` — returns canonical path
- `validate_root_policy(repo_root) -> tuple[bool, list[str]]` — checks root compliance
- `migrate_plan_locks(repo_root, migration_map) -> int` — updates lock file paths
- `PLAN_ROOT_ALLOWED = {"master-plan.md", "master-plan-memory.md"}`

### TC-PG2-018: Add V90 governance validator

File: [tools/supervisor/governance_validators_ext2.py](tools/supervisor/governance_validators_ext2.py) — append ~30 lines

```python
def validate_plans_root_policy(declaration: dict, repo_root: "Path | None" = None) -> dict:
    """V90: Only master-plan.md and master-plan-memory.md at plans/ root."""
```

Wire in [tools/supervisor/governance_validator_runner.py](tools/supervisor/governance_validator_runner.py):
- Import `validate_plans_root_policy as _validate_plans_root_policy`
- Add to results list

### TC-PG2-019: Run plan lock migration

Execute `migrate_plan_locks()` for all 17 path changes. Target: `.local/supervisor/plan-locks/*.json` and `.local/supervisor/active-plan-lock.json`.

---

## Wave 5: Tests

### TC-PG2-020: Add V90 validator tests

File: [tests/supervisor/test_governance_validators.py](tests/supervisor/test_governance_validators.py) — append TestPlansRootPolicy class

Tests:
1. `test_pass_clean_root` — only allowed files at root → PASS
2. `test_warn_extra_file` — unauthorized .md file → WARN
3. `test_subdirectories_ignored` — subfolders don't trigger violations
4. `test_empty_root_still_pass` — no root files (edge case) → PASS

### TC-PG2-021: Run existing plan governance tests

```bash
.venv/Scripts/pytest tests/supervisor/test_plan_governance.py tests/supervisor/test_plan_lock_machinery.py tests/supervisor/test_plan_governance_gates.py -v
```

Verify all pass after reference updates.

---

## Wave 6: Verification & Idempotency

### TC-PG2-022: Verify root contents

```bash
ls plans/*.md
# Expected: master-plan.md  master-plan-memory.md  (exactly 2)
```

### TC-PG2-023: Verify no stale references

```bash
# Must return 0 hits for direct-root paths of moved files
grep -rn "plans/spec-to-feature-radical-correction-plan\.md" --include="*.py" --include="*.yaml" .
grep -rn "plans/snoopy-juggling-seal\.md" --include="*.py" --include="*.yaml" .
# (repeat for all 17 moved files, or use alternation regex)
```

Note: `reports/` historical snapshots may retain old paths — that's acceptable.

### TC-PG2-024: Run V90 validator

```bash
python -c "
from tools.supervisor.governance_validators_ext2 import validate_plans_root_policy
from pathlib import Path
r = validate_plans_root_policy({}, Path('.'))
print(r['result'], r['summary'])
assert r['result'] == 'PASS'
"
```

### TC-PG2-025: Idempotency — second run

Run V90 validator again. Run plan placement tool validation again. Verify zero changes needed.

### TC-PG2-026: Final report

Create `reports/plans-governance/plans-folder-organization-report.md` with:
- Initial state (19 root files)
- Relocations table (17 moves)
- Reference update counts
- Subfolder model
- Validator result
- Idempotency proof
- Final root contents
- Verdict: `PLANS_FOLDER_CLEAN_GOVERNED_AUTOMATICALLY_ENFORCED_AND_IDEMPOTENT`

---

## Reference Counts Summary

| Moved Plan | Total References | Critical (*.py, *.yaml, CLAUDE.md) | Report-only |
|-----------|-----------------|-------------------------------------|-------------|
| spec-to-feature-radical-correction-plan.md | 63 across 48 files | ~15 | ~48 |
| snoopy-juggling-seal.md | 78 across 35 files | ~15 | ~63 |
| capability-fact-to-feature-production-plan.md | 19 across 12 files | ~5 | ~14 |
| continuation-isolation-plan.md | 4 across 3 files | ~2 | ~2 |
| Other 13 files | ~38 across 20 files | ~10 | ~28 |

---

## Risks & Mitigations

### R1: CLAUDE.md session-start breakage (CRITICAL)

**Impact:** If CLAUDE.md references `plans/spec-to-feature-radical-correction-plan.md` after the file moves to `plans/strategic/`, every new agent session will fail to read the spec-to-feature plan — silently degrading governance compliance.

**Mitigations:**
- TC-PG2-003 updates CLAUDE.md as the FIRST reference update after file moves
- TC-PG2-007b verification gate blocks all further work if CLAUDE.md still has old paths
- Rollback script (TC-PG2-001c) can revert CLAUDE.md with `git checkout HEAD -- CLAUDE.md`

### R2: Partial migration leaves inconsistent state (HIGH)

**Impact:** If execution stops mid-wave (context exhaustion, error), some files are moved but references still point to old paths, or vice versa.

**Mitigations:**
- Wave-level verification gates (TC-PG2-002b, TC-PG2-007b, TC-PG2-014b) detect inconsistency
- Rollback script (TC-PG2-001c) generated BEFORE any mutation
- Git mv is atomic per-file — partial moves are visible in `git status` and can be completed or reverted
- Each wave is independently verifiable — resume from last passing gate on context recovery

### R3: Plan lock path mismatch (MEDIUM)

**Impact:** Future `check_continuation.py` runs could fail to match plan paths if locks reference old paths.

**Mitigations:**
- Pre-verified: NO locks currently reference any of the 17 files (all are TERMINAL_CLOSED/SUPERSEDED or unrelated)
- TC-PG2-019 migrates any lock files as belt-and-suspenders safety
- `write_plan_lock.py` FORBIDDEN_AS_ACTIVE_PLAN list only blocks `master-plan-memory.md` — no impact from moves

### R4: V56 governance validator false positives (MEDIUM)

**Impact:** V56 uses `"snoopy-juggling-seal.md" in path_norm` substring match. This is path-agnostic and safe. But if future validators use full-path matching, they could break.

**Mitigations:**
- TC-PG2-006b explicitly tests V56 after migration
- V56 docstring (line 102) updated as cosmetic fix
- New V90 validator uses `plans/` root scanning (not path-matching) — inherently safe

### R5: Test failures from hardcoded paths (MEDIUM)

**Impact:** Tests in `test_plan_governance.py` (6 snoopy refs) and others use plan paths as test fixtures.

**Mitigations:**
- TC-PG2-013 updates all 8 test files
- TC-PG2-014c runs full test suite BEFORE building new infrastructure — catches breakage early
- TC-PG2-021 runs the same suite AFTER V90 is added — double verification

### R6: Cross-references within relocated files (LOW)

**Impact:** Relocated plans that reference each other (e.g., `cap-fact-forensics-repair` → `capability-fact-to-feature-production`) may have stale internal paths.

**Mitigations:**
- TC-PG2-012 explicitly lists all cross-referencing files and their paths
- These are documentation references, not runtime code — worst case is stale docs, not broken execution

### R7: Report historical snapshots retain old paths (LOW, ACCEPTED)

**Impact:** ~50+ report files under `reports/` reference old paths. These are historical evidence.

**Mitigations:**
- TC-PG2-014 does best-effort batch update
- Stale report paths have zero runtime impact
- Path migration map (TC-PG2-015) provides lookup for any consumer needing to resolve old paths

### R8: Future plan creation bypasses root policy (ONGOING)

**Impact:** Without enforcement, future plan creation could write new files to `plans/` root.

**Mitigations:**
- V90 validator (TC-PG2-018) detects root violations at closeout
- Plan placement tool (TC-PG2-017) provides governed path resolution
- Routing policy YAML (TC-PG2-016) is machine-readable for future automation
- Note: Full producer wiring (making all plan-creation skills call placement tool) is out-of-scope for this plan — tracked as follow-up work

---

## Rollback Protocol

If any wave fails catastrophically:

1. **Wave 1 rollback (file moves):** Run `.local/plans-rollback.sh` to reverse all git mv operations
2. **Wave 2-3 rollback (reference updates):** `git checkout HEAD -- CLAUDE.md AGENTS.md docs/ tools/supervisor/plan_identity.py .governance/ .supervisor/ .claude/commands/ plans/master-plan.md plans/master-plan-memory.md plans/layers/ plans/.claude/ tests/`
3. **Wave 4 rollback (new files):** `git rm tools/supervisor/plan_placement.py plans/.governance/` + revert governance_validators_ext2.py and runner edits
4. **Full rollback:** `git checkout HEAD -- .` (restores entire working tree to last commit)

Rollback at any point leaves the repo in a consistent pre-migration state because:
- Git mv tracks renames — reverting restores originals
- No data is deleted — only moved
- New files (plan_placement.py, .governance/) are additive and removable


---

## Taskcard Status

All taskcards CLOSED. Mission FF-PLAN-GOV-002 complete.

| Taskcard | Status |
|----------|--------|
| TC-PG2-001 | CLOSED |
| TC-PG2-001b | CLOSED |
| TC-PG2-001c | CLOSED |
| TC-PG2-002 | CLOSED |
| TC-PG2-002b | CLOSED |
| TC-PG2-003 | CLOSED |
| TC-PG2-004 | CLOSED |
| TC-PG2-005 | CLOSED |
| TC-PG2-006 | CLOSED |
| TC-PG2-006b | CLOSED |
| TC-PG2-007 | CLOSED |
| TC-PG2-007b | CLOSED |
| TC-PG2-008 | CLOSED |
| TC-PG2-009 | CLOSED |
| TC-PG2-010 | CLOSED |
| TC-PG2-011 | CLOSED |
| TC-PG2-012 | CLOSED |
| TC-PG2-013 | CLOSED |
| TC-PG2-014 | CLOSED |
| TC-PG2-014b | CLOSED |
| TC-PG2-014c | CLOSED |
| TC-PG2-015 | CLOSED |
| TC-PG2-016 | CLOSED |
| TC-PG2-017 | CLOSED |
| TC-PG2-018 | CLOSED |
| TC-PG2-019 | CLOSED |
| TC-PG2-020 | CLOSED |
| TC-PG2-021 | CLOSED |
| TC-PG2-022 | CLOSED |
| TC-PG2-023 | CLOSED |
| TC-PG2-024 | CLOSED |
| TC-PG2-025 | CLOSED |
| TC-PG2-026 | CLOSED |

<!--plan_terminal_lock:
  status: TERMINAL_CLOSED
  locked_at: "2026-06-29T12:02:06.290200+00:00"
  locked_by: "757bacd68ae8"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
