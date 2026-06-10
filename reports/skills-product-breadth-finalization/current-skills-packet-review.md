# Current Skills Packet Review
Sprint: FORMAT-FACTORY-SKILLS-PRODUCT-BREADTH-HANDOFF-FINALIZATION-001
Source: reports/skills-governed-execution-hardening/

---

## Packet Inventory (from Hardening IV Sprint)

### FODS — FULL packet (READY_FOR_MAINSTREAM)
- Source: reports/skills-governed-execution-hardening/fods-csv-packet-hardening.md
- Validation: PACKET_VALIDATION PASS, all 18 fields
- Gap ID: GAP-FODS-DOGFOOD-CSV-DOTNET-001
- Status: READY_FOR_MAINSTREAM — no finalization needed

### FODT — SHELL packet (NEEDS_MAINSTREAM_DISCOVERY)
- Source: reports/skills-governed-execution-hardening/fodt-packet-shell.json
- Limitations:
  - `{N}` placeholder — test R-number not assigned
  - `NEEDS_MAINSTREAM_DISCOVERY` for method name
  - No handoff YAML generated
  - Only covers `fodt_to_markdown_dotnet`; TXT variant not yet packaged
- poc-targets.yaml shows: `fodt_to_txt_dotnet: GAP_DOGFOOD_EXTERNAL` and `fodt_to_markdown_dotnet: GAP_DOGFOOD_EXTERNAL`
- Source files confirmed: FodtDocument.cs, FodtMarkdownExporter.cs, FodtTxtExporter.cs (all in src/net/fodt/)
- Next R-number: R114 (last test was FodtR113TxtDogfoodTests.cs)

### Netpbm — SHELL packet (NEEDS_MAINSTREAM_DISCOVERY)
- Source: reports/skills-governed-execution-hardening/netpbm-packet-shell.json
- Limitations:
  - `{N}{FeatureName}` placeholders — both test number and feature name TBD
  - No handoff YAML generated
  - Method name left for Mainstream to decide
- Acceleration packet chose: `dotnet_status.netpbm_flip_diagonal` (authority_state: ai_draft)
- Note: NetpbmR106FlipDiagonalTests.cs exists (R106 already implemented FlipDiagonal)
- Best next capability for R114: a new composite pipeline feature
- Source confirmed: src/net/netpbm/Model/NetpbmImage.cs, NetpbmExporter.cs
- Next R-number: R114 (last test was NetpbmR113TileTests.cs)

---

## Cross-Stream Packet Status

| Family | Hardening Sprint | Acceleration Packet | Combined Status |
|--------|----------------|---------------------|----------------|
| FODS | FULL — READY | N/A | READY (no finalization needed) |
| FODT | SHELL only | ai_draft (fodt_to_markdown) | NEEDS_FULL_PACKET |
| Netpbm | SHELL only | ai_draft (flip_diagonal — outdated) | NEEDS_FULL_PACKET |

---

## Finalization Work Required

1. **FODT Markdown** — Convert shell to full governed packet; generate handoff YAML
2. **FODT TXT** — Create new full packet (not in hardening sprint); generate handoff YAML
3. **Netpbm R114** — Convert shell to full governed packet with concrete feature; generate handoff YAML
4. **Schema compatibility maps** — Map Skills fields to Acceleration and Supervisor schemas
5. **Integration Contract** — Tri-lane consumable contract with all 3 full packets
