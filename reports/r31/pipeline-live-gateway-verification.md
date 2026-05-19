# Lane J: Pipeline Live-Gateway Verification

## Live Probes Performed
All probes used non-sensitive fixture content through the approved gateway.

### 1. Model Discovery (live)
- Endpoint: llm.professionalize.com
- Models discovered: 7
- Model IDs: qwen3-next, experimental, gpt-oss, recommended, qwen3-embedding-8b, Qwen2.5-VL-7B, stable-diffusion-3.5-large
- Fingerprints computed for all 7 models

### 2. Capability Probe (live)
- Model: gpt-oss
- Response: PROBE_OK
- Tokens: in=72, out=44, total=116
- Prompt hash: 2a5ace29cc39860b
- Status: success
- No secrets in telemetry: CONFIRMED

### 3. Structured Extraction Probe (live)
- Model: gpt-oss
- Input: Non-sensitive FODS spec fixture text
- Prompt: "Extract structured metadata" (format_name, encoding, root_element, compression)
- Response: `{"format_name":"FODS","encoding":"UTF-8","root_element":"office:document","compression":"none"}`
- Tokens: in=146, out=223
- Schema valid: true
- Citation verification: N/A (extraction task)
- Contradiction check: no_contradictions (against 2 verified facts)
- Evaluator: passed, score 1.0
- Authority state: ai_draft (NOT auto-promoted)

### 4. CLI Live Probe
```
python tools/ai/run_ai_checks.py --live-probe --sprint-id R31
```
- overall_passed: true
- probe_model: qwen3-next
- probe_success: true
- secrets_in_telemetry: false

## Evidence
- Live probe artifacts stored in reports/r31/pipeline-fixture-run/ai-pipeline-runner-output.json
- No secrets transmitted (fixture content only)
- No mutations performed
- No authority promotions

## Status: VERIFIED (live)
