# Generation Archaeology Report

**Sprint:** forensics-archaeology-20260621

---

## Overview

Four distinct generation waves are visible in the current `src/` tree. Waves are NOT cleanly
separated — individual packages often contain artifacts from multiple waves.

---

## Generation 1 — Format-First / Document-First Code

**What it is:** Format-prefixed monolithic loaders/parsers/writers with invented document
models. No spec identity. No namespace awareness. Function-API or dataclass-API.

**Evidence:**
```
dif/dif_parser.py       -> DifDocument (dataclass, no spec_qname)
ods/ods_parser.py       -> OdsDocument, OdsSheet, OdsRow, OdsCell (no spec_qname)
odt/odt_parser.py       -> OdtDocument, OdtParagraph, OdtHeading, OdtListItem (no spec_qname)
sylk/sylk_parser.py     -> SylkDocument, SylkCell (no spec_qname)
pbm/pbm_parser.py       -> PbmImage (no spec_qname)
pgm/pgm_parser.py       -> PgmImage (no spec_qname)
ppm/ppm_parser.py       -> PpmImage (no spec_qname)
qoi/qoi_parser.py       -> QoiImage (no spec_qname)
xcf/xcf_parser.py       -> XcfImage (no spec_qname)
toml/toml_codec.py      -> no explicit document class
ndjson/ndjson_codec.py  -> no explicit document class
tsv/tsv_parser.py       -> no explicit document class
gnumeric/gnumeric_codec.py -> no explicit document class
```

**Packages in this wave:** dif, ods, odt, sylk, pbm, pgm, ppm, qoi, xcf, toml, ndjson, tsv, gnumeric, abw, fodp

**Status:** ACTIVE (18/20 Python packages)
**Fate:** Must be spec-mapped in place. Format-prefixed document classes should gain spec_qname
attributes and be either replaced by spec stubs or officially registered as compat facades.

---

## Generation 2 — Capability-First / Analytics Code

**What it is:** Functions added to Gen 1 packages to demonstrate specific capabilities (row
count, column count, stats, analytics). No spec backing. Added to hit capability ledger targets.

**Evidence:**
```
csv/csv_analytics.py        -> arithmetic functions (mod_N_times_M pattern)
dif/dif_analytics.py        -> arithmetic analytics functions
fodg/fodg_analytics.py      -> analytics functions
xcf/xcf_analytics.py        -> analytics functions (4773 LOC — massive)
zst/zst_analytics.py        -> analytics functions (4604 LOC — massive)
```

**Key problem:** Many analytics functions follow the `{format}_{metric}_mod_{N}_times_{M}` pattern
which has NO spec backing, no GAP-ledger entry, and triggers `GOV_BLOCK:deepening_suspension_validator`.
The product deepening rotation that produced these was suspended 2026-06-18.

**Status:** SUSPENDED. New Gen 2 additions are blocked.
**Fate:** Analytics files are at LOC cap. No new functions should be added. Existing functions
that lack spec backing should be quarantined or removed in a future sprint.

---

## Generation 3 — Partial QName / Spec-Aware Code

**What it is:** Classes with `spec_qname` class attributes, organized in `spec/` namespace
directories, with spec fact references. Neutral models with formal entity schemas.

**Evidence (Python):**
```
fods/spec/office/document.py      -> Document, spec_qname="office:document", spec_fact_ref="FACT-FODS-001"
fods/spec/office/body.py          -> Body, spec_qname="office:body"
fods/spec/office/spreadsheet.py   -> Spreadsheet, spec_qname="office:spreadsheet"
fods/spec/table/table.py          -> Table, spec_qname="table:table"
fods/spec/table/table_row.py      -> TableRow, spec_qname="table:table-row"
fods/spec/table/table_cell.py     -> TableCell, spec_qname="table:table-cell"
fods/spec/text/paragraph.py       -> Paragraph, spec_qname="text:p"
fods/spec/text/span.py            -> Span, spec_qname="text:span"
fods/spec/style/style.py          -> Style, spec_qname="style:style"
fods/spec/number/date_style.py    -> DateStyle, spec_qname="number:date-style"
fods/neutral_model.py             -> formal Workbook/Sheet/Row/Cell/Formula/Warning schema
fodt/spec/table/table.py          -> Table, spec_qname="table:table"
fodt/spec/table/table_row.py      -> TableRow, spec_qname="table:table-row"
fodt/spec/table/table_cell.py     -> TableCell, spec_qname="table:table-cell"
fodt/spec/text/paragraph.py       -> Paragraph, spec_qname="text:p"
fodt/spec/text/heading.py         -> Heading, spec_qname="text:h"
fodt/spec/text/list_.py           -> List, spec_qname="text:list"
fodt/spec/text/list_item.py       -> ListItem, spec_qname="text:list-item"
fodt/spec/text/span.py            -> Span, spec_qname="text:span"
fodt/neutral_model.py             -> formal Document/Block/List/Table/etc schema
```

**Evidence (.NET):**
```
src/net/fods/Spec/Office/   -> (namespace-organized, check needed)
src/net/fods/Spec/Table/    -> (namespace-organized, check needed)
src/net/fods/Model/FodsSheet.cs, FodsRow.cs, FodsCell.cs  -> document object model
src/net/fodt/(inferred)
```

**Packages in this wave:** fods (Python), fodt (Python), fods (.NET), fodt (.NET)

**Status:** ACTIVE — these are the pilot targets for spec-to-library proof
**Fate:** Expand to cover all spec elements. Connect to SAL facts via spec_fact_ref. Add Compat/
facades for all canonical classes.

---

## Generation 4 — Live DOM / Wrapper Models

**What it is:** Objects backed by live XML DOM (XDocument/.NET), preserving unknown elements.
Namespace-aware query methods. `spec_qname`-adjacent metadata (XNamespace constants).

**Evidence (.NET):**
```
src/net/fods/FodsDocument.cs:
  - XDocument _doc
  - XNamespace NsOffice, NsTable, NsText, NsStyle, NsNumber, NsDc, NsMeta
  - Load() / CreateNew() / Save() / Reload()
  - ODF spec reference comments: §3.1.2, §3.7, §9.4.2, §9.4.4, §9.4.5, §6.1.1
  - Security: DTD prohibited, XmlResolver disabled, size guard

src/net/fodt/FodtDocument.cs:
  - Same pattern — XDocument-backed, namespace constants
  - ODF references: §3.1.2, §3.3, §3.4, §5.1.2, §5.1.3
  - Load/CreateEmpty/Save pattern
```

**Status:** ACTIVE (.NET only, FODS and FODT)
**Value:** This is the closest to production-quality in the repo. The load-edit-save-reload
vertical slice is implemented and tested.
**Fate:** Formalize the XNamespace constants as the .NET qname registry. Align with Python
spec stubs. Add spec_qname XML comments to .NET class definitions.

---

## Wave Summary Table

| Wave | Python Packages | .NET Packages | Active? | Fate |
|------|----------------|--------------|---------|------|
| Gen 1 (Format-First) | dif, ods, odt, sylk, pbm, pgm, ppm, qoi, xcf, toml, ndjson, tsv, gnumeric, abw, fodp | csv, ndjson, tsv, zst | YES | Backfill with spec stubs |
| Gen 2 (Capability/Analytics) | csv, dif, fodg, xcf, zst (analytics files) | None | SUSPENDED | Quarantine/remove non-spec analytics |
| Gen 3 (QName/Spec-aware) | fods, fodt | fods, fodt | YES | Expand to all formats |
| Gen 4 (Live DOM/Wrapper) | None | fods, fodt | YES | Formalize + align with Python |

---

## What Produced Each Wave

| Wave | Producer |
|------|---------|
| Gen 1 | Early sprint product deepening without QName enforcement |
| Gen 2 | Product deepening rotation (now suspended) |
| Gen 3 | spec-to-feature-radical-correction-plan Lanes 1+8 (recent) |
| Gen 4 | .NET architecture sprint (DEC-033 Option B) |

---

## What Should Survive

- Gen 1 document classes: KEEP but backfill with spec_qname and migrate to spec-shaped layout
- Gen 2 analytics: AUDIT — remove non-spec-backed arithmetic; keep spec-backed analytics
- Gen 3 spec stubs: EXPAND to all formats
- Gen 4 .NET DOM: FORMALIZE — add spec references to all XNamespace constants and DOM operations

---

## What Should Be Replaced / Quarantined

- `fods/fods/spec/` (nested duplicate): REMOVE — canonical stubs are in `fods/spec/`
- Non-spec analytics functions (`_mod_N_times_M` pattern): QUARANTINE → `_quarantine/`
- Recursive build/ artifacts: GITIGNORE + clean
- Duplicate egg-info at multiple levels: GITIGNORE + clean
