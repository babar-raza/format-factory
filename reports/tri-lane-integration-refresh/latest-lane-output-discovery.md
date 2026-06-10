# Latest Lane Output Discovery
# Sprint: FORMAT-FACTORY-TRI-LANE-INTEGRATION-REFRESH-AND-MAINSTREAM-READINESS-GATE-001

## Acceleration Hardening (LATEST)
- Sprint: FORMAT-FACTORY-ACCELERATION-HARDENING-IV-AND-CONSUMPTION-CONTRACT-001
- Hardening index: `reports/acceleration-hardening/mainstream-packet-index.json` — EXISTS
- All 4 packets (FODS, FODT, Netpbm, SYLK): runtime_status=ok
- Cross-lane readiness: ACCELERATION_CONSUMABLE_WITH_LIMITATIONS
- Determinism: proven (2 replay runs match)
- **Assessment: LATEST — hardening index must be used instead of product-first directory**

## Skills Product Breadth Finalization (LATEST for FODT/Netpbm)
- Sprint: FORMAT-FACTORY-SKILLS-PRODUCT-BREADTH-HANDOFF-FINALIZATION-001
- FODT Markdown: `reports/skills-product-breadth-finalization/fodt-markdown-packet.json` — FULL packet, READY_FOR_MAINSTREAM
- FODT TXT: `reports/skills-product-breadth-finalization/fodt-txt-packet.json` — FULL packet, READY_FOR_MAINSTREAM
- Netpbm: `reports/skills-product-breadth-finalization/netpbm-proof-packet.json` — FULL packet, READY_FOR_MAINSTREAM
- **Assessment: LATEST — these full packets supersede the old shell packets**

## Skills Product First (LATEST for FODS)
- Sprint: FORMAT-FACTORY-SKILLS-PRODUCT-FIRST-GOVERNED-EXECUTION-001
- FODS: `reports/skills-product-first/mainstream-consumption-packet.json` — FULL packet
- No newer FODS finalization packet exists
- **Assessment: LATEST_FOR_FODS**

## Supervisor Tri-Lane Reconciliation (BASE VALID, FODT/NETPBM STALE)
- Sprint: FORMAT-FACTORY-SUPERVISOR-TRI-LANE-RECONCILIATION-001
- Routing packet: `reports/supervisor-tri-lane-reconciliation/mainstream-readiness-packet.json` — EXISTS
- **Stale fields**: FODT and Netpbm Skills entries reference old SHELL packets
- **Assessment: STALE_FODT_NETPBM — base routing valid, Skills fields must be patched**

## Old Integration Fabric (SUPERSEDED)
- Sprint: FORMAT-FACTORY-TRI-LANE-INTEGRATION-FABRIC-001
- All outputs superseded by this refresh sprint
- **Assessment: SUPERSEDED**
