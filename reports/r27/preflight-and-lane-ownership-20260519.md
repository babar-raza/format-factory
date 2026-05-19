# R27 Preflight and Lane Ownership
# Sprint: FORMAT-FACTORY-R27-GATE4-PROTOTYPES-G11-C7-C8-HARDENING-PUBLICATION-PACKET-AND-METADATA-SYNC-001
# Date: 2026-05-19
# Gate: 0

## Branch and Head

- Branch: main
- HEAD: bcfe62e (chore(metadata): update R26 sprint-overview with BUNDLE_VALIDATION: PASS)

## Git Status

Working tree has unrelated dirty files from an independent AI agent:

| File | Type | Classification |
|------|------|----------------|
| tools/ai/control_plane/model_router.py | Modified | AI work — OUT OF SCOPE, do not touch |
| tools/evidence/contracts/ai-platform-phase1-control-plane-foundation-20260518.yaml | Modified | AI evidence contract — OUT OF SCOPE, do not touch |
| reports/ai/r27-ai-platform-full-cycle-20260519/ | Untracked dir | AI reports — OUT OF SCOPE, do not touch |

**Classification:** DIRTY_STATE_SAFELY_CLASSIFIED — all dirty files are AI-related from independent agent. R27 will not stage, modify, or touch any of these files. Exact-path staging ensures no accidental inclusion.

## R26 Baseline

- R26 VERDICT: R26_COMPLETE
- Commit: 7fabb9b + bcfe62e
- Tests: 2306 passed, 13 skipped
- BUNDLE_VALIDATION: PASS

## Lane Ownership

| Lane | Owner | Paths | Status |
|------|-------|-------|--------|
| 0 | Coordinator | reports/r27/**, tools/evidence/contracts/r27-* | PENDING |
| A | This agent | reports/r27/r26-metadata-*, reports/r26-sprint-metadata-* | PENDING |
| B | This agent | reports/planning/r27-gate4-authorization-* | PENDING |
| C | This agent | src/python/ods/**, tests/python/ods/**, reports/implementation/r27-ods-* | PENDING |
| D | This agent | src/python/odt/**, tests/python/odt/**, reports/implementation/r27-odt-* | PENDING |
| E | This agent | src/python/qoi/**, tests/python/qoi/**, reports/implementation/r27-qoi-* | PENDING |
| F | This agent | tests/python/test_gate4_prototype_common.py, reports/verification/r27-gate4-* | PENDING |
| G | This agent | src/net/fods/**, tests/net/fods/**, reports/implementation/r27-fods-* | PENDING |
| H | This agent | src/net/fodt/**, tests/net/fodt/**, reports/implementation/r27-fodt-* | PENDING |
| I | This agent | src/python/{zst,fodp,fodg,gnumeric,abw}/*.md, release-manifests/**, reports/packaging/r27-* | PENDING |
| J | This agent | acquisition-packs/{xcf,zpaq}/**, samples/by-format/{xcf,zpaq}/**, reports/planning/r27-new-format-* | PENDING |
| K | This agent | memory/46-*, memory/00-index.md, registry/**, reports/r27/memory-* | PENDING |
| L | This agent | reports/testing/r27-*, reports/verification/r27-*, reports/governance/r27-* | PENDING |

## AI Exclusion Zone

The following paths are FORBIDDEN for this sprint:
- tools/ai/**
- tests/ai/**
- reports/ai/** (except classification as out-of-scope)

**Gate 0 — PASS**
