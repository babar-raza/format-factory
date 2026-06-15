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

    # Step 2: Merge format-specific facts (override takes priority, appended after base)
    specific = _FORMAT_SPECIFIC_FACTS.get(fid, [])
    if specific:
        specific_qnames = {f["qname"] for f in specific}
        # Keep base facts whose qnames don't collide with specific ones
        merged = [f for f in base if f["qname"] not in specific_qnames]
        merged += [dict(f) for f in specific]
        return merged

    return base


def run_sal_pipeline(
    formats: Optional[List[str]] = None,
    output_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Run the SAL pipeline for one or more formats.

    Args:
        formats: list of format IDs to process (None = all registered)
        output_dir: directory to write output JSON (None = .local/sal-output)

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

    if not all_formats:
        print("[sal_master_runner] WARNING: no formats matched", file=sys.stderr)

    results = []
    for fmt in all_formats:
        fid = fmt.get("format_id", "")
        facts = _spec_facts_for_format(fmt)
        entry = {
            "format_id": fid,
            "display_name": fmt.get("display_name", fid),
            "spec_body": fmt.get("spec_body", ""),
            "spec_version": fmt.get("spec_version", ""),
            "spec_url": fmt.get("spec_url", ""),
            "spec_facts": facts,
        }
        results.append(entry)

    total_facts = sum(len(r["spec_facts"]) for r in results)

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": "sal_master_runner.py v1.0",
        "formats_processed": len(results),
        "spec_facts_total": total_facts,
        "results": results,
    }

    # Write timestamped + latest
    ts = datetime.now(timezone.utc).strftime("%Y%m%d")
    dated_path = output_dir / f"sal-facts-{ts}.json"
    latest_path = output_dir / "sal-facts-latest.json"

    payload = json.dumps(output, indent=2)
    dated_path.write_text(payload, encoding="utf-8")
    latest_path.write_text(payload, encoding="utf-8")

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
    args = parser.parse_args()

    if args.list_formats:
        fmts = _load_format_registry()
        for f in fmts:
            print(f"  {f.get('format_id', '?'):20s} {f.get('spec_body', '')}")
        return 0

    formats = None
    if args.format:
        formats = [args.format]
    elif not args.all:
        # Default: process all
        formats = None

    result = run_sal_pipeline(formats=formats, output_dir=Path(args.output_dir))

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
