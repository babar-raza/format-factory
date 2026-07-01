"""
build_section_index.py — Specification Section Index Builder
format-factory / tools/spec-normalize/

Purpose:
    Parse normalized pages.jsonl to detect section headings and produce:
    - sections.jsonl: section metadata (id, title, page range, char offset)
    - page-map.yaml: page-number → section mapping for fast lookup

Policy:
    - Reads from .local/spec-cache/{format-id}/{version}/normalized/
    - Writes to .local/spec-cache/{format-id}/{version}/normalized/
    - No network calls.
    - No LLM calls.
    - Never overwrites source PDF or text.txt.
    - All outputs are local-only (never committed).

Algorithm:
    1. Parse pages.jsonl (per-page extracted text).
    2. Detect TOC entries with section numbers, titles, and page refs.
    3. Detect body section headings (section number + title pattern).
    4. Merge and deduplicate into a unified section map.
    5. Output sections.jsonl and page-map.yaml.

See also:
    docs/python-foss/specification-normalization.md — full policy
    tools/spec-normalize/build_chunk_index.py — chunking tool (next step)
    tools/spec-normalize/query_normalized_spec.py — query tool
"""

import argparse
import datetime
import hashlib
import json
import pathlib
import re
import sys

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Section heading detection patterns
# ---------------------------------------------------------------------------

# TOC entries: "3.1.2   <office:document>...............90"
TOC_ENTRY_RE = re.compile(
    r'^(\d+(?:\.\d+)+)\s{2,}(.+?)\s*\.{5,}\s*(\d+)\s*$'
)

# Appendix TOC: "Appendix A   Title....90"
TOC_APPENDIX_RE = re.compile(
    r'^(Appendix\s+[A-Z])\s{2,}(.+?)\s*\.{5,}\s*(\d+)\s*$',
    re.IGNORECASE,
)

# Body section headings: "3.1.2   <office:document>"
# (no dots, no trailing page number)
BODY_HEADING_RE = re.compile(
    r'^(\d+(?:\.\d+)+)\s{2,}(\S.{1,150})$'
)

# Purely numeric section heading with short title
SHORT_HEADING_RE = re.compile(
    r'^(\d+(?:\.\d+)+)\s{1,8}([A-Z<\[][^\n]{2,80})$'
)


def detect_toc_pages(pages: list[dict]) -> tuple[int, int]:
    """Find the approximate page range containing the Table of Contents."""
    toc_start = -1
    toc_end = -1
    for pg in pages[:50]:  # TOC is always in the first 50 pages
        text = pg["text"]
        if "Table of Contents" in text or "table of contents" in text.lower():
            toc_start = pg["page"]
        # Count TOC entries on the page
        matches = TOC_ENTRY_RE.findall(text)
        if len(matches) >= 3:
            if toc_start < 0:
                toc_start = pg["page"]
            toc_end = pg["page"]
    if toc_start < 0:
        toc_start = 5  # fallback
    if toc_end < 0:
        toc_end = min(toc_start + 20, 50)
    return toc_start, toc_end


def extract_toc_sections(pages: list[dict], toc_start: int, toc_end: int) -> list[dict]:
    """Extract section entries from TOC pages."""
    sections = []
    seen_ids = set()

    for pg in pages:
        if pg["page"] < toc_start - 1 or pg["page"] > toc_end + 2:
            continue
        for line in pg["text"].splitlines():
            line = line.strip()
            m = TOC_ENTRY_RE.match(line)
            if m:
                sid, title, page_str = m.group(1), m.group(2).strip(), m.group(3)
                if sid not in seen_ids:
                    seen_ids.add(sid)
                    # Clean title
                    title = re.sub(r'\s+', ' ', title).strip()
                    # Remove trailing dots
                    title = title.rstrip('. ')
                    sections.append({
                        "section_id": sid,
                        "title": title[:200],
                        "first_page": int(page_str),
                        "last_page": None,  # filled in later
                        "source": "toc",
                    })
            m2 = TOC_APPENDIX_RE.match(line)
            if m2:
                sid, title, page_str = m2.group(1), m2.group(2).strip(), m2.group(3)
                if sid not in seen_ids:
                    seen_ids.add(sid)
                    title = title.rstrip('. ')
                    sections.append({
                        "section_id": sid,
                        "title": title[:200],
                        "first_page": int(page_str),
                        "last_page": None,
                        "source": "toc",
                    })

    return sections


def fill_last_pages(sections: list[dict], total_pages: int) -> list[dict]:
    """Fill in last_page for each section as the page before the next section starts."""
    # Sort by first_page
    sections.sort(key=lambda s: s["first_page"])
    for i, sec in enumerate(sections):
        if i + 1 < len(sections):
            sec["last_page"] = max(sec["first_page"], sections[i + 1]["first_page"] - 1)
        else:
            sec["last_page"] = total_pages
    return sections


def build_page_map(sections: list[dict], total_pages: int) -> dict:
    """Build page_number → section_id mapping."""
    page_map = {}
    for sec in sections:
        for p in range(sec["first_page"], (sec["last_page"] or sec["first_page"]) + 1):
            page_map[p] = sec["section_id"]
    return page_map


def compute_sha256_of_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"


def load_source_hash(normalized_dir: pathlib.Path) -> str:
    manifest_path = normalized_dir / "source-manifest.yaml"
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as f:
            m = yaml.safe_load(f)
        return m.get("source_manifest", {}).get("sha256_computed", "unknown")
    return "unknown"


def main():
    parser = argparse.ArgumentParser(description="Build section index from normalized pages.jsonl")
    parser.add_argument("--normalized-dir", required=True, help="Path to normalized/ directory")
    parser.add_argument("--format-id", required=True, help="Format ID (e.g. fods)")
    args = parser.parse_args()

    normalized_dir = pathlib.Path(args.normalized_dir)
    pages_file = normalized_dir / "pages.jsonl"
    sections_file = normalized_dir / "sections.jsonl"
    page_map_file = normalized_dir / "page-map.yaml"

    print(f"build_section_index.py ▶ format: {args.format_id}")
    print(f"  Normalized dir: {normalized_dir}")

    # --- Load source hash for provenance ---
    source_hash = load_source_hash(normalized_dir)
    print(f"  Source hash: {source_hash[:40]}...")

    # --- Load pages ---
    if not pages_file.exists():
        print(f"ERROR: pages.jsonl not found at {pages_file}", file=sys.stderr)
        sys.exit(1)

    print("1. Loading pages.jsonl...")
    pages = []
    with open(pages_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                pages.append(json.loads(line))
    total_pages = len(pages)
    print(f"   Loaded {total_pages} pages")

    # --- Detect TOC range ---
    print("2. Detecting Table of Contents...")
    toc_start, toc_end = detect_toc_pages(pages)
    print(f"   TOC pages: {toc_start}–{toc_end}")

    # --- Extract TOC sections ---
    print("3. Extracting sections from TOC...")
    sections = extract_toc_sections(pages, toc_start, toc_end)
    print(f"   Found {len(sections)} TOC sections")

    if len(sections) < 5:
        print("   WARNING: Very few TOC sections found. Trying broader detection...")
        # Expand TOC search
        toc_start = 1
        toc_end = min(80, total_pages)
        sections = extract_toc_sections(pages, toc_start, toc_end)
        print(f"   Expanded search found {len(sections)} sections")

    # --- Fill last pages ---
    print("4. Computing section page ranges...")
    sections = fill_last_pages(sections, total_pages)

    # --- Build page map ---
    print("5. Building page map...")
    page_map = build_page_map(sections, total_pages)

    # --- Write sections.jsonl ---
    print("6. Writing sections.jsonl...")
    generated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with open(sections_file, "w", encoding="utf-8") as f:
        for sec in sections:
            entry = {
                "section_id": sec["section_id"],
                "title": sec["title"],
                "first_page": sec["first_page"],
                "last_page": sec["last_page"],
                "source_hash": source_hash,
                "generated_at": generated_at,
                "format_id": args.format_id,
                "source": sec.get("source", "toc"),
                "local_only": True,
            }
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"   Wrote: {sections_file} ({len(sections)} sections)")

    # --- Write page-map.yaml ---
    print("7. Writing page-map.yaml...")
    page_map_doc = {
        "page_map": {
            "format_id": args.format_id,
            "total_pages": total_pages,
            "source_hash": source_hash,
            "generated_at": generated_at,
            "local_only": True,
            "notes": "Maps page numbers to section IDs. Derived from TOC-based section detection.",
            "entries": {p: page_map.get(p, "unknown") for p in range(1, total_pages + 1)},
        }
    }
    with open(page_map_file, "w", encoding="utf-8") as f:
        yaml.dump(page_map_doc, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"   Wrote: {page_map_file}")

    # --- Summary ---
    print()
    print("Status: SUCCESS")
    print(f"  Sections indexed: {len(sections)}")
    print(f"  Pages mapped: {len(page_map)}")
    print("  Artifacts: sections.jsonl, page-map.yaml")
    print()
    print(f"Section index is at: {normalized_dir}")
    print("These are LOCAL ONLY. Do not commit them.")


if __name__ == "__main__":
    main()
