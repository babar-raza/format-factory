---
artifact_id: r22-preflight-r21-baseline-and-lane-ownership
artifact_type: report
sprint: FORMAT-FACTORY-R22-FULL-THROTTLE-RELEASE-CANDIDATE-AND-GATE11-PROTOTYPE-TRAIN-001
date: "2026-05-17"
gate: "0"
visibility: internal
---

# R22 Gate 0 — Preflight and R21 Baseline Verification

## Git State

Branch: main
R21 commits verified:
- 144a52a feat(release): prepare Python FOSS release readiness and Gate 11 preexecution
- 5e8d676 fix(evidence): align R21 contract_id to sprint_id for metadata identity check
- 9e9ef97 chore(evidence): add R21 evidence bundle with BUNDLE_VALIDATION: PASS

Pre-existing dirty state at session start: FORMAT-FACTORY-SKILLS-PRD-HARDENING-001 artifacts
Resolution: committed with exact-path staging (chore(skills) commits d4a100e, 71dac7d)
Git tree after cleanup: CLEAN (only ?? format-factory.zip which is pre-existing)

## R21 Source Paths Verified

- [x] src/python/zst/__init__.py + zst_codec.py
- [x] src/python/fodp/__init__.py + fodp_codec.py
- [x] src/python/fodg/__init__.py + fodg_codec.py
- [x] src/python/gnumeric/__init__.py + gnumeric_codec.py
- [x] src/python/abw/__init__.py + abw_codec.py
- [x] examples/python/zst/ examples/python/fodp/ examples/python/fodg/ examples/python/gnumeric/ examples/python/abw/
- [x] release-manifests/python-foss/ (6 files)
- [x] packaging/python/package-matrix.yaml + pyproject.template.toml + build-local-packages.py
- [x] docs/python-foss/ (5 files)
- [x] acquisition-packs/fods/ gate11-architecture-approval.md, gate11-commercial-licensing.md, gate11-nuget-package-plan.md, gate11-conversion-export-technical-design.md
- [x] acquisition-packs/fodt/ (same)

## Tooling State

| Tool | Version | Status |
|------|---------|--------|
| Python | 3.13.2 | OK |
| python build | 1.4.2 | OK — R21 blocker RESOLVED |
| hatchling | 1.29.0 | OK — installed pip install --user |
| setuptools | 80.10.1 | OK (via user site-packages) |
| dotnet SDK | 10.0.204 | OK |
| pytest | 9.0.3 | OK (user site-packages) |
| jsonschema | available | OK |

## Quick Test Baseline

- tests/evidence: 106 passed (quick run)
- CURRENT_STATE_CONSISTENCY: PASS
- METHODOLOGY_LINK_CHECK: PASS
- FODS .NET tests (no-rebuild): 42/42 PASS
- FODT .NET tests (no-rebuild): 43/43 PASS

## R21 Known Issues to Address in R22

1. local package build: build_backend_unavailable in R21 → RESOLVED (hatchling installed)
2. FODP/FODG/Gnumeric/ABW Gate 4 shown as not_started in gate matrix → REPAIR required (Gate 1)
3. G11-E was Babar-required in R21 → CORRECTED in R22 prompt (delegated to agent)

## Lane Ownership

| Lane | Owner | Scope |
|------|-------|-------|
| A | Coordinator | Preflight, gate tracking |
| B | Authority repair | Registry/pack/manifest consistency |
| C | Packaging | Build backend + build system |
| D-H | Per-format Python | ZST/FODP/FODG/Gnumeric/ABW builds |
| I | Cross-format | Examples runner, CLI |
| J | FODS .NET | G11-E CSV prototype |
| K | FODT .NET | G11-E TXT prototype |
| L | Gate 11 IV | Commercial boundary audit |
| M | Normalization | Registry/pack/taskcard/memory |
| N | Validation | Test runs, evidence bundle |

## Status

GATE_0: PASS
