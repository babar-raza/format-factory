# TC-SRC-REVIEW-003: Seed FODT QName Registry

**Lane**: SRC-REVIEW
**Status**: backlog
**Owner**: autonomous agent
**Prerequisites**: TC-SRC-REVIEW-002 COMPLETE, tools/spec/validate_spec_registry.py CREATED
**item_type**: GOVERNANCE_ASSET
**gap_ledger_ref**: GAP-QNAME-FODT-001

## Objective

Create `shared/qname-registry/fodt.yaml` with 9 QName entries seeded from verified SAL context pack facts.

## Execution Steps

1. Read `reports/specification-authority-layer-mwp/context-pack-sample/fodt-context-pack.json`
2. Verify FACT-FODT-001 through FACT-FODT-007 present
   - If FACT-FODT-007 absent: omit table entries (proceed with 6 entries)
3. Create `shared/qname-registry/fodt.yaml` with the following entries:
   - office:body → Office.Body (FACT-FODT-002, python_file: null, dotnet only)
   - text:p → Text.Paragraph (FACT-FODT-003)
   - text:h → Text.Heading (FACT-FODT-004)
   - text:span → Text.Span (FACT-FODT-006)
   - text:list → Text.List (FACT-FODT-005)
   - text:list-item → Text.ListItem (FACT-FODT-005)
   - table:table → Table.Table (FACT-FODT-007, if present)
   - table:table-row → Table.TableRow (FACT-FODT-007, if present)
   - table:table-cell → Table.TableCell (FACT-FODT-007, if present)
4. `python tools/spec/validate_spec_registry.py shared/qname-registry/fodt.yaml` → PASS
5. Create `tests/spec_registry/test_fodt_registry.py`

## Validation

- validate_spec_registry.py returns PASS (exit 0)
- All expected QNames present in the file
- All spec_fact_refs resolvable in fodt-context-pack.json

## Evidence Required

- `shared/qname-registry/fodt.yaml` content
- validate_spec_registry.py PASS output
- test_fodt_registry.py PASS output

## Rollback

Delete `shared/qname-registry/fodt.yaml`

## Completion Criteria

9 (or 6 if FACT-FODT-007 absent) entries validated; all spec_fact_refs resolvable
