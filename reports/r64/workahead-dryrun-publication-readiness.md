# R64 W6 — Dry-Run Publication Readiness

**Sprint:** FORMAT-FACTORY-R64-DELIVERED-SIDECAR-PACKAGING-REPLAY-AI-LIVE-REVIEW-WORKAHEAD-MEGA-TRAIN-001
**Date:** 2026-05-25

---

## PyPI Dry-Run Readiness

| Field | Status | Value |
|---|---|---|
| Package names | READY | aspose-format-factory-{fods,fodt,...} |
| Version | READY | 0.1.0.dev0 |
| License | READY | Apache-2.0 |
| README | READY | Per-package README in packaging/ |
| Classifiers | READY | Development Status :: 2 - Pre-Alpha |
| Artifact hashes | READY | SHA-256 in manifest |
| Rollback notes | READY | `pip install aspose-format-factory-fods==<prev>` |
| **Publication gate** | **BLOCKED** | `publication_authorized: false` |

## NuGet Dry-Run Readiness

| Field | Status | Value |
|---|---|---|
| Package names | READY | FormatFactory.Fods, FormatFactory.Fodt |
| Version | READY | 0.1.0-tier0 |
| License | READY | Apache-2.0 |
| Description | READY | In .csproj metadata |
| Artifact hashes | READY | SHA-256 in manifest |
| Unpublish notes | READY | NuGet unlist (not true unpublish) |
| **Publication gate** | **BLOCKED** | Gate 11 G11-G NOT_STARTED |

## Gate Blockers

- PyPI: `publication_authorized: false` — requires human approval
- NuGet: Gate 11 G11-G NOT_STARTED — requires Babar Raza approval
- No upload performed in R64

---

W6_DRYRUN_PUBLICATION_STATUS: COMPLETE
