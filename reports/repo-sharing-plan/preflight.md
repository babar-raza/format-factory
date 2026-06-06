# Repo Sharing Plan — Preflight
# Sprint: FORMAT-FACTORY-REPO-SHARING-GITIGNORE-REMOTE-REFRESH-PLAN-001
# Generated: 2026-06-04

## Branch
main

## Remote
origin  https://github.com/babar-raza/format-factory.git (fetch)
origin  https://github.com/babar-raza/format-factory.git (push)

## Recent Commits (last 5)
3a86a05 feat(r93): context-pack, D92 defect repair, governed acceleration — FODS/FODT/Netpbm/.NET + ZST/PPM/SYLK FOSS
e283822 feat(r92): declaration materializer, skill expansion, POC deepening
be0bc9a chore(r91): fill autonomous-continuation-proof and final-adversarial-IV with actual closeout results
f881c49 feat(r91): autonomous supervisor healed + POC deepened
95c30f9 chore: commit stale supervisor outputs before R91 sprint start

## Tracked File Count
3761 tracked files total

Top-level breakdown (tracked):
- reports/      1867 files
- tests/         596 files
- tools/         351 files
- taskcards/     185 files
- acquisition-packs/ 165 files
- samples/       126 files
- docs/          116 files
- src/            97 files
- memory/         71 files
- schemas/        34 files
- .supervisor/    24 files
- .claude/        20 files
- examples/       19 files
- prototypes/     17 files
- generated-requirements/ 17 files
- release-manifests/ 15 files
- templates/       5 files
- registry/        5 files
- product-capability-matrix/ 5 files
- plans/           4 files

## Untracked File Count
375 untracked files

Top-level breakdown (untracked):
- tests/        276 files
- docs/          42 files
- tools/         32 files
- examples/      17 files
- .claude/        6 files
- memory/         2 files
- plans/          1 file
- .supervisor/    1 file

NOTE: reports/ has ZERO untracked files showing despite `reports/repo-sharing-plan/`
having been created. This is because `.gitignore` line 174 contains `/reports` which
gitignores the entire reports/ directory for NEW content. See current-ignore-rules.md
for details on this critical bug.

## Modified Tracked Files (M status) — 70 files
.claude/commands/     18 files (command definitions)
.supervisor/           6 files (config, schemas, prompts)
.gitignore             1 file
plans/                 1 file
product-capability-matrix/ 1 file
reports/r90/           1 file
reports/supervisor/   21 files (live supervisor cycle outputs)
src/net/fods/          1 file
src/net/fodt/          1 file
src/net/netpbm/        1 file
src/python/sylk/       1 file
state/                 1 file
tools/supervisor/     14 files

## Critical Findings

### FINDING 1 — CRITICAL: /reports appears twice in .gitignore (lines 173-174)
Pattern: `/reports`
Effect: ALL new files in reports/ are gitignored and cannot be `git add`ed without `-f`
Confirmed: `git check-ignore -v reports/repo-sharing-plan/` → `.gitignore:174:/reports`
Action required: Remove BOTH `/reports` lines from .gitignore before any remote refresh

### FINDING 2 — LOW: Absolute path in reports/supervisor/product-gap-selection.md
Line 1 contains: `C:/Users/prora/OneDrive/Documents/GitHub/format-factory/...`
Action required: Sanitize before committing

### FINDING 3 — INFO: Many gitignore patterns already present
dist/, build/, coverage/, .coverage, coverage.xml, *.snupkg — already covered
Remaining gaps: tmp/, temp/, .claude-flow/, output*/ (minor additions only)
