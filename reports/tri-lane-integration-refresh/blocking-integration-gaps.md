# Blocking Integration Gaps
# Sprint: FORMAT-FACTORY-TRI-LANE-INTEGRATION-REFRESH-AND-MAINSTREAM-READINESS-GATE-001

## BLOCKING Gaps (must be resolved before Mainstream can run)

### GAP-REFRESH-001: FODT Shell Packet in Old Integration
- **Type**: STALE_BLOCKING
- **Detail**: Old tri-lane-contract.json references shell packet for FODT
- **Fix**: Lane B updates tri_lane_integration.py resolver; Lane C creates contract v2 with full packet
- **Status**: FIXED_IN_THIS_SPRINT

### GAP-REFRESH-002: Netpbm Shell Packet in Old Integration
- **Type**: STALE_BLOCKING
- **Detail**: Old tri-lane-contract.json references shell packet for Netpbm
- **Fix**: Lane B updates tri_lane_integration.py resolver; Lane C creates contract v2 with full packet
- **Status**: FIXED_IN_THIS_SPRINT

### GAP-REFRESH-003: FODT TXT Missing from Old Integration
- **Type**: STALE_BLOCKING
- **Detail**: Old contract had no FODT TXT entry; finalization packet exists
- **Fix**: Lane C adds FODT TXT as fourth family; Lane D adds to packet v2
- **Status**: FIXED_IN_THIS_SPRINT

### GAP-REFRESH-004: Acceleration Source Stale in tri_lane_integration.py
- **Type**: STALE_WITH_REPAIR_REQUIRED
- **Detail**: Tool loads from product-first dir; hardening index not consulted
- **Fix**: Lane B adds hardening index resolver with fallback
- **Status**: FIXED_IN_THIS_SPRINT

### GAP-REFRESH-005: Invalid Pytest Commands for .NET Tests
- **Type**: BLOCKING_VALIDATOR_GAP
- **Detail**: generate_mainstream_execution_packet.py emits `python -m pytest *.cs` commands
- **Fix**: Lane D updates validation_commands to use only `dotnet test --filter ...`
- **Status**: FIXED_IN_THIS_SPRINT

## Non-Blocking Gaps (do not block Mainstream)

### GAP-REFRESH-NB-001: FODT TXT No Acceleration Advisory Packet
- **Type**: NON_BLOCKING
- **Detail**: Acceleration hardening does not include a FODT TXT packet (only FODT Markdown)
- **Fix**: Packet v2 marks Acceleration advisory for FODT TXT as "optional/missing allowed"
- **Status**: DOCUMENTED_IN_PACKET_V2

### GAP-REFRESH-NB-002: Pre-existing Product Source WIP
- **Type**: NON_BLOCKING_UNLESS_UNCLASSIFIED
- **Detail**: 4 product source files have pre-existing modifications
- **Fix**: Classified as PRE_EXISTING_PRODUCT_WIP in dirty-state-classification.json
- **Status**: CLASSIFIED_NOT_BLOCKING
