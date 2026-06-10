# Latest Input Selection
# Sprint: FORMAT-FACTORY-TRI-LANE-INTEGRATION-REFRESH-AND-MAINSTREAM-READINESS-GATE-001

## Skills Selections

### FODS — mainstream-consumption-packet.json
- Path: `reports/skills-product-first/mainstream-consumption-packet.json`
- Sprint: `FORMAT-FACTORY-SKILLS-PRODUCT-FIRST-GOVERNED-EXECUTION-001`
- Freshness: `LATEST_FOR_FODS`
- Reason: No newer FODS finalization packet; product-first packet is authoritative
- Fallback used: `False`

### FODT — fodt-markdown-packet.json
- Path: `reports/skills-product-breadth-finalization/fodt-markdown-packet.json`
- Sprint: `FORMAT-FACTORY-SKILLS-PRODUCT-BREADTH-HANDOFF-FINALIZATION-001`
- Freshness: `LATEST_FINALIZATION`
- Reason: Full finalization packet supersedes shell packet from skills-governed-execution-hardening
- Fallback used: `False`

### FODT — fodt-txt-packet.json
- Path: `reports/skills-product-breadth-finalization/fodt-txt-packet.json`
- Sprint: `FORMAT-FACTORY-SKILLS-PRODUCT-BREADTH-HANDOFF-FINALIZATION-001`
- Freshness: `LATEST_FINALIZATION`
- Reason: New in finalization sprint — FODT TXT capability previously missing from integration
- Fallback used: `False`

### Netpbm — netpbm-proof-packet.json
- Path: `reports/skills-product-breadth-finalization/netpbm-proof-packet.json`
- Sprint: `FORMAT-FACTORY-SKILLS-PRODUCT-BREADTH-HANDOFF-FINALIZATION-001`
- Freshness: `LATEST_FINALIZATION`
- Reason: Full finalization packet supersedes shell packet from skills-governed-execution-hardening
- Fallback used: `False`

## Acceleration Selection
- Path: `reports/acceleration-hardening/mainstream-packet-index.json`
- Freshness: `LATEST_HARDENING`
- Fallback used: `False`

## Stale Inputs Rejected
- `reports/skills-governed-execution-hardening/fodt-packet-shell.json` — STALE_BLOCKING: Shell packet superseded by full finalization packet
- `reports/skills-governed-execution-hardening/netpbm-packet-shell.json` — STALE_BLOCKING: Shell packet superseded by full finalization packet
- `reports/acceleration-product-first/mainstream-consumption-packets` — STALE_WITH_REPAIR_REQUIRED: Product-first dir superseded by hardening index (when index available)
