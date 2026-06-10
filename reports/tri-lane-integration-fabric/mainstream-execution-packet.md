# Mainstream Execution Packet
# Sprint: FORMAT-FACTORY-TRI-LANE-INTEGRATION-FABRIC-001
# Generated: 2026-06-04T14:00:00Z

> **Authority**: Advisory only. Mainstream product authority governs actual implementation.
> Acceleration advisory is `ai_draft` and must NOT be used as evidence.
> No gate approvals from this packet.

## Integration Status: `OK`
**Families**: 3

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
- Note: 

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
python -m pytest tests/net/fods/FodsR114ExportToCsvTests.cs -v
```
```
python tools/supervisor/validate_skill_transcript.py <transcript-path>
```
```
dotnet test --filter FodsR114
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
- **Gap ID**: `GAP-FODT-DOGFOOD-MARKDOWN-DOTNET-001`
- **Product track**: `commercial_net`
- **Readiness**: `READY_FOR_EXECUTION_WITH_DISCOVERY`

**Supervisor Route**
- Source file: `src/net/fodt/FodtDocument.cs`
- SVG replacement rejected: `False`
- Authority: `routing_authority`

**Skills Handoff**
- Packet type: `shell`
- Authority: `governed_execution_authority`
- Note: Mainstream must select specific method; Skills generates full handoff from shell

**Acceleration Advisory** *(ai_draft — not authoritative)*
- Use for: Skills stream may use packet data as advisory input; normalization required before registry entry.
- Authority: `ai_draft`

**Allowed Files**
- `src/net/fodt/FodtDocument.cs`
- `tests/net/fodt/FodtR114ExportToMarkdownTests.cs`
- `tests/net/fodt/`
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
python -m pytest tests/net/fodt/ -k R114 -v
```
```
python tools/supervisor/validate_skill_transcript.py <transcript-path>
```
```
dotnet test --filter FodtR114
```

**Stop Conditions**
- git push without human authorization
- Gate 8 or Gate 11 approval without human
- product source edit outside allowed_files
- product-capability-matrix/poc-targets.yaml direct write
- AI output declared authoritative without test evidence
- SVG declared as Netpbm replacement

### Netpbm
- **Capability**: `dotnet_status.netpbm_proof_dogfood`
- **Gap ID**: `GAP-NETPBM-DOTNET-PROOF-001`
- **Product track**: `commercial_net`
- **Readiness**: `READY_FOR_EXECUTION_WITH_DISCOVERY`

**Supervisor Route**
- Source file: `src/net/netpbm/Model/NetpbmImage.cs`
- SVG replacement rejected: `True`
- Authority: `routing_authority`

**Skills Handoff**
- Packet type: `shell`
- Authority: `governed_execution_authority`
- Note: Mainstream selects specific Netpbm capability; Skills generates handoff from shell

**Acceleration Advisory** *(ai_draft — not authoritative)*
- Use for: Skills stream may use packet data as advisory input; normalization required before registry entry.
- Authority: `ai_draft`

**Allowed Files**
- `src/net/netpbm/Model/NetpbmImage.cs`
- `tests/net/netpbm/NetpbmR114[Feature]Tests.cs`
- `tests/net/netpbm/`
- `examples/net/netpbm/`

**Forbidden Files**
- `src/python/`
- `registry/format-registry.yaml`
- `plans/master-plan.md`
- `product-capability-matrix/poc-targets.yaml`
- `src/net/svg/`

**Expected Tests**: tests/net/netpbm/NetpbmR114[Feature]Tests.cs with 8+ test methods
**Expected Dogfood Output**: Dogfood output produced from Netpbm image using NetpbmImage operations (flip, rotate, crop, overlay)
**Expected Transcript**: `reports/{sprint}/skill-transcripts/transcript-netpbm-{id}.json`

**Proposed Capability Delta** *(proposed only — not a direct write)*
- `netpbm.dotnet_status.{capability}` → `IMPLEMENTED`
- Requires test evidence: `True`

**Validation Commands**
```
python -m pytest tests/net/netpbm/ -k R114 -v
```
```
python tools/supervisor/validate_skill_transcript.py <transcript-path>
```
```
dotnet test --filter NetpbmR114
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
