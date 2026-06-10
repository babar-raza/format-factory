# R104 Package Identity Audit

**Audit ID:** R105-TRAIN-A-PACKAGE-IDENTITY-AUDIT
**Target:** `.local/supervisor/reviews/acceleration-r104/declaration-review-package.zip`
**Run ID:** `acceleration-r104`
**Sprint ID:** `FORMAT-FACTORY-ACCELERATION-R104-PACKAGED-ADOPTION-AND-STREAM-PROMPT-CORRECTION-CAMPAIGN-001`
**Expected Stream:** acceleration
**Total ZIP entries:** 68

---

## Executive Summary

The R104 acceleration review package contains **13 cross-stream contaminated files** (WRONG_STREAM), all originating from the same root cause: the package builder copies global supervisor state files from `reports/supervisor/*` and `.supervisor/context-pack.yaml`, which are overwritten by whichever stream runs `autonomous-cycle` last. In this case, `skills-r103` ran after `acceleration-r104`, so those global files reflect the skills stream.

The per-run artifacts (review/, sprint-evidence/, evidence/, materialized/) are all correctly scoped to acceleration-r104. The contamination is confined to the supervisor/ and state/ subfolders.

| Status | Count | Description |
|--------|-------|-------------|
| MATCH | 47 | Correctly belongs to acceleration-r104 |
| WRONG_STREAM | 13 | Contains sprint ID or content from a different stream |
| STALE | 3 | Contains outdated or cross-stream data (informational) |
| HISTORICAL_OK | 1 | Pre-stream historical artifact, acceptable |
| UNVERIFIABLE | 4 | Global/static content with no stream marker |

---

## Root Cause Analysis

### The Global State Overwrite Problem

The package builder (`tools/supervisor/build_declaration_review_package.py`) has two collection strategies:

1. **Per-run outputs** (from `.local/supervisor/reviews/<run_id>/`) -- These are stream-correct because each autonomous-cycle writes them to a run-specific subfolder. They end up in `review/` inside the ZIP.

2. **Global supervisor state** (from `reports/supervisor/*`, `.supervisor/context-pack.yaml`, `.local/supervisor/continuation-signal.json`) -- These are **singleton files** that every stream overwrites. Whichever stream runs last wins.

The execution order was:
```
supervisor-r103  --> overwrote reports/supervisor/* with supervisor-r103 data
mainstream-r105  --> overwrote reports/supervisor/* with mainstream-r105 data
acceleration-r104 --> overwrote reports/supervisor/* with acceleration-r104 data
skills-r103      --> overwrote reports/supervisor/* with skills-r103 data   <-- LAST WRITER
mainstream-r106  --> overwrote reports/supervisor/* with mainstream-r106 data  <-- current global state
```

When `build_declaration_review_package.py` ran for acceleration-r104, the global state already reflected skills-r103 (or possibly a later run). The builder blindly copied these stale global files into the ZIP.

### Why the supervisor/supervisor-cycle-manifest.yaml Is Correct

This file happens to be correct (acceleration-r104) because it was written by the acceleration-r104 cycle itself and the subsequent skills-r103 cycle may not have overwritten this specific file (or the package builder sourced it from the per-run review folder).

---

## Detailed Contamination Map

### WRONG_STREAM Files (13 total)

All 13 files share the same root cause: copied from global singleton state that was last written by a different stream.

#### Contaminated by skills-r103 (10 files)

| ZIP Path | Actual Sprint | Notes |
|----------|--------------|-------|
| `supervisor/latest-cycle-summary.md` | skills-r103 | Run = skills-r103, verdict = ACCEPTED |
| `supervisor/session-resume.md` | skills-r103 | Last sprint = skills-r103, tests: 29 passed |
| `supervisor/approval-gates.md` | skills-r103 | Sprint ID = skills-r103 |
| `supervisor/next-sprint.md` | skills-r103 | Source sprint = skills-r103; stream label says "mainstream" |
| `supervisor/work-item-grades.json` | skills-r103 | Contains W0-R102-RECONCILIATION..W8-STRATEGY (skills items) |
| `supervisor/work-item-grades.md` | skills-r103 | Same as JSON |
| `supervisor/work-item-grades.yaml` | skills-r103 | Same as JSON |
| `supervisor/materialized-evidence-review.md` | skills-r103 | Run ID = skills-r103 |
| `state/context-pack.yaml` | skills-r103 | latest_sprint.sprint_id = skills-r103 |
| `state/context-pack.md` | skills-r103 | Latest sprint = R103 (skills) |

#### Contaminated by supervisor-r103 (2 files)

| ZIP Path | Actual Sprint | Notes |
|----------|--------------|-------|
| `supervisor/evidence-review.md` | supervisor-r103 | Sprint ID = supervisor-r103 |
| `supervisor/contradictions.md` | supervisor-r103 | Sprint ID = supervisor-r103 |

#### Contaminated by skills-r103 loop state (1 file)

| ZIP Path | Actual Sprint | Notes |
|----------|--------------|-------|
| `state/continuation-signal.json` | skills-r103 | source_sprint_id = skills-r103, iteration 7/12 |

---

## STALE Files (3 total)

| ZIP Path | Actual Sprint | Notes |
|----------|--------------|-------|
| `state/product-code-change-ledger.json` | mainstream-r106 | Global shared ledger; latest_sprint = mainstream-r106 |
| `state/selected-product-gaps.json` | R98 (pre-stream) | Generated at R98, mainstream gaps only |
| `r91-review/r91-work-item-grades.md` | R92 (pre-stream) | Historical review from pre-stream era |

---

## Correct Artifacts (MATCH: 47)

These are all correctly scoped to acceleration-r104:

- **evidence/** (2 files): declaration + manifest
- **package-manifest.json** (1 file)
- **review/** (12 files): all per-run supervisor review outputs
- **sprint-evidence/** (26 files): all walked from evidence_root `reports/acceleration-r104/` plus changed tools/tests
- **materialized/** (3 files): per-run materialization outputs
- **supervisor/supervisor-cycle-manifest.yaml** (1 file): happened to be correct
- **supervisor/mcp-status.md + mcp-status.json** (2 files): global MCP config, stream-neutral (UNVERIFIABLE but functionally correct)

---

## Impact Assessment

### What This Means for Package Reviewers

A reviewer inspecting the R104 package would see:
- `supervisor/work-item-grades.md` listing skills-r103 work items (W0-R102-RECONCILIATION, W1-EVIDENCE-MANIFEST, etc.) instead of the actual acceleration-r104 items (ACCEL-R104-W0 through W6).
- `supervisor/session-resume.md` saying "Last sprint: skills-r103" instead of acceleration-r104.
- `state/context-pack.yaml` with iteration 7/12 from the skills loop, not the acceleration loop.

However, the `review/` subfolder contains the correct acceleration-r104 review. A reviewer who knows to look at `review/supervisor-review.md` instead of `supervisor/work-item-grades.md` will get the right data.

### Severity: MEDIUM

The contamination does not affect the correctness of the supervisor verdict (ACCEPTED with 7/7 items). The correct data exists in the `review/` folder. But the duplicate/conflicting data in `supervisor/` creates confusion and could mislead automated consumers.

---

## Recommended Fix (for future sprints, not implemented here)

The package builder should:

1. **Source supervisor state from per-run outputs** (`.local/supervisor/reviews/<run_id>/`) instead of global `reports/supervisor/*`.
2. **Or snapshot global state at autonomous-cycle time** into the per-run folder before any subsequent stream can overwrite it.
3. **Add a stream-identity validator** that checks every file's sprint ID against the declared run_id before including it in the ZIP.
4. **Remove or namespace the `supervisor/` folder** in the ZIP to avoid confusion with the authoritative `review/` folder.

---

## Structured Matrix

See `reports/acceleration-r105/r104-package-identity-matrix.json` for the machine-readable matrix with per-file status, detected stream, and notes.
