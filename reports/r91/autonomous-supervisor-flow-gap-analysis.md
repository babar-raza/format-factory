---
sprint: R91
generated_by: r91-worker
---

# Autonomous Supervisor Flow — Gap Analysis

## Current Flow (Actual)

```
agent completes work
  → agent builds ZIP bundle
  → supervisor discovers ZIP (watch/discover pattern)
  → supervisor validates bundle (structural checks)
  → supervisor grades globally (PASS / FAIL for entire bundle)
  → supervisor generates next-sprint.md
  → session-resume.md regenerated
```

## Required Flow (Target)

```
agent declares evidence-declaration.yaml
  → supervisor inspects declared artifacts, code, logs, reports
  → supervisor grades each work item individually:
      accepted | rework | overclaimed | insufficient | blocked | deferred
  → supervisor returns failed items as rework lanes
  → supervisor selects new POC work from master plan (poc-targets.yaml)
  → supervisor generates next-sprint.md with:
      Section 1: new product work lanes (from poc-targets.yaml)
      Section 2: rework lanes (from failed items)
      Section 3: context pack (sprint state, key files, SHAs)
  → agent reads next-sprint.md and continues
  → autonomous_continue: true (if no hard stops)
```

## Identified Gaps

### G1 — No Item-by-Item Grades

**Current:** Supervisor outputs a single bundle-level PASS/FAIL verdict.

**Required:** Supervisor outputs per-item grades in `reports/supervisor/work-item-grades.md` and `reports/supervisor/work-item-grades.json`. Each item declared in `evidence-declaration.yaml` gets one of: `accepted`, `rework`, `overclaimed`, `insufficient`, `blocked`, `deferred`.

**Addressed by:** Train D (implementation), Train V (output artifacts)

---

### G2 — Continuation Blocked by Inherited Failures Not Attributable to Current Sprint

**Current:** 12 pre-existing test failures prevent `autonomous_continue: true`. The continuation signal treats all failures equally regardless of origin.

**Required:** Continuation signal respects failure classification. Pre-existing failures classified before sprint start do not block continuation for new work.

**Addressed by:** Train C (repair inherited failures), Train F (classification protocol in policies)

---

### G3 — Next Sprint Does Not Mix Rework + New Product Work

**Current:** `next-sprint.md` either leads with repair tasks or with product tasks — not a structured blend.

**Required:** `next-sprint.md` always has: (1) new product lanes first, (2) rework lanes second, (3) context pack third. Product work is never demoted below repair work.

**Addressed by:** Train E (next-sprint generator update)

---

### G4 — No Context Pack in Generated Sprint

**Current:** Generated `next-sprint.md` does not include a context pack section (key SHAs, key file paths, continuation state).

**Required:** Context pack section embedded in every generated `next-sprint.md`. Contains: previous sprint SHA, key changed files, continuation iteration count, known blockers.

**Addressed by:** Train K (context pack definition), Train E (generator embeds context pack)

---

### G5 — Review Package Too Shallow (Cosmetic — Defer)

**Current:** Review package has 8 entries. Does not include raw test logs, package artifacts at top level, or raw .NET logs.

**Required (eventual):** Full review package with `--extra-top-level-dirs` for package-artifacts/, raw-install-logs/, raw-dotnet-logs/, raw-test-logs/, raw-negative-proof-logs/.

**Status:** COSMETIC — deferred. The 4-tool build chain (established R83) handles this when explicitly invoked. Product work takes priority.

---

## Gap Closure Summary

| Gap | Severity | Sprint | Trains |
|-----|----------|--------|--------|
| G1 — No item-by-item grades | HIGH | R91 | D, V |
| G2 — Inherited failures block continuation | MEDIUM | R91 | C, F |
| G3 — Next sprint no rework+product mix | HIGH | R91 | E |
| G4 — No context pack in generated sprint | MEDIUM | R91 | K, E |
| G5 — Review package shallow | LOW | Defer | — |

## Flow Healing Declaration

All HIGH and MEDIUM gaps are addressed within R91. After R91 closeout, the autonomous supervisor flow will support:

- Per-item grading from `evidence-declaration.yaml`
- Rework lanes fed back into next sprint
- New POC work selected from `poc-targets.yaml`
- Context pack embedded in every generated sprint prompt
- Pre-existing failure classification preventing false continuation blocks
