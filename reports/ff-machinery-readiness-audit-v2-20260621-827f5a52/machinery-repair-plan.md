# Machinery Repair Plan — Format Factory Machinery Audit v2
# Sprint ID: ff-machinery-readiness-audit-v2-20260621-827f5a52

## Repair Priority Order

All machinery repairs run in SEPARATE sprints from product deepening.

### P0 (Must Fix Before Next Product Sprint Starts)

None — all P0 issues are product-lane (test fix, commit).

### P1 (Next Machinery Sprint — Recommended Before Gate 11 Packet)

**Repair 1: TC-CAPABILITY-COMPILER-001**
Fix capability_compiler.py SAL path. 1-line change.
File: tools/supervisor/capability_compiler.py line ~20
Change: `SAL_OUTPUT_PATH = _REPO_ROOT / ".local" / "sal-output" / "sal-facts-latest.json"`
To: `SAL_OUTPUT_PATH = _REPO_ROOT / ".local" / "spec-cache" / "sal-facts-{format}.json"` (dynamic)
Test: python capability_compiler.py --format fods --gap-record '...' loads FODS facts

**Repair 2: TC-SKILL-QNAME-001**
Add 3 lines to each product skill prompt requiring spec_qname on new classes.
No code change — prompt text update only.
Files: .claude/commands/add-python-api.md, add-dotnet-api.md, add-python-object-model-feature.md

**Repair 3: TC-SAL-VERIFY-001**
Add `fact_type` field to SAL output distinguishing verified_independent vs auto_seeded.
File: tools/specification-authority-layer/sal_master_runner.py
Change: When loading workbench facts, check if fact was in original 78 seed set.
Test: SAL output shows fact_type distribution.

### P2 (Second Machinery Sprint)

**Repair 4: TC-BACKFILL-001**
Create tools/backfill/backfill_inventory.py for FODS Python.
Input: src/python/fods/ source
Output: YAML inventory of classes with suggested spec_qname mappings

**Repair 5: TC-SUPERVISOR-LANES-001**
Create separate continuation signals per lane.
Files: .local/supervisor/product-signal.json, machinery-signal.json
Change: check_continuation.py reads track-specific signal

### P3 (Deferred)

- QName structure for non-ODF formats (needs spec sources first)
- Overclaim detector wiring (SUP-GAP-003 from spec-to-feature plan)
- Dynamic SAL query at sprint time (vs. static gap ledger)
- Automated gate criteria check per sprint

## What NOT to Repair Now

1. Do NOT attempt XCF or ZST spec/ stubs — no published qname spec exists for XCF
2. Do NOT rebuild the SAL pipeline from scratch — incremental fixes are safer
3. Do NOT implement full lane separation with file locking — sequential operation is safe

## Estimated Machinery Sprint Scope

Sprint A (P1 repairs): ~3 hours of work (compiler fix, skill prompts, SAL fact type)
Sprint B (P2 repairs): ~6 hours of work (backfill inventory tool, lane signals)
Sprint C (P3 deferred): open-ended

## Machinery vs. Product Lane Rule

Machinery sprint: MUST NOT touch src/python/ or src/net/ production code
Product sprint: MUST NOT touch tools/supervisor/ or tools/specification-authority-layer/
Both can touch: registry/, tests/ (different subdirs), docs/, reports/

This rule is NOT mechanically enforced today. Agent must self-enforce.
