# Non-Blocking Evidence Caveats
# Sprint: FORMAT-FACTORY-TRI-LANE-INTEGRATION-REFRESH-AND-MAINSTREAM-READINESS-GATE-001

## Caveats That Do NOT Block Mainstream

### CAVEAT-001: Acceleration FODT TXT Advisory Missing
- Acceleration hardening index covers FODS, FODT Markdown, Netpbm, SYLK
- FODT TXT has no dedicated acceleration advisory packet
- **Impact**: FODT TXT Mainstream execution proceeds with Skills-only guidance (no acceleration advisory)
- **Resolution in packet v2**: FODT TXT acceleration field marked as "optional_missing_allowed"
- **Downstream action**: None required — Skills packet is sufficient for FODT TXT

### CAVEAT-002: Netpbm Acceleration Advisory Uses Older Capability
- Acceleration hardening covers `dotnet_status.netpbm_flip_diagonal`
- Skills finalization targets `dotnet_status.netpbm_flip_and_merge_pipeline` (composite Pipeline method)
- **Impact**: Acceleration advisory for Netpbm references a different (already implemented) capability
- **Resolution in packet v2**: Netpbm marked READY_FOR_EXECUTION_WITH_VALIDATION; Acceleration advisory marked as "advisory_capability_mismatch — use for implementation pattern reference only"
- **Downstream action**: Mainstream follows Skills handoff for Netpbm (Pipeline method)

### CAVEAT-003: Supervisor Reconciliation FODT/Netpbm Skills Fields Stale
- Supervisor tri-lane reconciliation packet predates Skills finalization
- FODT and Netpbm entries in reconciliation reference shell packets
- **Resolution**: This sprint patches the integration resolver to ignore reconciliation Skills fields for FODT/Netpbm and use finalization packets directly
- **Downstream action**: None — contract v2 reflects fresh data

### CAVEAT-004: Pre-existing Product Source WIP Files
- 4 files modified before this sprint (PRE_EXISTING_PRODUCT_WIP)
- Classification applied; Mainstream must re-confirm before editing
- **Not a blocker** unless Mainstream discovers unexpected content

## These Caveats Are NOT Sprint Goals
Per sprint instructions: evidence caveats are not made sprint goals.
All caveats above are classified and documented; none require additional sprint work.
