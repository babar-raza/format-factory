# Tri-Lane Integration Contract
# Sprint: FORMAT-FACTORY-TRI-LANE-INTEGRATION-FABRIC-001
# Generated: 2026-06-04

## Purpose
This contract defines the interface between Supervisor, Skills, and Acceleration streams, and the structured feed into Mainstream product implementation. It is an integration glue document — not a product authority document.

## Contract Blocks

### 1. Supervisor Routing Block
- **Authority**: ROUTING_AUTHORITY — Supervisor controls routing priority
- **Families**: FODS, FODT, Netpbm (all active)
- **SVG rejection**: Enforced — SVG cannot replace Netpbm
- **Source**: reports/supervisor-tri-lane-reconciliation/mainstream-readiness-packet.json

### 2. Skills Handoff Block
- **Authority**: GOVERNED_EXECUTION_AUTHORITY — Skills controls handoff structure
- **FODS**: full packet (handoff-spf-001-add-dotnet-api.yaml)
- **FODT**: shell packet (fodt-packet-shell.json)
- **Netpbm**: shell packet (netpbm-packet-shell.json)
- **Source**: reports/skills-product-first/mainstream-consumption-packet.json

### 3. Acceleration Advisory Block
- **Authority**: AI_DRAFT — advisory only, never authoritative
- **FODS**: fods-dogfood_status-fods_to_csv_dotnet.json
- **FODT**: fodt-dogfood_status-fodt_to_markdown_dotnet.json
- **Netpbm**: netpbm-dotnet_status-netpbm_flip_diagonal.json
- **Source**: reports/acceleration-product-first/mainstream-consumption-packets/

### 4. Mainstream Execution Block
Defines what Mainstream must implement per family:

| Family | Capability | Allowed Files | Expected Tests |
|--------|-----------|---------------|----------------|
| FODS | dogfood_status.fods_to_csv_dotnet | src/net/fods/FodsDocument.cs, tests/net/fods/FodsR114* | 8+ test methods |
| FODT | dogfood_status.fodt_to_markdown_dotnet | src/net/fodt/FodtDocument.cs, tests/net/fodt/ | 8+ test methods |
| Netpbm | dotnet_status.netpbm_proof_dogfood | src/net/netpbm/Model/NetpbmImage.cs, tests/net/netpbm/ | 8+ test methods |

### 5. Evidence Expectations Block
- Minimum passing tests: 24 (8 per family)
- Minimum governed transcripts: 3
- Minimum source diffs: 3
- Required for clean pass: 3 families, 3 source diffs, 3 governed transcripts, 3 raw logs, 3 capability deltas

### 6. Capability Delta Block
- Proposed only — never direct write
- Requires test evidence before any poc-targets.yaml update
- Authority: Mainstream implementation authority after evidence accepted

### 7. Validation Block
- Validator: tools/supervisor/validate_tri_lane_contract.py
- Pass criteria: Supervisor routing present, Skills handoff present, Acceleration advisory present (ai_draft), 3 families present, Netpbm present, SVG rejected
- Rejection conditions: Missing Supervisor routing, Acceleration claimed as authority, direct poc-targets mutation, Netpbm absent, SVG as Netpbm replacement

### 8. Authority Boundary Block
- Supervisor: Stream-control authority (routing, continuation states, cross-stream status)
- Skills: Governed execution authority (handoff templates, transcript validation)
- Acceleration: Advisory only (ai_draft, requires deterministic validation)
- Mainstream: Product implementation authority (source changes, tests, dogfood)
- Format Factory Gates: Human authority (never self-approved)

## Conflict Resolution
1. Supervisor controls routing priority (overrides all on routing)
2. Skills controls governed handoff structure
3. Acceleration advisory does NOT override Skills or Supervisor
4. Mainstream does NOT bypass format-registry.yaml or poc-targets.yaml
5. Capability readiness is NOT upgraded by integration alone

## Schema Reference
See: reports/tri-lane-integration-fabric/tri-lane-contract.schema.json
