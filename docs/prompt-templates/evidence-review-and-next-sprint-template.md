# Evidence Review and Next Sprint Template

**Added:** 2026-06-04
**Use:** When reviewing uploaded sprint evidence bundles and generating the next prompt.

## Pre-Review Checklist

Before producing a verdict or next prompt:
1. Inspect the uploaded evidence bundle (ZIP contents)
2. Verify declared work matches materialized artifacts
3. Classify evidence caveats as blocking or non-blocking
4. Determine whether forward progress is safe

## Evidence Review Format

### Bundle Metadata
- Bundle name: {{BUNDLE_NAME}}
- SHA-256: {{SHA256}}
- Entry count: {{ENTRY_COUNT}}
- Size: {{SIZE}} bytes

### Declared Work Items
| Work Item | Status | Evidence Found | Verdict |
|---|---|---|---|
| {{ITEM}} | {{DECLARED_STATUS}} | {{FOUND}} | {{VERDICT}} |

### Evidence Caveats
| Caveat | Severity | Blocking? | Action |
|---|---|---|---|
| {{CAVEAT}} | MINOR/MAJOR | YES/NO | {{ACTION}} |

### Forward Progress Decision
- Is forward progress safe? YES / NO
- If NO, state exact blocking reason.
- Do NOT block on non-blocking caveats.

## Verdict Guidance

**Accept with non-blocking caveats when:**
- Core work is real and materialized
- Tests pass (or failures are known/acceptable)
- No overclaimed product readiness
- No forbidden file changes

**Reject or require rework when:**
- Declared work items not materialized
- Tests not found/not run
- Forbidden files changed
- Gate self-approval attempted
- Evidence repair was the entire sprint (no product output)

**Never:**
- Block safe forward progress on ZIP metadata issues
- Treat evidence_quality_score=0.0 as rejection when work is real
- Let continuation-signal conflict block the next sprint

## Next Prompt Generation

After verdict, always generate the next prompt:

1. State the recommended next sprint stream and ID.
2. Include: product-first purpose, hard PASS quota (if Mainstream), allowed/forbidden paths, lane ownership, taskcards, evidence closeout requirements.
3. Use declaration-driven closeout: `python tools/supervisor/autonomous_cycle.py --declaration <path>`
4. Final response contract must include: absolute review package path, SHA-256.
5. Prompt must be ready-to-send without further human editing.

## Template Fields
- Stream: {{STREAM}}
- Sprint ID: {{SPRINT_ID}}
- Previous sprint: {{PREVIOUS_SPRINT_ID}} (verdict: {{PREVIOUS_VERDICT}})
- Product-first purpose: {{PURPOSE}}
- Hard PASS quota: {{QUOTA}} (or N/A for non-Mainstream)
- Allowed paths: {{ALLOWED_PATHS}}
- Forbidden paths: src/net/*, src/python/*, .vscode/mcp.json, .supervisor/policies.yaml (always)
