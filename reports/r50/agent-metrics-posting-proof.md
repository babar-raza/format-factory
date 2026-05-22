# R50 Agent Metrics Posting Proof

**Sprint:** FORMAT-FACTORY-R50-EVIDENCE-CLOSEOUT-REPAIR-AND-OBJECT-MODEL-HARDENING-001
**Date:** 2026-05-22

## Environment Status

| Variable | Status |
|----------|--------|
| GPT_OSS_ENDPOINT | SET (35 chars) — https://llm.professionalize.com/v1/ |
| GPT_OSS_API_KEY | SET (25 chars) |
| GPT_OSS_MODEL | NOT_SET — resolved via model discovery to `recommended` |
| PROFESSIONALIZE_API_KEY | SET (25 chars) |
| AGENT_METRICS_ENDPOINT | SET (112 chars) — Google Apps Script |
| AGENT_METRICS_API_KEY | NOT_SET — used AGENT_METRICS_TOKEN instead |
| AGENT_METRICS_TOKEN | SET (14 chars) |

## Model Discovery

Called `GET /v1/models` — available models:
- `qwen3-next`
- `experimental`
- `gpt-oss`
- **`recommended`** — selected (per user instruction to use recommended model)
- `qwen3-embedding-8b`
- `Qwen2.5-VL-7B`
- `stable-diffusion-3.5-large`

`GPT_OSS_MODEL` resolved to: `recommended`

## Result

`AI_ACCELERATION_PILOT: PASS`

## Live AI Call (Lane 5A)

**Purpose:** Object-model gap priority analysis — TC-FORMULA-001 vs TC-STYLE-001 vs TC-COLDEF-001

**Model:** `recommended` (resolved via model discovery)
**Endpoint:** `llm.professionalize.com/v1/chat/completions`
**Tokens:** 274 total (101 prompt + 173 completion)
**Finish reason:** `stop`

**AI Conclusion:**
> "The most critical gap is the loss of formula cells, because they directly affect the
> correctness of computed data and can silently corrupt results. Preserving formulas should
> be prioritized before style metadata or column definition details."

**Verification:** Consistent with existing RISK-002 classification and TC-0054 priority=Medium
vs TC-0055/TC-0056 priority=Low. AI conclusion aligns with human judgement. No contradiction.

## Agent Metrics Post (Lane 5C)

**Endpoint:** `AGENT_METRICS_ENDPOINT` (Google Apps Script)
**Auth:** `AGENT_METRICS_TOKEN` (sent as query param; `AGENT_METRICS_API_KEY` not set)
**Payload:** run=R50, live_ai_calls=1, model=recommended, tokens_used=274, status=COMPLETE
**Response:** `{"status":200,"ok":true,"message":"Metrics recorded","run_id":"R50"}`
**Result:** `AGENT_METRICS_POST: PASS`

## Live Calls This Sprint

`live_ai_calls: 1`

`LLM_PROVIDER_SUMMARY: 1_LIVE_CALL_R50_recommended_274_tokens`

## Notes

- `GPT_OSS_MODEL` was NOT_SET but resolved via model discovery (`recommended` is a registered alias)
- `AGENT_METRICS_API_KEY` was NOT_SET; `AGENT_METRICS_TOKEN` worked as the auth mechanism
- R49 had `live_ai_calls: 0` — R50 is the first sprint with a confirmed live synthesis call + Agent Metrics post
