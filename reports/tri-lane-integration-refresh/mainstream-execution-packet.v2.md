# Mainstream Execution Packet
# Sprint: FORMAT-FACTORY-TRI-LANE-INTEGRATION-REFRESH-AND-MAINSTREAM-READINESS-GATE-001
# Generated: 2026-06-04T00:00:00Z

> **Authority**: Advisory only. Mainstream product authority governs actual implementation.
> Acceleration advisory is `ai_draft` and must NOT be used as evidence.
> No gate approvals from this packet.

## Integration Status: `OK`
**Families**: 4

## Families

### FODS
- **Capability**: `dogfood_status.fods_to_csv_dotnet`
- **Gap ID**: `GAP-FODS-DOGFOOD-CSV-DOTNET-001`
- **Product track**: `commercial_net`
- **Readiness**: `READY_FOR_EXECUTION`

**Supervisor Route**
- Source file: `src/net/fods/FodsDocument.cs`
- SVG replacement rejected: `False`
- Authority: `routing_authority`

**Skills Handoff**
- Packet type: `full`
- Authority: `governed_execution_authority`
- Note: Full FODS packet from skills-product-first sprint

**Acceleration Advisory** *(ai_draft — not authoritative)*
- Use for: Skills stream may use packet data as advisory input; normalization required before registry entry.
- Authority: `ai_draft`

**Allowed Files**
- `src/net/fods/FodsDocument.cs`
- `src/net/fods/FodsWorkbook.cs`
- `tests/net/fods/FodsR114ExportToCsvTests.cs`
- `examples/net/fods/`

**Forbidden Files**
- `src/python/`
- `registry/format-registry.yaml`
- `plans/master-plan.md`
- `product-capability-matrix/poc-targets.yaml`

**Expected Tests**: tests/net/fods/FodsR114ExportToCsvTests.cs with 8+ test methods
**Expected Dogfood Output**: CSV file produced from FODS spreadsheet using FodsDocument.ExportToCsv()
**Expected Transcript**: `reports/{sprint}/skill-transcripts/transcript-fods-csv-{id}.json`

**Proposed Capability Delta** *(proposed only — not a direct write)*
- `fods.dogfood_status.fods_to_csv_dotnet` → `IMPLEMENTED`
- Requires test evidence: `True`

**Validation Commands**
```
dotnet test --filter FodsR114
```
```
python tools/supervisor/validate_skill_transcript.py <transcript-path>
```

**Stop Conditions**
- git push without human authorization
- Gate 8 or Gate 11 approval without human
- product source edit outside allowed_files
- product-capability-matrix/poc-targets.yaml direct write
- AI output declared authoritative without test evidence
- SVG declared as Netpbm replacement

### FODT
- **Capability**: `dogfood_status.fodt_to_markdown_dotnet`
- **Gap ID**: `GAP-FODT-DOGFOOD-MD-DOTNET-001`
- **Product track**: `commercial_net`
- **Readiness**: `READY_FOR_EXECUTION`

**Supervisor Route**
- Source file: `src/net/fodt/FodtDocument.cs`
- SVG replacement rejected: `False`
- Authority: `routing_authority`

**Skills Handoff**
- Packet type: `full`
- Authority: `governed_execution_authority`
- Note: Full FODT Markdown packet from skills-product-breadth-finalization sprint

**Acceleration Advisory** *(ai_draft — not authoritative)*
- Use for: Skills stream may use packet data as advisory input; normalization required before registry entry.
- Authority: `ai_draft`

**Allowed Files**
- `src/net/fodt/FodtDocument.cs`
- `src/net/fodt/FodtMarkdownExporter.cs`
- `tests/net/fodt/FodtR114ExportToMarkdownTests.cs`
- `examples/net/fodt/`

**Forbidden Files**
- `src/python/`
- `registry/format-registry.yaml`
- `plans/master-plan.md`
- `product-capability-matrix/poc-targets.yaml`

**Expected Tests**: tests/net/fodt/FodtR114ExportToMarkdownTests.cs with 8+ test methods
**Expected Dogfood Output**: Markdown file produced from FODT document using FodtDocument.ExportToMarkdown()
**Expected Transcript**: `reports/{sprint}/skill-transcripts/transcript-fodt-markdown-{id}.json`

**Proposed Capability Delta** *(proposed only — not a direct write)*
- `fodt.dogfood_status.fodt_to_markdown_dotnet` → `IMPLEMENTED`
- Requires test evidence: `True`

**Validation Commands**
```
dotnet test --filter FodtR114
```
```
python tools/supervisor/validate_skill_transcript.py <transcript-path>
```

**Stop Conditions**
- git push without human authorization
- Gate 8 or Gate 11 approval without human
- product source edit outside allowed_files
- product-capability-matrix/poc-targets.yaml direct write
- AI output declared authoritative without test evidence
- SVG declared as Netpbm replacement

### FODT_TXT
- **Capability**: `dogfood_status.fodt_to_txt_dotnet`
- **Gap ID**: `GAP-FODT-DOGFOOD-TXT-DOTNET-001`
- **Product track**: `commercial_net`
- **Readiness**: `READY_FOR_EXECUTION`

**Supervisor Route**
- Source file: `src/net/fodt/FodtDocument.cs`
- SVG replacement rejected: `False`
- Authority: `routing_authority`

**Skills Handoff**
- Packet type: `full`
- Authority: `governed_execution_authority`
- Note: Full FODT TXT packet from skills-product-breadth-finalization sprint (new in refresh)

**Acceleration Advisory** *(ai_draft — not authoritative)*
- Use for: Skills stream may use packet data as advisory input; normalization required before registry entry.
- Authority: `ai_draft`

**Allowed Files**
- `src/net/fodt/FodtDocument.cs`
- `src/net/fodt/FodtTxtExporter.cs`
- `tests/net/fodt/FodtR114ExportToTxtTests.cs`
- `examples/net/fodt/`

**Forbidden Files**
- `src/python/`
- `registry/format-registry.yaml`
- `plans/master-plan.md`
- `product-capability-matrix/poc-targets.yaml`

**Expected Tests**: tests/net/fodt/FodtR114ExportToTxtTests.cs with 8+ test methods
**Expected Dogfood Output**: Plain text file produced from FODT document using FodtDocument.ExportToTxt()
**Expected Transcript**: `reports/{sprint}/skill-transcripts/transcript-fodt-txt-{id}.json`

**Proposed Capability Delta** *(proposed only — not a direct write)*
- `fodt.dogfood_status.fodt_to_txt_dotnet` → `IMPLEMENTED`
- Requires test evidence: `True`

**Validation Commands**
```
dotnet test --filter FodtR114ExportToTxt
```
```
python tools/supervisor/validate_skill_transcript.py <transcript-path>
```

**Stop Conditions**
- git push without human authorization
- Gate 8 or Gate 11 approval without human
- product source edit outside allowed_files
- product-capability-matrix/poc-targets.yaml direct write
- AI output declared authoritative without test evidence
- SVG declared as Netpbm replacement

### Netpbm
- **Capability**: `dotnet_status.netpbm_flip_and_merge_pipeline`
- **Gap ID**: `GAP-NETPBM-DOGFOOD-PIPELINE-DOTNET-001`
- **Product track**: `commercial_net`
- **Readiness**: `READY_FOR_EXECUTION_WITH_VALIDATION`

**Supervisor Route**
- Source file: `src/net/netpbm/Model/NetpbmImage.cs`
- SVG replacement rejected: `True`
- Authority: `routing_authority`

**Skills Handoff**
- Packet type: `full`
- Authority: `governed_execution_authority`
- Note: Full Netpbm packet from skills-product-breadth-finalization sprint (upgraded from shell)

**Acceleration Advisory** *(ai_draft — not authoritative)*
- Use for: Skills stream may use packet data as advisory input; normalization required before registry entry.
- Authority: `ai_draft`

**Allowed Files**
- `src/net/netpbm/Model/NetpbmImage.cs`
- `tests/net/netpbm/NetpbmR114FlipMergePipelineTests.cs`
- `examples/net/netpbm/`

**Forbidden Files**
- `src/python/`
- `registry/format-registry.yaml`
- `plans/master-plan.md`
- `product-capability-matrix/poc-targets.yaml`
- `src/net/svg/`

**Expected Tests**: tests/net/netpbm/NetpbmR114FlipMergePipelineTests.cs with 8+ test methods
**Expected Dogfood Output**: Netpbm image produced using NetpbmImage.Pipeline() method chain (flip + merge steps)
**Expected Transcript**: `reports/{sprint}/skill-transcripts/transcript-netpbm-pipeline-{id}.json`

**Proposed Capability Delta** *(proposed only — not a direct write)*
- `netpbm.dotnet_status.netpbm_image_pipeline_dotnet` → `IMPLEMENTED`
- Requires test evidence: `True`

**Validation Commands**
```
dotnet test --filter NetpbmR114
```
```
python tools/supervisor/validate_skill_transcript.py <transcript-path>
```

**Stop Conditions**
- git push without human authorization
- Gate 8 or Gate 11 approval without human
- product source edit outside allowed_files
- product-capability-matrix/poc-targets.yaml direct write
- AI output declared authoritative without test evidence
- SVG declared as Netpbm replacement

## Global Stop Conditions
- git push without explicit human authorization
- Gate 8 or Gate 11 self-approval
- product-capability-matrix/poc-targets.yaml direct write from this packet
- Acceleration advisory used as authoritative evidence without test validation
- External tool activated without MODE 4+ authorization

## Authority Boundaries
- **supervisor**: routing_authority
- **skills**: governed_execution_authority
- **acceleration**: ai_draft (advisory only)
- **mainstream**: product_implementation_authority (this stream implements)
- **format_factory_gates**: human_authority (never self-approved)
