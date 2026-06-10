# Stale Input Analysis
# Sprint: FORMAT-FACTORY-TRI-LANE-INTEGRATION-REFRESH-AND-MAINSTREAM-READINESS-GATE-001

## Stale Inputs in Old tri-lane-contract.json

### 1. FODT Skills: Shell Packet — STALE_BLOCKING
- Old path: `reports/skills-governed-execution-hardening/fodt-packet-shell.json`
- Old type: shell
- Current state: Full finalization packets exist at:
  - `reports/skills-product-breadth-finalization/fodt-markdown-packet.json` (FULL, READY)
  - `reports/skills-product-breadth-finalization/fodt-txt-packet.json` (FULL, READY)
- **Classification: STALE_BLOCKING**
- **Resolution: Replace with full finalization packets in contract v2**

### 2. Netpbm Skills: Shell Packet — STALE_BLOCKING
- Old path: `reports/skills-governed-execution-hardening/netpbm-packet-shell.json`
- Old type: shell
- Current state: Full finalization packet exists at:
  - `reports/skills-product-breadth-finalization/netpbm-proof-packet.json` (FULL, READY)
- **Classification: STALE_BLOCKING**
- **Resolution: Replace with full finalization packet in contract v2**

### 3. FODT TXT: Missing Entirely — STALE_BLOCKING
- Old contract had no FODT TXT entry at all
- Current state: Full packet exists at:
  - `reports/skills-product-breadth-finalization/fodt-txt-packet.json` (FULL, READY)
- **Classification: STALE_BLOCKING**
- **Resolution: Add FODT TXT as fourth family in contract v2 and packet v2**

### 4. Acceleration Source: Product-First Directory — STALE_WITH_REPAIR_REQUIRED
- Old source: `reports/acceleration-product-first/mainstream-consumption-packets`
- Current state: Hardening index exists at:
  - `reports/acceleration-hardening/mainstream-packet-index.json`
- Hardening index has schema_version 1.1.0 and all packets validated
- **Classification: STALE_WITH_REPAIR_REQUIRED**
- **Resolution: Update tri_lane_integration.py to prefer hardening index**

### 5. Invalid Pytest Commands for .cs Files — BLOCKING_VALIDATOR_GAP
- Old validation_commands included:
  - `python -m pytest tests/net/fods/FodsR114ExportToCsvTests.cs -v`
  - `python -m pytest tests/net/fodt/ -k R114 -v`
  - `python -m pytest tests/net/netpbm/ -k R114 -v`
- These commands are invalid — .NET tests must use `dotnet test`, not Python pytest
- **Classification: BLOCKING_VALIDATOR_GAP**
- **Resolution: Update generate_mainstream_execution_packet.py to emit only valid dotnet test commands for .NET families**

## Non-Stale / Valid Inputs

### FODS Skills (product-first packet): VALID
- Path: `reports/skills-product-first/mainstream-consumption-packet.json`
- Status: FULL packet, no newer version exists

### Acceleration Hardening Index: VALID (new primary)
- Path: `reports/acceleration-hardening/mainstream-packet-index.json`
- Status: ACCELERATION_CONSUMABLE_WITH_LIMITATIONS, all runtime_status=ok

### Supervisor Routing: VALID (base)
- Path: `reports/supervisor-tri-lane-reconciliation/mainstream-readiness-packet.json`
- Status: Routing decisions valid; only FODT/Netpbm Skills fields stale
