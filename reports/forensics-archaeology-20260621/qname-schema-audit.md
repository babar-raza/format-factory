# QName Schema Audit

**Sprint:** forensics-archaeology-20260621

---

## QName Compliance Summary

| Metric | Count | Percentage |
|--------|-------|-----------|
| Total Python classes in src/python/ | 135 | 100% |
| Classes WITH spec_qname | 29 | 21% |
| Classes WITHOUT spec_qname | 106 | 79% |
| Classes in spec/ directories | ~30 | 22% |
| Exception classes (correctly no spec_qname) | ~60 | 44% |
| Domain classes missing spec_qname | ~46 | 34% |

---

## Classes WITH spec_qname (complete list)

```
# FODS Compat/ (production facades)
fods/Compat/fods_cell.py     :: FodsCell       => table:table-cell
fods/Compat/fods_document.py :: FodsDocument   => office:document
fods/Compat/fods_sheet.py    :: FodsSheet      => table:table

# FODS spec stubs (canonical)
fods/spec/number/date_style.py     :: DateStyle         => number:date-style
fods/spec/office/automatic_styles.py :: AutomaticStyles => office:automatic-styles
fods/spec/office/body.py           :: Body              => office:body
fods/spec/office/document.py       :: Document          => office:document
fods/spec/office/spreadsheet.py    :: Spreadsheet       => office:spreadsheet
fods/spec/style/style.py           :: Style             => style:style
fods/spec/table/table.py           :: Table             => table:table
fods/spec/table/table_cell.py      :: TableCell         => table:table-cell
fods/spec/table/table_row.py       :: TableRow          => table:table-row
fods/spec/text/paragraph.py        :: Paragraph         => text:p
fods/spec/text/span.py             :: Span              => text:span

# FODS models.py (thin wrappers — have spec_qname)
fods/models.py :: FodsCell     => table:table-cell
fods/models.py :: FodsSheet    => table:table
fods/models.py :: FodsDocument => office:document

# FODS nested (old structure — duplicate)
fods/fods/spec/spreadsheet/cell.py    :: Cell     => table:table-cell
fods/fods/spec/spreadsheet/row.py     :: Row      => table:table-row
fods/fods/spec/spreadsheet/sheet.py   :: Sheet    => table:table
fods/fods/spec/spreadsheet/workbook.py :: Workbook => office:document

# FODT spec stubs (canonical)
fodt/spec/table/table.py       :: Table     => table:table
fodt/spec/table/table_cell.py  :: TableCell => table:table-cell
fodt/spec/table/table_row.py   :: TableRow  => table:table-row
fodt/spec/text/heading.py      :: Heading   => text:h
fodt/spec/text/list_.py        :: List      => text:list
fodt/spec/text/list_item.py    :: ListItem  => text:list-item
fodt/spec/text/paragraph.py    :: Paragraph => text:p
fodt/spec/text/span.py         :: Span      => text:span
```

**Observation:** FODT has NO Compat/ layer yet. FODT's `models.py` classes (FodtSpan, FodtParagraph,
FodtDocument) have NO spec_qname attributes despite corresponding spec stubs existing.

---

## Domain Classes WITHOUT spec_qname (non-exception)

```
# ODS (should map to ODF table: namespace)
ods/ods_parser.py :: OdsCell     (should be: table:table-cell)
ods/ods_parser.py :: OdsRow      (should be: table:table-row)
ods/ods_parser.py :: OdsSheet    (should be: table:table)
ods/ods_parser.py :: OdsDocument (should be: office:document)

# ODT (should map to ODF text: namespace)
odt/odt_parser.py :: OdtParagraph  (should be: text:p)
odt/odt_parser.py :: OdtHeading    (should be: text:h)
odt/odt_parser.py :: OdtListItem   (should be: text:list-item)
odt/odt_parser.py :: OdtDocument   (should be: office:document)

# DIF (binary/text format — no XML namespace)
dif/dif_parser.py :: DifCell     (governed canonical name needed)
dif/dif_parser.py :: DifDocument (governed canonical name needed)

# SYLK (text format — no XML namespace)
sylk/sylk_parser.py :: SylkCell     (governed canonical name needed)
sylk/sylk_parser.py :: SylkDocument (governed canonical name needed)

# Image formats (binary — no XML namespace)
pbm/pbm_parser.py :: PbmImage
pgm/pgm_parser.py :: PgmImage
ppm/ppm_parser.py :: PpmImage
qoi/qoi_parser.py :: QoiImage, QoiDecodeError (the latter is an exception)
xcf/xcf_parser.py :: XcfImage

# FODT models (MISSING despite spec stubs existing!)
fodt/models.py :: FodtSpan      (spec stub exists: fodt/spec/text/span.py::Span)
fodt/models.py :: FodtParagraph (spec stub exists: fodt/spec/text/paragraph.py::Paragraph)
fodt/models.py :: FodtDocument  (no direct spec stub yet for document root)
```

---

## QName Schema Implementation Assessment

### What Is Implemented

1. **`spec_qname` class attribute** — standard pattern, used in fods/ and fodt/ spec stubs and Compat/ facades
2. **`spec_fact_ref`** attribute — references specific FACT-FORMAT-NNN fact ID (in spec stubs)
3. **`namespace_uri`** attribute — full URI (in spec stubs and Compat/ facades)
4. **`local_name`** attribute — element local name (in spec stubs)
5. **`facade_names`** list — links canonical class to its facade(s) (in spec stubs)
6. **`spec/` directory structure** — namespace-organized (`spec/office/`, `spec/table/`, `spec/text/`)
7. **`Compat/` directory** — facade layer for production API (fods only so far)

### What Is Missing

1. **No qname-registry file** — there is no `shared/qname-registry/fods.yaml` or similar (referenced in Compat/ docstrings but not present)
2. **No qname validator integration into generation** — generation skills do not check spec_qname before writing product code
3. **No qname validation in CI** — `qname_structure_validator.py` exists but does not appear to be wired into CI
4. **No .NET qname equivalent** — .NET has XNamespace constants but no `spec_qname` metadata pattern
5. **No qname registry for non-XML formats** — DIF, SYLK, CSV, ZST, XCF etc. have no governed canonical naming system
6. **18/20 Python packages** have no spec/ directory and no spec_qname on any domain class

---

## QName Translation Standard (Current Practice vs Required)

### ODF Formats (fods, fodt, ods, odt, fodg, fodp)

| Spec QName | Current Python | Expected Python | Compliant? |
|-----------|---------------|-----------------|-----------|
| office:document | Document (fods/spec/), FodsDocument (Compat/) | Office.Document + FodsDocument facade | PARTIAL |
| table:table | Table (fods/spec/) | Table.Table | YES |
| table:table-row | TableRow (fods/spec/) | Table.TableRow | YES |
| table:table-cell | TableCell (fods/spec/), FodsCell (Compat/) | Table.TableCell + FodsCell facade | YES |
| text:p | Paragraph (fods/spec/) | Text.Paragraph | YES |
| office:document (ods) | OdsDocument (no spec_qname) | Missing spec stub | NO |
| table:table-cell (ods) | OdsCell (no spec_qname) | Missing spec stub | NO |

### Non-XML Formats (dif, sylk, csv, zst, xcf, pbm etc.)

These formats have no formal qname namespace. Required action:
- Create governed canonical names with evidence (from spec/RFC/format documentation)
- Register in `registry/format-canonical-names.yaml` (does not exist yet)
- Annotate with `spec_fact_ref` pointing to SAL facts

---

## QName Enforcement Points Assessment

| Enforcement Point | Exists? | Wired? | Effective? |
|------------------|---------|--------|-----------|
| `qname_structure_validator.py` | YES | NO (not in CI/governance loop) | NO |
| `governance_validators.py` V45+ | PARTIAL | YES | PARTIAL |
| Skill commands enforce spec_qname | NO | NO | NO |
| Generation templates require spec_qname | NO | NO | NO |
| SAL fact → spec_qname link | YES (FODS/FODT) | PARTIAL | PARTIAL |
| Capability compiler checks spec_qname | YES | PARTIAL | PARTIAL |

---

## Verdict

QName compliance is an early-stage system. The pattern is correctly designed (spec stubs with
`spec_qname`, Compat/ facades, SAL fact refs) but only covers 2 of 20 Python packages and
exists only as stubs in .NET. Enforcement is weak — the validator exists but is not wired
into CI or generation pipelines.

**Required before product deepening:** Wire `qname_structure_validator.py` into governance
loop. Create spec stubs for ODS, ODT at minimum (they share 80% of FODS/FODT's namespace).
Add spec_qname to FODT's models.py classes. Create qname-registry YAML files.
