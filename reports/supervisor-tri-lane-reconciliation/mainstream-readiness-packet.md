# Mainstream Readiness Packet — Lane D

## Sprint
`FORMAT-FACTORY-SUPERVISOR-TRI-LANE-RECONCILIATION-001`

## Authority
This packet is **advisory** — `authority_state: advisory, non_authoritative: true`.
Mainstream is the product implementation authority. This packet guides, not commands.

## Three Required Families

### 1. FODS — `READY_FOR_EXECUTION`
- Gap: `dogfood_status.fods_to_csv_dotnet` (GAP-FODS-DOGFOOD-CSV-DOTNET-001)
- Skills handoff: Full packet ready (`mainstream-consumption-packet.json`)
- Skill: `add-dotnet-api`
- Acceleration advisory: `fods-dogfood_status-fods_to_csv_dotnet.json` (ai_draft)
- Source: `src/net/fods/FodsDocument.cs` (M in git)
- Expected: `tests/net/fods/FodsR114ExportToCsvTests.cs` (8+ tests)
- Transcript required: YES — `validate_skill_transcript.py`

### 2. FODT — `READY_FOR_EXECUTION_WITH_DISCOVERY`
- Gap: `dogfood_status.fodt_to_markdown_dotnet`
- Skills handoff: Shell packet — Mainstream must select specific method first
- Acceleration advisory: `fodt-dogfood_status-fodt_to_markdown_dotnet.json` (ai_draft)
- Source: `src/net/fodt/FodtDocument.cs` (M in git)
- Expected: `tests/net/fodt/FodtR114ExportToMarkdownTests.cs` (8+ tests)

### 3. Netpbm — `READY_FOR_EXECUTION_WITH_DISCOVERY`
- Gap: `dotnet_status.netpbm_proof_dogfood`
- Skills handoff: Shell packet — Mainstream must select specific capability
- Acceleration advisory: `netpbm-dotnet_status-netpbm_flip_diagonal.json` (ai_draft)
- Source: `src/net/netpbm/Model/NetpbmImage.cs` (M in git)
- **Netpbm RETAINED** — SVG replacement REJECTED (vector ≠ raster)
- Expected: `tests/net/netpbm/NetpbmR114[Feature]Tests.cs` (8+ tests)

## Optional Capabilities

| Family | Status | Notes |
|--------|--------|-------|
| SYLK | ACCELERATION_ONLY_ADVISORY | ai_draft only, no Skills packet |
| ZST | NO_TRI_LANE_PACKET | Deprioritized |
| DIF | NO_TRI_LANE_PACKET | Deprioritized |

## Product Output Floor (for CLEAN_PASS)
- families_touched: ≥ 3 ✓ (4 active)
- source_diffs: ≥ 3 ✓ (4 files)
- governed_transcripts: ≥ 3 ← **MISSING 1** (current: 2)
- raw_logs: ≥ 3 ✓
- capability_matrix_deltas: ≥ 3 ← **MISSING 1** (current: 2)

## Cross-Stream Consumption Requirements

| Flag | Trigger | Current Status |
|------|---------|---------------|
| `governed_execution_consumed` | Skills handoff executed + transcript validates | SKILLS_CONSUMABLE_NOT_YET_CONSUMED |
| `reusable_accelerator_consumed` | Acceleration design used + tests pass | ACCELERATION_CONSUMABLE_PARTIAL |

## Authority Hierarchy

```
Supervisor → stream-control authority (routing, continuation, cross-stream)
    ↓
Skills → governed execution authority (handoffs, transcript validation)
    ↓
Acceleration → advisory only (ai_draft, non-authoritative)
    ↓
Mainstream → product implementation authority (source, tests, dogfood, deltas)
```

## Stop Conditions
- git push without human authorization
- Gate 8 or Gate 11 without human
- Direct write to `product-capability-matrix/poc-targets.yaml`
- AI output declared authoritative without deterministic validation
- Edit to `src/net/**` or `src/python/**` outside allowed_files

## Evidence Expectations Per Family
Each executed capability must produce:
1. 8+ passing tests with raw log
2. Governed transcript (validated by `validate_skill_transcript.py`)
3. Proposed capability delta (not direct write to poc-targets.yaml)
4. Source diff in allowed_files only

## Limitations
1. FODT and Netpbm Skills packets need Mainstream discovery step
2. Acceleration hardening not independently verified
3. Mainstream has not yet consumed Skills or Acceleration packets
