# External Tool Boundary Hardening

**Sprint:** FORMAT-FACTORY-ACCELERATION-HARDENING-IV-AND-CONSUMPTION-CONTRACT-001
**Date:** 2026-06-04

## Verified Tool States

| Tool | Mode Confirmed | Installation Check | Result |
|------|---------------|-------------------|--------|
| Ruflo | absent | `importlib.util.find_spec('ruflo')` → None | ABSENT |
| Superpowers | audit_only | `ls .claude/commands/ | grep superpowers` → no match | NOT_INSTALLED |
| GhidraMCP | disabled | `.mcp.json` absent or no ghidra entry | NOT_ACTIVE |

## Boundary Rules Enforced

| Rule | Status |
|------|--------|
| No Ruflo install or activation in any sprint | ENFORCED |
| No Superpowers plugin install by Acceleration | ENFORCED |
| No GhidraMCP binary analysis performed | ENFORCED |
| All external_tool_context fields carry authority_state: ai_draft | ENFORCED |
| external_tool_activation_required_for_packet: false in all 4 packets | ENFORCED |
| No external tool output used as authority for capability matrix | ENFORCED |

## TC-EXT-007 Verification (Hardening Sprint)

Commands run at Gate 7 closeout:

```
python -c "import importlib.util; print('ruflo:', 'ABSENT' if importlib.util.find_spec('ruflo') is None else 'PRESENT')"
→ ruflo: ABSENT

ls .claude/commands/ | grep -i superpowers
→ (no output — no superpowers commands present)

python -c "import json; from pathlib import Path; mcp = Path('.mcp.json'); print('NO_MCP_CONFIG: OK') if not mcp.exists() else print([k for k in json.loads(mcp.read_text()).get('mcpServers',{}) if 'ghidra' in k.lower()])"
→ NO_MCP_CONFIG: OK
```

All 7 external-tool authority invariants: **VERIFIED**

## Packet external_tool_context Compliance

All 4 Mainstream packets (FODS, FODT, Netpbm, SYLK) confirmed to contain:

```json
"external_tool_context": {
  "ruflo_context_available": false,
  "ruflo_mode": "absent",
  "superpowers_skill_pattern_available": false,
  "superpowers_relevant_skills": [],
  "ghidra_mcp_applicable": false,
  "ghidra_mcp_activation_required": false,
  "external_tool_recommendations": [],
  "external_tool_activation_required_for_packet": false,
  "authority_state": "ai_draft",
  "non_authoritative": true
}
```

A Mainstream worker can consume all 4 packets without any external tool installed.

## Risk Register Compliance

- `reports/acceleration-product-first/external-tool-risk-register.json` present
- 3 entries: Ruflo (DISABLED_BY_DEFAULT), Superpowers (AUDIT_ONLY), GhidraMCP (DISABLED)
- All entries validate against `reports/acceleration-plan-repair/tool-risk-register-schema.json`

## Negative Fixture Coverage (External Tool)

NEG-004: External tool closes taskcard → REJECT (covered in authority-negative-fixtures.json)
NEG-005: External tool recommendation mutates workspace → REJECT (covered)

Both fixtures tested in `tests/supervisor/acceleration/test_acceleration_hardening_iv.py`.

## Final Verdict

**EXTERNAL_TOOL_BOUNDARY: HARDENED**

No external tool installed, activated, or used as authority during this sprint.
All packets usable without external tools.
