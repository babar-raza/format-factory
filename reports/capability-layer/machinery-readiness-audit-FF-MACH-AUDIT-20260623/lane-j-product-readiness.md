# Lane J — Product Deepening Readiness
**Plan:** sorted-purring-stardust | **Taskcard:** TC-LANE-J | **Requirement:** REQ-LANE-J

## 1. Gate 11 Criteria Assessment

### Gate 11 Structure (registry/gate11-criteria.yaml)
- **7 mandatory criteria**, zero tolerance
- **Python:** P1-P11
- **C#/.NET:** C1-C20
- **Approver:** Babar Raza (sole authority for G11-G execution)

### Per-Format Gate 11 Status

| Format | G11-G Approved | commercial_ready | Gate Activity |
|--------|---------------|-----------------|---------------|
| FODS | YES (2026-06-05) | false | Active — Python + .NET |
| FODT | YES (2026-06-05) | false | Active — .NET only |
| All others | NO | false | None |

Only 2 of 20 formats have any Gate 11 activity.

### FODS Python — P1-P11 Assessment

| Criterion | Status | Evidence |
|-----------|--------|----------|
| P1: Parser exists | MET | parse_fods() with defusedxml XXE protection |
| P2: Writer exists | MET | write_fods() serializes neutral model to XML |
| P3: Domain model | MET | FodsCell, FodsSheet, FodsDocument with @property accessors |
| P4: spec_qname on all classes | MET | All 3 production classes have spec_qname |
| P5: Load→modify→save workflow | MET | Real behavioral workflow verified |
| P6: Behavioral tests | MET | 761+ pgm tests pass (FODS tests included) |
| P7: SAL fact coverage | PARTIAL | 4,991 FODS facts in SAL, 99.8% verified |
| P8: Package installable | MET | FODS wheel built and install-verified |
| P9: No architecture_only stubs in public API | MET | Compat/ facades are not in public API |
| P10: QName registry entries | MET | 12 entries (11 implemented, 1 implementing) |
| P11: Gap-ledger coverage | PARTIAL | 4 open FODS gaps remaining |

**FODS Python verdict:** 9/11 MET, 2 PARTIAL — CONDITIONALLY READY

### FODS .NET — C1-C20 Assessment
- FodsDocument.cs: 1293 LOC, DOM-backed (XDocument), DtdProcessing.Prohibit
- ODF spec citations present throughout
- 20+ test files covering roundtrip/edit/export
- commercial_ready: false (Gate 11 G11-G approved but not executed)

## 2. Pilot Format Selection

### Primary Pilot: FODS (Python)
**Rationale:**
- Most mature Python format (GREEN rating in Lane C)
- All 3 production classes have spec_qname
- Real parser/writer with behavioral tests
- 12 QName registry entries (11 implemented)
- SAL coverage: 4,991 verified facts

### Secondary Pilot: NDJSON
**Rationale:**
- GREEN rating in Lane C
- load_ndjson() + write_ndjson() are real codecs
- 2 QName registry entries (both implementing)
- Over-export issue (88% analytics) needs V50 governance first

## 3. GO/NO-GO Gates for Product Deepening

### GO Conditions (ALL required)
1. capability_compiler wired → selected-product-gaps.json non-empty (TC-MACH-CAP-001)
2. autonomous_task_generator reads selected gaps (TC-MACH-CAP-002)
3. V50 in ramp mode (REWORK_REQUIRED, not BLOCK) (TC-MACH-VAL-001)
4. 0 test failures in target format test suite
5. SAL facts < 7 days old for target format

### NO-GO Conditions (ANY blocks)
1. selected-product-gaps.json still empty after TC-MACH-CAP-001
2. Test failures in target format
3. SAL staleness > 7 days AND product sprint type

## 4. Recommended Product Deepening Sequence (After Machinery Repairs)

1. **FODS Python deepening** — close 4 remaining open gaps
2. **NDJSON Python deepening** — close 19 open gaps (prioritize core API over analytics)
3. **FODT .NET deepening** — close 9 open gaps
4. **XCF Python deepening** — close 5 open gaps (read-only: no write capability)
5. **ABW Python seeding** — 39 open gaps (lowest maturity, needs SAL facts first)

## 5. Spec-to-Library-to-Export Proof Definition (FODS Pilot)

For the FODS pilot sprint to be considered successful:
1. **Spec:** SAL fact referenced in evidence (FACT-FODS-*)
2. **Library:** Production class modified or added with spec_qname
3. **Export:** Function exported in __init__.py with test coverage
4. **Ledger:** gap_ledger_ref pointing to closed gap
5. **Evidence:** evidence-declaration.yaml with spec_fact_refs, changed_files, test_results
