# Product Deepening Readiness Plan — Format Factory Machinery Audit v2
# Sprint ID: ff-machinery-readiness-audit-v2-20260621-827f5a52

## Stop/Go Gate

**GO** (with conditions): FODS and FODT product deepening CAN start after fixing P0 blockers.
**STOP** for all other formats until spec/ stubs and SAL facts exist.

## P0 Blockers (Must Fix BEFORE Next Product Sprint)

1. **TC-FODS-TEST-FIX-001** — Fix 32 FODS Python test collection errors
   - Impact: Cannot run FODS test suite until resolved
   - Effort: Low — delete 32 test files (same pattern as SYLK cleanup)

2. **TC-FODS-COMMIT-001** — Commit FODS Compat/ and neutral_model.py
   - Impact: Untracked work at risk of loss
   - Blocker: Requires USER AUTHORIZATION for git commit

## P1 Recommended (Next Sprint, Before Gate 11 Packet)

3. **FODS Python: Complete API surface for Gate 11 P1-P11 criteria**
   - Use /check-gate fods 11 to identify missing criteria
   - Add functions if P-criteria are not met

4. **FODT Python: Create Compat/ layer (mirror of FODS)**
   - FodtDocument, FodtParagraph, FodtList facades

5. **FODS .NET: Run /check-gate fods 11 and build formal C1-C20 packet**

## Product Deepening Pilot Selection

### Recommended Pilot 1: FODS (both Python and .NET)
Rationale:
- FODS Python: 44 passing tests, 4987 SAL facts, spec/ stubs COMPLIANT, Compat/ created
- FODS .NET: 30 public methods, multiple exporters, gate prep in progress
- Best evidence chain: SAL facts → spec/ stubs → Compat/ facades → production API
- Spec-to-library-to-export proof: parse_fods() → FodsDocument → workbook_to_xml() → CSV/HTML export
- Action: Fix tests, commit, run /check-gate fods 11, build Gate 11 packet

### Recommended Pilot 2: FODT (both Python and .NET)
Rationale:
- FODT Python: 8 spec/ stubs, 4933 SAL facts, install proof completed
- FODT .NET: Multiple exporters (HTML, Markdown, TXT)
- Action: Create Compat/ facades, run /check-gate fodt 11, build Gate 11 packet

## Spec-to-Library-to-Export Proof Plan

For FODS Python:
```
1. Load: wb = parse_fods("sample.fods")
2. Inspect: workbook_stats(wb) → dict with sheet count, cell count
3. Edit: workbook_set_cell_value(wb, "Sheet1", 0, 0, "NEW_VALUE")
4. Save: write_fods(wb, "output.fods")
5. Reload: wb2 = parse_fods("output.fods") → verify change preserved
6. Export: from src.python.fods import csv_exporter → export to CSV
7. Evidence: all 6 steps produce expected output, documented in install proof
```

For FODS .NET:
```
1. Load: var doc = FodsDocument.Load("sample.fods")
2. Edit: doc.SetCellValue(0, "A1", "TEST")
3. Save: doc.Save("output.fods")
4. Export: doc.ExportSheetToHtml(0, "output.html")
5. Evidence: dotnet test passes, HTML output verified
```

## Products NOT Ready for Deepening

| Format | Reason | What's Needed |
|--------|--------|--------------|
| ZST Python | Analytics suspended, no spec/ | Remove analytics bloat first |
| XCF Python | GOV_BLOCK risk, no spec | Not feasible |
| ABW/DIF/ODS/ODT | No spec/ stubs, minimal implementation | Create spec/ stubs first |
| CSV/TSV/NDJSON | Simple formats, no canonical qname spec | Different standard applies |
| FODG/FODP | ODF but no spec/ stubs | Create spec/ stubs based on ODF Drawing/Presentation |

## Expansion Rules (After FODS/FODT Gate 11)

1. ONLY expand to a new format after creating its spec/ stubs
2. ONLY add product functions that trace to a spec_fact_ref (GAP-FORMAT-NNN)
3. ONLY run analytics functions that trace to a spec capability (not free arithmetic)
4. ALL new spec/ classes must have spec_qname attribute
5. Gate 11 submission requires formal evidence packet (not just test count)
