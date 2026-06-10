# EXECUTION PROMPT: Master Plan Healing Sprint

**Sprint ID:** FORMAT-FACTORY-MASTER-PLAN-HEALING-EXECUTION-001
**Mode:** EXECUTION
**Goal:** Heal plans/master-plan.md from 2229 lines to 400-700 lines by archiving historical content, condensing stale sections, removing contradictions, and establishing freshness mechanisms.

---

## Allowed Paths

```
plans/master-plan.md                              EDIT (the target)
docs/history/master-plan-full-before-healing-2026-06-10.md    CREATE (full backup)
docs/history/master-plan-archived-sections-2026-06-10.md      CREATE (archived sections)
docs/governance/master-plan-canonical-source-map.md           CREATE (new governance doc)
docs/governance/master-plan-sync-policy.md                    CREATE (new governance doc)
reports/master-plan-healing-execution/**                      CREATE (execution outputs)
.local/evidences/master-plan-healing-execution/**             CREATE (evidence package)
```

## Forbidden Paths

```
src/net/*                     NO EDIT
src/python/*                  NO EDIT
tests/*                       NO EDIT
registry/format-registry.yaml NO EDIT
product-capability-matrix/*   NO EDIT
state/current-state.md        NO EDIT (note: this file has a contradiction but fixing it is out of scope)
docs/governance/* (existing)  NO EDIT (only CREATE new files listed above)
```

---

## PHASE 1: PREFLIGHT (TC-MP-COORD-001)

1. Read these files:
   - `plans/master-plan.md` — the target document
   - `reports/supervisor/session-resume.md` — current sprint state
   - `product-capability-matrix/poc-targets.yaml` — current POC targets
   - `reports/master-plan-healing-plan-repair/target-master-plan-structure.md` — target structure
   - `reports/master-plan-healing-plan-repair/archive-and-split-strategy.md` — archive plan
   - `reports/master-plan-healing-plan-repair/master-plan-healing-patch-plan.md` — edit sequence

2. Create output directory: `reports/master-plan-healing-execution/`

3. Record preflight:
   ```bash
   wc -l plans/master-plan.md > reports/master-plan-healing-execution/preflight.md
   git status --short >> reports/master-plan-healing-execution/preflight.md
   ```

---

## PHASE 2: BACKUP (TC-MP-COORD-002)

**This phase is MANDATORY and must complete before any edit to plans/master-plan.md.**

1. Compute SHA-256:
   ```bash
   sha256sum plans/master-plan.md > reports/master-plan-healing-execution/preedit-sha.txt
   ```

2. Create full backup:
   ```bash
   mkdir -p docs/history
   cp plans/master-plan.md docs/history/master-plan-full-before-healing-2026-06-10.md
   ```

3. Verify backup matches:
   ```bash
   diff plans/master-plan.md docs/history/master-plan-full-before-healing-2026-06-10.md
   # Must show no differences
   ```

---

## PHASE 3: CREATE NEW GOVERNANCE DOCS (TC-MP-EXEC-001, TC-MP-EXEC-002)

### TC-MP-EXEC-001: Create docs/governance/master-plan-canonical-source-map.md

Content must include a table mapping each truth domain to its canonical source:

| Truth Domain | Canonical Source | Master Plan Treatment |
|-------------|-----------------|----------------------|
| Product targets | product-capability-matrix/poc-targets.yaml | Pointer only |
| Format status | registry/format-registry.yaml | Pointer only |
| Current sprint state | reports/supervisor/session-resume.md | Pointer only |
| Gate approval status | reports/supervisor/approval-gates.md | Pointer only |
| Next sprint work | reports/supervisor/next-sprint.md | Pointer only |
| Governance rules | docs/governance/*.md | Brief canonical summary + pointer |
| Stream definitions | docs/governance/four-stream-operating-model.md | Brief summary + pointer |
| AI authority | docs/governance/ai-authority-boundary.md | Brief summary + pointer |
| Operating rules | plans/master-plan.md §1 | Canonical (master plan owns) |
| Phase model | plans/master-plan.md §14 | Canonical (master plan owns) |
| Gate model | plans/master-plan.md §13 | Canonical (master plan owns) |
| Decision register | plans/master-plan.md §16 | Canonical (master plan owns) |
| Tier model | plans/master-plan.md §4 | Canonical (master plan owns) |

### TC-MP-EXEC-002: Create docs/governance/master-plan-sync-policy.md

Must include:
- **No-append-only rule:** Every update must review and condense existing content
- **Line budget:** 400-700 lines; exceeding 700 triggers mandatory condensation sprint
- **Freshness triggers:** Phase change, gate transition, major decision, architecture amendment
- **Stale-claim lint:** 10 grep patterns to run at every healing sprint
- **Source-of-truth rule:** Any claim duplicating a canonical source must be a pointer, not a copy
- **Split-out authorization:** docs/governance/ files are authorized split-outs
- **Archive rule:** Historical content archived to docs/history/, never deleted
- **Version rule:** Header and footer versions must always match

---

## PHASE 4: CREATE ARCHIVE FILES (TC-MP-COORD-003)

### Create docs/history/master-plan-archived-sections-2026-06-10.md

Copy the following sections from `docs/history/master-plan-full-before-healing-2026-06-10.md` into the archived sections file, each with a context header:

1. **§7** Evidence Bundle Inspection Rule (lines 152-166)
2. **§9** Phase 0 Required Files (lines 209-260)
3. **§25** Active Taskcards TC-0001..0053 (lines 666-691)
4. **§27** Gap Register (approx lines 780-840)
5. **§28** Healing Gap Register G-HEAL-001..036+ (approx lines 840-900)
6. **§31** Phase 0 Review Checklist (approx lines 990-1000)
7. **§32** Run History Table run001-run042 (approx lines 1000-1050)
8. **§33** Run Commit Ledger (lines 1052-1429)
9. **§36** S-F2F Secondary Sprint Roadmap (lines 1506-1577)
10. **§37** Format Understanding Layer (lines 1582-1656)
11. **§39** AI/LLM Platform Layer (lines 1747-1844)

Each section must be preceded by:
```markdown
---
## Archived Section [N] — [Title]
**Archived from:** plans/master-plan.md version 2.70
**Archived date:** 2026-06-10
**Reason:** [HISTORICAL | SUPERSEDED | UNAUTHORIZED_BACKLOG]
---
```

### Create reports/master-plan-healing-execution/archive-pointer-map.json

```json
{
  "archive_date": "2026-06-10",
  "full_backup": "docs/history/master-plan-full-before-healing-2026-06-10.md",
  "archived_sections": "docs/history/master-plan-archived-sections-2026-06-10.md",
  "preedit_sha256": "<from preedit-sha.txt>",
  "mappings": [
    {"old_section": "7", "reason": "SUPERSEDED", "pointer_in_healed": "Section 12"},
    {"old_section": "9", "reason": "HISTORICAL", "pointer_in_healed": "ARCHIVE-PTR"},
    {"old_section": "25", "reason": "HISTORICAL", "pointer_in_healed": "ARCHIVE-PTR"},
    {"old_section": "27", "reason": "HISTORICAL", "pointer_in_healed": "ARCHIVE-PTR"},
    {"old_section": "28", "reason": "HISTORICAL", "pointer_in_healed": "ARCHIVE-PTR"},
    {"old_section": "31", "reason": "HISTORICAL", "pointer_in_healed": "ARCHIVE-PTR"},
    {"old_section": "32", "reason": "HISTORICAL", "pointer_in_healed": "ARCHIVE-PTR"},
    {"old_section": "33", "reason": "HISTORICAL", "pointer_in_healed": "ARCHIVE-PTR"},
    {"old_section": "36", "reason": "HISTORICAL", "pointer_in_healed": "ARCHIVE-PTR"},
    {"old_section": "37", "reason": "UNAUTHORIZED_BACKLOG", "pointer_in_healed": "ARCHIVE-PTR"},
    {"old_section": "39", "reason": "UNAUTHORIZED_BACKLOG", "pointer_in_healed": "ARCHIVE-PTR"}
  ]
}
```

---

## PHASE 5: EDIT MASTER PLAN (TC-MP-EXEC-003 through TC-MP-EXEC-013)

**Edit plans/master-plan.md according to the target structure.** The healed document must have approximately 21 sections plus a header, footer, and ARCHIVE-PTR block.

### Target Structure (write this document):

```
Header block (~20 lines):
  - version: 3.0
  - last_updated: <execution date>
  - Current phase: Multi-format POC (11 targets, 3 commercial .NET, 8 FOSS Python)
  - Canonical sources: poc-targets.yaml, session-resume.md, format-registry.yaml
  - Gate 11: APPROVED by Babar Raza 2026-06-05 (FODS, FODT, Netpbm)
  - commercial_product_ready: false (all entries)

§1 Non-Negotiable Operating Rules (~20 lines):
  - Update rule 6: replace "bundle must be uploaded" with "declaration-driven pipeline"
  - Keep all safety rules intact
  - Remove any stale references

§2 Project Purpose (~15 lines): keep as-is

§3 Desired End State and POC Targets (~40 lines):
  - Merge old §3 (end state table) + §40.2 (11 POC targets)
  - Pointer: "Canonical product target list: product-capability-matrix/poc-targets.yaml"
  - List 3 commercial .NET + 8 FOSS/reduced targets
  - Success criteria from §40.3

§4 Feature Tier Model (~15 lines): keep as-is

§5 Four-Stream Architecture (~30 lines):
  - Condensed from §43: Mainstream, Acceleration, Skills, Supervisor
  - Pointer: docs/governance/four-stream-operating-model.md
  - Cross-stream dependency model (5 lines)

§6 Mainstream Product Lane (~15 lines):
  - Pointer: docs/governance/mainstream-poc-mega-train.md
  - Product-output floor pointer
  - Dogfooding requirement (5 lines from §40.4)

§7 Acceleration Layer (~15 lines):
  - Pointer: docs/governance/acceleration-definition.md

§8 Skills / Governed Execution (~15 lines):
  - Pointer: .supervisor/skill-registry.yaml
  - Product Factory Acceleration Layer summary

§9 Autonomous Supervisor (~15 lines):
  - Pointer: docs/governance/autonomous-supervisor-role.md
  - Declaration-driven pipeline summary
  - Continuous autonomous loop protocol (5 lines)

§10 AI Authority Boundary (~10 lines):
  - Pointer: docs/governance/ai-authority-boundary.md
  - "AI thinks and drafts. Evidence decides."

§11 External Tool Architecture (~10 lines):
  - Pointer: docs/governance/external-tool-architecture.md

§12 Evidence and Review Package Model (~15 lines):
  - Declaration-driven model: evidence-declaration.yaml + autonomous_cycle.py
  - Review package build command
  - 8-level grading model summary

§13 Gate Model (~20 lines):
  - 11 gates with required artifacts (table from §20)
  - All gates require human approval
  - WIP limits updated for multi-format reality

§14 Phase Model (~25 lines):
  - Condensed from §8: Phase 0-4+ definitions
  - Forbidden paths table (from §10)

§15 Legal and Oracle Models (~15 lines):
  - 6 legal categories (from §21)
  - Spec-is-authority oracle rule (from §22)

§16 Decision Register (~60 lines):
  - All DECs from §26, condensed notes
  - Risk summary (10 lines, from §29)

§17 Current Status Summary (~20 lines):
  - NO narrative — source pointers only:
    - Product targets: poc-targets.yaml
    - Current sprint: session-resume.md
    - Format status: format-registry.yaml
    - Gate approvals: approval-gates.md
  - Gate 11 status: APPROVED by Babar Raza 2026-06-05 (FODS, FODT, Netpbm)
  - commercial_product_ready: false

§18 Governance, Visibility, Release Control (~20 lines):
  - Pointer: docs/governance/master-plan-canonical-source-map.md
  - Pointer: docs/governance/master-plan-sync-policy.md
  - Visibility classes summary (from §17)

§19 Memory Layer (~10 lines):
  - Authority hierarchy (from §35)
  - Required memory files

§20 Agent Instructions (~10 lines):
  - Top 10 rules (from §34)
  - Plan/execution mode table (from §12)

§21 Independent Authority Layers (~15 lines):
  - Core principle (from §44.1)
  - Pointer: docs/governance/independent-authority-layers.md
  - Spec authority and requirement/capability authority status

ARCHIVE-PTR block (~10 lines):
  - Pointer: docs/history/master-plan-full-before-healing-2026-06-10.md
  - Pointer: docs/history/master-plan-archived-sections-2026-06-10.md
  - List: "Archived sections: §7, §9, §25, §27, §28, §31, §32, §33, §36, §37, §39"

Footer (~3 lines):
  - version 3.0, execution date, authority statement
```

### Critical Rules During Editing:

1. **Never use the word "delete"** — always "archive and replace with pointer"
2. **Every archived section must have a pointer** in the healed master plan
3. **All DECs must be preserved** (condensed, not removed)
4. **No commercial_product_ready: true** — safety check
5. **Header and footer versions must match**
6. **Codex references removed** from active operations
7. **"No functional commands exist" removed** — 25 commands exist
8. **"bundle must be uploaded by human" removed** — declaration-driven pipeline is current
9. **"Product stages: 1 format" removed** — 11 active targets
10. **POC targets pointer to poc-targets.yaml** — not inline copy

---

## PHASE 6: VALIDATION (TC-MP-EXEC-014)

Run all validation commands and record results in `reports/master-plan-healing-execution/validation-results.md`:

```bash
# 1. Line count in target range
wc -l plans/master-plan.md
# Expected: 400-700

# 2. No stale claims remain
grep -c "No functional commands exist" plans/master-plan.md
# Expected: 0

grep -c "bundle must be uploaded by human" plans/master-plan.md
# Expected: 0

grep -c "Product stages.*1 format" plans/master-plan.md
# Expected: 0

grep -c "Codex.*optional secondary" plans/master-plan.md
# Expected: 0

# 3. Version consistency
head -10 plans/master-plan.md | grep "Version"
tail -5 plans/master-plan.md | grep "version"
# Both must show same version (3.0)

# 4. Archive files exist
ls docs/history/master-plan-full-before-healing-2026-06-10.md
ls docs/history/master-plan-archived-sections-2026-06-10.md

# 5. New governance docs exist
ls docs/governance/master-plan-canonical-source-map.md
ls docs/governance/master-plan-sync-policy.md

# 6. SHA-256 pre-edit recorded
cat reports/master-plan-healing-execution/preedit-sha.txt

# 7. No forbidden files modified
git diff --name-only -- src/net src/python tests registry product-capability-matrix
# Expected: no output

# 8. ARCHIVE-PTR block exists
grep -c "ARCHIVE-PTR" plans/master-plan.md
# Expected: >= 1

# 9. POC targets pointer exists
grep -c "poc-targets.yaml" plans/master-plan.md
# Expected: >= 1

# 10. commercial_product_ready safety check
grep -c "commercial_product_ready.*true" plans/master-plan.md
# Expected: 0

# 11. Gate 11 approved reference exists
grep -c "APPROVED.*Babar Raza.*2026-06-05" plans/master-plan.md
# Expected: >= 1

# 12. Declaration-driven pipeline referenced
grep -c "declaration-driven\|evidence-declaration.yaml\|autonomous_cycle" plans/master-plan.md
# Expected: >= 1
```

---

## PHASE 7: STALE-CLAIM LINT (TC-MP-EXEC-015)

Run 10 grep patterns on the HEALED master plan and classify each finding:

1. `COMMERCIAL-LOAD-SAVE-VERTICAL-SLICE` — should return 0 (or HISTORICAL_OK only)
2. `No functional commands exist` — must return 0
3. `bundle must be uploaded by human` — must return 0
4. `Product stages.*1 format` — must return 0
5. `Codex` — must return 0 (or HISTORICAL_OK in decision register only)
6. `SVG` — check for "replace Netpbm" pattern (should not exist)
7. `commercial_product_ready.*true` — must return 0
8. `not yet authorized` — check context (OK in backlog references)
9. Old run numbers `run015|run016|run017|run027` — should return 0 (archived)
10. Old sprint names `QUARTER-MILE|SWARM-001` — should return 0 (archived)

Write results to `reports/master-plan-healing-execution/stale-claim-lint-report.md`

If any FALSE_CLAIM or STALE_CLAIM found: fix them in plans/master-plan.md before proceeding.

---

## PHASE 8: EVIDENCE PACKAGE (TC-MP-COORD-004)

### Write .local/evidences/master-plan-healing-execution/evidence-declaration.yaml

```yaml
sprint_id: FORMAT-FACTORY-MASTER-PLAN-HEALING-EXECUTION-001
run_id: master-plan-healing-execution
worker_id: claude-code
timestamp: <ISO-8601>
declared_scope: "Master plan healing — 2229 lines to 400-700 lines with archive safety"
planned_work_items:
  - item_id: TC-MP-COORD-001
    title: "Preflight"
    status: completed
  - item_id: TC-MP-COORD-002
    title: "Backup"
    status: completed
  - item_id: TC-MP-COORD-003
    title: "Archive map"
    status: completed
  - item_id: TC-MP-EXEC-001
    title: "Canonical source map"
    status: completed
  - item_id: TC-MP-EXEC-002
    title: "Sync policy"
    status: completed
  - item_id: TC-MP-EXEC-003
    title: "Rewrite header"
    status: completed
  - item_id: TC-MP-EXEC-004
    title: "Condense §1"
    status: completed
  - item_id: TC-MP-EXEC-005
    title: "Merge §3+§40.2, rewrite §5, condense §6"
    status: completed
  - item_id: TC-MP-EXEC-006
    title: "Archive §7, §9"
    status: completed
  - item_id: TC-MP-EXEC-007
    title: "Rewrite §11, §13"
    status: completed
  - item_id: TC-MP-EXEC-008
    title: "Rewrite §24"
    status: completed
  - item_id: TC-MP-EXEC-009
    title: "Archive §25, §27, §28, §31, §32, §33"
    status: completed
  - item_id: TC-MP-EXEC-010
    title: "Archive §36, §37, §39"
    status: completed
  - item_id: TC-MP-EXEC-011
    title: "Merge §40-§43"
    status: completed
  - item_id: TC-MP-EXEC-012
    title: "Condense §26, §29, §44"
    status: completed
  - item_id: TC-MP-EXEC-013
    title: "Add ARCHIVE-PTR + footer"
    status: completed
  - item_id: TC-MP-EXEC-014
    title: "Validation"
    status: completed
  - item_id: TC-MP-EXEC-015
    title: "Stale-claim lint"
    status: completed
  - item_id: TC-MP-COORD-004
    title: "Evidence package"
    status: completed
completed_work_items:
  - TC-MP-COORD-001
  - TC-MP-COORD-002
  - TC-MP-COORD-003
  - TC-MP-EXEC-001
  - TC-MP-EXEC-002
  - TC-MP-EXEC-003
  - TC-MP-EXEC-004
  - TC-MP-EXEC-005
  - TC-MP-EXEC-006
  - TC-MP-EXEC-007
  - TC-MP-EXEC-008
  - TC-MP-EXEC-009
  - TC-MP-EXEC-010
  - TC-MP-EXEC-011
  - TC-MP-EXEC-012
  - TC-MP-EXEC-013
  - TC-MP-EXEC-014
  - TC-MP-EXEC-015
  - TC-MP-COORD-004
evidence_artifacts:
  - path: reports/master-plan-healing-execution/preflight.md
    type: preflight
  - path: reports/master-plan-healing-execution/preedit-sha.txt
    type: sha256
  - path: docs/history/master-plan-full-before-healing-2026-06-10.md
    type: backup
  - path: docs/history/master-plan-archived-sections-2026-06-10.md
    type: archive
  - path: docs/governance/master-plan-canonical-source-map.md
    type: governance
  - path: docs/governance/master-plan-sync-policy.md
    type: governance
  - path: reports/master-plan-healing-execution/archive-pointer-map.json
    type: archive_map
  - path: reports/master-plan-healing-execution/validation-results.md
    type: validation
  - path: reports/master-plan-healing-execution/stale-claim-lint-report.md
    type: lint
test_results:
  passed: 12
  failed: 0
  skipped: 0
  errors: 0
worker_self_grade: PASS
worker_self_verdict: MASTER_PLAN_HEALED_READY_FOR_REVIEW
explicit_no_edit_statement: "src/net/*, src/python/*, tests/*, registry/format-registry.yaml, product-capability-matrix/poc-targets.yaml were NOT edited."
```

### Build review package

```bash
.local/venv/Scripts/python tools/supervisor/build_declaration_review_package.py \
  --declaration .local/evidences/master-plan-healing-execution/evidence-declaration.yaml
```

### Write reports/master-plan-healing-execution/review-package-proof.md

- Absolute ZIP path
- SHA-256 of ZIP
- Entry count
- Validation result

---

## ROLLBACK PROCEDURE

If the edit fails at any point:
1. `cp docs/history/master-plan-full-before-healing-2026-06-10.md plans/master-plan.md`
2. `sha256sum plans/master-plan.md` — verify matches preedit-sha.txt
3. Delete any partially-created files in docs/history/ and docs/governance/
4. Re-attempt from Phase 3

---

## FINAL RESPONSE CONTRACT

The execution agent must report:

1. **Sprint ID:** FORMAT-FACTORY-MASTER-PLAN-HEALING-EXECUTION-001
2. **Verdict:** MASTER_PLAN_HEALED_READY_FOR_REVIEW or HEALING_INCOMPLETE_NEEDS_REWORK
3. **Pre-edit SHA-256:** (from preedit-sha.txt)
4. **Post-edit line count:** (from wc -l)
5. **Archived sections count:** 11
6. **New governance docs created:** 2
7. **Stale claims remaining:** 0 (or list them)
8. **Validation results:** 12/12 pass (or list failures)
9. **Review package absolute path:** C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\supervisor\reviews\master-plan-healing-execution\declaration-review-package.zip
10. **Review package SHA-256:** (computed)
11. **Files NOT edited:** src/net/*, src/python/*, tests/*, registry/*, product-capability-matrix/*

---

## ALLOWED VERDICTS

- **MASTER_PLAN_HEALED_READY_FOR_REVIEW** — All edits complete, all validations pass, evidence package built
- **HEALING_INCOMPLETE_NEEDS_REWORK** — Some edits failed or validations failed; list what remains
- **HEALING_BLOCKED** — Cannot proceed due to external dependency; describe blocker

---

*This prompt is self-contained. An agent with no prior context can execute it to produce the healed master plan.*
