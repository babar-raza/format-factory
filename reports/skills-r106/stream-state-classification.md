# Stream-State Classification -- Skills R106
# Generated: 2026-06-03
# Prior report: reports/skills-r105/stream-state-isolation.md

## Purpose

Re-classify all global state files to determine which stream they currently point to,
compare against the R105 contamination baseline, document Skills R106 mitigation strategy,
and provide an infrastructure handoff note for the Supervisor stream.

---

## Global State File Classification Table

| # | File | R105 Classification | R105 Actual Stream | R106 Actual Stream | R106 Actual Sprint ID | R106 Classification | Delta |
|---|------|--------------------|--------------------|--------------------|-----------------------|--------------------|-------|
| 1 | `reports/supervisor/session-resume.md` | WRONG_STREAM_PRIMARY (mainstream R107) | mainstream | skills | `FORMAT-FACTORY-SKILLS-R105-TRANSCRIPT-ENFORCEMENT-STREAM-STATE-ISOLATION-LIVE-HANDOFF-PROOF-MEGA-TRAIN-001` | SKILLS_PRIMARY | IMPROVED |
| 2 | `reports/supervisor/evidence-review.json` | WRONG_STREAM_PRIMARY (mainstream R107) | mainstream | skills | `FORMAT-FACTORY-SKILLS-R105-TRANSCRIPT-ENFORCEMENT-STREAM-STATE-ISOLATION-LIVE-HANDOFF-PROOF-MEGA-TRAIN-001` | SKILLS_PRIMARY | IMPROVED |
| 3 | `reports/supervisor/contradictions.json` | WRONG_STREAM_PRIMARY (mainstream R107) | mainstream | skills | `FORMAT-FACTORY-SKILLS-R105-TRANSCRIPT-ENFORCEMENT-STREAM-STATE-ISOLATION-LIVE-HANDOFF-PROOF-MEGA-TRAIN-001` | SKILLS_PRIMARY | IMPROVED |
| 4 | `reports/supervisor/next-sprint.md` | WRONG_STREAM_PRIMARY (mainstream R107) | mainstream | skills (mislabeled) | Source: Skills R105, but header reads `Stream: mainstream`; content is generic mainstream-style tasks | WRONG_STREAM_PRIMARY | PARTIAL — source sprint correct, stream label and task content wrong |
| 5 | `.supervisor/context-pack.yaml` | WRONG_STREAM_PRIMARY (acceleration R105) | acceleration | mainstream | `latest_sprint.sprint_id: FORMAT-FACTORY-MAINSTREAM-R107-...`, `run_id: R107` | WRONG_STREAM_PRIMARY | CHANGED (acceleration -> mainstream, still not skills) |
| 6 | `.local/supervisor/selected-product-gaps.json` | STALE_PRIMARY (R98) | stale (R98) | stale (R98) | `sprint: R98` (presumed unchanged) | STALE_PRIMARY | UNCHANGED |

---

## Summary Counts

| Classification | R105 Count | R106 Count | Change |
|---------------|-----------|-----------|--------|
| SKILLS_PRIMARY | 0 | 3 | +3 |
| WRONG_STREAM_PRIMARY | 5 | 2 | -3 |
| STALE_PRIMARY | 1 | 1 | 0 |
| Total analyzed | 6 | 6 | 0 |

---

## Analysis of Changes Since R105

### What improved

The Skills R105 supervisor pipeline ran **after** Mainstream R107 and Acceleration R105,
which means the last-writer-wins behavior now favors Skills for three of the six global
state files. Specifically:

- `session-resume.md` now references `FORMAT-FACTORY-SKILLS-R105-...` as the last sprint.
- `evidence-review.json` contains Skills R105 verdict (ACCEPTED, 63 tests passed).
- `contradictions.json` contains Skills R105 sprint ID with CLEAN status.

### What remains contaminated

1. **`next-sprint.md`** — The source sprint is correctly Skills R105, but the file header
   declares `Stream: mainstream` and the task content is generic mainstream product-deepening
   work (FODS Gate 11, FODT Gate 11, ABW parser, etc.), not skills-stream tasks. This is a
   template/generator bug: the supervisor's `evidence-review-next-prompt` skill does not
   propagate the source stream into the generated prompt's stream label or task selection.

2. **`context-pack.yaml`** — The `latest_sprint` block reads `sprint_id: FORMAT-FACTORY-MAINSTREAM-R107-...`
   and `run_id: R107`. The context pack generator (`build_context_pack.py`) appears to run
   on a different cadence or was last invoked during the Mainstream R107 cycle. It was NOT
   refreshed when the Skills R105 supervisor pipeline ran. The `poc_matrix.sprint` field
   reads `R106`, which is the Acceleration stream's next target, not Skills.

3. **`selected-product-gaps.json`** — Still stale at R98. No stream has refreshed it.

### Root cause (unchanged from R105)

The `reports/supervisor/` directory is a single-writer-wins shared resource. Whichever
stream runs the supervisor pipeline last overwrites all global state files. There is no
per-stream namespace enforcement at the infrastructure level.

---

## Skills R106 Mitigation Strategy

### Isolated evidence directory

All Skills R106 primary state and evidence lives under:
```
reports/skills-r106/
```

This directory already contains preflight, lane-ownership, scoreboard, and other
Skills R106-specific artifacts. No Skills R106 worker should treat files under
`reports/supervisor/` as authoritative for the Skills stream.

### Rules carried forward from R105

1. **Skills primary state** is generated at `reports/skills-r106/`, never at `reports/supervisor/`.
2. **Global state** under `reports/supervisor/` is labeled `GLOBAL_CONTEXT` (non-authoritative)
   in any Skills evidence package.
3. **Wrong-stream outputs** are excluded from Skills acceptance criteria.
4. **Skills next prompt** is authored at `reports/skills-r106/repair-plus-advancement-plan.md`
   (or equivalent), not sourced from `reports/supervisor/next-sprint.md`.

### What Skills R106 does NOT do

Skills R106 does not modify any `reports/supervisor/` files. The contamination is an
infrastructure-level problem that must be fixed in the Supervisor stream's tooling, not
worked around per-sprint by individual streams.

---

## Infrastructure Handoff Note for Supervisor Stream

### Problem

The supervisor pipeline (`supervisor_loop.py autonomous-cycle`) writes to a shared
`reports/supervisor/` directory with no stream isolation. In a multi-stream environment
(Mainstream, Acceleration, Skills), the last stream to run overwrites all prior streams'
state. This creates three specific defects:

### Defect 1: `next-sprint.md` stream label hardcoded to `mainstream`

The `evidence-review-next-prompt` skill (or the template it uses) hardcodes `Stream: mainstream`
in the generated next-sprint prompt header regardless of which stream's declaration was
processed. The source sprint ID is correct (it comes from the declaration), but the stream
label and task selection logic do not respect the source stream.

**Fix:** The next-prompt generator should read the stream identifier from the declaration
or from a stream metadata field and propagate it into both the header and the task
selection filter.

### Defect 2: `context-pack.yaml` not refreshed per stream

`build_context_pack.py` appears to only run during certain streams or at a separate cadence.
When Skills R105 ran the supervisor pipeline, `context-pack.yaml` was not updated — it still
reflects Mainstream R107. This means any tool or worker that reads the context pack gets
stale cross-stream state.

**Fix:** Either (a) run `build_context_pack.py` as part of every `autonomous-cycle` invocation,
or (b) generate per-stream context packs at `reports/{stream}-{run}/context-pack.yaml`.

### Defect 3: No per-stream namespace in `reports/supervisor/`

All streams write to the same six files. There is no directory partitioning, filename
prefixing, or stream-aware routing.

**Fix:** Introduce per-stream output directories, e.g.:
```
reports/supervisor/skills-r106/session-resume.md
reports/supervisor/mainstream-r108/session-resume.md
reports/supervisor/acceleration-r106/session-resume.md
```
Or use the existing `reports/{stream}-{run}/` convention that Skills already uses, and
update `CLAUDE.md` session-start instructions to read the stream-specific resume instead
of the global one.

### Priority

These defects are non-blocking for individual streams (each stream can mitigate with
isolated directories), but they create ongoing confusion for any worker that follows
`CLAUDE.md` instructions verbatim (which direct reading `reports/supervisor/session-resume.md`
as the first action). Fixing defect 3 would eliminate the class of contamination entirely.

### Suggested Supervisor Taskcard

```
ID: TC-SUP-STREAM-ISOLATION-001
Title: Per-stream state isolation in supervisor pipeline
Priority: MEDIUM
Scope: supervisor_loop.py, build_context_pack.py, CLAUDE.md session-start instructions
Acceptance: Each stream's autonomous-cycle writes to a stream-namespaced directory;
            CLAUDE.md session-start reads the correct stream's resume file;
            no cross-stream overwrite possible.
```

---

## Conclusion

The contamination situation has partially improved since R105: three of six global state
files now reflect Skills R105 (because it ran last). However, two files remain wrong-stream
(`next-sprint.md` mislabeled as mainstream, `context-pack.yaml` frozen at Mainstream R107),
and one remains stale (`selected-product-gaps.json` at R98). The improvement is accidental
(last-writer-wins) and will regress the next time another stream runs the supervisor pipeline.

Skills R106 mitigates by using `reports/skills-r106/` as its isolated evidence directory.
The permanent fix requires Supervisor stream infrastructure changes as described in the
handoff note above.
