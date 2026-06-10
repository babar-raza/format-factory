# Tri-Lane Contract v2.0
# Sprint: FORMAT-FACTORY-TRI-LANE-INTEGRATION-REFRESH-AND-MAINSTREAM-READINESS-GATE-001
# Supersedes: reports/tri-lane-integration-fabric/tri-lane-contract.json (v1.0)

> **Authority**: Advisory only. Mainstream product authority governs actual implementation.
> Acceleration advisory is `ai_draft` and must NOT be used as evidence.
> No gate approvals from this contract.

## Changes from v1.0
1. FODT Skills: upgraded from shell → full finalization packet
2. FODT TXT: new family added (was missing from v1)
3. Netpbm Skills: upgraded from shell → full finalization packet
4. Acceleration: upgraded from product-first dir → hardening index
5. Validation commands: removed invalid `python -m pytest *.cs` commands
6. Validator: now rejects shell packets when finalization exists
7. Validator: now rejects `python -m pytest` commands for .NET test paths

## Contract Validation
- Verdict: **TRI_LANE_CONTRACT_VALID**
- Checks passed: 32/32
- Errors: 0
- Limitations: 0

## Supervisor Routing (routing_authority)
Source: `reports/supervisor-tri-lane-reconciliation/mainstream-readiness-packet.json`
Routing decision: CONTINUE_TO_MAINSTREAM

| Family | Active | SVG Rejected | Source File |
|--------|--------|-------------|-------------|
| FODS | YES | N/A | src/net/fods/FodsDocument.cs |
| FODT | YES | N/A | src/net/fodt/FodtDocument.cs |
| FODT TXT | YES (new) | N/A | src/net/fodt/FodtDocument.cs |
| Netpbm | YES | YES | src/net/netpbm/Model/NetpbmImage.cs |

## Skills Handoff (governed_execution_authority)
Source: `reports/skills-product-breadth-finalization/handoff-to-mainstream.json`

| Family | Packet Type | Packet Path | Status |
|--------|------------|-------------|--------|
| FODS | FULL | reports/skills-product-first/mainstream-consumption-packet.json | READY |
| FODT Markdown | FULL | reports/skills-product-breadth-finalization/fodt-markdown-packet.json | READY |
| FODT TXT | FULL | reports/skills-product-breadth-finalization/fodt-txt-packet.json | READY |
| Netpbm | FULL | reports/skills-product-breadth-finalization/netpbm-proof-packet.json | READY |

## Acceleration Advisory (ai_draft — NOT authoritative)
Source: `reports/acceleration-hardening/mainstream-packet-index.json`

| Family | Status | Note |
|--------|--------|------|
| FODS | ok | Use for implementation pattern reference only |
| FODT Markdown | ok | Use for method selection guidance only |
| FODT TXT | n/a | Not in hardening index — optional missing allowed |
| Netpbm | ok | Capability mismatch (flip_diagonal vs Pipeline) — follow Skills handoff |

## Mainstream Execution Families (4)

### FODS — dogfood_status.fods_to_csv_dotnet
- Test: `dotnet test --filter FodsR114`
- Expected output: CSV from FodsDocument.ExportToCsv()

### FODT Markdown — dogfood_status.fodt_to_markdown_dotnet
- Test: `dotnet test --filter FodtR114`
- Expected output: Markdown from FodtDocument.ExportToMarkdown()

### FODT TXT — dogfood_status.fodt_to_txt_dotnet (NEW in v2)
- Test: `dotnet test --filter FodtR114ExportToTxt`
- Expected output: Plain text from FodtDocument.ExportToTxt()

### Netpbm — dotnet_status.netpbm_flip_and_merge_pipeline
- Test: `dotnet test --filter NetpbmR114`
- Expected output: NetpbmImage.Pipeline() chained transforms
- SVG replacement: REJECTED

## Authority Boundary
- **Supervisor**: routing_authority
- **Skills**: governed_execution_authority
- **Acceleration**: ai_draft (advisory only)
- **Mainstream**: product_implementation_authority (this stream implements)
- **Format Factory Gates**: human_authority (Gate 8 + Gate 11 never self-approved)
