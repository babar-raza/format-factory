"""
normalize_pdf.py — Specification PDF Normalization Tool
format-factory / tools/spec-normalize/

Purpose:
    Convert a cached specification PDF into local-only machine-readable derived
    artifacts: text extraction, page map, section map.

Policy:
    - Reads ONLY from local cached spec files (never downloads).
    - Writes ONLY to .local/spec-cache/{format-id}/{version}/normalized/.
    - Verifies source SHA-256 against spec-index.yaml before processing.
    - Does NOT call network endpoints.
    - Does NOT call LLM endpoints.
    - Falls back to metadata-only mode if PDF extraction library unavailable.
    - Does NOT commit normalized artifacts.

See also:
    docs/specification-normalization.md — full policy
    docs/specification-cache.md        — source cache policy
    tools/spec-normalize/_readme.md    — directory orientation
"""

import argparse
import datetime
import hashlib
import json
import os
import pathlib
import sys
from typing import Optional

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

# Optional PDF extraction libraries — graceful fallback if unavailable
PDFMINER_AVAILABLE = False
PYPDF_AVAILABLE = False

try:
    from pdfminer.high_level import extract_text, extract_pages
    from pdfminer.layout import LTTextBox, LTTextLine, LTChar
    PDFMINER_AVAILABLE = True
except ImportError:
    pass

if not PDFMINER_AVAILABLE:
    try:
        import pypdf
        PYPDF_AVAILABLE = True
    except ImportError:
        pass


# ---------------------------------------------------------------------------
# Hash verification
# ---------------------------------------------------------------------------

def compute_sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"


def load_spec_index(spec_dir: pathlib.Path) -> dict:
    index_path = spec_dir / "spec-index.yaml"
    if not index_path.exists():
        raise FileNotFoundError(f"spec-index.yaml not found at {index_path}")
    with open(index_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def find_cached_pdf(spec_dir: pathlib.Path) -> Optional[pathlib.Path]:
    for p in spec_dir.iterdir():
        if p.suffix.lower() == ".pdf" and p.is_file():
            return p
    return None


def verify_source_hash(pdf_path: pathlib.Path, spec_index: dict) -> tuple[bool, str, str]:
    """Returns (match, computed_hash, expected_hash)."""
    computed = compute_sha256(pdf_path)
    entry = spec_index.get("spec_cache_entry", spec_index)
    expected = entry.get("sha256", entry.get("content_hash", ""))
    return computed == expected, computed, expected


# ---------------------------------------------------------------------------
# Source manifest
# ---------------------------------------------------------------------------

def write_source_manifest(
    normalized_dir: pathlib.Path,
    pdf_path: pathlib.Path,
    spec_index: dict,
    hash_match: bool,
    computed_hash: str,
    expected_hash: str,
) -> None:
    entry = spec_index.get("spec_cache_entry", spec_index)
    manifest = {
        "source_manifest": {
            "format_id": entry.get("format_id", "unknown"),
            "spec_name": entry.get("spec_name", "unknown"),
            "version": entry.get("version", "unknown"),
            "source_url": entry.get("source_url", "unknown"),
            "canonical_url": entry.get("canonical_url", "unknown"),
            "source_local_path": str(pdf_path),
            "file_size_bytes": pdf_path.stat().st_size,
            "sha256_expected": expected_hash,
            "sha256_computed": computed_hash,
            "sha256_match": hash_match,
            "verified_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "redistribution_permitted": entry.get("redistribution_permitted", False),
            "local_only": True,
            "notes": (
                "Hash MATCH — source verified."
                if hash_match
                else "WARNING: Hash MISMATCH — do not use this source. Investigate corruption."
            ),
        }
    }
    out = normalized_dir / "source-manifest.yaml"
    with open(out, "w", encoding="utf-8") as f:
        yaml.dump(manifest, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"  Wrote: {out}")


# ---------------------------------------------------------------------------
# Normalization plan (written when library unavailable)
# ---------------------------------------------------------------------------

def write_normalization_plan(
    normalized_dir: pathlib.Path,
    pdf_path: pathlib.Path,
    format_id: str,
    reason: str,
) -> None:
    plan = f"""# Normalization Plan — {format_id}

**Status:** PLANNED — blocked by missing dependency
**Reason:** {reason}
**Source:** {pdf_path}
**Generated:** {datetime.datetime.now(datetime.timezone.utc).isoformat()}

## Planned extractions

1. **text.txt** — full plain-text extraction from PDF
2. **pages.jsonl** — per-page content with page number and raw text
3. **sections.jsonl** — detected section headings with page references
4. **page-map.yaml** — page number to section heading mapping
5. **tables/** — extracted tables as JSON structures
6. **parser-requirements.yaml** — spec sections relevant to parsing FODS

## Dependency

PDF extraction requires `pdfminer.six` or `pypdf`.

To install:
    pip install pdfminer.six

Re-run after installation:
    python tools/spec-normalize/normalize_pdf.py --spec-dir .local/spec-cache/{format_id}/1.3 --format-id {format_id}

## Action required

Install PDF extraction library. Log gap G-NORM-001 if extraction cannot proceed for Gate 4 planning.
"""
    out = normalized_dir / "normalization-plan.md"
    with open(out, "w", encoding="utf-8") as f:
        f.write(plan)
    print(f"  Wrote: {out}")


# ---------------------------------------------------------------------------
# Extraction (pdfminer)
# ---------------------------------------------------------------------------

def extract_with_pdfminer(pdf_path: pathlib.Path, normalized_dir: pathlib.Path) -> dict:
    """Extract text and page content using pdfminer.six."""
    print("  Extracting with pdfminer.six...")
    from pdfminer.high_level import extract_text, extract_pages
    from pdfminer.layout import LTTextBox, LTTextLine

    # Full text
    full_text = extract_text(str(pdf_path))
    text_path = normalized_dir / "text.txt"
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(full_text)
    print(f"  Wrote: {text_path} ({len(full_text):,} chars)")

    # Per-page content
    pages_data = []
    for page_num, page_layout in enumerate(extract_pages(str(pdf_path)), start=1):
        page_text_parts = []
        for element in page_layout:
            if isinstance(element, (LTTextBox, LTTextLine)):
                page_text_parts.append(element.get_text())
        page_text = "".join(page_text_parts).strip()
        pages_data.append({"page": page_num, "text": page_text})

    pages_path = normalized_dir / "pages.jsonl"
    with open(pages_path, "w", encoding="utf-8") as f:
        for page in pages_data:
            f.write(json.dumps(page, ensure_ascii=False) + "\n")
    print(f"  Wrote: {pages_path} ({len(pages_data)} pages)")

    return {"pages": len(pages_data), "chars": len(full_text)}


def extract_with_pypdf(pdf_path: pathlib.Path, normalized_dir: pathlib.Path) -> dict:
    """Extract text using pypdf (fallback)."""
    print("  Extracting with pypdf...")
    reader = pypdf.PdfReader(str(pdf_path))
    pages_data = []
    full_text_parts = []
    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        full_text_parts.append(text)
        pages_data.append({"page": page_num, "text": text.strip()})

    full_text = "\n".join(full_text_parts)
    text_path = normalized_dir / "text.txt"
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(full_text)
    print(f"  Wrote: {text_path} ({len(full_text):,} chars)")

    pages_path = normalized_dir / "pages.jsonl"
    with open(pages_path, "w", encoding="utf-8") as f:
        for page in pages_data:
            f.write(json.dumps(page, ensure_ascii=False) + "\n")
    print(f"  Wrote: {pages_path} ({len(pages_data)} pages)")

    return {"pages": len(pages_data), "chars": len(full_text)}


# ---------------------------------------------------------------------------
# Extraction report
# ---------------------------------------------------------------------------

def write_extraction_report(
    normalized_dir: pathlib.Path,
    pdf_path: pathlib.Path,
    format_id: str,
    extraction_result: dict,
) -> None:
    status = extraction_result.get("status", "unknown")
    report = f"""# Extraction Report — {format_id}

**Generated:** {datetime.datetime.now(datetime.timezone.utc).isoformat()}
**Source:** {pdf_path}
**Status:** {status}

## Summary

{extraction_result.get('summary', 'No summary available.')}

## Artifacts produced

{chr(10).join('- ' + a for a in extraction_result.get('artifacts', []))}

## Gaps logged

{chr(10).join('- ' + g for g in extraction_result.get('gaps', ['None']))}

## Notes

{extraction_result.get('notes', 'No additional notes.')}
"""
    out = normalized_dir / "extraction-report.md"
    with open(out, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"  Wrote: {out}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Normalize a cached specification PDF into structured local-only artifacts."
    )
    parser.add_argument("--spec-dir", required=True,
                        help="Path to .local/spec-cache/{format-id}/{version}/")
    parser.add_argument("--format-id", required=True,
                        help="Format ID (e.g., fods)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Verify hash and write manifest only; do not extract text")
    args = parser.parse_args()

    spec_dir = pathlib.Path(args.spec_dir)
    normalized_dir = spec_dir / "normalized"
    normalized_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nnormalize_pdf.py — format: {args.format_id}")
    print(f"  Spec dir:       {spec_dir}")
    print(f"  Normalized dir: {normalized_dir}")
    print()

    # 1. Load spec index
    print("1. Loading spec-index.yaml...")
    try:
        spec_index = load_spec_index(spec_dir)
    except FileNotFoundError as e:
        print(f"  ERROR: {e}")
        sys.exit(1)
    print("  OK")

    # 2. Find cached PDF
    print("2. Finding cached PDF...")
    pdf_path = find_cached_pdf(spec_dir)
    if pdf_path is None:
        print("  ERROR: No PDF file found in spec directory.")
        print("  Expected a .pdf file under:", spec_dir)
        sys.exit(1)
    print(f"  Found: {pdf_path} ({pdf_path.stat().st_size:,} bytes)")

    # 3. Verify hash
    print("3. Verifying source SHA-256...")
    hash_match, computed, expected = verify_source_hash(pdf_path, spec_index)
    if hash_match:
        print(f"  MATCH: {computed}")
    else:
        print(f"  MISMATCH!")
        print(f"  Expected:  {expected}")
        print(f"  Computed:  {computed}")
        write_source_manifest(normalized_dir, pdf_path, spec_index, False, computed, expected)
        print("\nERROR: Hash mismatch — aborting normalization. Investigate source file integrity.")
        print("Log gap G-NORM-002 and wait for human resolution.")
        sys.exit(1)

    # 4. Write source manifest
    print("4. Writing source manifest...")
    write_source_manifest(normalized_dir, pdf_path, spec_index, True, computed, expected)

    if args.dry_run:
        print("\nDry-run mode — source manifest written. Skipping text extraction.")
        print("Run without --dry-run to extract text (requires pdfminer.six or pypdf).")
        return

    # 5. Extract text
    extraction_result = {}
    artifacts = ["source-manifest.yaml"]
    gaps = []

    if PDFMINER_AVAILABLE:
        print("5. Extracting with pdfminer.six...")
        try:
            stats = extract_with_pdfminer(pdf_path, normalized_dir)
            artifacts += ["text.txt", "pages.jsonl"]
            extraction_result = {
                "status": "SUCCESS (pdfminer.six)",
                "summary": f"Extracted {stats['pages']} pages, {stats['chars']:,} characters.",
                "artifacts": artifacts,
                "gaps": gaps,
                "notes": "Full extraction completed. Normalized artifacts are local-only.",
            }
        except Exception as e:
            print(f"  ERROR: {e}")
            gaps.append(f"G-NORM-001: pdfminer extraction failed: {e}")
            extraction_result = {
                "status": "PARTIAL — pdfminer error",
                "summary": f"pdfminer extraction failed: {e}",
                "artifacts": artifacts,
                "gaps": gaps,
                "notes": "Source manifest written. Text extraction failed.",
            }
    elif PYPDF_AVAILABLE:
        print("5. Extracting with pypdf (fallback)...")
        try:
            stats = extract_with_pypdf(pdf_path, normalized_dir)
            artifacts += ["text.txt", "pages.jsonl"]
            extraction_result = {
                "status": "SUCCESS (pypdf)",
                "summary": f"Extracted {stats['pages']} pages, {stats['chars']:,} characters.",
                "artifacts": artifacts,
                "gaps": gaps,
                "notes": "Full extraction completed using pypdf. Normalized artifacts are local-only.",
            }
        except Exception as e:
            print(f"  ERROR: {e}")
            gaps.append(f"G-NORM-001: pypdf extraction failed: {e}")
            extraction_result = {
                "status": "PARTIAL — pypdf error",
                "summary": f"pypdf extraction failed: {e}",
                "artifacts": artifacts,
                "gaps": gaps,
                "notes": "Source manifest written. Text extraction failed.",
            }
    else:
        print("5. No PDF extraction library available.")
        print("   Install pdfminer.six: pip install pdfminer.six")
        reason = "Neither pdfminer.six nor pypdf is installed."
        write_normalization_plan(normalized_dir, pdf_path, args.format_id, reason)
        artifacts.append("normalization-plan.md")
        gaps.append("G-NORM-001: PDF extraction library unavailable. Install pdfminer.six.")
        extraction_result = {
            "status": "METADATA ONLY — library unavailable",
            "summary": "No PDF text extraction performed. Source hash verified. Plan written.",
            "artifacts": artifacts,
            "gaps": gaps,
            "notes": reason + " Install pdfminer.six and re-run to perform full extraction.",
        }

    # 6. Write extraction report
    print("6. Writing extraction report...")
    write_extraction_report(normalized_dir, pdf_path, args.format_id, extraction_result)

    print(f"\nStatus: {extraction_result['status']}")
    print(f"Artifacts: {', '.join(extraction_result['artifacts'])}")
    if extraction_result["gaps"]:
        print(f"Gaps logged: {', '.join(extraction_result['gaps'])}")
    print(f"\nNormalized artifacts are at: {normalized_dir}")
    print("These are LOCAL ONLY. Do not commit them.")


if __name__ == "__main__":
    main()
