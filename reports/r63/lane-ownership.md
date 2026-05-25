# R63 Lane Ownership

**Sprint:** FORMAT-FACTORY-R63-AI-ASSISTED-RC-CLOSURE-AND-WORKAHEAD-MULTI-SPRINT-MEGA-TRAIN-001
**Date:** 2026-05-24

---

## Coordinator (Train 0)

**Owner:** Integration lead
**Allowed paths:**
- state/current-state.md, state/current-state.json
- reports/r63/final-verdict.md
- reports/r63/multi-mega-train-scoreboard.md
- reports/r63/work-ahead-scoreboard.md
- .local/r63-metadata/
- tools/evidence/contracts/r63-*.yaml

**Forbidden paths:**
- src/python/ (owned by Trains D, H, I)
- tests/ (owned by Trains C, D, H, I, W3)
- release-manifests/ (owned by Train H after API proof)

---

## Train A — R62 IV

**Owner:** Independent verifier
**Allowed paths:** reports/r63/r62-independent-verification.md, reports/r63/r62-defect-ledger.*
**Forbidden paths:** All source files, state files
**Stop condition:** All 12 R62 defects verified with exact commands

---

## Train B — AI Acceleration

**Owner:** AI orchestration lead
**Allowed paths:** reports/r63/ai-*.json, reports/r63/ai-telemetry-controlled-acceleration.md
**Forbidden paths:** Any source or authority file (advisory only)
**Stop condition:** 6 reviewer roles output structured JSON

---

## Train C — Sidecar Closure

**Owner:** Evidence engineer
**Allowed paths:**
- tests/evidence/test_r63_*.py
- reports/r63/final-sidecar-delivery-proof.md
- .local/r63-metadata/missing-sidecar-negative-proof.txt
- .local/r63-metadata/wrong-sidecar-negative-proof.txt
**Shared files:** tools/evidence/validate_evidence_bundle.py (read-only)
**Stop condition:** R63 sidecar tests pass + negative proofs documented

---

## Train D — Public API Repair

**Owner:** Package engineer
**Allowed paths:**
- src/python/fods/__init__.py
- src/python/fodt/__init__.py
**Shared files:** neutral_model.py files (read-only)
**Stop condition:** 9 FODS + 9 FODT public APIs exported and importable

---

## Train E — Packaging Replay Normalization

**Owner:** Packaging engineer
**Allowed paths:**
- tests/packaging/test_r63_*.py
- reports/r63/packaging-replay-normalization.md
**Forbidden paths:** src/ (source unchanged in this train)
**Stop condition:** Packaging replay passes with no current-RC skips

---

## Train F — Python RC Artifact Rebuild

**Owner:** Release engineer
**Allowed paths:**
- .local/package-builds/ (build outputs only)
- .local/r63-metadata/package-artifacts/
- .local/r63-metadata/package-artifact-manifest.yaml
**Shared files:** src/python/ (read-only after Train D completes)
**Stop condition:** 10 wheels + 10 sdists built, hashes validated

---

## Train G — .NET NuGet Proof

**Owner:** .NET engineer
**Allowed paths:**
- .local/r63-metadata/dotnet-nupkgs/
- reports/r63/dotnet-nuget-replay-proof.md
**Stop condition:** nupkgs present + hashes documented

---

## Train H — FODS/FODT Product Advancement

**Owner:** Product engineer (FODS/FODT)
**Allowed paths:**
- src/python/fods/neutral_model.py
- src/python/fodt/neutral_model.py
- tests/python/fods/test_r63_*.py
- tests/python/fodt/test_r63_*.py
- reports/r63/fods-fodt-product-advancement.md
**Shared files:** release-manifests/ (update after API proof, after Train D)
**Stop condition:** 2+ new FODS + 2+ new FODT capabilities with tests

---

## Train I — Four Format Track Advances

**Owner:** Format expansion engineer
**Allowed paths:**
- src/python/{dif,ppm,ods,csv,pgm,pbm,sylk,qoi,xpm,pam}/
- tests/python/{dif,ppm,ods,csv,pgm,pbm,sylk,qoi,xpm,pam}/test_r63_*.py
- reports/r63/non-fods-fodt-four-track-advancement.md
**Stop condition:** 4 tracks advanced with code + tests

---

## Train J — Phase Audits

**Owner:** Phase audit lead
**Allowed paths:** reports/r63/phase-audit-13-repair.md, reports/r63/phase-audit-14-rc-handoff-and-workahead.md
**Forbidden paths:** Gate approval files (no self-approval)
**Stop condition:** PA13 repaired + PA14 verdict issued

---

## Trains W1-W6 — Work-Ahead

**Owner:** Work-ahead planner
**Allowed paths:** reports/r63/workahead-*.md
**Forbidden paths:** All authority files (acquisition-packs/*, registry/*, state/*)
**Stop condition:** 6 work-ahead reports complete; no gate mutations

---

## Train K — Spec-Cache Authority

**Owner:** Acquisition lead
**Allowed paths:** reports/r63/acquisition-spec-cache-sample-authority.md
**Forbidden paths:** acquisition-packs/ (read-only)
**Stop condition:** Authority verified for ODS/CSV/DIF/PPM + 2 lower-maturity formats

---

## Train L — Docs/Memory/Sync

**Owner:** Memory/docs lead
**Allowed paths:**
- memory/
- reports/r63/docs-taskcards-memory-sync.md
**Shared files:** release-manifests/ (update after Train D + F complete)
**Stop condition:** Memory + master-plan updated with R63 evidence

---

## Train M — Final Bundle + Sidecar

**Owner:** Coordinator
**Allowed paths:** All (coordinator authority)
**Stop condition:** BUNDLE_VALIDATION: PASS + SIDECAR_PROOF_VALIDATION: PASS
