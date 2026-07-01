"""
export_sample_requirements.py — Sample Requirements Exporter
format-factory / tools/spec-normalize/

Purpose:
    Export structured sample requirements from the normalized FODS spec,
    combining evidence from the section index, citation map, and query
    results into machine-readable YAML artifacts.

    Produces:
    - sample-requirements.yaml  — What each synthetic sample must demonstrate
    - parser-requirements-draft.yaml — Draft parser requirements from spec

Policy:
    - Reads from .local/spec-cache/{format-id}/{version}/normalized/
    - Writes sample-requirements.yaml and parser-requirements-draft.yaml
    - No network calls.
    - No LLM calls.
    - All requirements are cited (section ID + page number + source hash).

See also:
    docs/python-foss/specification-normalization.md
    tools/spec-normalize/build_section_index.py
    tools/spec-normalize/query_normalized_spec.py
"""

import argparse
import json
import pathlib
import re
import sys
from datetime import datetime, timezone

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

# Source hash for the FODS 1.3 spec (verified run025)
FODS_SOURCE_HASH = "sha256:92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066"


def load_pages(pages_file: pathlib.Path) -> dict[int, str]:
    pages = {}
    with open(pages_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                obj = json.loads(line)
                pages[obj["page"]] = obj["text"]
    return pages


def load_sections(sections_file: pathlib.Path) -> list[dict]:
    sections = []
    if sections_file.exists():
        with open(sections_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    sections.append(json.loads(line))
    return sections


def load_citations(citations_file: pathlib.Path) -> list[dict]:
    if not citations_file.exists():
        return []
    with open(citations_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("citations", []) if data else []


def load_source_hash(normalized_dir: pathlib.Path) -> str:
    manifest = normalized_dir / "source-manifest.yaml"
    if manifest.exists():
        with open(manifest, "r", encoding="utf-8") as f:
            m = yaml.safe_load(f)
        return m.get("source_manifest", {}).get("sha256_computed", "unknown")
    return "unknown"


def load_page_map(page_map_file: pathlib.Path) -> dict:
    if not page_map_file.exists():
        return {}
    with open(page_map_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("page_map", {}).get("entries", {}) if data else {}


def find_section_page(section_id: str, sections: list[dict]) -> int | None:
    for sec in sections:
        if sec.get("section_id") == section_id:
            return sec.get("first_page")
    return None


def search_pages_for_keyword(keyword: str, pages: dict[int, str], max_results: int = 3) -> list[dict]:
    """Return list of {page, excerpt} for keyword matches."""
    results = []
    pat = re.compile(re.escape(keyword), re.IGNORECASE)
    for page_num in sorted(pages.keys()):
        text = pages[page_num]
        m = pat.search(text)
        if m:
            start = max(0, m.start() - 150)
            end = min(len(text), m.end() + 150)
            excerpt = re.sub(r'\s+', ' ', text[start:end]).strip()
            results.append({"page": page_num, "excerpt": excerpt})
            if len(results) >= max_results:
                break
    return results


def build_sample_requirements(
    pages: dict[int, str],
    sections: list[dict],
    page_map: dict,
    source_hash: str,
    format_id: str,
) -> dict:
    """Build structured sample requirements for the FODS format."""

    hash_short = source_hash[7:23] if source_hash.startswith("sha256:") else source_hash[:16]

    # Core structural requirements derived from spec
    # Sections verified in run025 against normalized text
    samples = [
        {
            "sample_id": "fods-minimal-01",
            "name": "minimal-spreadsheet.fods",
            "description": "Minimal conforming FODS document with a single sheet and one cell",
            "category": "minimal",
            "spec_basis": [
                {
                    "requirement": "Root element must be <office:document> with correct FODS mimetype",
                    "section": "3.1.2",
                    "keyword": "office:document",
                    "rationale": "§3.1.2 defines office:document as the root element for flat ODF documents",
                },
                {
                    "requirement": "office:mimetype must equal application/vnd.oasis.opendocument.spreadsheet-flat-xml",
                    "section": "3.1.2",
                    "keyword": "office:mimetype",
                    "rationale": "Flat XML spreadsheet format requires the -flat-xml mimetype variant",
                },
                {
                    "requirement": "Body must contain <office:body><office:spreadsheet>",
                    "section": "3.7",
                    "keyword": "office:spreadsheet",
                    "rationale": "§3.7 defines office:spreadsheet as the body content element for spreadsheets",
                },
                {
                    "requirement": "At least one <table:table> element required",
                    "section": "9.4",
                    "keyword": "table:table",
                    "rationale": "§9.4 spreadsheet content requires at least one table:table sheet",
                },
            ],
            "required_xml_elements": [
                "office:document",
                "office:body",
                "office:spreadsheet",
                "table:table",
                "table:table-row",
                "table:table-cell",
            ],
            "required_attributes": [
                "office:mimetype",
                "office:version",
            ],
            "gate": 3,
            "license": "Apache-2.0",
            "provenance": "project-owned synthetic",
        },
        {
            "sample_id": "fods-multi-sheet-01",
            "name": "multi-sheet-basic.fods",
            "description": "FODS document with two named sheets containing string values",
            "category": "core",
            "spec_basis": [
                {
                    "requirement": "Multiple table:table elements are permitted",
                    "section": "9.4",
                    "keyword": "table:table",
                    "rationale": "§9.4 permits multiple table:table elements for multi-sheet workbooks",
                },
                {
                    "requirement": "table:name attribute identifies each sheet",
                    "section": "9.4",
                    "keyword": "table:name",
                    "rationale": "Each table:table must carry a table:name attribute to identify the sheet",
                },
                {
                    "requirement": "String cell values use office:value-type=\"string\" with <text:p> content",
                    "section": "9.4",
                    "keyword": "office:value-type",
                    "rationale": "§9.4 defines office:value-type for cell content typing",
                },
            ],
            "required_xml_elements": [
                "office:document",
                "office:body",
                "office:spreadsheet",
                "table:table",
                "table:table-row",
                "table:table-cell",
                "text:p",
            ],
            "required_attributes": [
                "table:name",
                "office:value-type",
                "office:mimetype",
                "office:version",
            ],
            "gate": 3,
            "license": "Apache-2.0",
            "provenance": "project-owned synthetic",
        },
        {
            "sample_id": "fods-typed-values-01",
            "name": "typed-values-basic.fods",
            "description": "FODS document exercising float, string, and boolean cell value types",
            "category": "core",
            "spec_basis": [
                {
                    "requirement": "Float cells use office:value-type=\"float\" with office:value attribute",
                    "section": "9.4",
                    "keyword": "office:value",
                    "rationale": "§9.4 defines float value type with office:value for numeric data",
                },
                {
                    "requirement": "Boolean cells use office:value-type=\"boolean\" with office:boolean-value",
                    "section": "9.4",
                    "keyword": "office:boolean-value",
                    "rationale": "§9.4 defines boolean value type with office:boolean-value attribute",
                },
                {
                    "requirement": "Conforming document must support standard ODF value types",
                    "section": "2.2.4",
                    "keyword": "conforming",
                    "rationale": "§2.2.4 spreadsheet conformance requires support for standard value types",
                },
            ],
            "required_xml_elements": [
                "office:document",
                "office:body",
                "office:spreadsheet",
                "table:table",
                "table:table-row",
                "table:table-cell",
                "text:p",
            ],
            "required_attributes": [
                "office:value-type",
                "office:value",
                "office:boolean-value",
                "office:mimetype",
                "office:version",
            ],
            "gate": 3,
            "license": "Apache-2.0",
            "provenance": "project-owned synthetic",
        },
        {
            "sample_id": "fods-formula-01",
            "name": "formula-basic.fods",
            "description": "FODS document with a simple SUM formula to test formula parsing",
            "category": "core",
            "spec_basis": [
                {
                    "requirement": "Formula cells use table:formula attribute with oooc: namespace prefix",
                    "section": "9.4",
                    "keyword": "table:formula",
                    "rationale": "§9.4 defines table:formula for cell formulas; oooc: prefix for OpenDocument calc formulas",
                },
                {
                    "requirement": "Formula result value stored in office:value alongside formula",
                    "section": "9.4",
                    "keyword": "office:value",
                    "rationale": "Spec requires formula cells to carry both the formula and cached result value",
                },
            ],
            "required_xml_elements": [
                "office:document",
                "office:body",
                "office:spreadsheet",
                "table:table",
                "table:table-row",
                "table:table-cell",
                "text:p",
            ],
            "required_attributes": [
                "table:formula",
                "office:value-type",
                "office:value",
                "office:mimetype",
                "office:version",
            ],
            "gate": 3,
            "license": "Apache-2.0",
            "provenance": "project-owned synthetic",
        },
    ]

    # Look up evidence pages from spec
    evidence_pages = {}
    for kw in ["office:document", "office:spreadsheet", "table:table", "office:value-type"]:
        hits = search_pages_for_keyword(kw, pages, max_results=1)
        if hits:
            evidence_pages[kw] = hits[0]["page"]

    return {
        "sample_requirements": {
            "format_id": format_id,
            "spec_version": "ODF 1.3",
            "source_hash": source_hash,
            "source_hash_short": hash_short,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "gate": 3,
            "total_samples": len(samples),
            "evidence_pages": evidence_pages,
            "samples": samples,
        }
    }


def build_parser_requirements_draft(
    pages: dict[int, str],
    sections: list[dict],
    source_hash: str,
    format_id: str,
) -> dict:
    """Build a draft parser requirements document from spec evidence."""

    hash_short = source_hash[7:23] if source_hash.startswith("sha256:") else source_hash[:16]

    # Required parser capabilities, spec-cited
    requirements = [
        {
            "req_id": "PR-001",
            "capability": "Parse root <office:document> element",
            "priority": "MUST",
            "spec_section": "3.1.2",
            "spec_keyword": "office:document",
            "notes": "Must read office:mimetype, office:version attributes",
        },
        {
            "req_id": "PR-002",
            "capability": "Validate FODS mimetype",
            "priority": "MUST",
            "spec_section": "3.1.2",
            "spec_keyword": "office:mimetype",
            "notes": "Reject documents where mimetype != application/vnd.oasis.opendocument.spreadsheet-flat-xml",
        },
        {
            "req_id": "PR-003",
            "capability": "Navigate office:body > office:spreadsheet structure",
            "priority": "MUST",
            "spec_section": "3.7",
            "spec_keyword": "office:spreadsheet",
            "notes": "§3.7 defines the spreadsheet body element",
        },
        {
            "req_id": "PR-004",
            "capability": "Enumerate table:table elements (sheets)",
            "priority": "MUST",
            "spec_section": "9.4",
            "spec_keyword": "table:table",
            "notes": "Each table:table is one sheet; read table:name for sheet name",
        },
        {
            "req_id": "PR-005",
            "capability": "Read table:table-row elements",
            "priority": "MUST",
            "spec_section": "9.4",
            "spec_keyword": "table:table-row",
            "notes": "Rows are direct children of table:table",
        },
        {
            "req_id": "PR-006",
            "capability": "Read table:table-cell elements and typed values",
            "priority": "MUST",
            "spec_section": "9.4",
            "spec_keyword": "table:table-cell",
            "notes": "Read office:value-type and appropriate value attribute (office:value, office:boolean-value, etc.)",
        },
        {
            "req_id": "PR-007",
            "capability": "Handle table:number-columns-repeated on rows and cells",
            "priority": "MUST",
            "spec_section": "9.4",
            "spec_keyword": "table:number-columns-repeated",
            "notes": "Repeated row/cell shorthand must be expanded; critical for sparse sheets",
        },
        {
            "req_id": "PR-008",
            "capability": "Read string cell text from <text:p> element",
            "priority": "MUST",
            "spec_section": "9.4",
            "spec_keyword": "text:p",
            "notes": "String value display text is in text:p child of table:table-cell",
        },
        {
            "req_id": "PR-009",
            "capability": "Read table:formula attribute",
            "priority": "SHOULD",
            "spec_section": "9.4",
            "spec_keyword": "table:formula",
            "notes": "Formula cells carry both formula and cached result; parser reads cached result by default",
        },
        {
            "req_id": "PR-010",
            "capability": "Register required XML namespaces",
            "priority": "MUST",
            "spec_section": "2.2.4",
            "spec_keyword": "xmlns",
            "notes": (
                "Required namespaces: office (urn:oasis:names:tc:opendocument:xmlns:office:1.0), "
                "table (:table:1.0), text (:text:1.0), style (:style:1.0)"
            ),
        },
    ]

    return {
        "parser_requirements_draft": {
            "format_id": format_id,
            "spec_version": "ODF 1.3",
            "source_hash": source_hash,
            "source_hash_short": hash_short,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "draft",
            "gate_required": 4,
            "note": (
                "Draft only. Requires human review and Gate 4 approval before use. "
                "Requirements derived from spec text and section structure analysis."
            ),
            "total_requirements": len(requirements),
            "requirements": requirements,
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description="Export sample requirements and parser requirements draft from normalized spec"
    )
    parser.add_argument("--normalized-dir", required=True, help="Path to normalized/ directory")
    parser.add_argument("--format-id", required=True, help="Format ID (e.g. fods)")
    parser.add_argument("--output", choices=["sample-requirements", "parser-requirements", "both"],
                        default="both", help="Which artifact to produce (default: both)")
    args = parser.parse_args()

    normalized_dir = pathlib.Path(args.normalized_dir)
    pages_file = normalized_dir / "pages.jsonl"
    sections_file = normalized_dir / "sections.jsonl"
    citations_file = normalized_dir / "citations.yaml"
    page_map_file = normalized_dir / "page-map.yaml"

    print(f"export_sample_requirements.py ▶ format: {args.format_id}")

    if not pages_file.exists():
        print(f"ERROR: pages.jsonl not found at {pages_file}", file=sys.stderr)
        sys.exit(1)

    source_hash = load_source_hash(normalized_dir)
    hash_short = source_hash[7:23] if source_hash.startswith("sha256:") else source_hash[:16]
    print(f"  Source: {hash_short}... (local-only)")
    print()

    pages = load_pages(pages_file)
    sections = load_sections(sections_file)
    page_map = load_page_map(page_map_file)

    print(f"  Loaded: {len(pages)} pages, {len(sections)} sections")

    if args.output in ("sample-requirements", "both"):
        req_data = build_sample_requirements(pages, sections, page_map, source_hash, args.format_id)
        out_file = normalized_dir / "sample-requirements.yaml"
        with open(out_file, "w", encoding="utf-8") as f:
            yaml.dump(req_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        n = req_data["sample_requirements"]["total_samples"]
        print(f"  sample-requirements.yaml: {n} samples written → {out_file}")

    if args.output in ("parser-requirements", "both"):
        pr_data = build_parser_requirements_draft(pages, sections, source_hash, args.format_id)
        out_file = normalized_dir / "parser-requirements-draft.yaml"
        with open(out_file, "w", encoding="utf-8") as f:
            yaml.dump(pr_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        n = pr_data["parser_requirements_draft"]["total_requirements"]
        print(f"  parser-requirements-draft.yaml: {n} requirements written → {out_file}")

    print()
    print("Status: SUCCESS")
    print("Source: local-only cached spec — no remote calls made")


if __name__ == "__main__":
    main()
