# AI Phase 2: Runtime Guard and Evidence Adapter Report
# Sprint: R26 Lane D
# Date: 2026-05-19

## Runtime Guard Enhancements

### Phase 2 Changes
1. **Direct endpoint bypass detection**: New `scan_for_direct_endpoint_calls()` function scans tools/ai/ for Python files that make HTTP calls (httpx.Client, requests.get, etc.) with AI context (GPT_OSS, professionalize.com, /v1/chat, etc.)
2. **Excluded files**: gateway.py, model_discovery.py, capability_probe.py, runtime_guard.py — these are authorized to reference endpoints
3. **tools/ai/ scan**: run_guard() now scans tools/ai/ in addition to src/python/ and src/net/

### Scan Coverage

| Path | Scan Type | Status |
|------|-----------|--------|
| src/python/ | Forbidden imports + env + URLs | PASS (0 violations) |
| src/net/ | Forbidden imports + env + URLs | PASS (0 violations) |
| tools/ai/ | Direct endpoint bypass detection | PASS (0 violations) |

### What Gets Detected
- Direct httpx/requests calls + AI URL/env context → violation
- Authorized gateway/discovery files → excluded from scan
- Non-AI HTTP calls → not flagged (no AI context)

## Evidence Adapter Status

Phase 2 establishes the runtime guard and telemetry as evidence-producing components. The evidence adapter pattern is:
- Runtime guard result is serializable (RuntimeGuardResult → JSON)
- Telemetry spool is JSONL (directly includable in evidence bundles)
- Model discovery results are serializable (ModelCapability → JSON)
- Spool replay validation produces summary dict for evidence

Formal evidence adapter (automated bundle inclusion) deferred to Phase 3 when telemetry volume warrants it.

## New Tests (Lane D): 7 tests

| Test Class | Tests | Status |
|-----------|-------|--------|
| TestDirectEndpointBypass | 5 | PASS |
| TestGuardPhase2Integration | 2 | PASS |
