# Live AI Gateway Policy

**Sprint:** FORMAT-FACTORY-ACCELERATION-PRODUCT-FIRST-AI-LLM-EMBEDDING-EXECUTION-001
**Date:** 2026-06-04

---

## Per-Role Fixture Table

| Role | Fixture OK? | No-Model Behavior | This Sprint Status |
|------|-------------|------------------|--------------------|
| summarization | YES | Fixture template | LIVE |
| structured_extraction | YES | Fixture template | LIVE |
| test_generation | YES | Fixture template | LIVE |
| evidence_review | YES | Fixture template | LIVE |
| agentic_low_risk | NO | status: skipped | SKIPPED (no model) |
| security_analysis | NO | status: skipped | N/A |

## ai-usage-ledger.jsonl Schema

```json
{
  "timestamp": "<ISO8601>",
  "sprint_id": "<sprint-id>",
  "tool": "<tool_name>",
  "role": "<AIRole>",
  "operation": "<operation_name>",
  "status": "success | fixture | skipped | blocked_no_model | error",
  "authority_state": "ai_draft",
  "live_ai_used": true | false
}
```

**Rule:** `fixture` mode → `live_ai_used: false`. `success` → `live_ai_used: true`.
`skipped` → no output produced; ledger row written with `status: skipped`.

## Forbidden Patterns

| Pattern | Reason |
|---------|--------|
| `import openai` directly in any tool | Bypasses approved gateway |
| `import anthropic` directly in any tool | Bypasses approved gateway |
| `os.environ["OPENAI_API_KEY"]` read directly | Key management bypassed |
| fixture output labeled as `status: success` | Misleads live_ai_used accounting |
| agentic_low_risk with fixture fallback | Hard prohibition — skipped mode required |
| API key value in any written file | Security violation |

## Gateway Configuration

- Endpoint: `PROFESSIONALIZE_BASE_URL` or `GPT_OSS_ENDPOINT` env var
- API key: `GPT_OSS_API_KEY` env var
- All calls: `gateway_chat()` in `tools/ai/control_plane/gateway.py`
- Via: litellm backend

## This Sprint

- Gateway mode: LIVE (`is_configured=True`)
- Live AI calls: ≥1 (summarization, structured_extraction, test_generation, evidence_review)
- Fixture fallback: 0 (gateway was live for all fixture-OK roles)
- Skipped (agentic_low_risk): pre/mid/final management passes
