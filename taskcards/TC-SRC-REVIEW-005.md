# TC-SRC-REVIEW-005: FODT Spec Stubs and compat.py

**Lane**: SRC-REVIEW
**Status**: backlog
**Owner**: autonomous agent
**Prerequisites**: TC-SRC-REVIEW-004 COMPLETE, tools/spec/generate_canonical_stubs.py CREATED
**item_type**: GOVERNANCE_ASSET
**gap_ledger_ref**: GAP-QNAME-FODT-003

## Objective

Run generate_canonical_stubs.py to create architecture_only spec skeletons for FODT in both Python
and .NET. Create compat.py (bootstrap mode — imports from models.py only).

## CRITICAL BOOTSTRAP RULE

compat.py MUST import from models.py ONLY during bootstrap (status < implemented).
NEVER import from spec/ stubs until they reach status: implemented AND tests prove equivalence.

## Execution Steps

1. Run `python tools/spec/generate_canonical_stubs.py --format fodt`
2. Verify Python files created (all architecture_only):
   - src/python/fodt/spec/__init__.py
   - src/python/fodt/spec/office/__init__.py
   - src/python/fodt/spec/text/__init__.py
   - src/python/fodt/spec/table/__init__.py
   - src/python/fodt/spec/text/paragraph.py (spec_qname = "text:p")
   - src/python/fodt/spec/text/heading.py
   - src/python/fodt/spec/text/span.py
   - src/python/fodt/spec/text/list_.py
   - src/python/fodt/spec/text/list_item.py
   - src/python/fodt/spec/table/table.py
   - src/python/fodt/spec/table/table_row.py
   - src/python/fodt/spec/table/table_cell.py
3. Verify .NET files created:
   - src/net/fodt/Spec/Office/Body.cs
   - src/net/fodt/Spec/Text/Paragraph.cs, Span.cs, Heading.cs, List.cs, ListItem.cs
   - src/net/fodt/Spec/Table/Table.cs, TableRow.cs, TableCell.cs
4. Create src/python/fodt/compat.py (bootstrap: re-exports from models.py)
5. Update registry: change status seeded → architecture_only for all 9 entries
6. DO NOT modify src/python/fodt/models.py

## Validation

- All 4 __init__.py files exist in spec/ subdirectories
- All stub .py files have spec_qname attribute
- compat.py imports succeed and FodtParagraph has .kind, .text, .spans properties
- models.py unchanged

## Evidence Required

- File listing of src/python/fodt/spec/
- compat.py content
- Python import check passing

## Completion Criteria

All stubs created with spec_qname; compat.py exports real models.py classes; __init__.py present in all dirs
