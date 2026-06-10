# Mainstream AI Acceleration Contract

**Sprint:** FORMAT-FACTORY-ACCELERATION-PRODUCT-FIRST-AI-LLM-EMBEDDING-EXECUTION-001
**Date:** 2026-06-04

---

## 4 Packets Produced

| # | Format | Gap | Track | Packet Path |
|---|--------|-----|-------|-------------|
| 1 | FODS | dogfood_status.fods_to_csv_dotnet | commercial_net | mainstream-consumption-packets/fods-dogfood_status-fods_to_csv_dotnet.json |
| 2 | FODT | dogfood_status.fodt_to_markdown_dotnet | commercial_net | mainstream-consumption-packets/fodt-dogfood_status-fodt_to_markdown_dotnet.json |
| 3 | Netpbm | dotnet_status.netpbm_flip_diagonal | commercial_net | mainstream-consumption-packets/netpbm-dotnet_status-netpbm_flip_diagonal.json |
| 4 | SYLK | python_status.write_sylk | foss_reduced | mainstream-consumption-packets/sylk-python_status-write_sylk.json |

## Mainstream Consumption Workflow

1. Mainstream worker reads packet JSON
2. Extracts: selected_gap, implementation_design (path), test_strategy, source_patterns, test_plan
3. Reads TRACK_FILE_RULES: allowed_files (worker may create/edit) + forbidden_files (must not touch)
4. Follows implementation_design.md for code changes in allowed paths
5. Uses test_plan for test file creation (authority_state: ai_draft — must be verified by running tests)
6. Applies downgrade_rules if capability cannot be fully implemented
7. Writes evidence declaration referencing packet as context source

## Downgrade Rules (example — per packet)

| Scenario | Downgrade Path |
|----------|---------------|
| Full dogfood export not implementable | Partial export with documented limitation |
| Test count < 8 | Minimum 6 tests + documented gap |
| API signature change needed | Propose in evidence declaration; Supervisor decides |
| Format incompatibility discovered | Document in evidence; update poc-targets.yaml via Supervisor |

## Packet Does Not Replace

- Test evidence (tests must actually pass)
- Gate approval (human gates still apply)
- poc-targets.yaml authority (checksum must be verified)
- Evidence declaration (worker writes their own)

## External Tool Context

All packets include:
```json
"external_tool_context": {
  "ruflo_context_available": false,
  "ruflo_mode": "absent",
  "superpowers_skill_pattern_available": false,
  "ghidra_mcp_applicable": false,
  "external_tool_activation_required_for_packet": false
}
```

A Mainstream worker needs no external tool to use any packet.
