# Pilot Fix Plan
# Format Factory — Expert Manual System Review
# Phase 8 output — Generated: 2026-06-25

## Purpose

Define the pilot fix to test the system-first healing methodology.
The pilot selects ONE system gap and ONE product gap.
System gap is fixed first. Then product gap is fixed through the healed system.

## Pilot Selection Rationale

### System Pilot: Gap Ledger Taxonomy Repair (PROB-009)

**Why this first:**
- The gap ledger is the routing engine for ALL product fixes
- 1,131 of 1,132 gaps with "unknown" category means the system cannot prioritize or route any gap
- Fixing this unblocks all future governed product repairs
- Low risk (output files only — no source changes)
- Verifiable: before and after gap counts by category

**Expected outcome:**
- Gaps get meaningful categories (extraction_missing, api_surface_incomplete, spec_parity_gap, etc.)
- category-based routing and filtering becomes possible
- Future sprints can target specific gap categories

**System pilot steps:**
1. Read `tools/supervisor/gap_ledger_to_work_items.py` — find where category is set
2. Read `tools/capability_layer/capability_map_generator.py` — find where categories come from
3. Implement category inference logic (from gap_id prefix, from capability_ref type, from format type)
4. Re-run gap ledger generation
5. Verify: category distribution is no longer 99.9% unknown

### Product Pilot: ZST .NET Decompression (PROB-001)

**Why this second (after system healing):**
- PROB-001 is CRITICAL (compression library with no decompression)
- Gap ledger (after PROB-009 fix) should track this with category "extraction_missing"
- Fix requires adding ZstDecompressor to src/net/zst/ — governed sprint
- Verifiable: test.zst → decompress → content matches original

**Product pilot steps:**
1. Verify gap ledger has entry for ZST decompression with real category
2. Execute governed sprint: add ZstDecompressor.cs to src/net/zst/
3. Add test: load sample ZST → decompress → verify content
4. Verify gap ledger marks the entry as test_verified or closed

## Pilot Success Criteria

### System pilot success:
- `reports/capability-layer/gap-ledger.json` no longer has 99.9% unknown categories
- At least 10 distinct categories appear
- Gap routing logic in gap_ledger_to_work_items.py works on categorized gaps

### Product pilot success:
- `src/net/zst/ZstDecompressor.cs` (or equivalent) exists with decompression logic
- Test in `tests/net/zst/` verifies actual content extraction
- ZstDocument exposes decompressed content or stream
- poc-targets.yaml updated: decompression = PASS (with test evidence)

## Pilot Failure Modes

| Failure | Root Cause | Response |
|---------|-----------|---------|
| Category inference too slow | Too many gaps to process | Batch inference; run overnight |
| ZST decompression blocked by dependency | No .NET ZST library | Use DotNetZip; evaluate ZstdNet NuGet |
| Test fails | ZstDecompressor wrong | Debug test; fix implementation |
| Gap ledger doesn't update | Closure engine not triggered | Manually invoke gap closure |

## Pilot Timeline

The pilot is the first governed repair sprint after the expert review phase completes.
It runs in a single sprint: ~2 hours for system pilot, ~2 hours for product pilot.
Evidence declaration produced after both pilots complete.

## Post-Pilot Assessment

After pilot:
1. Review gap ledger — are categories meaningful?
2. Review ZST .NET — does decompression work?
3. Update confirmed-problems.json — close PROB-001 and PROB-009 if resolved
4. Document pilot findings in `pilot-results.md`
5. Determine if methodology is ready for unified fix execution (Phase F)
