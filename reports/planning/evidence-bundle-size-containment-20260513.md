---
document_type: evidence_bundle_size_containment_review
sprint: CONWAY-R2R3-CONTEXT-AND-LANE-SELECTOR-SWARM-001
lane: E
title: "Evidence Bundle Size Containment Review"
date: "2026-05-13"
visibility: internal
publish_allowed: false
---

# Evidence Bundle Size Containment Review — Lane E

**Sprint:** CONWAY-R2R3-CONTEXT-AND-LANE-SELECTOR-SWARM-001
**Date:** 2026-05-13

---

## SUMMARY

The latest evidence bundle (`conway-r1r2-accelerated-foundation-swarm-20260513.zip`) is ~101 MB
(110 MB uncompressed). The actual repo content is only 6.9 MB. The remaining ~103.5 MB is
previous evidence bundles included as `bundle-metadata/` entries.

**Root cause: O(n²) bundling growth.**

---

## Section 1: Size Analysis

### Bundle breakdown

| Category | Files | Uncompressed Size |
|----------|-------|-------------------|
| `bundle-metadata/` (previous bundles as .zip files) | 128 | 103.5 MB |
| `repo/` (actual repository content) | 749 | 6.9 MB |
| **Total** | **877** | **110.4 MB** |

### Bundle size history

| Bundle | Compressed Size |
|--------|----------------|
| Most sprints (pre-May-13) | ~1.4-1.7 MB |
| conway-r1r2-accelerated-foundation-swarm-20260513 | **~101 MB** |

### Growth mechanism

The `build_evidence_bundle.py` uses `.local/evidence-bundles/` as both:
1. The **output directory** where completed bundles are saved
2. The **metadata source directory** passed via `--metadata-dir .local/evidence-bundles`

Because `build_bundle()` iterates `metadata_path.iterdir()` and adds every file as
`bundle-metadata/<filename>`, all previously built bundles (`.zip` files) in the directory
are included in each new bundle. The sprint R1R2 bundle had 128 previous bundles as metadata.

**This is an O(n²) growth pattern.** Each new bundle includes all N previous bundles;
the next bundle will include N+1. If left uncapped, bundles will exceed 200 MB by the
next sprint.

---

## Section 2: Root Cause

```
.local/evidence-bundles/
├── bundle-manifest.yaml       ← metadata intent (correct)
├── git-log.txt                ← metadata intent (correct)
├── git-status-final.txt       ← metadata intent (correct)
├── sprint-A.zip               ← SHOULD NOT BE INCLUDED as metadata
├── sprint-B.zip               ← SHOULD NOT BE INCLUDED as metadata
└── current-sprint.zip         ← build output stored here
```

The intent was that `.local/evidence-bundles/` would contain only per-sprint metadata
(git-log, git-status, manifest). The `.zip` output files accumulate there because `--output`
and `--metadata-dir` point to the same directory.

---

## Section 3: Proposed Capping Policy

**This section is advisory. No changes to build infrastructure are made in this sprint.**

### Option A: Sprint-specific metadata subdirectory (RECOMMENDED)

Use a subdirectory for each sprint's metadata, separate from the bundle output directory:

```
.local/evidence-bundles/          ← bundle .zip outputs only
.local/metadata/current-sprint/   ← sprint metadata (git-log.txt, etc.)
```

Command change:
```bash
# Before (problematic):
python build_evidence_bundle.py \
  --metadata-dir .local/evidence-bundles \
  --output .local/evidence-bundles/sprint.zip

# After (proposed):
python build_evidence_bundle.py \
  --metadata-dir .local/metadata/current-sprint \
  --output .local/evidence-bundles/sprint.zip
```

This separates concern: metadata dir contains only the sprint's metadata files;
bundle dir contains only the `.zip` artifacts.

**Impact:** Zero breaking changes to validation logic. Metadata files are still included
via `bundle-metadata/` prefix in the zip. Build command changes only.

### Option B: Exclude .zip files from metadata collection

Modify `build_evidence_bundle.py` to skip `.zip` entries in the metadata directory:

```python
# In build_bundle(), metadata collection:
for mf in sorted(metadata_path.iterdir()):
    if mf.suffix == ".zip":
        continue  # Never include previous bundles as metadata
    metadata_files.append(mf.name)
```

**Impact:** Non-breaking. Existing bundles are not affected. Future bundles will only
include non-zip metadata files.

### Option C: Cap bundle-metadata size at 5 MB

Add a `max_metadata_size_bytes` contract field. If metadata exceeds the cap, the builder
warns (does not fail) and skips oversized entries.

**Impact:** More complex implementation. Low priority compared to Options A or B.

---

## Section 4: Target Size Policy (Proposed)

| Metric | Current | Target |
|--------|---------|--------|
| Bundle compressed size | ~101 MB | ≤ 10 MB per sprint |
| `bundle-metadata/` content | Previous bundles (O(n²)) | Git logs + manifest only (~100 KB) |
| Repo content | 6.9 MB | ~5-7 MB (acceptable) |

---

## Section 5: Implementation Priority

| Action | Priority | Notes |
|--------|----------|-------|
| Switch to sprint-specific metadata subdirectory (Option A) | HIGH | Cleanest fix; zero code changes |
| Exclude .zip files from metadata scan (Option B) | MEDIUM | Code change; more robust long-term |
| Document capping policy in AGENTS.md | MEDIUM | Should be recorded as a rule |
| Retroactively clean up old bundles in .local/ | LOW | Optional; does not affect future builds |

**Recommend: Option A for immediate next sprint; Option B as follow-up hardening.**

---

**LANE_E_STATUS: COMPLETE**
**ROOT_CAUSE: O(n^2) — previous bundles included as metadata**
**BLOCKER: NO — analysis only, no breaking changes**
**PROPOSED_FIX: Sprint-specific metadata subdirectory (Option A)**
**NEXT_SPRINT_ACTION: Use `.local/metadata/<sprint-id>/` as --metadata-dir**
