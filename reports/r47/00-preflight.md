# R47 Preflight

**Sprint:** FORMAT-FACTORY-R47-ARTIFACT-PROOF-REPAIR-AND-PHASE-AUDIT-PROGRESSION-001
**Run Number:** R47
**Date:** 2026-05-22
**Purpose:** Fix R46 artifact-containment false positive; genuine artifact-contained RC proof; Phase Audit correction and progression.

---

## Run Number Detection

- Latest report dir: `reports/r46/`
- R47 not yet used in reports/, contracts, git log
- **Selected: R47**

---

## Environment

| Item | Value |
|------|-------|
| Branch | main |
| HEAD | 9f0e30d |
| Git status | clean |
| Python | 3.13.2 |
| dotnet SDK | 10.0.204 |
| `.git` present | YES |
| `python -m build` | NOT AVAILABLE (base env) |
| `.local/build-venv/Scripts/python.exe` | PRESENT — `build 1.5.0` |

---

## R46 Verification

**R46 bundle ZIP artifact check (direct inspection):**
- File: `.local/r46-bundle.zip`
- `.whl` files: **0** (expected 2)
- `.tar.gz` files: **0** (expected 2)
- `.nupkg` files: **0** (expected 2)
- Manifest: `bundle-metadata/package-artifact-manifest.yaml` PRESENT (text only)

**Root cause identified:** `build_evidence_bundle.py` line 350-352 uses
`metadata_path.iterdir()` with `if mf.is_file()` — only top-level files are
collected. The `package-artifacts/` subdirectory is a directory, not a file,
so it is silently skipped. No binary artifact ever entered the ZIP.

**Local cache check:**
- `.local/r46-metadata/package-artifacts/` — EXISTS (6 artifacts locally)
- `.local/consumer-proof-r46/` — EXISTS (locally only)

**Conclusion:** R46 claimed artifact containment but the artifacts were never
in the ZIP. The validator passed because it only checked for
`package-artifact-manifest.yaml` (a text file), not for actual artifact bytes.

**R46 Supersession:** `R46_CODE_PROGRESS_ACCEPTED_ARTIFACT_CONTAINMENT_FALSE`

---

## Spec-Cache Status

- FODS/ZST/ODS/ODT: cached or documented
- FODT: reuses FODS cache (documented)
- QOI/XCF/DIF/PPM/PGM/PBM/SYLK: source URLs documented, no local cache

---

## Sample Directories

- ZST: `samples/by-format/zst/` — `_provenance.yaml` present
- FODS/FODT/ODS/ODT/QOI/XCF/DIF/PPM/PGM/PBM/SYLK: samples present, no provenance YAML

---

## Baseline Test Results

| Suite | Result |
|-------|--------|
| tests/python/fods + tests/python/fodt | 311 passed, 4 skipped |
| STATE_SNAPSHOT | PASS |

---

## Phase Audit Roadmap Drift

R46 roadmap Phase 2 was "Parser Implementation Quality" — this drifted from the
required sequence. Correct Phase 2 is: **Sample Acquisition / Sample Provenance**.

---

## Sprint Blockers at Start

1. R46 artifact-containment false positive (PRIMARY)
2. Builder subdirectory bug
3. Validator does not enforce actual artifact presence
4. Phase Audit 1 overclaims PASS
5. Phase Audit roadmap drifted from required sequence

---

## Lane Assignments

See `reports/r47/lane-ownership.md`.

PREFLIGHT_STATUS: PASS
