"""
build_citation_map.py — Citation Map Builder
format-factory / tools/spec-normalize/

Purpose:
    Build a citation map from normalized spec text artifacts. Identifies
    cross-references, section citations, and external references within
    a normalized specification.

Policy:
    - Reads ONLY from local normalized artifacts (never downloads).
    - Writes ONLY to .local/spec-cache/{format-id}/{version}/normalized/.
    - Requires text.txt or pages.jsonl to be present (produced by normalize_pdf.py).
    - Does NOT call network endpoints.
    - Does NOT call LLM endpoints.
    - Does NOT commit citation artifacts.

See also:
    docs/specification-normalization.md — full policy
    tools/spec-normalize/_readme.md    — directory orientation
"""

import argparse
import datetime
import json
import pathlib
import re
import sys
from typing import Optional

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Section reference patterns
# ---------------------------------------------------------------------------

# Matches patterns like: section 3.2.1, Section 4, §3.2, clause 5.1.2
SECTION_PATTERNS = [
    re.compile(r'\bsection\s+(\d+(?:\.\d+)*)\b', re.IGNORECASE),
    re.compile(r'\bclause\s+(\d+(?:\.\d+)*)\b', re.IGNORECASE),
    re.compile(r'§\s*(\d+(?:\.\d+)*)'),
    re.compile(r'\bappendix\s+([A-Z](?:\.\d+)*)\b', re.IGNORECASE),
    re.compile(r'\btable\s+(\d+(?:\.\d+)*)\b', re.IGNORECASE),
    re.compile(r'\bfigure\s+(\d+(?:\.\d+)*)\b', re.IGNORECASE),
]

# Matches patterns like: [RFC 4288], [ODF 1.3], [ISO 8601]
EXTERNAL_REF_PATTERNS = [
    re.compile(r'\[([A-Z][A-Z0-9\s\-\.]+\d+[A-Z0-9\s\-\.]*)\]'),
    re.compile(r'\bRFC\s+(\d{4})\b', re.IGNORECASE),
    re.compile(r'\bISO\s+(\d{4,5}(?:[:\-]\d+)?)\b', re.IGNORECASE),
    re.compile(r'\bIEC\s+(\d{4,5}(?:[:\-]\d+)?)\b', re.IGNORECASE),
    re.compile(r'\bW3C\s+([A-Z][A-Z\-]+\b)', re.IGNORECASE),
]


# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------

def extract_section_refs(text: str) -> list[dict]:
    """Extract section cross-references from text."""
    refs = []
    for pattern in SECTION_PATTERNS:
        for match in pattern.finditer(text):
            ref_type = "section"
            if "table" in match.group(0).lower():
                ref_type = "table"
            elif "figure" in match.group(0).lower():
                ref_type = "figure"
            elif "appendix" in match.group(0).lower():
                ref_type = "appendix"

            refs.append({
                "ref_type": ref_type,
                "ref_id": match.group(1),
                "context": match.group(0),
            })
    return refs


def extract_external_refs(text: str) -> list[dict]:
    """Extract external document references from text."""
    refs = []
    for pattern in EXTERNAL_REF_PATTERNS:
        for match in pattern.finditer(text):
            refs.append({
                "ref_type": "external",
                "ref_id": match.group(1) if match.lastindex >= 1 else match.group(0),
                "context": match.group(0),
            })
    return refs


def deduplicate_refs(refs: list[dict]) -> list[dict]:
    """Deduplicate references, keeping unique (ref_type, ref_id) pairs with count."""
    seen = {}
    for ref in refs:
        key = (ref["ref_type"], ref["ref_id"])
        if key not in seen:
            seen[key] = {"ref_type": ref["ref_type"], "ref_id": ref["ref_id"], "count": 0, "contexts": []}
        seen[key]["count"] += 1
        ctx = ref.get("context", "")
        if ctx and ctx not in seen[key]["contexts"] and len(seen[key]["contexts"]) < 3:
            seen[key]["contexts"].append(ctx)
    return sorted(seen.values(), key=lambda r: (-r["count"], r["ref_type"], r["ref_id"]))


# ---------------------------------------------------------------------------
# Load normalized artifacts
# ---------------------------------------------------------------------------

def load_pages_jsonl(normalized_dir: pathlib.Path) -> Optional[list[dict]]:
    """Load pages.jsonl if present."""
    pages_path = normalized_dir / "pages.jsonl"
    if not pages_path.exists():
        return None
    pages = []
    with open(pages_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    pages.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return pages


def load_text_txt(normalized_dir: pathlib.Path) -> Optional[str]:
    """Load text.txt if present."""
    text_path = normalized_dir / "text.txt"
    if not text_path.exists():
        return None
    with open(text_path, "r", encoding="utf-8") as f:
        return f.read()


def load_source_manifest(normalized_dir: pathlib.Path) -> Optional[dict]:
    """Load source-manifest.yaml if present."""
    manifest_path = normalized_dir / "source-manifest.yaml"
    if not manifest_path.exists():
        return None
    with open(manifest_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Write outputs
# ---------------------------------------------------------------------------

def write_citations_yaml(
    normalized_dir: pathlib.Path,
    section_refs: list[dict],
    external_refs: list[dict],
    format_id: str,
    source: str,
) -> None:
    """Write citations.yaml."""
    data = {
        "citation_map": {
            "format_id": format_id,
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "source": source,
            "local_only": True,
            "section_references": {
                "total_unique": len(section_refs),
                "entries": section_refs,
            },
            "external_references": {
                "total_unique": len(external_refs),
                "entries": external_refs,
            },
        }
    }
    out = normalized_dir / "citations.yaml"
    with open(out, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"  Wrote: {out}")


def write_citation_report(
    normalized_dir: pathlib.Path,
    format_id: str,
    section_count: int,
    external_count: int,
    source: str,
    gaps: list[str],
) -> None:
    """Write citation-report.md."""
    gap_text = "\n".join(f"- {g}" for g in gaps) if gaps else "- None"
    report = f"""# Citation Map Report — {format_id}

**Generated:** {datetime.datetime.now(datetime.timezone.utc).isoformat()}
**Source:** {source}

## Summary

- Section/table/figure cross-references found: {section_count}
- External document references found: {external_count}

## Gaps

{gap_text}

## Notes

Citation map is local-only. It is derived from normalized text artifacts.
Do not commit citations.yaml — it may contain spec text context fragments.
"""
    out = normalized_dir / "citation-report.md"
    with open(out, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"  Wrote: {out}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Build a citation map from normalized spec artifacts."
    )
    parser.add_argument("--normalized-dir", required=True,
                        help="Path to .local/spec-cache/{format-id}/{version}/normalized/")
    parser.add_argument("--format-id", required=True,
                        help="Format ID (e.g., fods)")
    args = parser.parse_args()

    normalized_dir = pathlib.Path(args.normalized_dir)
    if not normalized_dir.exists():
        print(f"ERROR: normalized directory not found: {normalized_dir}", file=sys.stderr)
        print("Run normalize_pdf.py first to produce normalized artifacts.", file=sys.stderr)
        sys.exit(1)

    print(f"\nbuild_citation_map.py — format: {args.format_id}")
    print(f"  Normalized dir: {normalized_dir}")
    print()

    gaps = []

    # 1. Verify source manifest present
    print("1. Loading source manifest...")
    manifest = load_source_manifest(normalized_dir)
    if manifest is None:
        print("  WARNING: source-manifest.yaml not found. Run normalize_pdf.py first.")
        gaps.append("G-NORM-005: source-manifest.yaml missing — hash verification unavailable.")
    else:
        sm = manifest.get("source_manifest", manifest)
        if not sm.get("sha256_match", False):
            print("  ERROR: source-manifest.yaml shows hash MISMATCH. Aborting.")
            print("  Investigate source file integrity before building citation map.")
            sys.exit(1)
        print(f"  OK — source: {sm.get('spec_name', 'unknown')}")

    # 2. Load text
    print("2. Loading normalized text...")
    full_text = None
    source_artifact = "unknown"

    # Prefer pages.jsonl (page-level granularity)
    pages = load_pages_jsonl(normalized_dir)
    if pages is not None:
        full_text = "\n".join(p.get("text", "") for p in pages)
        source_artifact = "pages.jsonl"
        print(f"  Loaded pages.jsonl ({len(pages)} pages, {len(full_text):,} chars)")
    else:
        text = load_text_txt(normalized_dir)
        if text is not None:
            full_text = text
            source_artifact = "text.txt"
            print(f"  Loaded text.txt ({len(full_text):,} chars)")
        else:
            print("  ERROR: Neither pages.jsonl nor text.txt found in normalized directory.")
            print("  Run normalize_pdf.py with PDF extraction library to produce text artifacts.")
            gaps.append("G-NORM-001: No text artifacts available. Install pdfminer.six and re-run normalize_pdf.py.")
            write_citation_report(normalized_dir, args.format_id, 0, 0, source_artifact, gaps)
            print("\nStatus: SKIPPED — no text available for citation extraction")
            sys.exit(0)

    # 3. Extract section references
    print("3. Extracting section cross-references...")
    raw_section_refs = extract_section_refs(full_text)
    section_refs = deduplicate_refs(raw_section_refs)
    print(f"  Found {len(section_refs)} unique section/table/figure references")

    # 4. Extract external references
    print("4. Extracting external document references...")
    raw_external_refs = extract_external_refs(full_text)
    external_refs = deduplicate_refs(raw_external_refs)
    print(f"  Found {len(external_refs)} unique external references")

    if not section_refs and not full_text.strip():
        gaps.append("G-NORM-003: No section references detected — section detection may have failed.")

    # 5. Write outputs
    print("5. Writing citation map...")
    write_citations_yaml(normalized_dir, section_refs, external_refs, args.format_id, source_artifact)

    print("6. Writing citation report...")
    write_citation_report(
        normalized_dir, args.format_id,
        len(section_refs), len(external_refs),
        source_artifact, gaps,
    )

    print(f"\nStatus: SUCCESS")
    print(f"  Section refs: {len(section_refs)}")
    print(f"  External refs: {len(external_refs)}")
    print(f"  Artifacts: citations.yaml, citation-report.md")
    if gaps:
        print(f"  Gaps: {'; '.join(gaps)}")
    print(f"\nCitation artifacts are at: {normalized_dir}")
    print("These are LOCAL ONLY. Do not commit them.")


if __name__ == "__main__":
    main()
