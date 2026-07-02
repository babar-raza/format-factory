---
version: "1.0"
last-updated: "2026-06-24"
phase-available: "all"
gate-required: null
skill_type: ATOMIC_SKILL
idempotency: "Same git log + transcripts produce same report"
loc_budget: "<90 lines"
test_path: "tests/supervisor/test_scan_residual_bypasses.py"
---

# /scan-residual-bypasses

Scan git log (last 20 commits) for `src/` file mutations, cross-reference against
`.local/transcripts/` to find mutations that have no corresponding skill transcript;
report as UNGOVERNED_MUTATION.

## Purpose

Post-hoc detection of `src/` mutations that bypassed the skill execution governance
layer. Used to monitor compliance after the skill-first policy is in effect.

**NOTE:** UNGOVERNED_MUTATION is expected for commits predating the skill-first policy
(SKILL-FIRST-001, 2026-06-24). Monitor trend over time, not absolute count.

## Steps

1. Run `git log -20 --name-only --format=%H` to get last 20 commits + changed files
2. Filter to only `src/` paths
3. Scan `.local/transcripts/*.json` — collect commit SHAs with skill transcripts
4. For each commit with `src/` changes: GOVERNED if transcript exists; else UNGOVERNED_MUTATION
5. Write report to `.supervisor/residual-bypass-report.yaml`

```bash
python tools/supervisor/scan_residual_bypasses.py
```

## Output

`.supervisor/residual-bypass-report.yaml` with:
- `commits_scanned`, `ungoverned_mutation_count`
- `entries[]`: commit_sha, src_paths_changed, has_skill_transcript, verdict

## Allowed Paths

- `.supervisor/residual-bypass-report.yaml` (write)
- `.local/transcripts/` (read)
- Git history (read via subprocess)

## Forbidden Paths

- `src/**` (read-only reference via git log)
- No mutations

## Constraints

- Read-only: reads git log and transcript files, no mutations
- UNGOVERNED_MUTATION in last 5 commits is the key compliance metric

## Idempotency Contract

Same git log + same transcripts produce same report. Deterministic.

## Error Handling

On git command failure: write empty entries list; log stderr. Exit 0.

## Usage

```
/scan-residual-bypasses
```

## Output Format

- YAML or JSON inventory file at the configured output path
- Summary counts: total scanned, found, flagged
- Per-item entries with classification and evidence
