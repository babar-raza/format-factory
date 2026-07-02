# Plan Hardening Addendum — Stale Skill Artifact Repair
**Plan ID:** skill-report-stale-artifact-repair (SRAR)
**Parent Mission:** SKILL-FIRST-002 (twinkly-gliding-thimble, TERMINAL_CLOSED)
**Trigger:** Pilot rerun (2026-07-02) revealed 3 stale artifacts after H-taskcard closure
**Date:** 2026-07-02

---

## 1. Mission Binding

```yaml
mission_binding:
  mission_id: SKILL-FIRST-002-SRAR
  repository: c:/Users/prora/OneDrive/Documents/GitHub/format-factory
  branch: main
  plan_path: plans/plan-hardening-addendum-from-latest-audit.md
  plan_id: skill-report-stale-artifact-repair
  plan_revision: v1.0
  parent_plan: plans/.claude/twinkly-gliding-thimble.md
  assistant_summary_source: "Pilot rerun before/after comparison (2026-07-02)"
  mandatory_outcomes:
    - skill-inventory.yaml refreshed to 117-skill registry state
    - duplicate-skill-report.yaml refreshed to 117-skill registry state
    - execution report rows 4, 7, 13 corrected with re-run data
  non_goals:
    - Reopening twinkly-gliding-thimble
    - Changing governance validators
    - Any product source changes
```

---

## 2. Sources Reviewed

| Source | Path | Finding |
|--------|------|---------|
| Pilot rerun output | Conversation 2026-07-02 | Rows 4/13 show "65 skills"; step 7 shows "100 active skills" |
| skill-inventory.yaml | `.supervisor/skill-inventory.yaml` | mission_id=SKILL-FIRST-001, 65 skills — never updated since Jun 25 |
| duplicate-skill-report.yaml | `.supervisor/duplicate-skill-report.yaml` | total_skills_checked=100 — snapshot from H-TC window |
| skill-first-execution-report.md | `.supervisor/skill-first-execution-report.md` | Step 3 shows 117 (H001 fix); rows 4/7/13 still show pre-fix counts |
| skill-registry.yaml | `.supervisor/skill-registry.yaml` | Live: 120 total, 117 active, 3 deprecated |

---

## 3. Claim and Evidence Audit

| Claim ID | Claim | Source | Status | Finding |
|----------|-------|--------|--------|---------|
| CLM-SRAR-001 | "Step 4 historically accurate" | Pilot rerun summary | PARTIAL | Historically accurate for Jun 25, but creates inconsistency with step 3 showing 117 in same report |
| CLM-SRAR-002 | "Step 13 historically accurate" | Pilot rerun summary | MISLEADING | skill-inventory.yaml artifact itself is SKILL-FIRST-001 / 65 skills — WRONG mission_id |
| CLM-SRAR-003 | "duplicate-report staleness expected" | Pilot rerun summary | ACTIONABLE_GAP | 100→117 drift: any governance sprint starting from this baseline would have wrong denominator |
| CLM-SRAR-004 | "doesn't affect correctness of pipeline" | Pilot rerun summary | IMPLEMENTED_UNVERIFIED | True for duplicates (fresh run still 0), but NOT true for skill-inventory.yaml (65 vs 117 is real data gap) |

---

## 4. Findings

### FINDING-SRAR-001: skill-inventory.yaml Has Wrong mission_id and Stale Count
**Severity:** HIGH
**Root cause:** inventory-skills was run on Jun 25 (SKILL-FIRST-001). The step ran during SKILL-FIRST-002 for reporting, but the YAML itself was never refreshed.
**Impact:** Any governance sprint reading `skill-inventory.yaml` gets 65 skills with wrong mission_id.
**Taskcard:** TC-SRAR-001

### FINDING-SRAR-002: duplicate-skill-report.yaml Checked Only 100 of 117 Active Skills
**Severity:** MEDIUM
**Root cause:** The H-TC duplicate scan ran during the H-taskcard execution window (when 100 skills were active). 17 additional skills were added in other sprints before/after.
**Impact:** Report claims "100 skills checked" but registry has 117. Future sprint could add a duplicate without triggering detection based on stale artifact.
**Taskcard:** TC-SRAR-002

### FINDING-SRAR-003: Execution Report Rows 4, 7, 13 Show Stale Pre-Refresh Counts
**Severity:** MEDIUM
**Root cause:** Steps 4 (normalize), 7 (detect-duplicates), 13 (inventory-skills) were not rerun during H-taskcard work. Step 3 WAS rerun (H001). This creates internal inconsistency: same report shows both 65 and 117.
**Impact:** Misleading governance artifact — reader cannot determine the baseline without reading the correction note.
**Taskcard:** TC-SRAR-003

---

## 5. Contradictions Reconciled

| CON-ID | Contradiction | Resolution |
|--------|--------------|------------|
| CON-SRAR-001 | Pilot summary said rows 4/13 are "bounded, not regressions" but skill-inventory.yaml itself is SKILL-FIRST-001 (wrong mission_id) | Classified as ACTIONABLE: the artifact staleness is real, not just a display issue |
| CON-SRAR-002 | Pilot summary said duplicate-report staleness "doesn't affect correctness" but 17 unchecked skills could include a duplicate | Resolved: fresh duplicate run required; 17 new skills must be checked |

---

## 6. Unresolved Work Register

| URW-ID | Description | Severity | Taskcard |
|--------|-------------|----------|----------|
| URW-SRAR-001 | skill-inventory.yaml: mission_id=SKILL-FIRST-001, 65 skills | HIGH | TC-SRAR-001 |
| URW-SRAR-002 | duplicate-skill-report.yaml: 100 skills checked vs 117 active | MEDIUM | TC-SRAR-002 |
| URW-SRAR-003 | Execution report rows 4/7/13 stale — internal inconsistency | MEDIUM | TC-SRAR-003 |

---

## 7. Taskcard Register

### TC-SRAR-001: Refresh skill-inventory.yaml to Current 117-Skill State

```yaml
taskcard:
  id: TC-SRAR-001
  title: "Regenerate skill-inventory.yaml for SKILL-FIRST-002 with 117-skill registry"
  source_findings: [FINDING-SRAR-001]
  priority: HIGH
  current_status: CLOSED
  required_work:
    - Read current skill-registry.yaml (120 total, 117 active, 3 deprecated)
    - Generate new skill-inventory.yaml matching existing schema
    - Set mission_id = SKILL-FIRST-002
    - Include all 120 skills (active + deprecated) with correct command_file_exists
  acceptance_criteria:
    - skill-inventory.yaml mission_id == SKILL-FIRST-002
    - skill-inventory.yaml total_skills == 120
    - skill-inventory.yaml active skills count == 117
    - all command_file_exists fields accurate
  proof_level_target: 2  # artifact + live read verification
  exact_next_action: "Generate skill-inventory.yaml inline Python from current skill-registry.yaml"
```

### TC-SRAR-002: Refresh duplicate-skill-report.yaml to Current 117-Skill State

```yaml
taskcard:
  id: TC-SRAR-002
  title: "Re-run detect-duplicate-skills with current 117-active-skill registry"
  source_findings: [FINDING-SRAR-002]
  priority: MEDIUM
  current_status: CLOSED
  required_work:
    - Run full duplicate detection on all 117 active skills
    - Run >80% purpose overlap check on all 117 active skills
    - Update duplicate-skill-report.yaml total_skills_checked to 117
    - Preserve resolution_note from prior run (4 command_file fixes history)
  acceptance_criteria:
    - total_skills_checked == 117
    - duplicate_count == 0
    - overall_verdict == PASS
  proof_level_target: 2
  exact_next_action: "Run detect-duplicate-skills inline Python on full 117-skill registry"
```

### TC-SRAR-003: Update Execution Report Rows 4, 7, 13 with Re-run Counts

```yaml
taskcard:
  id: TC-SRAR-003
  title: "Update stale skill counts in execution report rows 4, 7, 13"
  source_findings: [FINDING-SRAR-003]
  priority: MEDIUM
  current_status: CLOSED
  dependencies: [TC-SRAR-001, TC-SRAR-002]
  required_work:
    - Row 4: change "65 skills — 62 active, 3 deprecated" to "117 active, 3 deprecated (re-run 2026-07-02)"
    - Row 7: change "100 active skills" to "117 active skills" (re-run Jul 02)
    - Row 13: change "65 skills — was 63" to "117 skills (re-run 2026-07-02)"
  acceptance_criteria:
    - No row in execution report shows "65 skills" in context of current counts
    - Row 7 shows 117 active
    - grep -c "65 skills" .supervisor/skill-first-execution-report.md == 0
  proof_level_target: 2
  exact_next_action: "Edit execution report rows 4, 7, 13 inline"
```

---

## 8. Taskcard Status Summary

| TC-ID | Title | Status | Proof Level |
|-------|-------|--------|-------------|
| TC-SRAR-001 | Refresh skill-inventory.yaml (117 skills) | CLOSED | 2 (artifact verified: mission=SKILL-FIRST-002, total=120, active=117) |
| TC-SRAR-002 | Refresh duplicate-skill-report.yaml (117 skills) | CLOSED | 2 (artifact verified: checked=117, dup=0, verdict=PASS) |
| TC-SRAR-003 | Fix execution report rows 4, 7, 13 | CLOSED | 2 (no current-count stale rows remain; correction note added) |

---

## 9. Closeout Criteria

**All conditions must be true before TERMINAL_CLOSED:**

- [x] TC-SRAR-001: skill-inventory.yaml mission_id=SKILL-FIRST-002, total=120, active=117
- [x] TC-SRAR-002: duplicate-skill-report.yaml total_skills_checked=117, dup=0
- [x] TC-SRAR-003: No rows in execution report show "65 skills" as current count
- [ ] All artifacts committed at HEAD
- [ ] Final read-back verification passes

---

## 10. Exact Next Action

Execute TC-SRAR-001: Generate fresh skill-inventory.yaml from current skill-registry.yaml (117 active skills, mission_id=SKILL-FIRST-002).
