"""
sal_master_runner.py — SAL (Specification Authority Layer) Master Runner.

Orchestrates all SAL tools to produce structured spec-fact output per format.
Reads format-registry.yaml as the authoritative source of spec metadata,
then enriches with registered sources from spec_source_registry.

Output schema per format:
  {
    "format_id": str,
    "spec_body": str,
    "spec_version": str,
    "spec_facts": [
      {"qname": str, "section": str, "description": str, "authority": str}
    ]
  }

CLI:
  python sal_master_runner.py --format FODS
  python sal_master_runner.py --all --output-dir .local/sal-output/
  python sal_master_runner.py --list-formats
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# ── Paths ──────────────────────────────────────────────────────────────────────
_HERE = Path(__file__).parent
_REPO_ROOT = _HERE.parent.parent
_FORMAT_REGISTRY = _REPO_ROOT / "registry" / "format-registry.yaml"
_DEFAULT_OUTPUT_DIR = _REPO_ROOT / ".local" / "sal-output"


# ── Known spec fact templates keyed by spec_body ──────────────────────────────
# These are structural facts derived from the specification family, not from
# parsing full spec PDFs. They represent the architectural facts every
# implementation of the format must satisfy.
_SPEC_FACT_TEMPLATES: Dict[str, List[Dict[str, str]]] = {
    "OASIS": [
        {
            "qname": "ODF-FACT-NAMESPACE",
            "section": "ODF 1.3 §2 — Namespaces",
            "description": (
                "All ODF documents must declare the ODF namespace "
                "urn:oasis:names:tc:opendocument:xmlns:office:1.0. "
                "Every element belongs to a declared namespace."
            ),
        },
        {
            "qname": "ODF-FACT-ROOT-ELEMENT",
            "section": "ODF 1.3 §3 — Document Structure",
            "description": (
                "The root element of a flat ODF document must be "
                "<office:document> with the appropriate MIME type attribute."
            ),
        },
        {
            "qname": "ODF-FACT-STYLES",
            "section": "ODF 1.3 §16 — Styles",
            "description": (
                "ODF documents carry style definitions in office:styles, "
                "office:automatic-styles, and office:master-styles. "
                "Implementations must preserve style inheritance chains."
            ),
        },
        {
            "qname": "ODF-FACT-METADATA",
            "section": "ODF 1.3 §2.2 — Document Metadata",
            "description": (
                "ODF documents may contain office:meta with Dublin Core and "
                "ODF-specific metadata elements including dc:title, "
                "dc:creator, meta:creation-date."
            ),
        },
        {
            "qname": "ODF-FACT-BODY",
            "section": "ODF 1.3 §3.3 — Document Body",
            "description": (
                "Every ODF document has an office:body element containing "
                "exactly one content-type element (office:spreadsheet, "
                "office:text, office:presentation, or office:drawing)."
            ),
        },
    ],
    "OASIS-SPREADSHEET": [
        {
            "qname": "ODF-SHEET-FACT-TABLE",
            "section": "ODF 1.3 §9 — Spreadsheet Content",
            "description": (
                "Spreadsheet content is organized in table:table elements. "
                "Each table represents one worksheet with table:name attribute."
            ),
        },
        {
            "qname": "ODF-SHEET-FACT-ROW",
            "section": "ODF 1.3 §9.1 — Table Rows",
            "description": (
                "Rows are represented by table:table-row. Repeated rows "
                "use table:number-rows-repeated attribute."
            ),
        },
        {
            "qname": "ODF-SHEET-FACT-CELL",
            "section": "ODF 1.3 §9.2 — Table Cells",
            "description": (
                "Cells are table:table-cell or table:covered-table-cell. "
                "Value type is specified via office:value-type attribute "
                "(string, float, boolean, date, time, percentage, currency)."
            ),
        },
    ],
    "OASIS-TEXT": [
        {
            "qname": "ODF-TEXT-FACT-PARAGRAPH",
            "section": "ODF 1.3 §5 — Text Content",
            "description": (
                "Text content uses text:p for paragraphs and text:h for "
                "headings. Lists are text:list with text:list-item children."
            ),
        },
        {
            "qname": "ODF-TEXT-FACT-SPAN",
            "section": "ODF 1.3 §5.3 — Text Spans",
            "description": (
                "Inline formatting uses text:span with a text:style-name "
                "attribute. Nested spans are permitted."
            ),
        },
        {
            "qname": "ODF-TEXT-FACT-TABLE",
            "section": "ODF 1.3 §9 — Tables in Text Documents",
            "description": (
                "Text documents may embed tables using table:table. "
                "Tables in text follow the same schema as in spreadsheets."
            ),
        },
    ],
    "IETF": [
        {
            "qname": "IETF-FACT-MAGIC",
            "section": "RFC — File Identification",
            "description": (
                "IETF-specified formats typically define a magic number "
                "or header signature for format identification."
            ),
        },
        {
            "qname": "IETF-FACT-FRAMING",
            "section": "RFC — Frame Structure",
            "description": (
                "IETF formats define a frame or record structure. "
                "Each frame has a defined header and payload layout."
            ),
        },
        {
            "qname": "IETF-FACT-ERROR-HANDLING",
            "section": "RFC — Error Handling",
            "description": (
                "RFC-defined formats specify mandatory error handling "
                "for malformed frames or out-of-range values."
            ),
        },
    ],
    "DEFAULT": [
        {
            "qname": "FORMAT-FACT-MAGIC",
            "section": "Spec §1 — File Identification",
            "description": (
                "This format defines a magic number, extension, or "
                "MIME type for identification."
            ),
        },
        {
            "qname": "FORMAT-FACT-STRUCTURE",
            "section": "Spec §2 — Data Structure",
            "description": (
                "This format defines a structural grammar or schema "
                "for how data is organized in the file."
            ),
        },
        {
            "qname": "FORMAT-FACT-ENCODING",
            "section": "Spec §3 — Character/Byte Encoding",
            "description": (
                "This format specifies encoding requirements "
                "(text encoding, binary layout, or compression)."
            ),
        },
    ],
}

# ── Format-specific fact overrides ────────────────────────────────────────────
_FORMAT_SPECIFIC_FACTS: Dict[str, List[Dict[str, str]]] = {
    "fods": [
        {
            "qname": "FODS-FACT-001",
            "section": "ODF 1.3 §3 — Flat XML Variant",
            "description": (
                "FODS is the flat-XML variant of ODS. The entire document "
                "is a single XML file with no ZIP container. "
                "Root element: <office:document> with "
                "office:mimetype='application/vnd.oasis.opendocument.spreadsheet-flat-xml'."
            ),
        },
        {
            "qname": "FODS-FACT-002",
            "section": "ODF 1.3 §9 — Spreadsheet Structure",
            "description": (
                "FODS spreadsheet content lives in office:body/office:spreadsheet. "
                "Worksheets are table:table elements with mandatory table:name attribute."
            ),
        },
        {
            "qname": "FODS-FACT-003",
            "section": "ODF 1.3 §9.2 — Cell Value Types",
            "description": (
                "Cell values use office:value-type: string, float, boolean, "
                "date, time, percentage, currency. "
                "The typed value is in office:value (float), office:date-value "
                "(date), office:time-value (time), office:boolean-value (bool), "
                "office:string-value (string), office:currency-value (currency)."
            ),
        },
        {
            "qname": "FODS-FACT-004",
            "section": "ODF 1.3 §16 — FODS Styles",
            "description": (
                "FODS carries automatic styles (column widths, cell formats) "
                "in office:automatic-styles. Named styles in office:styles. "
                "Style inheritance: cell style references paragraph style."
            ),
        },
        {
            "qname": "FODS-FACT-005",
            "section": "ODF 1.3 §11 — Formulas (OpenFormula)",
            "description": (
                "Cell formulas use the OpenFormula syntax (OASIS OpenFormula TC). "
                "Formula is in table:formula attribute with of: prefix. "
                "Cached result in office:value attributes."
            ),
        },
        {
            "qname": "FODS-FACT-006",
            "section": "ODF 1.3 §9.1.3 — Column Attributes",
            "description": (
                "Table columns are table:table-column with optional "
                "table:number-columns-repeated, table:style-name, "
                "and table:default-cell-style-name attributes."
            ),
        },
        {
            "qname": "FODS-FACT-007",
            "section": "ODF 1.3 §9.3 — Merged Cells",
            "description": (
                "Merged cells use table:number-columns-spanned and "
                "table:number-rows-spanned on table:table-cell. "
                "Covered cells are table:covered-table-cell elements."
            ),
        },
        {
            "qname": "FODS-FACT-008",
            "section": "ODF 1.3 §9.1.5 — Covered Table Cell",
            "description": (
                "table:covered-table-cell represents a cell covered by a "
                "merge span. It occupies space in the row but carries no "
                "independent value. Used in workbook_merged_cell_summary."
            ),
        },
        {
            "qname": "FODS-FACT-009",
            "section": "ODF 1.3 §19.642 — Formula Attribute",
            "description": (
                "table:formula attribute on table:table-cell contains a "
                "formula expression with namespace prefix (e.g. of:=SUM(A1:A5)). "
                "The cached result is stored in office:value attributes."
            ),
        },
        {
            "qname": "FODS-FACT-010",
            "section": "ODF 1.3 §16.2 — Style Element",
            "description": (
                "style:style defines a named style with style:family attribute "
                "(table-cell, table-column, table-row, paragraph). "
                "Referenced by style:name from content elements."
            ),
        },
        {
            "qname": "FODS-FACT-011",
            "section": "ODF 1.3 §9.4.4 — Content Validation",
            "description": (
                "table:content-validation in table:content-validations defines "
                "cell validation rules. Attributes: table:condition (formula), "
                "table:allow-empty-cell, table:base-cell-address."
            ),
        },
        {
            "qname": "FODS-FACT-012",
            "section": "ODF 1.3 §16.27 — Number Style",
            "description": (
                "number:number-style defines numeric formatting. Contains "
                "number:number (decimal places, grouping), number:text "
                "(literal text). Referenced via style:data-style-name."
            ),
        },
        {
            "qname": "FODS-FACT-013",
            "section": "ODF 1.3 §5.1.3 — Text Paragraph in Cell",
            "description": (
                "Cell text content is wrapped in text:p elements inside "
                "table:table-cell. Multiple text:p elements represent "
                "multi-line cell content. Used by workbook_cell_text_at."
            ),
        },
        {
            "qname": "FODS-FACT-014",
            "section": "ODF 1.3 §17.16 — Table Column Properties",
            "description": (
                "style:table-column-properties defines column layout. "
                "Key attribute: style:column-width (length value). "
                "Referenced from table:table-column via table:style-name."
            ),
        },
    ],
    "fodt": [
        {
            "qname": "FODT-FACT-001",
            "section": "ODF 1.3 §3 — Flat XML Text Variant",
            "description": (
                "FODT is the flat-XML variant of ODT. Single XML file, "
                "no ZIP. Root: <office:document> with "
                "office:mimetype='application/vnd.oasis.opendocument.text-flat-xml'."
            ),
        },
        {
            "qname": "FODT-FACT-002",
            "section": "ODF 1.3 §5 — Text Content",
            "description": (
                "FODT text content in office:body/office:text. "
                "Paragraphs: text:p. Headings: text:h with text:outline-level. "
                "Lists: text:list / text:list-item."
            ),
        },
        {
            "qname": "FODT-FACT-003",
            "section": "ODF 1.3 §5.3 — Inline Formatting",
            "description": (
                "Inline text formatting uses text:span with text:style-name. "
                "Hyperlinks: text:a with xlink:href. "
                "Footnotes: text:note with text:note-class='footnote'."
            ),
        },
        {
            "qname": "FODT-FACT-004",
            "section": "ODF 1.3 §9 — Tables in Text",
            "description": (
                "Text documents embed tables as table:table. "
                "Cells: table:table-cell. "
                "Merged cells use table:number-columns-spanned, "
                "table:number-rows-spanned."
            ),
        },
        {
            "qname": "FODT-FACT-005",
            "section": "ODF 1.3 §10 — Lists",
            "description": (
                "Ordered and unordered lists: text:list with "
                "text:style-name pointing to a list style. "
                "List items: text:list-item. Nested lists allowed."
            ),
        },
        {
            "qname": "FODT-FACT-006",
            "section": "ODF 1.3 §7 — Sections and Frames",
            "description": (
                "Text sections: text:section with text:name. "
                "Frames: draw:frame containing draw:image or draw:text-box. "
                "Anchoring: text:anchor-type (paragraph, page, char, as-char)."
            ),
        },
        {
            "qname": "FODT-FACT-007",
            "section": "ODF 1.3 §6 — Change Tracking",
            "description": (
                "Change tracking in text:tracked-changes. "
                "Insertions: text:change-start/text:change-end. "
                "Deletions: text:deletion with deleted content. "
                "Creator and date in dc:creator, dc:date."
            ),
        },
        {
            "qname": "FODT-FACT-008",
            "section": "ODF 1.3 §5.3.3 — List Item",
            "description": (
                "text:list-item is a child of text:list. Contains text:p "
                "or nested text:list for multi-level lists. "
                "Used by document_list_item_count."
            ),
        },
        {
            "qname": "FODT-FACT-009",
            "section": "ODF 1.3 §16.2 — Paragraph Style",
            "description": (
                "style:style with style:family='paragraph' defines paragraph "
                "formatting. Properties in style:paragraph-properties "
                "(alignment, margin) and style:text-properties (font, size)."
            ),
        },
        {
            "qname": "FODT-FACT-010",
            "section": "ODF 1.3 §6.3.2 — Footnotes and Endnotes",
            "description": (
                "text:note with text:note-class='footnote' or 'endnote'. "
                "Contains text:note-citation (mark) and text:note-body "
                "(content). Used by document_footnote_endnote_summary."
            ),
        },
        {
            "qname": "FODT-FACT-011",
            "section": "ODF 1.3 §6.1.8 — Hyperlinks",
            "description": (
                "text:a element with xlink:href for the URL, "
                "xlink:type='simple'. May wrap text:span for styled links. "
                "Used by document_hyperlink_count."
            ),
        },
        {
            "qname": "FODT-FACT-012",
            "section": "ODF 1.3 §10.4.2 — Draw Frame",
            "description": (
                "draw:frame contains draw:image (with xlink:href to image data) "
                "or draw:text-box. Attributes: svg:width, svg:height, "
                "text:anchor-type. Used by document_image_frame_list."
            ),
        },
        {
            "qname": "FODT-FACT-013",
            "section": "ODF 1.3 §3.1.2 — Document Language",
            "description": (
                "fo:language and fo:country attributes on style:text-properties "
                "specify text language. Multiple languages may coexist in a "
                "document via different paragraph styles."
            ),
        },
        {
            "qname": "FODT-FACT-014",
            "section": "ODF 1.3 §7.4 — User Field Declarations",
            "description": (
                "text:user-field-decl defines reusable text variables. "
                "Attributes: text:name, office:value-type, office:string-value. "
                "Displayed via text:user-field-get. Used by document_text_field_warnings."
            ),
        },
        {
            "qname": "FODT-FACT-015",
            "section": "ODF 1.3 §5.1.2 — Headings",
            "description": (
                "text:h elements represent headings with mandatory "
                "text:outline-level attribute (1-10). Heading style is "
                "determined by text:style-name. Used by document_extract_headings."
            ),
        },
        {
            "qname": "FODT-FACT-016",
            "section": "ODF 1.3 §5.4 — Text Sections",
            "description": (
                "text:section partitions document content with text:name. "
                "Sections can be linked (text:section-source) or protected "
                "(text:protected). Used by document_section_summary."
            ),
        },
    ],
    "zst": [
        {
            "qname": "ZST-FACT-001",
            "section": "RFC 8878 §3 — Zstandard Frame Format",
            "description": (
                "A Zstandard frame starts with a 4-byte magic number 0xFD2FB528. "
                "Frame header contains: frame content size, single segment flag, "
                "content checksum flag, dictionary ID flag."
            ),
        },
        {
            "qname": "ZST-FACT-002",
            "section": "RFC 8878 §3.1 — Blocks",
            "description": (
                "Each frame contains one or more blocks. Block header (3 bytes): "
                "Last_Block flag, Block_Type (Raw, RLE, Compressed), Block_Size."
            ),
        },
        {
            "qname": "ZST-FACT-003",
            "section": "RFC 8878 §8 — Skippable Frames",
            "description": (
                "Skippable frames start with 0x184D2A50-0x184D2A5F magic. "
                "Applications must skip them. Used for metadata."
            ),
        },
        {
            "qname": "ZST-FACT-004",
            "section": "RFC 8878 §3.1.1 — Compressed Blocks",
            "description": (
                "Compressed blocks use Zstandard's encoding: sequences of "
                "literals and match copies. Literals section + sequences section. "
                "Huffman or FSE entropy coding for literals."
            ),
        },
        {
            "qname": "ZST-FACT-005",
            "section": "RFC 8878 §3.1.1.1 — Literals Section",
            "description": (
                "Literals section header specifies: Literals_Section_Type "
                "(Raw, RLE, Compressed, Treeless), Regenerated_Size, "
                "Compressed_Size. Huffman tree may be embedded."
            ),
        },
        {
            "qname": "ZST-FACT-006",
            "section": "RFC 8878 §3.1.1.2 — Sequences Section",
            "description": (
                "Sequences section encodes match copies: Number_of_Sequences, "
                "Symbol_Compression_Modes (predefined, RLE, FSE, repeat). "
                "Each sequence: Literals_Length, Match_Length, Offset."
            ),
        },
        {
            "qname": "ZST-FACT-007",
            "section": "RFC 8878 §4 — Dictionaries",
            "description": (
                "Dictionary compression uses a 4-byte dict ID in the frame header. "
                "Dictionary content: header (magic 0xEC30A437), entropy tables, "
                "and a content section used as initial history."
            ),
        },
        {
            "qname": "ZST-FACT-008",
            "section": "RFC 8878 §3 — Frame Header Descriptor",
            "description": (
                "Frame_Header_Descriptor byte: Frame_Content_Size_flag (2 bits), "
                "Single_Segment_flag, Content_Checksum_flag, Dictionary_ID_flag (2 bits). "
                "Window_Descriptor follows if Single_Segment_flag=0."
            ),
        },
        {
            "qname": "ZST-FACT-009",
            "section": "RFC 8878 §3 — Window Size",
            "description": (
                "Window_Descriptor encodes maximum back-reference distance. "
                "Window_Size = windowBase + (windowBase >> 3) * Exponent. "
                "Max window size: 2^41 bytes (decoder may impose lower limit)."
            ),
        },
        {
            "qname": "ZST-FACT-010",
            "section": "RFC 8878 §3 — Content Checksum",
            "description": (
                "Optional 4-byte content checksum (lower 32 bits of XXH64 of "
                "original decompressed data). Present when Content_Checksum_flag=1."
            ),
        },
        {
            "qname": "ZST-FACT-011",
            "section": "RFC 8878 §5 — FSE Encoding",
            "description": (
                "Finite State Entropy (tANS) is used for sequence symbol encoding. "
                "Accuracy_Log determines table size. Distribution is encoded "
                "in a normalized probability table."
            ),
        },
        {
            "qname": "ZST-FACT-012",
            "section": "RFC 8878 §6 — Huffman Coding",
            "description": (
                "Huffman coding used for literals when Literals_Section_Type=Compressed. "
                "Weight table defines symbol weights. Max number of bits per symbol: 11."
            ),
        },
    ],
    "csv": [
        {
            "qname": "CSV-FACT-001",
            "section": "RFC 4180 §2 — MIME Type and Extension",
            "description": (
                "CSV uses MIME type text/csv and .csv extension. "
                "Each record is on a separate line delimited by CRLF."
            ),
        },
        {
            "qname": "CSV-FACT-002",
            "section": "RFC 4180 §2 — Field Separation",
            "description": (
                "Fields are separated by commas. Fields containing commas, "
                "double-quotes, or line breaks must be enclosed in double-quotes. "
                "A double-quote inside a quoted field is escaped by preceding it "
                "with another double-quote."
            ),
        },
        {
            "qname": "CSV-FACT-003",
            "section": "RFC 4180 §2 — Optional Header",
            "description": (
                "The first record may be an optional header line with field names. "
                "Each field in the header has the same format as fields in data records."
            ),
        },
    ],
    "dif": [
        {
            "qname": "DIF-FACT-001",
            "section": "DIF Spec §1 — Header Section",
            "description": (
                "DIF files start with a header section containing TABLE, VECTORS, "
                "and TUPLES directives that define the document dimensions."
            ),
        },
        {
            "qname": "DIF-FACT-002",
            "section": "DIF Spec §2 — Data Section",
            "description": (
                "The DATA section contains cell values. Each cell has a type "
                "indicator (0=numeric, 1=string) followed by the value. "
                "Special markers: BOT (beginning of tuple), EOD (end of data)."
            ),
        },
        {
            "qname": "DIF-FACT-003",
            "section": "DIF Spec §3 — Value Encoding",
            "description": (
                "Numeric values are on line 1 as float; string values follow "
                "on line 2 in double-quotes. V marker indicates a value cell."
            ),
        },
    ],
    "gnumeric": [
        {
            "qname": "GNUMERIC-FACT-001",
            "section": "Gnumeric XML §1 — Container",
            "description": (
                "Gnumeric files are gzip-compressed XML. Root element: "
                "gnm:Workbook in namespace http://www.gnumeric.org/v10.dtd."
            ),
        },
        {
            "qname": "GNUMERIC-FACT-002",
            "section": "Gnumeric XML §2 — Sheet Structure",
            "description": (
                "Sheets are gnm:Sheet elements with gnm:Name child. "
                "Cells in gnm:Cells/gnm:Cell with Row and Col attributes. "
                "Cell types: 10=empty, 20=bool, 30=int, 40=float, 60=string."
            ),
        },
        {
            "qname": "GNUMERIC-FACT-003",
            "section": "Gnumeric XML §3 — Geometry",
            "description": (
                "Sheet geometry in gnm:MaxCol and gnm:MaxRow elements. "
                "Column widths in gnm:ColInfo, row heights in gnm:RowInfo."
            ),
        },
    ],
    "sylk": [
        {
            "qname": "SYLK-FACT-001",
            "section": "SYLK Spec §1 — File Header",
            "description": (
                "SYLK files start with 'ID' record. Fields separated by "
                "semicolons. Record types: ID, B (bounds), C (cell), F (format), E (end)."
            ),
        },
        {
            "qname": "SYLK-FACT-002",
            "section": "SYLK Spec §2 — Cell Records",
            "description": (
                "C records contain cell data: X=column, Y=row, K=value. "
                "String values in double-quotes. Numeric values as literals."
            ),
        },
        {
            "qname": "SYLK-FACT-003",
            "section": "SYLK Spec §3 — Bounds",
            "description": (
                "B record defines grid bounds: X=max column, Y=max row. "
                "E record marks end of file."
            ),
        },
    ],
}


def _load_registered_source_ids() -> Dict[str, str]:
    """Load spec-source-registry/sources.jsonl and return {format_id: source_id}.

    When multiple sources exist for a format (e.g. zst has RFC8878 and RFC9659),
    the first registered entry wins (primary spec).  Entries with status
    'unavailable' are included but downstream quality_level() treats them as
    Level 0 when the source file is absent.
    """
    registry_path = _REPO_ROOT / ".local" / "spec-source-registry" / "sources.jsonl"
    mapping: Dict[str, str] = {}
    if not registry_path.exists():
        return mapping
    try:
        for line in registry_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            fid = entry.get("format_id", "").lower()
            sid = entry.get("source_id", "")
            if fid and sid and fid not in mapping:
                mapping[fid] = sid
    except Exception:
        pass
    return mapping


# Module-level cache populated on first call
_SOURCE_ID_MAP: Optional[Dict[str, str]] = None


# ODF family formats share the ODF 1.3 spec but may have individual registry entries.
# When a format is not in the registry, try its family parent.
_ODF_FAMILY_FORMATS = frozenset(["fodt", "fods", "fodg", "fodp", "ods", "odt"])


def _get_source_id_for_format(format_id: str) -> Optional[str]:
    """Return the registered source_id for a format, or None if unregistered.

    ODF family formats fall back to the 'fods' registry entry (shared ODF 1.3 spec)
    when the specific format is not registered.
    """
    global _SOURCE_ID_MAP
    if _SOURCE_ID_MAP is None:
        _SOURCE_ID_MAP = _load_registered_source_ids()
    fid = format_id.lower()
    sid = _SOURCE_ID_MAP.get(fid)
    if sid is None and fid in _ODF_FAMILY_FORMATS:
        sid = _SOURCE_ID_MAP.get("fods")  # ODF 1.3 shared spec
    return sid


def _try_verify_facts_against_spec(
    format_id: str, facts: List[Dict[str, str]]
) -> List[Dict[str, str]]:
    """Attempt to verify fact text against normalized spec text.

    If normalized text exists for the format, checks each fact's first 50 chars
    against the full text. Facts that match get fact_status upgraded to
    'text_verified' (Level 2). Facts that don't match keep their current status.

    Non-blocking: returns facts unchanged if normalized text is unavailable.
    """
    spec_cache = _REPO_ROOT / ".local" / "spec-cache"
    text_candidates = list(spec_cache.glob(f"{format_id.lower()}/*/normalized/text.txt"))
    if not text_candidates:
        return facts

    try:
        full_text = text_candidates[0].read_text(encoding="utf-8")
    except Exception:
        return facts

    if len(full_text) < 100:
        return facts

    # Fast inline verification: pre-build lowercase text once, then check each fact's
    # first-50-chars substring. This is O(n) per fact instead of O(n*m) via spec_verifier.
    full_text_lower = full_text.lower()

    upgraded = 0
    for f in facts:
        desc = f.get("description", "") or f.get("claim", "")
        if not desc or len(desc) < 10:
            continue
        fragment = desc[:50].lower()
        if fragment in full_text_lower:
            if f.get("fact_status") != "text_verified":
                f["fact_status"] = "text_verified"
                upgraded += 1

    if upgraded:
        print(
            f"[sal_master_runner] {format_id}: {upgraded} facts upgraded to text_verified",
            file=sys.stderr,
        )

    return facts


def _load_format_registry() -> List[Dict[str, Any]]:
    """Load format-registry.yaml and return list of format dicts."""
    try:
        import yaml  # type: ignore
        with _FORMAT_REGISTRY.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data.get("formats", [])
    except ImportError:
        # Fallback: manual YAML parsing for format_id and spec fields
        text = _FORMAT_REGISTRY.read_text(encoding="utf-8")
        formats = []
        current: Dict[str, Any] = {}
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("- format_id:"):
                if current:
                    formats.append(current)
                current = {"format_id": stripped.split(":", 1)[1].strip()}
            elif current and ":" in stripped:
                key, _, val = stripped.partition(":")
                key = key.strip()
                val = val.strip().strip('"')
                if key in ("spec_body", "spec_version", "spec_url",
                           "display_name", "family"):
                    current[key] = val
        if current:
            formats.append(current)
        return formats
    except Exception as exc:
        print(f"[sal_master_runner] WARNING: could not load format-registry: {exc}",
              file=sys.stderr)
        return []


def _spec_facts_for_format(fmt: Dict[str, Any]) -> List[Dict[str, str]]:
    """Return spec facts for a given format dict.

    Combines base family facts (from spec_body) with format-specific facts
    to ensure depth >= 15 for priority formats.
    """
    fid = fmt.get("format_id", "").lower()
    spec_body = fmt.get("spec_body", "")

    # Step 1: Collect base family facts from spec_body
    base: List[Dict[str, str]] = []
    if "OASIS" in spec_body:
        family = fmt.get("family", "")
        base = [dict(f) for f in _SPEC_FACT_TEMPLATES["OASIS"]]
        if family == "cells":
            base += [dict(f) for f in _SPEC_FACT_TEMPLATES["OASIS-SPREADSHEET"]]
        elif family in ("text", "words"):
            base += [dict(f) for f in _SPEC_FACT_TEMPLATES["OASIS-TEXT"]]
        for fact in base:
            fact["authority"] = f"ODF 1.3 / OASIS (format: {fid.upper()})"
    elif "IETF" in spec_body or "RFC" in spec_body:
        base = [dict(f) for f in _SPEC_FACT_TEMPLATES["IETF"]]
        spec_version = fmt.get("spec_version", "")
        for f in base:
            f["authority"] = spec_version or "IETF RFC"
    else:
        base = [dict(f) for f in _SPEC_FACT_TEMPLATES["DEFAULT"]]
        for f in base:
            f["qname"] = f["qname"].replace("FORMAT", fid.upper())
            f["authority"] = spec_body or "Unknown spec body"

    # Tag all base template facts as bootstrap_only.
    # Link to registered source_id when available (raises quality from Level 0 to Level 1).
    registered_sid = _get_source_id_for_format(fid)
    for f in base:
        f["fact_status"] = "bootstrap_only"
        f["source_id"] = registered_sid  # None if format has no registered spec

    # Step 2: Merge format-specific facts (override takes priority, appended after base)
    specific = _FORMAT_SPECIFIC_FACTS.get(fid, [])
    if specific:
        specific_qnames = {f["qname"] for f in specific}
        # Keep base facts whose qnames don't collide with specific ones
        merged = [f for f in base if f["qname"] not in specific_qnames]
        specific_tagged = [dict(f, fact_status="bootstrap_only",
                                source_id=registered_sid)
                           for f in specific]
        merged += specific_tagged
        return merged

    return base


def _load_workbench_verified_facts(format_id: str) -> List[Dict[str, str]]:
    """Load verified facts from workbench verified-facts-review.yaml for a format.

    Returns a list of fact dicts with qname=claim_id, source="workbench_verified".
    Only returns facts with verification_status in (verified, verified_with_note).
    Returns empty list if no workbench file exists (graceful degradation).
    """
    _VERIFIED = frozenset(["verified", "verified_with_note"])
    spec_cache = _REPO_ROOT / ".local" / "spec-cache"
    pattern = f"{format_id.lower()}/*/workbench/verified-facts-review.yaml"
    workbench_facts: List[Dict[str, str]] = []

    for rf in spec_cache.glob(pattern):
        try:
            # TC-SA-HEAL-011: JSON cache with mtime invalidation (avoids 60s+ YAML parse)
            _cp = rf.with_suffix(".json")
            if _cp.exists() and _cp.stat().st_mtime >= rf.stat().st_mtime:
                data = json.loads(_cp.read_text(encoding="utf-8"))
            else:
                text = rf.read_text(encoding="utf-8")
                if text.lstrip().startswith("{"):
                    data = json.loads(text)
                else:
                    try:
                        import yaml  # type: ignore
                        data = yaml.safe_load(text) or {}
                    except ImportError:
                        continue
                try:
                    _cp.write_text(
                        json.dumps(data, separators=(",", ":")), encoding="utf-8"
                    )
                except Exception:
                    pass

            raw_facts = data.get("facts", [])

            # RC-3: anti-bypass — reject facts with no source_id (GAP-SA-NEW-003)
            rejected_ids: set = set()
            try:
                from spec_verifier import verify_requirements  # lazy import — same dir
                verify_input = []
                for fact in raw_facts:
                    prov = fact.get("provenance", {}) or {}
                    claim_id = fact.get("claim_id") or fact.get("fact_id") or ""
                    raw_source_id = prov.get("spec_id") or prov.get("normalized_artifact")
                    verify_input.append({"req_id": claim_id, "source_id": raw_source_id, "text_fragment": fact.get("claim", "")})
                verify_results = verify_requirements(verify_input)
                rejected_ids = {r.req_id for r in verify_results
                                if r.status == "ANTI_BYPASS_REJECTED"}
                unverifiable_count = sum(1 for r in verify_results
                                         if r.status == "UNVERIFIABLE")
                if rejected_ids: print(f"[sal_master_runner] WARN: {len(rejected_ids)} ANTI_BYPASS_REJECTED for {format_id} — excluded", file=sys.stderr)
                if unverifiable_count: print(f"[sal_master_runner] WARN: {unverifiable_count} UNVERIFIABLE for {format_id} — included", file=sys.stderr)
            except ImportError:
                pass  # spec_verifier unavailable — proceed without anti-bypass check

            for fact in raw_facts:
                prov = fact.get("provenance", {}) or {}
                status = prov.get("verification_status") or fact.get("verification_status", "")
                if status not in _VERIFIED:
                    continue
                claim_id = fact.get("claim_id") or fact.get("fact_id") or ""
                if not claim_id:
                    continue
                # RC-3: skip facts that failed the anti-bypass check
                if claim_id in rejected_ids:
                    continue
                workbench_facts.append({
                    "qname": claim_id,
                    "claim": fact.get("claim", ""),
                    "section": prov.get("section_id", ""),
                    "description": fact.get("claim", ""),
                    "authority": f"verified-facts-review.yaml (status: {status})",
                    "verification_status": status,
                    "source": "workbench_verified",
                    "fact_status": "verified",
                    "source_id": (
                        prov.get("spec_id")
                        or prov.get("normalized_artifact")
                        or f"workbench-{format_id.lower()}"
                    ),
                })
        except Exception:
            pass

    return workbench_facts


def run_sal_pipeline(
    formats: Optional[List[str]] = None,
    output_dir: Optional[Path] = None,
    from_cache_only: bool = False,
    write_latest: bool = True,
) -> Dict[str, Any]:
    """
    Run the SAL pipeline for one or more formats.

    Args:
        formats: list of format IDs to process (None = all registered)
        output_dir: directory to write output JSON (None = .local/sal-output)
        from_cache_only: if True, suppress template facts and emit only
            workbench-verified FACT-<FORMAT>-NNN facts (TC-SAL-IMPL-001)

    Returns:
        dict with keys: formats_processed, spec_facts_total, output_path, results
    """
    output_dir = Path(output_dir) if output_dir else _DEFAULT_OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    all_formats = _load_format_registry()

    if formats:
        formats_lower = {f.lower() for f in formats}
        all_formats = [f for f in all_formats if f.get("format_id", "").lower()
                       in formats_lower]
        # RC-1 (GAP-SA-NEW-001): single/subset-format run on the production output dir
        # must NOT overwrite the all-format sal-facts-latest.json.
        # Tests using a custom output_dir (e.g. tmp_path) are unaffected.
        if write_latest and output_dir.resolve() == _DEFAULT_OUTPUT_DIR.resolve():
            write_latest = False

    if not all_formats:
        print("[sal_master_runner] WARNING: no formats matched", file=sys.stderr)

    results = []
    for fmt in all_formats:
        fid = fmt.get("format_id", "")

        if from_cache_only:
            # TC-SAL-IMPL-001: emit ONLY workbench-verified facts
            facts = []
            workbench_facts = _load_workbench_verified_facts(fid)
            if workbench_facts:
                facts = list(workbench_facts)
        else:
            facts = _spec_facts_for_format(fmt)
            # TC-SAL-014: Merge verified workbench facts (additive — template facts preserved)
            workbench_facts = _load_workbench_verified_facts(fid)
            if workbench_facts:
                existing_qnames = {f.get("qname", "") for f in facts}
                new_facts = [wf for wf in workbench_facts if wf["qname"] not in existing_qnames]
                facts = facts + new_facts

        # Lane C: Run spec_verifier to upgrade fact_status where possible.
        # Facts verified against normalized spec text get fact_status="text_verified" (Level 2).
        facts = _try_verify_facts_against_spec(fid, facts)

        entry = {
            "format_id": fid,
            "display_name": fmt.get("display_name", fid),
            "spec_body": fmt.get("spec_body", ""),
            "spec_version": fmt.get("spec_version", ""),
            "spec_url": fmt.get("spec_url", ""),
            "spec_facts": facts,
            "workbench_verified_fact_count": len(workbench_facts),
        }
        results.append(entry)

    total_facts = sum(len(r["spec_facts"]) for r in results)
    total_workbench = sum(r.get("workbench_verified_fact_count", 0) for r in results)

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": "sal_master_runner.py v1.0",
        "formats_processed": len(results),
        "spec_facts_total": total_facts,
        "workbench_verified_fact_total": total_workbench,
        "results": results,
    }

    # Write per-format output files (sal-facts-<format_id>.json)
    for entry in results:
        fid = entry["format_id"].lower()
        per_format_output = {
            "generated_at": output["generated_at"],
            "generator": output["generator"],
            "format_id": entry["format_id"],
            "spec_facts": entry["spec_facts"],
        }
        per_format_path = output_dir / f"sal-facts-{fid}.json"
        per_format_path.write_text(json.dumps(per_format_output, indent=2), encoding="utf-8")

    # Write timestamped + latest (only when processing all formats — TC-SAL-IDEMPOTENCY)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d")
    dated_path = output_dir / f"sal-facts-{ts}.json"
    latest_path = output_dir / "sal-output-latest.json"
    # Keep backward compat: also write sal-facts-latest.json
    sal_latest_path = output_dir / "sal-facts-latest.json"

    payload = json.dumps(output, indent=2)
    if write_latest:
        dated_path.write_text(payload, encoding="utf-8")
        latest_path.write_text(payload, encoding="utf-8")
        sal_latest_path.write_text(payload, encoding="utf-8")

    output["output_path"] = str(latest_path)
    return output


# ── CLI ────────────────────────────────────────────────────────────────────────

def _cli() -> int:
    parser = argparse.ArgumentParser(
        description="SAL Master Runner — produce spec facts per format"
    )
    parser.add_argument("--format", help="Format ID to process (e.g. FODS)")
    parser.add_argument("--all", action="store_true", help="Process all formats")
    parser.add_argument(
        "--output-dir",
        default=str(_DEFAULT_OUTPUT_DIR),
        help="Directory to write sal-facts-*.json",
    )
    parser.add_argument("--list-formats", action="store_true",
                        help="List all known format IDs and exit")
    parser.add_argument("--from-cache-only", action="store_true",
                        help="Emit only workbench-verified FACT-<FORMAT>-NNN facts (suppress templates)")
    args = parser.parse_args()

    if args.list_formats:
        fmts = _load_format_registry()
        for f in fmts:
            print(f"  {f.get('format_id', '?'):20s} {f.get('spec_body', '')}")
        return 0

    formats = None
    write_latest = True
    if args.format:
        formats = [args.format]
        write_latest = False  # TC-SAL-IDEMPOTENCY: single-format run must not overwrite combined output
    elif not args.all:
        # Default: process all
        formats = None

    result = run_sal_pipeline(
        formats=formats,
        output_dir=Path(args.output_dir),
        from_cache_only=args.from_cache_only,
        write_latest=write_latest,
    )

    print(f"[sal_master_runner] Processed {result['formats_processed']} formats")
    print(f"[sal_master_runner] Total spec facts: {result['spec_facts_total']}")
    print(f"[sal_master_runner] Output: {result['output_path']}")

    if result["formats_processed"] == 0:
        print("[sal_master_runner] WARNING: no formats processed — output is empty",
              file=sys.stderr)
        return 1

    if result["spec_facts_total"] == 0:
        print("[sal_master_runner] WARNING: no spec facts produced",
              file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(_cli())
