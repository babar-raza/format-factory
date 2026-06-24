# Product Deepening Execution Plan
**Plan:** sorted-purring-stardust | **Taskcard:** TC-SOL-001-02 | **Requirement:** REQ-SOL-001

## Pilot Format: FODS (Python)

### Preconditions (ALL must be met before pilot starts)
1. TC-MACH-CAP-001 CLOSED — capability_compiler writes selected-product-gaps.json
2. TC-MACH-CAP-002 CLOSED — task generator uses scored gap selections
3. V50 in ramp mode (REWORK_REQUIRED, not BLOCK)
4. 0 test failures in tests/python/fods/
5. SAL facts for FODS < 7 days old (4,991 facts, 99.8% verified)
6. All 4 FODS open gaps visible in selected-product-gaps.json

### FODS Sprint Template
Each FODS deepening sprint should:
1. **Select gap:** Use selected-product-gaps.json (not advisory template)
2. **Read SAL:** Identify FACT-FODS-* referenced by the gap
3. **Generate code:** Use add-python-api or add-python-object-model-feature skill
4. **Verify:** spec_fact_refs present in evidence declaration
5. **Test:** Behavioral tests (not just spec_qname assertions)
6. **Close gap:** Update gap-ledger entry to status=closed

### Pass/Fail Criteria
| Criterion | PASS | FAIL |
|-----------|------|------|
| Gap referenced in evidence | gap_ledger_ref present | No gap reference |
| SAL fact used | spec_fact_refs has FACT-FODS-* | No fact reference |
| Code has spec_qname | Production class with spec_qname attribute | Missing spec_qname |
| Tests behavioral | @property accessors tested, roundtrip verified | Only spec_qname assertion |
| V50 satisfied | >= 1 spec_fact_ref in evidence | V50 REWORK_REQUIRED |

### Evidence Expectations
- evidence-declaration.yaml with: spec_fact_refs, gap_ledger_ref, changed_files, test_results
- Changed files in src/python/fods/ (models.py, parser.py, or writer.py)
- New or modified tests in tests/python/fods/
- V50 validation: PASS

### Expansion Rules (After FODS Pilot Succeeds)
1. **NDJSON** — 19 open gaps, GREEN rating, but address over-export first (V51)
2. **FODT .NET** — 9 open gaps, G11-G approved
3. **XCF** — 5 open gaps, read-only (no write capability)
4. **ZST** — 6 open gaps, analytics at LOC cap
5. **ABW** — 39 open gaps, lowest maturity (needs SAL facts first)

### Secondary Pilot: NDJSON
- Precondition: V51 public API governance active (addresses 88% analytics export)
- Focus: Close core API gaps first (load/write/filter), defer analytics gaps
- Target: 5 of 19 gaps closed per sprint
