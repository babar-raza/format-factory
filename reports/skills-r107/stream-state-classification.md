# Stream-State Classification -- Skills R107
# Generated: 2026-06-03
# Prior report: reports/skills-r106/stream-state-classification.md

## Purpose

Investigate and document the stream-state contamination in `reports/supervisor/` and
the `artifacts_missing_count=1` issue reported by `build_declaration_review_package.py`
for both skills-r106 and acceleration-r106.

---

## Part 1: Global State File Contamination

### Current State (post-Supervisor-R106 cycle)

The Supervisor stream was the last to run `autonomous-cycle`, so all global state files
now reference `FORMAT-FACTORY-SUPERVISOR-R106-STREAM-CLEAN-CYCLE-ENFORCEMENT-RAW-LOGS-AND-STRICT-GRADING-001`.

| # | File | Current Sprint ID | Current Stream | Classification |
|---|------|-------------------|----------------|----------------|
| 1 | `reports/supervisor/session-resume.md` | SUPERVISOR-R106 | supervisor | SUPERVISOR_PRIMARY |
| 2 | `reports/supervisor/evidence-review.json` | SUPERVISOR-R106 | supervisor | SUPERVISOR_PRIMARY |
| 3 | `reports/supervisor/contradictions.json` | SUPERVISOR-R106 | supervisor | SUPERVISOR_PRIMARY |
| 4 | `reports/supervisor/evidence-review.md` | ACCELERATION-R106 | acceleration | WRONG_STREAM (stale from prior cycle) |
| 5 | `reports/supervisor/latest-review.md` | SUPERVISOR-R106 | supervisor | SUPERVISOR_PRIMARY |
| 6 | `reports/supervisor/latest-cycle-summary.md` | SUPERVISOR-R106 | supervisor | SUPERVISOR_PRIMARY |
| 7 | `reports/supervisor/next-sprint.md` | SUPERVISOR-R106 | supervisor | SUPERVISOR_PRIMARY |
| 8 | `reports/supervisor/approval-gates.md` | SUPERVISOR-R106 | supervisor | SUPERVISOR_PRIMARY |
| 9 | `reports/supervisor/discovery-summary.md` | ACCELERATION-R106 | acceleration | WRONG_STREAM (stale) |
| 10 | `reports/supervisor/memory-sync-report.md` | ACCELERATION-R106 | acceleration | WRONG_STREAM (stale) |
| 11 | `.supervisor/context-pack.yaml` | (last rebuilt by supervisor-r106 cycle) | mixed | GLOBAL_CONTEXT |
| 12 | `.local/supervisor/selected-product-gaps.json` | R98 | stale | STALE_PRIMARY |

### Key Observation: evidence-review.md vs evidence-review.json Mismatch

`evidence-review.md` references `FORMAT-FACTORY-ACCELERATION-R106-...` (292 tests, 81 entries)
while `evidence-review.json` references `FORMAT-FACTORY-SUPERVISOR-R106-...` (722 tests, 7 entries).
These two files disagree because they are written by different steps:

- `evidence-review.md` is written by Step 2c/3 (not overwritten by Step 7)
- `evidence-review.json` is written by Step 7 (`bridge_to_legacy_format`)
- `session-resume.md`, `approval-gates.md`, `next-sprint.md` are written by Step 7b (`generate_packet`)

If streams run in sequence (Skills -> Supervisor -> Mainstream -> Acceleration -> Supervisor),
the Supervisor stream's Step 7 overwrites the JSON files but the `.md` evidence-review is
a separate file written earlier and may persist from a different stream's run.

---

## Part 2: Root Cause Analysis

### Root Cause 1: Step 6 copies latest summaries without stream isolation

`autonomous_cycle.py` Step 6 (lines 274-334) copies review outputs to `reports/supervisor/`:
- `supervisor-review.md` -> `latest-review.md`
- `combined-next-worker-prompt.md` -> `latest-next-worker-prompt.md`
- `item-grades.json` -> `work-item-grades.json`
- `item-grades.yaml` -> `work-item-grades.yaml`
- Plus `work-item-grades.md` and `latest-cycle-summary.md`

All of these go to the same `reports/supervisor/` directory regardless of which stream
produced them. The last stream to run overwrites all prior streams' outputs.

### Root Cause 2: Step 7 bridge_to_legacy_format overwrites JSON state

`autonomous_cycle.py` Step 7 (lines 337-525) writes:
- `reports/supervisor/evidence-review.json`
- `reports/supervisor/contradictions.json`

These are consumed by Step 7b's `generate_packet()` to regenerate the markdown files.

### Root Cause 3: Step 7b generate_packet() overwrites all markdown state

`autonomous_cycle.py` Step 7b (lines 344-353) calls `generate_packet(repo_root, stream=detected_stream)`,
which regenerates:
- `reports/supervisor/session-resume.md`
- `reports/supervisor/approval-gates.md`
- `reports/supervisor/next-sprint.md`

The `stream` parameter (added in R101) ensures the next-sprint prompt is stream-specific,
but the files still go to the shared `reports/supervisor/` directory, overwriting whatever
the previous stream wrote.

### Root Cause 4: Some files are NOT overwritten by Steps 6/7/7b

`evidence-review.md`, `discovery-summary.md`, and `memory-sync-report.md` appear to be
written by earlier steps (or by the build_declaration_review_package.py) and are NOT
refreshed by the Supervisor-R106 cycle's Steps 6/7/7b. This is why they still reference
the Acceleration-R106 stream -- they were last written when the Acceleration stream ran.

---

## Part 3: artifacts_missing_count=1 Investigation

### Observed

Both skills-r106 and acceleration-r106 declaration review packages report
`artifacts_missing_count: 1` in their SHA-256 sidecar files:

```
# skills-r106
.local/supervisor/reviews/skills-r106/declaration-review-package.sha256.json
  "artifacts_missing_count": 1

# acceleration-r106
.local/supervisor/reviews/acceleration-r106/declaration-review-package.sha256.json
  "artifacts_missing_count": 1
```

### Root Cause: Hardcoded evidence_root path in build_declaration_review_package.py

`build_declaration_review_package.py` line 82 computes the evidence manifest location as:

```python
evidence_root = repo_root / ".local" / "evidences" / run_id   # line 82
```

Then on lines 90-91:

```python
manifest_path = evidence_root / "evidence-manifest.yaml"
add_file_to_zip(zf, manifest_path, "evidence/evidence-manifest.yaml", missing)
```

This looks for `evidence-manifest.yaml` at `.local/evidences/{run_id}/evidence-manifest.yaml`.

However, the `autonomous_cycle.py` Step 2b writes the evidence manifest at the declaration's
`evidence_root` path, which differs by stream:

- Skills R106: `evidence_root: reports/skills-r106` -> manifest at `reports/skills-r106/evidence-manifest.yaml`
- Acceleration R106: `evidence_root: reports/acceleration-r106` -> manifest at `reports/acceleration-r106/evidence-manifest.yaml`

The `.local/evidences/{run_id}/` directory only contains `evidence-declaration.yaml` (no manifest).

**Verification:**

```
.local/evidences/skills-r106/               -> only evidence-declaration.yaml
reports/skills-r106/evidence-manifest.yaml   -> EXISTS (written by autonomous_cycle Step 2b)

.local/evidences/acceleration-r106/          -> only evidence-declaration.yaml
reports/acceleration-r106/evidence-manifest.yaml -> EXISTS (written by autonomous_cycle Step 2b)
```

### Classification: Builder Limitation (NOT a real missing artifact)

The `evidence-manifest.yaml` file exists -- it is just not where the builder expects it.
The builder hardcodes `.local/evidences/{run_id}/` instead of reading the declaration's
`evidence_root` field. Meanwhile, `autonomous_cycle.py` Step 2b writes the manifest to
`{declaration.evidence_root}/evidence-manifest.yaml`.

The materialized evidence manifests (`.local/supervisor/materialized/{run_id}/`) correctly
report `artifacts_missing: 0` because the materializer reads the declaration's evidence_root.

### Fix (for Supervisor stream)

In `build_declaration_review_package.py`, change line 90-91 from:

```python
manifest_path = evidence_root / "evidence-manifest.yaml"
```

to:

```python
decl_evidence_root = decl.get("evidence_root", "")
manifest_path = (repo_root / decl_evidence_root / "evidence-manifest.yaml") if decl_evidence_root else (evidence_root / "evidence-manifest.yaml")
```

This would find the manifest at its actual location. Alternatively, `autonomous_cycle.py`
Step 2b could write a copy to `.local/evidences/{run_id}/` as well.

---

## Part 4: Comparison with R106 Classification

| Issue | R106 Classification | R107 Classification | Delta |
|-------|--------------------|--------------------|-------|
| Global state contamination | 3 SKILLS_PRIMARY, 2 WRONG_STREAM, 1 STALE | All now SUPERVISOR (supervisor ran last) | REGRESSED (as predicted) |
| next-sprint.md stream label | WRONG (mainstream label) | CORRECT (supervisor label, since supervisor ran last) | ACCIDENTAL FIX |
| context-pack.yaml freshness | Frozen at Mainstream R107 | Refreshed by Supervisor R106 cycle (Step 7c) | IMPROVED |
| selected-product-gaps.json | STALE (R98) | STALE (R98) | UNCHANGED |
| artifacts_missing_count | Not investigated | Builder limitation: hardcoded path vs declaration evidence_root | NEW FINDING |

---

## Part 5: Recommendations

### Option A: Accept as Known Limitation (LOW effort)

- Document that `reports/supervisor/` files are always last-writer-wins
- Each stream continues to use isolated `reports/{stream}-{run}/` directories
- `artifacts_missing_count=1` is cosmetic and does not affect grading or continuation
- Update `CLAUDE.md` session-start to note that `session-resume.md` reflects the last stream

### Option B: Stream-Tagged Output Files (MEDIUM effort)

- `autonomous_cycle.py` Steps 6/7/7b write to `reports/supervisor/{stream}-{run}/` subdirectories
- A global `reports/supervisor/latest-stream-index.json` maps stream names to their latest run
- `CLAUDE.md` session-start reads the stream-index to find the correct resume file
- Fix `build_declaration_review_package.py` to read `evidence_root` from declaration

### Option C: Per-Stream Autonomous Cycle Output (HIGH effort)

- Each stream's `autonomous-cycle` writes exclusively to `reports/{stream}-{run}/`
- Global `reports/supervisor/` becomes a read-only aggregate (rebuilt from all streams)
- Requires refactoring `generate_supervisor_packet.py` to merge multi-stream state

### Recommended Path

**Option A** for immediate acceptance, with the single code fix for `artifacts_missing_count`
from Option B (reading `evidence_root` from the declaration in the builder).

The contamination is structural and well-understood. Every stream already mitigates it by
using isolated directories. The permanent fix (Option B or C) belongs in the Supervisor
stream's roadmap, not in Skills R107.

---

## Conclusion

1. **Stream contamination**: All `reports/supervisor/` files now reference the Supervisor R106
   stream because it ran last. Three files (`evidence-review.md`, `discovery-summary.md`,
   `memory-sync-report.md`) are stale from the Acceleration R106 cycle because Steps 6/7/7b
   do not overwrite them. This is the expected last-writer-wins behavior and will shift
   every time a different stream runs.

2. **artifacts_missing_count=1**: This is a builder limitation, not a real missing artifact.
   `build_declaration_review_package.py` hardcodes `.local/evidences/{run_id}/` for the
   manifest path, but `autonomous_cycle.py` writes the manifest to the declaration's
   `evidence_root` (e.g., `reports/skills-r106/`). The fix is a one-line path change in
   the builder.

3. **Skills R107 mitigation**: Continue using `reports/skills-r107/` as the isolated evidence
   directory. Do not treat `reports/supervisor/` as authoritative for the Skills stream.
