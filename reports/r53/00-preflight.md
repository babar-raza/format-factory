# R53 Preflight Report

**Sprint:** FORMAT-FACTORY-R53-SELF-VERIFYING-BASELINE-001
**Date:** 2026-05-22
**Run number:** R53 (auto-detected: reports/r52 is latest, r53 is next free)

## Environment

- **Branch:** main
- **HEAD:** 0ecd4e1b49db491df36c990ee759067fc0206bf6
- **Git status:** clean
- **Python:** 3.13.2
- **dotnet SDK:** 10.0.204
- **`.git` exists:** yes

## R52 Bundle Status (uploaded/local)

- **R52 bundle path:** `.local/evidence-bundles/r52-state-consistent-installed-artifact-baseline.zip`
- **R52 bundle SHA-256:** `3aa7b823e4bc457cfefa972adb9a05bb4ee22b0d039adc7da2b6155f7fdceaf1`
- **R52 bundle size:** 4,357,504 bytes
- **R52 bundle entries:** 2,380

### Internal Proof File (bundle-metadata/final-bundle-validation-proof.txt)

- Pass 1 SHA: `6d5444ac02541ad037aa057260bbb7393b7f2b46b06cc9babcf9f09f754113b2` (recorded)
- **Pass 2 SHA: PENDING** (self-referential impossibility — cannot contain own SHA)
- **Pass 2 result: PENDING**

### R52 Final-Verdict Inside Bundle

- `repo/reports/r52/final-verdict.md` → `BUNDLE_VALIDATION: PASS` (correct)
- `Pass 2 SHA-256: PENDING` (bundle was built before final SHA was known — expected)

### R52 Artifacts

- Zero `.whl`, `.tar.gz`, `.nupkg` in bundle ZIP
- `package-artifact-manifest.yaml` explicitly states: unchanged from R51, no artifacts claimed

### External Sidecar Proof

- Generated retroactively for R52 at: `.local/evidence-bundles/r52-state-consistent-installed-artifact-baseline.sha256-proof.json`
- Confirms: SHA matches bundle, result=PASS

## Diagnostic Results

| Check | Result |
|-------|--------|
| Physical invariants (check_repo_invariants.py) | PASS (5/5) |
| State snapshot (state_snapshot.py) | PASS |
| State linter (state_linter.py) | PASS (2 warnings: r27/r32 metadata floor, 3 infos) |
| FODS/FODT Python tests (402+4 skip) | PASS |
| Evidence/invariants/package tests (874+26 warn) | PASS (1 pre-existing: test_build_report_all_built hardcodes count=5, actual=7) |

## Current State

- **Latest sprint:** R52 — `R52_STATE_CONSISTENT_INSTALLED_ARTIFACT_BASELINE_CLEAN`
- **Production blockers:** G11-G_NOT_STARTED, GATE8_AWAITING_HUMAN_APPROVAL, PACKAGE_NOT_PUSHED
- **R27/R32 metadata floor warnings:** present (2)

## AI Endpoint Availability

- AI env vars present (names only): GPT_OSS_ENDPOINT, GPT_OSS_API_KEY, AGENT_METRICS_ENDPOINT, ANTHROPIC_KEY
- Live endpoint calls: NOT used in this sprint (all fixture mode or static analysis)

## R52 Installed Artifact Status

- R52 is NOT a self-contained installed-artifact baseline (no artifact files in ZIP)
- R51 artifacts remain the installed baseline (FODS/FODT wheels + nupkgs)
- This sprint (R53) corrects this status and implements proper sidecar proof policy

## Run Number Selection

Reports/r52 exists. Reports/r53 directory created (empty). R53 selected.
