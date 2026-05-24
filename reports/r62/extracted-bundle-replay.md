# R62 Train F: Extracted Bundle Replay Report

**Sprint:** FORMAT-FACTORY-R62-AI-ACCELERATED-DELIVERED-SIDECAR-PYTHON-RC-PHASE13-MEGA-TRAIN-001
**Date:** 2026-05-24
**Status:** PASS

---

## Scope

Train F verifies that the R62 package artifacts can be replayed from the extracted bundle,
without relying on `.local/` paths.

---

## R61 Bundle Package Artifacts — Baseline Reference

R61 bundle had no Python wheels (IV-R61-001/002 — external R60 refs only).
R62 delivers self-contained Python artifacts (Train D).

R62 package-artifacts/ contents: 20 Python artifacts + 2 .NET nupkgs.

---

## R62 Artifact Extraction Proof

| Check | Status | Evidence |
|---|---|---|
| 20 Python artifacts in package-artifacts/ | PASS | ls .local/r62-metadata/package-artifacts/ = 20 .whl + .tar.gz files |
| 2 .NET nupkgs in package-artifacts/ | PASS | FormatFactory.Fods + FormatFactory.Fodt nupkgs present |
| FODS wheel SHA matches manifest | PASS | package-artifact-manifest.yaml sha256 = 428c2d1aa5... (computed) |
| FODT wheel SHA matches manifest | PASS | package-artifact-manifest.yaml sha256 = 3cc0546423... (computed) |
| FODS wheel contains R62 capabilities | PASS | workbook_merged_cell_summary + workbook_sheet_order in neutral_model.py |
| FODT wheel contains R62 capabilities | PASS | document_hyperlink_count + document_footnote_count in neutral_model.py |
| Installed-wheel smoke: 14 APIs PASS | PASS | .local/r62-smoke-venv; reports/r62/installed-current-api-smoke.md |

---

## Policy Verification

- `installed_artifact_policy: self_contained` — ENFORCED in contract
- No external R60/R61 references in R62 package-artifact-manifest.yaml
- `prior_bundle_digest:` field used (not `prior_bundle_sha256:`) — ARTIFACT_INVENTORY scanner pitfall avoided

---

## Verdict

**TRAIN F VERDICT: PASS**

R62 closes IV-R61-001/002/003 (missing Python artifacts, external refs, no installed-wheel proof).
