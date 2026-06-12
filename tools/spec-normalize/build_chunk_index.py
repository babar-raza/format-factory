"""
build_chunk_index.py — Specification Chunk Index Builder
format-factory / tools/spec-normalize/

Purpose:
    Split normalized spec pages into addressable chunks for efficient agent use.
    Produces chunks.jsonl: each entry is a metadata record (no full text stored inline)
    with a stable chunk_id, page range, estimated word count, and section reference.

    This enables agents to navigate the 50,000+ line spec by chunk ID instead of
    reading the full text. Chunk text is retrieved on demand from pages.jsonl.

Policy:
    - Reads from .local/spec-cache/{format-id}/{version}/normalized/
    - Writes to .local/spec-cache/{format-id}/{version}/normalized/
    - No network calls.
    - No LLM calls.
    - chunks.jsonl contains METADATA only (no full text).
    - Full text per chunk is retrieved by loading the relevant pages from pages.jsonl.
    - All outputs are local-only (never committed).

Chunking strategy:
    1. Primary split: by section boundaries (from sections.jsonl if available).
    2. Fallback split: by page groups of CHUNK_PAGES_DEFAULT pages each.
    3. Maximum chunk size: CHUNK_MAX_WORDS words (re-split if exceeded).
    4. Chunk IDs are stable: {format_id}-chunk-{start_page:04d}-{end_page:04d}

See also:
    docs/specification-normalization.md — full policy
    tools/spec-normalize/build_section_index.py — section index (run first)
    tools/spec-normalize/query_normalized_spec.py — query tool
"""

import argparse
import datetime
import json
import pathlib
import re
import sys

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

CHUNK_PAGES_DEFAULT = 8   # pages per chunk when no section boundaries available
CHUNK_MAX_WORDS = 2000    # re-split if a chunk exceeds this word count


def load_source_hash(normalized_dir: pathlib.Path) -> str:
    manifest_path = normalized_dir / "source-manifest.yaml"
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as f:
            m = yaml.safe_load(f)
        return m.get("source_manifest", {}).get("sha256_computed", "unknown")
    return "unknown"


def load_pages(pages_file: pathlib.Path) -> list[dict]:
    pages = []
    with open(pages_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                pages.append(json.loads(line))
    return pages


def load_sections(sections_file: pathlib.Path) -> list[dict]:
    if not sections_file.exists():
        return []
    sections = []
    with open(sections_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                sections.append(json.loads(line))
    return sections


def word_count(text: str) -> int:
    return len(text.split())


def build_section_chunks(sections: list[dict], pages: list[dict]) -> list[dict]:
    """Build chunks aligned to section boundaries."""
    page_text = {pg["page"]: pg["text"] for pg in pages}
    chunks = []

    for sec in sections:
        start_p = sec["first_page"]
        end_p = sec.get("last_page") or start_p

        # Collect all text for this section
        section_text = ""
        for p in range(start_p, end_p + 1):
            section_text += page_text.get(p, "")

        wc = word_count(section_text)

        if wc <= CHUNK_MAX_WORDS:
            # Single chunk for this section
            chunks.append({
                "start_page": start_p,
                "end_page": end_p,
                "section_ids": [sec["section_id"]],
                "section_title": sec.get("title", "")[:200],
                "word_count": wc,
                "page_count": end_p - start_p + 1,
            })
        else:
            # Split into sub-chunks by page groups
            sub_start = start_p
            while sub_start <= end_p:
                sub_end = min(sub_start + CHUNK_PAGES_DEFAULT - 1, end_p)
                sub_text = "".join(page_text.get(p, "") for p in range(sub_start, sub_end + 1))
                chunks.append({
                    "start_page": sub_start,
                    "end_page": sub_end,
                    "section_ids": [sec["section_id"]],
                    "section_title": sec.get("title", "")[:200] + f" (part, pp.{sub_start}-{sub_end})",
                    "word_count": word_count(sub_text),
                    "page_count": sub_end - sub_start + 1,
                })
                sub_start = sub_end + 1

    return chunks


def build_page_group_chunks(pages: list[dict], chunk_pages: int = CHUNK_PAGES_DEFAULT) -> list[dict]:
    """Build chunks by grouping consecutive pages."""
    chunks = []
    i = 0
    while i < len(pages):
        batch = pages[i:i + chunk_pages]
        start_p = batch[0]["page"]
        end_p = batch[-1]["page"]
        text = "".join(pg["text"] for pg in batch)
        chunks.append({
            "start_page": start_p,
            "end_page": end_p,
            "section_ids": [],
            "section_title": f"Pages {start_p}–{end_p}",
            "word_count": word_count(text),
            "page_count": len(batch),
        })
        i += chunk_pages
    return chunks


def assign_chunk_ids(chunks: list[dict], format_id: str) -> list[dict]:
    for chunk in chunks:
        chunk["chunk_id"] = f"{format_id}-chunk-{chunk['start_page']:04d}-{chunk['end_page']:04d}"
    return chunks


def extract_text_preview(
    chunks: list[dict], pages: list[dict], preview_chars: int = 200
) -> list[dict]:
    """Add a short text preview to each chunk (first N chars of first page)."""
    page_text = {pg["page"]: pg["text"] for pg in pages}
    for chunk in chunks:
        first_text = page_text.get(chunk["start_page"], "")
        # Clean up whitespace for preview
        preview = re.sub(r'\s+', ' ', first_text[:preview_chars * 2]).strip()[:preview_chars]
        chunk["text_preview"] = preview
    return chunks


def main():
    parser = argparse.ArgumentParser(description="Build chunk index from normalized pages.jsonl")
    parser.add_argument("--normalized-dir", required=True, help="Path to normalized/ directory")
    parser.add_argument("--format-id", required=True, help="Format ID (e.g. fods)")
    parser.add_argument(
        "--chunk-pages", type=int, default=CHUNK_PAGES_DEFAULT,
        help=f"Pages per chunk when section-based chunking is unavailable (default: {CHUNK_PAGES_DEFAULT})"
    )
    args = parser.parse_args()

    normalized_dir = pathlib.Path(args.normalized_dir)
    pages_file = normalized_dir / "pages.jsonl"
    sections_file = normalized_dir / "sections.jsonl"
    chunks_file = normalized_dir / "chunks.jsonl"
    nav_report_file = normalized_dir / "navigation-report.md"

    print(f"build_chunk_index.py ▶ format: {args.format_id}")
    print(f"  Normalized dir: {normalized_dir}")

    # --- Load source hash ---
    source_hash = load_source_hash(normalized_dir)
    print(f"  Source hash: {source_hash[:40]}...")

    # --- Load pages ---
    if not pages_file.exists():
        print(f"ERROR: pages.jsonl not found at {pages_file}", file=sys.stderr)
        sys.exit(1)

    print("1. Loading pages.jsonl...")
    pages = load_pages(pages_file)
    total_pages = len(pages)
    print(f"   Loaded {total_pages} pages")

    # --- Load sections (optional) ---
    print("2. Loading sections.jsonl (optional)...")
    sections = load_sections(sections_file)
    if sections:
        print(f"   Loaded {len(sections)} sections — using section-based chunking")
        chunks = build_section_chunks(sections, pages)
        chunking_method = "section-based"
    else:
        print(f"   sections.jsonl not found — using page-group chunking ({args.chunk_pages} pages/chunk)")
        chunks = build_page_group_chunks(pages, args.chunk_pages)
        chunking_method = f"page-group ({args.chunk_pages} pages/chunk)"

    # --- Assign IDs and previews ---
    print(f"3. Assigning chunk IDs ({len(chunks)} chunks)...")
    chunks = assign_chunk_ids(chunks, args.format_id)
    print("4. Adding text previews...")
    chunks = extract_text_preview(chunks, pages)

    # --- Write chunks.jsonl ---
    print("5. Writing chunks.jsonl...")
    generated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with open(chunks_file, "w", encoding="utf-8") as f:
        for chunk in chunks:
            entry = {
                "chunk_id": chunk["chunk_id"],
                "start_page": chunk["start_page"],
                "end_page": chunk["end_page"],
                "page_count": chunk["page_count"],
                "section_ids": chunk["section_ids"],
                "section_title": chunk["section_title"],
                "word_count": chunk["word_count"],
                "text_preview": chunk["text_preview"],
                "source_hash": source_hash,
                "format_id": args.format_id,
                "generated_at": generated_at,
                "local_only": True,
                "note": "Chunk metadata only. Load pages from pages.jsonl for full text.",
            }
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"   Wrote: {chunks_file} ({len(chunks)} chunks)")

    # --- Summary stats ---
    total_words = sum(c["word_count"] for c in chunks)
    avg_words = total_words // len(chunks) if chunks else 0
    max_words = max((c["word_count"] for c in chunks), default=0)
    min_words = min((c["word_count"] for c in chunks), default=0)

    # --- Write navigation report ---
    print("6. Writing navigation-report.md...")
    report = f"""# Navigation Report — {args.format_id}

**Generated:** {generated_at}
**Source hash:** {source_hash}
**Chunking method:** {chunking_method}

## Summary

- Total pages: {total_pages}
- Total chunks: {len(chunks)}
- Total words: {total_words:,}
- Average words/chunk: {avg_words:,}
- Max words/chunk: {max_words:,}
- Min words/chunk: {min_words:,}
- Section-based chunks: {len(sections) > 0}

## Artifacts produced

- `chunks.jsonl` — {len(chunks)} chunk metadata entries (no full text)
- `navigation-report.md` — this file

## Usage

To retrieve text for a chunk:
1. Look up the chunk in chunks.jsonl by chunk_id.
2. Load pages from pages.jsonl for the chunk's start_page to end_page.
3. Use query_normalized_spec.py for keyword/section search.

## Notes

Full text is NOT stored in chunks.jsonl — only metadata.
Use pages.jsonl for full text retrieval.
These artifacts are local-only. Do not commit them.
"""
    with open(nav_report_file, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"   Wrote: {nav_report_file}")

    print()
    print("Status: SUCCESS")
    print(f"  Chunks: {len(chunks)} ({chunking_method})")
    print(f"  Total words indexed: {total_words:,}")
    print("  Artifacts: chunks.jsonl, navigation-report.md")
    print()
    print(f"Chunk index is at: {normalized_dir}")
    print("These are LOCAL ONLY. Do not commit them.")


if __name__ == "__main__":
    main()
