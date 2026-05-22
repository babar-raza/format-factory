# AI Gateway / Direct-Call Audit

**Sprint:** FORMAT-FACTORY-R53-SELF-VERIFYING-BASELINE-001
**Date:** 2026-05-22
**Tool:** grep scan of tools/ai/ and src/ for LLM call patterns

## Scan Patterns

- `litellm.completion`
- `openai.ChatCompletion`
- `anthropic`
- `requests.post` (to LLM endpoints)

## Scan Results

```
tools/ai/control_plane/gateway.py:80:  response = litellm.completion(
tools/ai/validators/runtime_guard.py:85: "requests.post",
```

## Classification

| Location | Pattern | Classification | Notes |
|----------|---------|---------------|-------|
| `tools/ai/control_plane/gateway.py:80` | `litellm.completion` | **GOVERNED** | This IS the gateway. All AI calls must route through this path. |
| `tools/ai/validators/runtime_guard.py:85` | `"requests.post"` | **GUARD** | This is the guard that DETECTS ungoverned calls — it scans for the pattern as a string, does not make calls |

## Result: PASS — 0 Ungoverned Calls Found

All LLM calls in the codebase route through:
`tools/ai/control_plane/gateway.py` → `litellm.completion`

The `runtime_guard.py` scan confirms that it monitors for:
- `litellm.completion`
- `openai.ChatCompletion`
- `anthropic`
- `requests.post`

These appear in source only in the governed gateway and in the guard itself.

## AI Endpoint Configuration

- `GPT_OSS_ENDPOINT`: present in environment
- `GPT_OSS_API_KEY`: present
- `AGENT_METRICS_ENDPOINT`: present
- `ANTHROPIC_KEY`: present
- Live endpoint calls: NOT invoked in R53 (all fixture mode)

## Conclusion

AI gateway audit: **PASS**
No ungoverned LLM call path detected.
