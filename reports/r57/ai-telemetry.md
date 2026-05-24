# R57 Train J — AI/Telemetry Report

**Sprint:** FORMAT-FACTORY-R57-SELF_VERIFYING-RC-REPLAY-PRODUCT-EXPANSION-PHASE8-MEGA-TRAIN-001
**Train:** J — AI/Telemetry
**Date:** 2026-05-23
**Status:** COMPLETE

---

## AI Test Execution

**Command:** `.local/venv/Scripts/pytest.exe tests/ai/ --ignore=tests/ai/test_model_discovery.py --ignore=tests/ai/test_phase2_model_registry.py`

| Metric | Value |
|--------|-------|
| Passed | 590 |
| Failed | 4 |
| Skipped | 1 |
| Total collected | 595 |
| Duration | ~86 s |

---

## Failure Analysis

All 4 failures are pre-existing and unrelated to R57:

| Test | Root Cause | Classification |
|------|-----------|----------------|
| `test_r31_ai_system_verification::test_discover_models_uses_mocked_api_key` | `No module named 'httpx'` in test venv | PRE_EXISTING |
| `test_r31_ai_system_verification::test_discover_returns_empty_when_api_key_missing_and_env_clear` | Same: `No module named 'httpx'` | PRE_EXISTING |
| `test_r31_ai_system_verification::test_malformed_model_list_returns_empty` | Same: `No module named 'httpx'` | PRE_EXISTING |
| `test_r31_ai_system_verification::test_model_with_empty_id_skipped` | Same: `No module named 'httpx'` | PRE_EXISTING |

**httpx** is not installed in `.local/venv`. These tests import `tools.ai.control_plane.model_discovery` which requires `httpx`. These 4 failures appeared consistently in R56 and prior sprints. They do not indicate regression.

---

## Collection Errors (2 files ignored)

| File | Root Cause | Classification |
|------|-----------|----------------|
| `test_model_discovery.py` | Imports `model_discovery` at module level → `No module named 'httpx'` | PRE_EXISTING |
| `test_phase2_model_registry.py` | Same root cause | PRE_EXISTING |

---

## AI Governance Audit

| Dimension | Status |
|-----------|--------|
| Ungoverned direct endpoint calls | 0 (AI gateway audit from R53/R56 — no change) |
| Fixture mode active | YES — no `GPT_OSS_ENDPOINT`/`GPT_OSS_API_KEY` in env |
| Live call (test_r38) | BLOCKED_OR_PASSES (fixture mode gates the live probe) |
| AI usage policy | ACTIVE — AI is accelerator not authority |
| Gate approval delegation to AI | PROHIBITED |

---

## Train J Verdict

TRAIN_J_COMPLETE — 590/595 AI tests pass; 4 pre-existing httpx failures unchanged from R56.
AI governance: 0 ungoverned calls; fixture mode active.
