# R55 Lane Ownership

**Sprint:** FORMAT-FACTORY-R55-MULTI-MEGA-TRAIN-PRODUCT-RC-PHASE6-ACQUISITION-AI-VALIDATOR-001
**Date:** 2026-05-23

## Train Structure

R55 is a multi-mega-train sprint. Each train contains multiple lanes. Trains run in parallel.
Train K (final bundle) runs last, after all A–J trains complete.

---

## Train A: Validator Repair + State Authority

**Goal:** Fix state/current-state.md staleness; add INV-011..014; validator latest-sprint check.

| Lane | Description | Owner |
|------|-------------|-------|
| A-1 | Regenerate state/current-state.md via state_snapshot.py | R55 agent |
| A-2 | Add INV-011: latest state snapshot matches contract run_number | R55 agent |
| A-3 | Add INV-012: format-completion-matrix.yaml has entry for every format | R55 agent |
| A-4 | Add INV-013: all OPEN taskcards are referenced in a risk register | R55 agent |
| A-5 | Add INV-014: state snapshot run date is within 14 days of sprint date | R55 agent |
| A-6 | Write tests for INV-011..014 in test_r55_validator_repair.py | R55 agent |

---

## Train B: FODT Full Preservation

**Goal:** Close TC-0057 (inline spans); fix document ordering; promote TC-0058/TC-0059 to PASS.

| Lane | Description | Owner |
|------|-------------|-------|
| B-1 | Read fodt/parser.py — audit inline span capture in block dict | R55 agent |
| B-2 | Add inline span capture to parser (text:span → runs list) | R55 agent |
| B-3 | Add _write_span() to fodt/writer.py — emit text:span for runs with style | R55 agent |
| B-4 | Fix document ordering — merge blocks/lists/tables into unified sequence | R55 agent |
| B-5 | Create TC-0060: FODT document ordering TC | R55 agent |
| B-6 | Write tests for inline span round-trip (≥5 tests) | R55 agent |
| B-7 | Update TC-0057 status: CLOSED_VERIFIED if tests pass | R55 agent |
| B-8 | Update TC-0058/TC-0059 status: PASS if ordering fix confirmed | R55 agent |

---

## Train C: FODS Deepening

**Goal:** Advance TC-0055 (style metadata) and TC-0056 (column definitions).

| Lane | Description | Owner |
|------|-------------|-------|
| C-1 | Read fods/parser.py — audit styles + column def capture | R55 agent |
| C-2 | Add styles block capture to parser (office:styles, office:automatic-styles) | R55 agent |
| C-3 | Add column definition capture to parser (table:table-column per sheet) | R55 agent |
| C-4 | Update fods/writer.py — re-emit styles block verbatim | R55 agent |
| C-5 | Update fods/writer.py — emit table:table-column before row data | R55 agent |
| C-6 | Write tests for style round-trip (≥3 tests) and column-def round-trip (≥3 tests) | R55 agent |
| C-7 | Update TC-0055 status: CLOSED_VERIFIED if tests pass | R55 agent |
| C-8 | Update TC-0056 status: CLOSED_VERIFIED if tests pass | R55 agent |

---

## Train D: Package RC Self-Contained

**Goal:** Rebuild Python FOSS wheels post-R54; achieve installed_artifact_policy: self_contained.

| Lane | Description | Owner |
|------|-------------|-------|
| D-1 | Run build-local-packages.py — rebuild 3+ wheels (fods, fodt, zst) | R55 agent |
| D-2 | Create clean venv; pip install each wheel; smoke test import | R55 agent |
| D-3 | Verify fods wheel: parse + write round-trip from installed wheel | R55 agent |
| D-4 | Verify fodt wheel: parse + write round-trip from installed wheel | R55 agent |
| D-5 | Update package-artifact-manifest.yaml with R55 wheel SHAs | R55 agent |
| D-6 | Write test_r55_package_rc.py: 3+ installed-wheel smoke tests | R55 agent |

---

## Train E: .NET Commercial Readiness

**Goal:** Fix test_build_report_all_built count mismatch; run .NET bounded verification.

| Lane | Description | Owner |
|------|-------------|-------|
| E-1 | Read test_python_local_package_artifacts.py — find hardcoded count=5 | R55 agent |
| E-2 | Fix count to match actual package count (7) | R55 agent |
| E-3 | Run dotnet test for fods/fodt — record result | R55 agent |
| E-4 | Confirm commercial_product_ready: false unchanged | R55 agent |
| E-5 | Update dotnet-bounded-verification.md for R55 | R55 agent |

---

## Train F: Next-Format Advancement

**Goal:** Advance 3+ format tracks — binary support for Netpbm family.

| Lane | Description | Owner |
|------|-------------|-------|
| F-1 | Add P5 binary support to pgm/pgm_parser.py | R55 agent |
| F-2 | Add P4 binary support to pbm/pbm_parser.py | R55 agent |
| F-3 | Add P6 binary support to ppm/ppm_parser.py | R55 agent |
| F-4 | Write tests for P5 PGM binary (≥5 tests) | R55 agent |
| F-5 | Write tests for P4 PBM binary (≥5 tests) | R55 agent |
| F-6 | Write tests for P6 PPM binary (≥5 tests) | R55 agent |
| F-7 | Update format-completion-matrix.yaml for pgm/pbm/ppm maturity advancement | R55 agent |

---

## Train G: Phase Audit 6

**Goal:** Package/RC/install/consumer proof; add fods/fodt to release manifest matrix.

| Lane | Description | Owner |
|------|-------------|-------|
| G-1 | Add fods + fodt entries to release-manifests/python-foss/_matrix.yaml | R55 agent |
| G-2 | Add ods + zst entries to matrix (if package exists) | R55 agent |
| G-3 | Document install proof: fods/fodt wheels from clean venv (from Train D) | R55 agent |
| G-4 | Document consumer proof: example script that imports from installed wheel | R55 agent |
| G-5 | Write reports/r55/phase-audit-6-rc-mapping.md | R55 agent |

---

## Train H: Acquisition + Spec-Cache Authority

**Goal:** Advance 4+ lower-maturity format tracks (CSV/TSV/XPM/PAM → Gate 4).

| Lane | Description | Owner |
|------|-------------|-------|
| H-1 | Create src/python/csv/ with csv_parser.py (read-only prototype) | R55 agent |
| H-2 | Create src/python/tsv/ with tsv_parser.py (read-only prototype) | R55 agent |
| H-3 | Write tests for csv parser (≥8 tests) | R55 agent |
| H-4 | Write tests for tsv parser (≥8 tests) | R55 agent |
| H-5 | Update format-completion-matrix.yaml: csv/tsv maturity = read_only_prototype | R55 agent |
| H-6 | Update acquisition-packs/csv/pack.yaml and tsv/pack.yaml with Gate 4 status | R55 agent |

---

## Train I: AI Governance Proof

**Goal:** Controlled acceleration fixture-mode proof; 0 ungoverned calls; telemetry record.

| Lane | Description | Owner |
|------|-------------|-------|
| I-1 | Run AI governance audit: scan_for_direct_endpoint_calls() | R55 agent |
| I-2 | Verify all AI tests run in fixture mode (no live endpoint required) | R55 agent |
| I-3 | Write reports/r55/ai-usage-telemetry-proof.md (AI_GOVERNANCE_R55: PASS) | R55 agent |

---

## Train J: Memory + Docs Sync

**Goal:** Update all stale memory and documentation to R55 state.

| Lane | Description | Owner |
|------|-------------|-------|
| J-1 | Update format-completion-matrix.yaml test counts (fods/fodt post-R55) | R55 agent |
| J-2 | Write memory/60-r55-*.md | R55 agent |
| J-3 | Update memory/00-index.md with R55 row | R55 agent |
| J-4 | Update MEMORY.md: R55 current state section | R55 agent |

---

## Train K: Final IV + Bundle

**Goal:** Final validation, contract, bundle build (PASS 1 + PASS 2 + sidecar).

| Lane | Description | Owner |
|------|-------------|-------|
| K-1 | Run full pytest suite — record AUTHORITATIVE_TEST_RESULT | R55 agent |
| K-2 | Run check_repo_invariants.py — all INV-001..014 must PASS | R55 agent |
| K-3 | Commit all R55 changes | R55 agent |
| K-4 | Build bundle Pass 1 — record SHA | R55 agent |
| K-5 | Update final-verdict.md with Pass 1 SHA | R55 agent |
| K-6 | Commit final-verdict.md | R55 agent |
| K-7 | Build bundle Pass 2 + sidecar proof | R55 agent |
| K-8 | Validate bundle: BUNDLE_VALIDATION: PASS | R55 agent |

## Anti-Shrink Policy

A blocker in one train does NOT stop other trains. If a lane cannot complete,
it is marked BLOCKED with a reason, and the next available lane in the same
or another train picks up. No train may be cancelled mid-sprint.
