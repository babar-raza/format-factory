# Product Breadth Handoff Hardening
Sprint: FORMAT-FACTORY-SKILLS-GOVERNED-EXECUTION-HARDENING-IV-001

---

## Result: PASS — 3 Families Covered (FODS full + FODT shell + Netpbm shell)

---

## FODS — Full Packet (READY_FOR_MAINSTREAM)

- Gap: GAP-FODS-DOGFOOD-CSV-DOTNET-001
- Capability: dogfood_status.fods_to_csv_dotnet
- Packet: reports/skills-product-first/mainstream-consumption-packet.json
- Handoff: reports/skills-product-first/generated-handoffs/handoff-spf-001-add-dotnet-api.yaml
- Template: docs/prompt-templates/skills/add-dotnet-api-handoff-template.md
- Status: FULL — All 18 fields present. Safe. Independently consumable.
- Authority mutation: NOT required. Downgrade rule fires if capability update missing.

---

## FODT — Shell Packet (SHELL — NEEDS_MAINSTREAM_DISCOVERY)

- Gap: GAP-FODT-DOGFOOD-MD-DOTNET-001
- Capability: dogfood_status.fodt_to_markdown_dotnet
- Shell: reports/skills-governed-execution-hardening/fodt-packet-shell.json
- Template: docs/prompt-templates/skills/add-dotnet-api-handoff-template.md (reusable)
- Status: SHELL — Mainstream can proceed with discovery phase
- Limitations:
  - Exact sprint test number needs assignment by Mainstream
  - FodtDocument.cs method name to confirm
  - Skills must run dry-run handoff generation before live execution
- Forbidden files: src/python/*, src/net/fods/*, src/net/netpbm/*, registry, plans, poc-targets, .vscode/mcp.json, .supervisor/policies.yaml, .claude-plugin/*
- Proposed delta (not direct mutation): fodt.dogfood_status.fodt_to_markdown_dotnet → IMPLEMENTED

---

## Netpbm — Shell Packet (SHELL — NEEDS_MAINSTREAM_DISCOVERY)

- Gap: GAP-NETPBM-DOGFOOD-PACKAGE-DOTNET-001
- Capability: dogfood_status.netpbm_image_pipeline_dotnet
- Shell: reports/skills-governed-execution-hardening/netpbm-packet-shell.json
- Template: docs/prompt-templates/skills/add-dotnet-api-handoff-template.md (reusable)
- Status: SHELL — Mainstream selects which Netpbm API to implement
- Limitations:
  - Exact Netpbm method (Crop, Overlay, Gamma, etc.) selected by Mainstream from current capability matrix
  - Sprint test number needs assignment
  - Skills must run dry-run before Mainstream live execution
- Forbidden files: src/python/*, src/net/fods/*, src/net/fodt/*, registry, plans, poc-targets, .vscode/mcp.json, .supervisor/policies.yaml, .claude-plugin/*
- Proposed delta (not direct mutation): netpbm.dogfood_status.netpbm_image_pipeline_dotnet → IMPLEMENTED

---

## Breadth Requirement

Supervisor requires 3 product families for breadth coverage.
- FODS: FULL packet — directly consumable ✓
- FODT: shell packet — safe fallback ✓
- Netpbm: shell packet — safe fallback ✓

Mainstream can use FODS full packet immediately.
FODT and Netpbm shells unblock Mainstream without waiting for perfect handoffs.
