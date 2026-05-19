# Lane C: Control-Plane Isolated Verification

## Components Verified
1. **Config** (`config.py`): load_ai_config, AIConfig, get_api_key
2. **Model Discovery** (`model_discovery.py`): discover_models, guess_model_family, infer_role_candidates
3. **Model Router** (`model_router.py`): ModelRouter.select, fail-closed, fallback
4. **Capability Probe** (`capability_probe.py`): probe_model

## Test Results (isolation)
| Test | Status |
|------|--------|
| Missing env returns unconfigured | PASS |
| Invalid endpoint URL handled | PASS |
| API key never in config repr | PASS |
| Malformed model list returns empty | PASS |
| Model with empty ID skipped | PASS |
| Capability probe blocked when unconfigured | PASS |
| No-fallback role fails closed | PASS |
| Empty model list fails closed | PASS |
| Fallback logging includes model ID | PASS |

## Live Probes (authorized by R31 prompt)
| Probe | Result |
|-------|--------|
| Model discovery | 7 models at llm.professionalize.com |
| Capability probe (gpt-oss) | PROBE_OK, 116 tokens |
| No secrets in telemetry | CONFIRMED |

## Models Discovered (live)
| Model ID | Family | Chat | Embed |
|----------|--------|------|-------|
| qwen3-next | qwen | yes | no |
| experimental | unknown | yes | no |
| gpt-oss | gpt | yes | no |
| recommended | unknown | yes | no |
| qwen3-embedding-8b | qwen | yes | yes |
| Qwen2.5-VL-7B | qwen | yes | no |
| stable-diffusion-3.5-large | unknown | yes | no |

## Status: VERIFIED (isolated + live)
