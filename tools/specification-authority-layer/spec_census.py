"""
spec_census.py -- Semantic Census Tool for SAL specification texts.

Scans normalized specification text and counts semantic units by taxonomy category
as defined in snoopy-juggling-seal.md Section 2.3.

Categories:
  NORM-REQ  -- Normative requirements (MUST/SHALL/SHOULD)
  ELEM-DEF  -- XML element definitions with namespace
  ATTR-DEF  -- Attribute definitions on elements
  ENUM-VAL  -- Enumerated allowed values
  CARD-RULE -- Cardinality rules (required, optional, repeated)
  DATA-TYPE -- Data type specifications
  GRAMMAR   -- Syntax grammar (ABNF, BNF, XML schema rules)
  ENCODING  -- Byte layout or character encoding
  ERROR     -- Prohibited state or error condition
  CONFORM   -- Conformance class or implementation level

Usage:
  python spec_census.py --format fods
  python spec_census.py --format zst
  python spec_census.py --all
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

_REPO = Path(__file__).resolve().parents[2]
_SPEC_CACHE = _REPO / ".local" / "spec-cache"
_EVIDENCE_DIR = _REPO / ".local" / "evidences"

# ---- Patterns per taxonomy category ----

# NORM-REQ: RFC 2119 keywords in normative context
_NORM_REQ_RE = re.compile(
    r'\b(MUST|SHALL|SHOULD|MUST NOT|SHALL NOT|SHOULD NOT|REQUIRED|OPTIONAL)\b'
)

# ELEM-DEF: XML element definitions (ODF namespace:localname)
_ELEM_DEF_RE = re.compile(
    r'<([a-z][a-z0-9]*:[a-z][a-z0-9\-]+)>|'
    r'\b([a-z][a-z0-9]*:[a-z][a-z0-9\-]+)\s+element\b',
    re.IGNORECASE,
)

# ATTR-DEF: Attribute definitions
_ATTR_DEF_RE = re.compile(
    r'\b([a-z][a-z0-9]*:[a-z][a-z0-9\-]+)\s+attribute\b|'
    r'attribute\s+["]?([a-z][a-z0-9]*:[a-z][a-z0-9\-]+)["]?',
    re.IGNORECASE,
)

# ENUM-VAL: Enumerated values in quotes or after "allowed values"
_ENUM_VAL_RE = re.compile(
    r'allowed\s+values?\b|'
    r'enumerat(ed|ion)\b|'
    r'one\s+of\s+\{|'
    r'value\s+type\b',
    re.IGNORECASE,
)

# CARD-RULE: Cardinality patterns
_CARD_RULE_RE = re.compile(
    r'\b(zero or more|one or more|exactly one|at most one|optional|required|repeatable|'
    r'0\.\.\*|1\.\.\*|0\.\.1|1\.\.1|minOccurs|maxOccurs)\b',
    re.IGNORECASE,
)

# DATA-TYPE: Data type references
_DATA_TYPE_RE = re.compile(
    r'\b(ISO\s+8601|xs?d?:string|xs?d?:integer|xs?d?:boolean|xs?d?:date|xs?d?:decimal|'
    r'xs?d?:float|xs?d?:double|xs?d?:positiveInteger|xs?d?:nonNegativeInteger|'
    r'xs?d?:anyURI|data\s+type|value\s+type)\b',
    re.IGNORECASE,
)

# GRAMMAR: Syntax grammar patterns
_GRAMMAR_RE = re.compile(
    r'\b(ABNF|BNF|grammar|production|syntax|::=)\b|'
    r'^\s*[A-Z][A-Za-z_]+\s*=\s',
    re.IGNORECASE,
)

# ENCODING: Byte layout and encoding
_ENCODING_RE = re.compile(
    r'\b(byte|octet|little.endian|big.endian|magic\s+number|0x[0-9A-Fa-f]+|'
    r'UTF-8|UTF-16|ASCII|encoding|checksum)\b',
    re.IGNORECASE,
)

# ERROR: Prohibited states and error conditions
_ERROR_RE = re.compile(
    r'\b(MUST NOT|SHALL NOT|error|invalid|prohibited|illegal|malformed|'
    r'not\s+allowed|rejected|abort)\b',
    re.IGNORECASE,
)

# CONFORM: Conformance classes
_CONFORM_RE = re.compile(
    r'\b(conformance|conforming|compliance|level\s+\d|'
    r'extended\s+document|strict\s+document|profile)\b',
    re.IGNORECASE,
)


def _find_text(format_id: str) -> Optional[Path]:
    """Find normalized or raw spec text for a format."""
    # Primary: normalized/text.txt
    matches = list(_SPEC_CACHE.glob(f"{format_id}/*/normalized/text.txt"))
    if matches:
        return matches[0]
    # Fallback: any .txt in spec-cache subdirectory
    txt_matches = list(_SPEC_CACHE.glob(f"{format_id}/*/*.txt"))
    if txt_matches:
        return txt_matches[0]
    return None


def run_census(format_id: str) -> Dict[str, Any]:
    """Run semantic census for one format. Returns category counts."""
    text_path = _find_text(format_id)
    if text_path is None:
        return {
            "format_id": format_id,
            "status": "no_text",
            "categories": {},
            "total_units": 0,
        }

    lines = text_path.read_text(encoding="utf-8", errors="ignore").splitlines()

    # Count unique matches per category (deduplicated by match text)
    categories: Dict[str, set] = {
        "NORM-REQ": set(),
        "ELEM-DEF": set(),
        "ATTR-DEF": set(),
        "ENUM-VAL": set(),
        "CARD-RULE": set(),
        "DATA-TYPE": set(),
        "GRAMMAR": set(),
        "ENCODING": set(),
        "ERROR": set(),
        "CONFORM": set(),
    }

    for line in lines:
        for m in _NORM_REQ_RE.finditer(line):
            # Deduplicate by the containing sentence (first 100 chars of line)
            categories["NORM-REQ"].add(line.strip()[:100])

        for m in _ELEM_DEF_RE.finditer(line):
            qname = m.group(1) or m.group(2)
            if qname:
                categories["ELEM-DEF"].add(qname.lower())

        for m in _ATTR_DEF_RE.finditer(line):
            qname = m.group(1) or m.group(2)
            if qname:
                categories["ATTR-DEF"].add(qname.lower())

        for m in _ENUM_VAL_RE.finditer(line):
            categories["ENUM-VAL"].add(line.strip()[:100])

        for m in _CARD_RULE_RE.finditer(line):
            categories["CARD-RULE"].add(line.strip()[:100])

        for m in _DATA_TYPE_RE.finditer(line):
            categories["DATA-TYPE"].add(line.strip()[:100])

        for m in _GRAMMAR_RE.finditer(line):
            categories["GRAMMAR"].add(line.strip()[:100])

        for m in _ENCODING_RE.finditer(line):
            categories["ENCODING"].add(line.strip()[:100])

        for m in _ERROR_RE.finditer(line):
            categories["ERROR"].add(line.strip()[:100])

        for m in _CONFORM_RE.finditer(line):
            categories["CONFORM"].add(line.strip()[:100])

    counts = {cat: len(items) for cat, items in categories.items()}
    total = sum(counts.values())

    return {
        "format_id": format_id,
        "status": "ok",
        "text_path": str(text_path),
        "text_lines": len(lines),
        "categories": counts,
        "total_units": total,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="SAL Semantic Census — count extractable semantic units by category"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--format", dest="format_id", help="Format ID (e.g., fods, zst)")
    group.add_argument("--all", action="store_true", help="Run for all formats with spec text")
    parser.add_argument("--output", help="Output JSON path (default: stdout)")
    args = parser.parse_args()

    if args.all:
        formats = sorted({
            p.parts[-4] if "normalized" in str(p) else p.parts[-3]
            for p in _SPEC_CACHE.glob("*/*/*.txt")
        } | {
            p.parts[-4]
            for p in _SPEC_CACHE.glob("*/*/normalized/text.txt")
        })
    else:
        formats = [args.format_id]

    results = []
    for fmt in formats:
        r = run_census(fmt)
        results.append(r)
        if r["status"] == "ok":
            print(f"[census] {fmt}: {r['total_units']} units across {r['text_lines']} lines",
                  file=sys.stderr)
            for cat, count in r["categories"].items():
                if count > 0:
                    print(f"  {cat}: {count}", file=sys.stderr)
        else:
            print(f"[census] {fmt}: {r['status']}", file=sys.stderr)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": "spec_census.py v1.0",
        "formats_processed": len(formats),
        "results": results,
        "total_semantic_units": sum(r.get("total_units", 0) for r in results),
    }

    output_text = json.dumps(report, indent=2)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output_text, encoding="utf-8")
        print(f"[census] Report written to {out_path}", file=sys.stderr)
    else:
        print(output_text)


if __name__ == "__main__":
    main()
