# Skills Consumption Readiness
Sprint: FORMAT-FACTORY-SKILLS-GOVERNED-EXECUTION-HARDENING-IV-001

---

## Status: SKILLS_CONSUMABLE_WITH_LIMITATIONS

Mainstream can proceed. Supervisor should not classify Skills as missing.

---

## Immediately Consumable

**FODS CSV Dogfood Export (add-dotnet-api)**
- Gap: GAP-FODS-DOGFOOD-CSV-DOTNET-001
- Packet: reports/skills-product-first/mainstream-consumption-packet.json
- Handoff: reports/skills-product-first/generated-handoffs/handoff-spf-001-add-dotnet-api.yaml
- Template: docs/prompt-templates/skills/add-dotnet-api-handoff-template.md
- Mode for live execution: Change `mode: dry-run` → `mode: live` in Mainstream's copy
- Validation: `python tools/supervisor/validate_skill_transcript.py <transcript>`

## Available as Shell (with Discovery)

**FODT Markdown Export**
- Shell: reports/skills-governed-execution-hardening/fodt-packet-shell.json
- Action: Mainstream selects method → Skills generates dry-run handoff → Mainstream executes live

**Netpbm Image Pipeline**
- Shell: reports/skills-governed-execution-hardening/netpbm-packet-shell.json
- Action: Mainstream selects which Netpbm method → Skills generates dry-run handoff → Mainstream executes live

---

## Limitations

1. FODT and Netpbm shells require Mainstream to trigger a Skills dry-run handoff generation
2. MCP check-mcp-status remains deferred — not blocking product consumption
3. Capability matrix updates are proposed deltas, not direct authority mutations

---

## No-Go Conditions

None currently. Skills output is safe and consumable.

---

## Routing Packet Reference

Latest supervisor routing packet:
- reports/supervisor-streams/mainstream/latest-routing-packet.json
- Stream decision: CONTINUE_WITH_LIMITATIONS
- Top gap: commercial-net-fods-dogfood-status-fods-to-csv-dotnet (priority_score 125)
- This is exactly what the Skills full packet targets.

governed_execution_consumed flag: Set to `true` in routing packet after Mainstream
successfully executes GAP-FODS-DOGFOOD-CSV-DOTNET-001 and transcript validates.
