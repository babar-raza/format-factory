# Master Plan Healing Patch Plan

**Sprint ID:** FORMAT-FACTORY-MASTER-PLAN-GOVERNANCE-REVIEW-HEALING-PLAN-001
**Date:** 2026-06-10

## Phase 1: Backup

1. Compute SHA-256 of `plans/master-plan.md`:
   ```bash
   sha256sum plans/master-plan.md > reports/master-plan-healing-plan-repair/preedit-sha.txt
   ```
2. Copy full backup:
   ```bash
   cp plans/master-plan.md docs/history/master-plan-full-before-healing-2026-06-10.md
   ```
3. Verify backup matches:
   ```bash
   diff plans/master-plan.md docs/history/master-plan-full-before-healing-2026-06-10.md
   ```

## Phase 2: Pre-Edit Section Map

Create `section-map-before.json`:
```json
{
  "date": "2026-06-10",
  "total_lines": 2229,
  "sections": [
    {"number": "header", "heading": "Header Block", "start_line": 1, "end_line": 16},
    {"number": "1", "heading": "Non-Negotiable Operating Rules", "start_line": 19, "end_line": 39},
    ...
  ]
}
```
(Full section map already produced in master-plan-structure-inventory.json)

## Phase 3: Edits (in order)

### Edit 1: Create new governance docs
- Create `docs/governance/master-plan-canonical-source-map.md`
- Create `docs/governance/master-plan-sync-policy.md`

### Edit 2: Create archive files
- Create `docs/history/master-plan-archived-sections-2026-06-10.md`
  - Copy sections §7, §9, §25, §27, §28, §31, §32, §33, §36, §37, §39 with context headers

### Edit 3: Rewrite header block
- Set version to next (e.g., 3.0)
- Set last_updated to execution date
- Replace stale "Current phase" narrative with 1-sentence summary
- Add canonical source pointers
- Update Gate 11 status to reflect approval

### Edit 4: Condense §1 (Non-Negotiable Rules)
- Update rule 6: replace bundle upload with declaration-driven reference
- Keep all safety rules

### Edit 5: Keep §2, §3, §4 (minor updates only)
- §3: Merge POC targets from §40.2
- Add pointer to poc-targets.yaml

### Edit 6: Rewrite §5 (Living Master Plan Policy)
- Amend rule 6 to authorize governance doc split-outs
- Add pointer to canonical-source-map.md and sync-policy.md

### Edit 7: Condense §6 (Current Project State)
- Replace 38-line narrative with 20-line source-pointer table
- No run history, no stale sprint names

### Edit 8: Archive §7 (Evidence Bundle Inspection Rule)
- Replace with 2-line pointer to declaration-driven model (§12)

### Edit 9: Keep §8 (Phase Model), §10 (Forbidden Paths)
- Minor updates only

### Edit 10: Archive §9 (Phase 0 Required Files)
- Replace with 1-line archive pointer

### Edit 11: Rewrite §11 (Agent Operations)
- Remove Codex secondary executor
- Update to current executor model

### Edit 12: Keep §12 (Plan/Execution Mode)

### Edit 13: Rewrite §13 (Commands)
- Update to reflect 25 existing commands
- Remove "planned commands" table

### Edit 14: Condense §14 (LLM Strategy)
- Remove Codex references
- Keep Claude primary, local fallback

### Edit 15: Keep §15-§22 (minimal changes)

### Edit 16: Condense §23 (Pilot Recommendation)
- 5-line summary: "First pilot FODS, completed"

### Edit 17: Rewrite §24 (WIP Limits)
- Update to reflect multi-format POC reality

### Edit 18: Archive §25 (Active Taskcards)
- Replace with 1-line archive pointer

### Edit 19: Condense §26 (Decision Register)
- Keep all DECs, shorten notes

### Edit 20: Archive §27, §28 (Gap and Healing Registers)
- Replace with 1-line archive pointers each

### Edit 21: Condense §29 (Risk Register)
- 10-line summary

### Edit 22: Keep §30 (Phase/Gate Reference)

### Edit 23: Archive §31, §32, §33 (Phase 0 Checklist, Run History, Commit Ledger)
- Replace with archive pointers
- §33: Keep 3-line header about declaration-driven model

### Edit 24: Condense §34 (Standing Instructions)
- Keep 10 most important rules

### Edit 25: Condense §35 (Memory Layer)
- 10-line summary

### Edit 26: Archive §36, §37, §39 (S-F2F, Format Understanding, AI Platform)
- Replace with archive pointers

### Edit 27: Keep §40-§44 (with condensation)
- §40: Keep POC targets (merged into §3)
- §41: Keep declaration-driven pipeline (merged into §9, §12)
- §42: Keep acceleration layer (merged into §8)
- §43: Keep product-first model (merged into §5, §6)
- §44: Condense to 15 lines (merged into §21)

### Edit 28: Add ARCHIVE-PTR block
- List all archived sections with pointer paths

### Edit 29: Rewrite footer
- Match header version
- Update date

## Phase 4: Validation

```bash
# Line count in target range
wc -l plans/master-plan.md  # expect 400-700

# No stale claims remain
grep -c "No functional commands exist" plans/master-plan.md  # expect 0
grep -c "bundle must be uploaded by human" plans/master-plan.md  # expect 0
grep -c "Product stages.*1 format" plans/master-plan.md  # expect 0
grep -c "Codex.*optional secondary" plans/master-plan.md  # expect 0

# Version consistency
head -10 plans/master-plan.md | grep "Version"
tail -5 plans/master-plan.md | grep "version"

# Archive files exist
ls docs/history/master-plan-full-before-healing-2026-06-10.md
ls docs/history/master-plan-archived-sections-2026-06-10.md

# New governance docs exist
ls docs/governance/master-plan-canonical-source-map.md
ls docs/governance/master-plan-sync-policy.md

# SHA-256 pre-edit recorded
cat reports/master-plan-healing-plan-repair/preedit-sha.txt

# No forbidden files modified (beyond master plan and governance)
git diff --name-only -- src/net src/python tests registry product-capability-matrix
# expect: no output
```

## Phase 5: Rollback Procedure

If the edit fails midway:
1. Restore from backup: `cp docs/history/master-plan-full-before-healing-2026-06-10.md plans/master-plan.md`
2. Verify SHA-256 matches pre-edit: `sha256sum plans/master-plan.md`
3. Delete any partially-created archive files
4. Re-attempt from Phase 3
