# R73 AI-Assisted Requirements and Telemetry

**Sprint:** FORMAT-FACTORY-R73-DELIVERY-PACKAGE-TRUTH-PRODUCT-ADVANCEMENT-GATE-READINESS-MEGA-TRAIN-001
**Date:** 2026-05-29
**Train:** K

---

## New Generated Requirements

Format: PBM (Portable Bitmap)
Mode: fixture (no live AI call — endpoint not configured in environment)

| Artifact | Requirements | Stage |
|---|---|---|
| generated-requirements/pbm/object-model-requirements.yaml | 3 entities (PBM-ENT-001..003) | ai_draft |
| generated-requirements/pbm/functional-requirements.yaml | 5 requirements (PBM-REQ-001..005) | ai_draft |
| generated-requirements/pbm/generation-report.md | Generation metadata | COMPLETE |

**Total new requirements:** 8
**Lifecycle stage:** ai_draft (all pending schema validation + human IV)

Coverage:
- PBM-ENT-001: PbmImage entity model
- PBM-ENT-002: PbmPixelStats (new R73 image_pixel_stats() API)
- PBM-ENT-003: PbmProbeResult
- PBM-REQ-001: Parse P1 ASCII PBM
- PBM-REQ-002: Parse P4 Binary PBM
- PBM-REQ-003: File size guard (security)
- PBM-REQ-004: image_pixel_stats() API (R73 addition)
- PBM-REQ-005: Comment stripping

---

## AI Telemetry Verification (Fixture Mode)

Test suite: `tests/ai/` (excluding test_model_discovery.py, test_phase2_model_registry.py — require httpx)

| Test File | Tests | Result |
|---|---|---|
| test_r27_telemetry_drain.py | — | PASS |
| test_r30_ai_defect_closure.py | — | PASS |
| test_r31_ai_system_verification.py | 86/91 PASS | 4 pre-existing failures (httpx) |
| test_r32_ai_deepening.py | — | PASS |
| test_r38_clean_closure_repair.py | — | PASS |

Pre-existing failures (4): `TestCleanEnvRegression` + `TestControlPlaneModelDiscovery` tests that
import `tools.ai.control_plane.model_discovery` — requires `httpx` library not in `.local/venv`.
These are pre-existing baseline failures unrelated to R73 work.

---

## Live AI Call Record

LIVE_AI_CALL: NONE (fixture mode — GPT_OSS_ENDPOINT not set in environment)
Expected behavior: fixture mode when endpoint absent. CONFIRMED.

---

## Lifecycle Note

Requirements pipeline enforces:
- `ai_draft` → `schema_validated` → `source_cited` → `authoritative_after_gate`
- No shortcut to `authoritative` status
- Schema validation required before any requirement is used for product decisions

GENERATED_REQUIREMENTS: 8_NEW_FOSS_PBM_AI_DRAFT
AI_TELEMETRY_PIPELINE: FIXTURE_MODE_PASS
AI_REQUIREMENTS_TELEMETRY: PASS
