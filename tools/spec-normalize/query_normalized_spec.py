"""
query_normalized_spec.py — Specification Navigation Query Tool
format-factory / tools/spec-normalize/

Purpose:
    Query normalized spec artifacts to find relevant sections and text
    without loading the full 50,000-line text.txt directly.

    Supports queries by:
    - keyword (text search in page content)
    - section number (e.g. --section 3.1.2)
    - element name (e.g. --element "office:document")
    - page number (--page 93)
    - sample requirement category (--sample-req minimal|core|edge)

    All output is cited (page number + section ID + source hash).

Policy:
    - Reads from .local/spec-cache/{format-id}/{version}/normalized/
    - No writes unless --export is specified.
    - No network calls.
    - No LLM calls.
    - Returns short, cited excerpts — not the full spec.

See also:
    docs/specification-normalization.md
    tools/spec-normalize/build_section_index.py
    tools/spec-normalize/build_chunk_index.py
    tools/spec-normalize/export_sample_requirements.py
"""

import argparse
import json
import pathlib
import re
import sys

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

# How many characters of context to show per match
CONTEXT_CHARS = 400
# Maximum matches to return per query
MAX_RESULTS = 20


def load_pages(pages_file: pathlib.Path) -> dict[int, str]:
    """Load pages as {page_number: text} dict."""
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


def load_page_map(page_map_file: pathlib.Path) -> dict:
    if not page_map_file.exists():
        return {}
    with open(page_map_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("page_map", {}).get("entries", {})


def load_source_hash(normalized_dir: pathlib.Path) -> str:
    manifest = normalized_dir / "source-manifest.yaml"
    if manifest.exists():
        with open(manifest, "r", encoding="utf-8") as f:
            m = yaml.safe_load(f)
        return m.get("source_manifest", {}).get("sha256_computed", "unknown")
    return "unknown"


def section_for_page(page_num: int, page_map: dict) -> str:
    """Get section ID for a page number."""
    return page_map.get(page_num, page_map.get(str(page_num), "unknown"))


def format_result(page_num: int, section_id: str, source_hash: str, excerpt: str) -> str:
    hash_short = source_hash[7:15] if source_hash.startswith("sha256:") else source_hash[:8]
    excerpt_clean = re.sub(r'\s+', ' ', excerpt).strip()
    return (
        f"  [Page {page_num}] [§{section_id}] [src:{hash_short}...]\n"
        f"  {excerpt_clean}\n"
    )


def query_by_keyword(
    keyword: str,
    pages: dict[int, str],
    page_map: dict,
    source_hash: str,
    max_results: int = MAX_RESULTS,
    context: int = CONTEXT_CHARS,
) -> list[str]:
    results = []
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)

    for page_num in sorted(pages.keys()):
        text = pages[page_num]
        for m in pattern.finditer(text):
            start = max(0, m.start() - context // 2)
            end = min(len(text), m.end() + context // 2)
            excerpt = text[start:end]
            sec_id = section_for_page(page_num, page_map)
            results.append(format_result(page_num, sec_id, source_hash, excerpt))
            if len(results) >= max_results:
                return results
    return results


def query_by_element(
    element: str,
    pages: dict[int, str],
    page_map: dict,
    source_hash: str,
    max_results: int = MAX_RESULTS,
    context: int = CONTEXT_CHARS,
) -> list[str]:
    """Search for XML element names like <office:document> or office:document."""
    # Build variants to search for
    clean = element.strip("<>").strip()
    patterns = [
        re.compile(re.escape(f"<{clean}>"), re.IGNORECASE),
        re.compile(re.escape(f"<{clean}"), re.IGNORECASE),
        re.compile(re.escape(clean), re.IGNORECASE),
    ]

    results = []
    for page_num in sorted(pages.keys()):
        text = pages[page_num]
        for pat in patterns:
            for m in pat.finditer(text):
                start = max(0, m.start() - context // 2)
                end = min(len(text), m.end() + context // 2)
                excerpt = text[start:end]
                sec_id = section_for_page(page_num, page_map)
                result_str = format_result(page_num, sec_id, source_hash, excerpt)
                if result_str not in results:  # deduplicate
                    results.append(result_str)
                if len(results) >= max_results:
                    return results
            break  # use first matching pattern variant

    return results


def query_by_section(
    section_id: str,
    sections: list[dict],
    pages: dict[int, str],
    source_hash: str,
    context_pages: int = 2,
) -> list[str]:
    """Return text from a specific section."""
    target = None
    for sec in sections:
        if sec["section_id"] == section_id or sec["section_id"].startswith(section_id + "."):
            target = sec
            break

    if not target:
        # Try prefix match
        for sec in sections:
            if sec["section_id"].startswith(section_id):
                target = sec
                break

    if not target:
        return [f"  Section {section_id} not found in section index.\n"]

    results = []
    start_p = target["first_page"]
    end_p = min(target.get("last_page") or start_p, start_p + context_pages)

    for p in range(start_p, end_p + 1):
        text = pages.get(p, "")
        if text.strip():
            excerpt = re.sub(r'\s+', ' ', text[:CONTEXT_CHARS * 2]).strip()[:CONTEXT_CHARS]
            results.append(format_result(p, target["section_id"], source_hash, excerpt))

    return results if results else [f"  Section {section_id} found but no text on pages {start_p}–{end_p}.\n"]


def query_by_page(
    page_num: int,
    pages: dict[int, str],
    page_map: dict,
    source_hash: str,
) -> list[str]:
    text = pages.get(page_num, "")
    if not text:
        return [f"  Page {page_num} not found.\n"]
    sec_id = section_for_page(page_num, page_map)
    excerpt = re.sub(r'\s+', ' ', text[:CONTEXT_CHARS * 2]).strip()[:CONTEXT_CHARS]
    return [format_result(page_num, sec_id, source_hash, excerpt)]


# Sample requirement keyword sets
SAMPLE_REQ_KEYWORDS = {
    "minimal": [
        "office:document", "office:spreadsheet", "office:body",
        "mimetype", "office:version", "minimal", "conforming",
        "table:table", "table:table-row", "table:table-cell",
    ],
    "core": [
        "text:p", "office:value-type", "string", "float", "number",
        "table:number-columns-repeated", "multiple", "sheet",
        "office:automatic-styles", "column",
    ],
    "edge": [
        "unicode", "utf-8", "merged", "table:number-columns-spanned",
        "table:number-rows-spanned", "empty", "special character",
        "table:covered-table-cell",
    ],
}


def query_sample_requirements(
    category: str,
    pages: dict[int, str],
    page_map: dict,
    source_hash: str,
) -> list[str]:
    """Find pages relevant to a sample requirement category."""
    keywords = SAMPLE_REQ_KEYWORDS.get(category, [])
    if not keywords:
        return [f"  Unknown sample requirement category: {category}\n"]

    results = []
    for kw in keywords[:5]:  # limit keywords to avoid too many results
        hits = query_by_keyword(kw, pages, page_map, source_hash, max_results=3)
        if hits:
            results.append(f"  --- Keyword: '{kw}' ---\n")
            results.extend(hits[:2])

    return results[:20]


def main():
    parser = argparse.ArgumentParser(
        description="Query normalized spec artifacts without loading full text"
    )
    parser.add_argument("--normalized-dir", required=True, help="Path to normalized/ directory")
    parser.add_argument("--format-id", required=True, help="Format ID (e.g. fods)")
    parser.add_argument("--keyword", help="Search by keyword (text search)")
    parser.add_argument("--element", help="Search by XML element name (e.g. 'office:document')")
    parser.add_argument("--section", help="Get content from section (e.g. '3.1.2')")
    parser.add_argument("--page", type=int, help="Get content from page number")
    parser.add_argument("--sample-req", choices=list(SAMPLE_REQ_KEYWORDS.keys()),
                        help="Find pages relevant to sample requirement category")
    parser.add_argument("--max-results", type=int, default=MAX_RESULTS,
                        help=f"Maximum results to return (default: {MAX_RESULTS})")
    args = parser.parse_args()

    if not any([args.keyword, args.element, args.section, args.page, args.sample_req]):
        parser.error("Specify at least one query: --keyword, --element, --section, --page, or --sample-req")

    normalized_dir = pathlib.Path(args.normalized_dir)
    pages_file = normalized_dir / "pages.jsonl"
    sections_file = normalized_dir / "sections.jsonl"
    page_map_file = normalized_dir / "page-map.yaml"

    print(f"query_normalized_spec.py ▶ format: {args.format_id}")

    source_hash = load_source_hash(normalized_dir)
    hash_short = source_hash[7:23] if source_hash.startswith("sha256:") else source_hash[:16]
    print(f"  Source: {hash_short}... (local-only)")
    print()

    # Load what we need
    if not pages_file.exists():
        print(f"ERROR: pages.jsonl not found at {pages_file}", file=sys.stderr)
        sys.exit(1)

    pages = load_pages(pages_file)
    sections = load_sections(sections_file)
    page_map = load_page_map(page_map_file)

    results = []

    if args.keyword:
        print(f"Query: keyword = '{args.keyword}'")
        results = query_by_keyword(args.keyword, pages, page_map, source_hash, args.max_results)

    elif args.element:
        print(f"Query: element = '{args.element}'")
        results = query_by_element(args.element, pages, page_map, source_hash, args.max_results)

    elif args.section:
        print(f"Query: section = '{args.section}'")
        results = query_by_section(args.section, sections, pages, source_hash)

    elif args.page:
        print(f"Query: page = {args.page}")
        results = query_by_page(args.page, pages, page_map, source_hash)

    elif args.sample_req:
        print(f"Query: sample-req category = '{args.sample_req}'")
        results = query_sample_requirements(args.sample_req, pages, page_map, source_hash)

    print(f"Results ({len(results)}):")
    print("-" * 60)
    for r in results:
        print(r)

    if not results:
        print("  (no results found)")

    print("-" * 60)
    print(f"Total: {len(results)} result(s)")
    print("Source: local-only cached spec — no remote calls made")


if __name__ == "__main__":
    main()
