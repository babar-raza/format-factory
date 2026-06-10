# LLM Usage and Metrics Policy

**Sprint:** FORMAT-FACTORY-ACCELERATION-PRODUCT-FIRST-AI-LLM-EMBEDDING-EXECUTION-001
**Date:** 2026-06-04

---

## JSONL Schema (ai-usage-ledger.jsonl)

Each row in `reports/acceleration-product-first/ai-usage-ledger.jsonl`:

```json
{
  "timestamp": "2026-06-04T07:00:00+00:00",
  "sprint_id": "FORMAT-FACTORY-ACCELERATION-PRODUCT-FIRST-AI-LLM-EMBEDDING-EXECUTION-001",
  "tool": "ai_product_brain",
  "role": "summarization",
  "operation": "capability_gap_analysis",
  "status": "success",
  "authority_state": "ai_draft",
  "live_ai_used": true
}
```

**Forbidden fields in ledger:**
- No API key values
- No raw prompt content
- No PII
- No model version beyond what gateway reports

## Fixture Rule

`fixture` status in ledger → `live_ai_used: false`.
Fixture output is acceptable for roles where fixture is permitted (all except agentic_low_risk).
Fixture output is NEVER labeled as `status: success` or `live_ai_used: true`.

## Metrics Tracked

| Metric | Where | Purpose |
|--------|-------|---------|
| Live AI call count | ai-usage-ledger.jsonl rows with status=success | Gateway cost tracking |
| Fixture fallback count | rows with status=fixture | Identifies unreliable roles |
| Skipped count | rows with status=skipped | Documents agentic_low_risk unavailability |
| Machinery creep ratio | evidence-critique.json.machinery_creep_ratio | Sprint health check |
| Product velocity | product-velocity-impact-scorecard.json | Mainstream throughput impact |

## Gateway Metrics This Sprint

- Total AI tool invocations: ≥8 (one per tool per format; some multi-format)
- Live AI calls: majority (gateway LIVE confirmed)
- Fixture fallbacks: 0 (gateway was live for all fixture-OK roles)
- Skipped: 3 (pre/mid/final agentic_low_risk passes — no model configured)
- Errors: 0

## Policy: No API Cost Without Ledger Row

Every gateway_chat() call MUST append a row to ai-usage-ledger.jsonl.
Missing ledger rows are a policy violation and must be caught in evidence review.
