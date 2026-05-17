---
artifact_id: r21-preflight-r20-baseline-and-lane-ownership
artifact_type: report
sprint: FORMAT-FACTORY-R21-FOSS-RELEASE-READINESS-AND-GATE11-COMMERCIAL-PREEXECUTION-TRAIN-001
date: "2026-05-17"
gate: "0"
status: PASS
visibility: internal
---

# R21 Gate 0 — Preflight and R20 Baseline Verification

## Git State

- Branch: main
- R20 sprint commit: 0d7e8c7 (feat: complete R20 productization train — 40 files, 3951 insertions)
- R20 evidence commit: 0392354 (chore: add R20 evidence bundle)
- Working tree: clean (only unrelated untracked: .claude/commands/export-plan-context.md, format-factory.zip)

## R20 Bundle

- Path: evidence-bundles/r20-productization-train-bundle.zip — EXISTS
- Validated: PASS (--check-no-pending, 1552 passed, 12 skipped)

## Source Paths

| Path | Exists |
|------|--------|
| src/python/zst/ | YES |
| src/python/fodp/ | YES |
| src/python/fodg/ | YES |
| src/python/gnumeric/ | YES |
| src/python/abw/ | YES |
| tests/python/zst/ | YES |
| tests/python/fodp/ | YES |
| tests/python/fodg/ | YES |
| tests/python/gnumeric/ | YES |
| tests/python/abw/ | YES |

## Registry State

| Format | Gates 1-7 | Gate 8 | Gate 9 | Gate 10 | impl_authorized | py_source |
|--------|-----------|--------|--------|---------|-----------------|-----------|
| ZST    | ALL PASSED | not_started | not_started | not_started | true | true |
| FODP   | ALL PASSED | not_started | not_started | not_started | true | true |
| FODG   | ALL PASSED | not_started | not_started | not_started | true | true |
| Gnumeric | ALL PASSED | not_started | not_started | not_started | true | true |
| ABW    | ALL PASSED | not_started | not_started | not_started | true | true |

## Commercial Product State

- commercial_product_ready: false (FODS, FODT, and all five tracks)
- src/net: contains only fods/ and fodt/ C4-C6 vertical slice (R20 baseline unchanged)
- Gate 11 status: in_progress, NOT APPROVED for FODS and FODT

## ORA / dnumber

- ORA: DEFERRED_BORDERLINE (6.8/10 < 7.0) — no source created
- dnumber: FORMAL_REJECT — no source created

## R21 Lane Ownership

| Lane | Formats | Target Gates | Stop Condition |
|------|---------|--------------|----------------|
| Python FOSS release readiness | ZST, FODP, FODG, Gnumeric, ABW | 8, 9, 10 | Source/test failure |
| Package metadata | All five | packaging | No build backend available |
| Examples | All five | examples smoke | Network required |
| Gate 11 planning | FODS, FODT | G11-A/B/C/E | src/net mutation |

## Gate 0 Verdict

GATE_0: PASS — R20 baseline verified, lanes classified, no stop conditions triggered.
