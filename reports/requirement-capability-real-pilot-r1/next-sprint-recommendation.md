# Next Sprint Recommendation
# Sprint: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-REAL-PILOT-R1-001

## Current State After Real Pilot R1

The RCA layer is verified working against real product evidence. Key confirmed capabilities:
- Proof graph builds deterministically from real pilot data (81 nodes, 102 edges)
- Coverage evaluator correctly handles all 10 proof levels
- Overclaim detector + remediation prevents false PASS
- Staleness invalidation propagates through proof graph
- Gap queue generated from proof state (not ad hoc)
- Supervisor verdict packet produced with 16 fields
- 6/6 golden replay fixtures pass deterministically

## Remaining Gaps Blocking POC Progress

### Priority 1: FODS CSV/HTML Export
- **Gap:** `claim:fods:export_csv` and `claim:fods:export_html` remain BLOCKED
- **Root cause:** No standalone FormatFactory.Csv / FormatFactory.Html target writer libraries
- **Required action:** Mainstream sprint to implement FODS → CSV/HTML serializer as .NET library
- **Gap queue entry:** `mainstream-gap-queue.json` → gap_id: `GAP-FODS-CSV-001`, `GAP-FODS-HTML-001`
- **Expected lane:** COMMERCIAL_NET

### Priority 2: FODT Markdown/TXT Export
- **Gap:** `claim:fodt:export_markdown` and `claim:fodt:export_txt` remain BLOCKED
- **Root cause:** Same architecture issue — inline serializers only, no standalone writer libraries
- **Required action:** Mainstream sprint for FODT → Markdown/TXT serializer libraries
- **Gap queue entry:** `mainstream-gap-queue.json` → gap_id: `GAP-FODT-MARKDOWN-001`, `GAP-FODT-TXT-001`
- **Expected lane:** COMMERCIAL_NET

### Priority 3: SYLK Pilot
- **Gap:** SYLK was not included in R1 (no Spec Authority R2 coverage pack)
- **Required action:** Spec Authority R3 should cover SYLK; then SYLK pilot can run
- **Expected lane:** FOSS_REDUCED

### Priority 4: ZST Stale Claim Recomputation
- **Gap:** `claim:zst:old-compress` is stale (synthetic)
- **Required action:** Mainstream sprint to verify compress claim is still valid after source change
- **Gap queue entry:** `mainstream-gap-queue.json` → gap_id: `GAP-ZST-RECOMPUTE-001`

## Recommended Next Sprint

**Sprint ID:** `FORMAT-FACTORY-MAINSTREAM-FODS-CSV-HTML-EXPORT-IMPLEMENTATION-001`

Focus: Implement FODS CSV and HTML export as proper standalone writer targets (not inline serializers).
This unblocks `claim:fods:export_csv` and `claim:fods:export_html` in the proof graph, which unlocks
FODS to READY status in POC readiness.

Alternatively:
**Sprint ID:** `FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-REAL-PILOT-R2-001`

Focus: Extend R1 pilot to cover SYLK (now that SYLK test suite exists) and DIF roundtrip (after
spec authority coverage). Run full pilot with real SYLK examples.
