"""
run_extraction_pipeline.py — Orchestrator for SAL spec fact extraction pipeline.

Pipeline steps (per format):
  1. Discovery    — check spec-index.yaml for normalized_text_cached
  2. Section idx  — call spec_indexer.build_index() if index missing
  3. Extraction   — format-aware dispatch:
                    ODF (fods/fodt): XML element/attribute pattern scanner (direct)
                    ZST:             requirement_extractor.py (RFC 2119 mode)
  4. Dedup        — skip facts whose claim_id already exists in workbench
  5. Write        — append candidates with pending_verification to workbench YAML
  6. Verify       — trigger run_fact_verification.py on newly added facts

Usage:
  python run_extraction_pipeline.py --format fods
  python run_extraction_pipeline.py --format fods --dry-run
  python run_extraction_pipeline.py --all
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

_REPO = Path(__file__).resolve().parents[2]
_SPEC_CACHE = _REPO / ".local" / "spec-cache"
_ARTIFACTS_DIR = _REPO / ".local" / "spec-artifacts"
_SAL_OUTPUT = _REPO / ".local" / "sal-output"

# Formats with ODF XML namespace — use XML element scan instead of RFC 2119
_ODF_FORMATS = {"fods", "fodt"}

# XML element/attribute patterns that appear in ODF spec text
_ODF_ELEMENT_PATTERNS = [
    re.compile(r'\b([a-z][a-z0-9]*:[a-z][a-z0-9\-]+)\s+element', re.IGNORECASE),
    re.compile(r'element\s+[<"]?([a-z][a-z0-9]*:[a-z][a-z0-9\-]+)[>"]?', re.IGNORECASE),
    re.compile(r'\b([a-z][a-z0-9]*:[a-z][a-z0-9\-]+)\s+attribute', re.IGNORECASE),
    re.compile(r'attribute\s+["]?([a-z][a-z0-9]*:[a-z][a-z0-9\-]+)["]?', re.IGNORECASE),
]

# Valid ODF namespace prefixes to reduce false positives
_ODF_NAMESPACES = {
    "office", "table", "text", "draw", "style", "fo", "chart", "form",
    "presentation", "meta", "number", "anim", "db", "field", "script",
    "math", "svg", "xlink", "dc", "grddl", "xhtml", "pkg",
}

_MAX_CANDIDATES_PER_FORMAT = 5000  # ROOT-09 fix: raised from 200 to enable comprehensive extraction


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_spec_index(format_id: str) -> Optional[Dict[str, Any]]:
    """Load spec-index.yaml for a format. Returns None if not found."""
    if yaml is None:
        return None
    matches = list(_SPEC_CACHE.glob(f"{format_id}/*/spec-index.yaml"))
    if not matches:
        return None
    with open(matches[0], encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _find_normalized_text(format_id: str) -> Optional[Path]:
    """Find normalized/text.txt for a format.

    ROOT-07 fix: Also searches for RFC .txt files when normalized/text.txt
    is not found (e.g., zst/rfc8878/rfc8878.txt).
    """
    # Primary: standard normalized path
    matches = list(_SPEC_CACHE.glob(f"{format_id}/*/normalized/text.txt"))
    if matches:
        return matches[0]
    # Fallback: RFC text files (e.g., zst/rfc8878/rfc8878.txt)
    rfc_matches = list(_SPEC_CACHE.glob(f"{format_id}/*/*.txt"))
    if rfc_matches:
        return rfc_matches[0]
    return None


def _find_workbench_yaml(format_id: str) -> Optional[Path]:
    matches = list(_SPEC_CACHE.glob(f"{format_id}/*/workbench/verified-facts-review.yaml"))
    return matches[0] if matches else None


def _load_workbench(path: Path) -> Dict[str, Any]:
    if yaml is None:
        raise ImportError("PyYAML is required")
    if not path.exists():
        return {"facts": []}
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if "facts" not in data:
        data["facts"] = []
    return data


def _save_workbench(path: Path, data: Dict[str, Any]) -> None:
    if yaml is None:
        raise ImportError("PyYAML is required")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


def _existing_claim_ids(workbench_data: Dict[str, Any]) -> set:
    return {f.get("claim_id", "") for f in workbench_data.get("facts", [])}


def _next_ex_number(existing_ids: set, format_id: str) -> int:
    prefix = f"FACT-{format_id.upper()}-EX-"
    used = set()
    for cid in existing_ids:
        if cid.startswith(prefix):
            try:
                used.add(int(cid[len(prefix):]))
            except ValueError:
                pass
    n = 1
    while n in used:
        n += 1
    return n


def _scan_odf_xml_elements(text_path: Path) -> List[Dict[str, Any]]:
    """
    Scan ODF normalized text for XML element/attribute references.
    Returns a list of candidate dicts with req_id, section_id, text_fragment, keyword.
    """
    candidates: List[Dict[str, Any]] = []
    seen_fragments: set = set()

    lines = text_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    current_section = "section-unknown"

    for i, line in enumerate(lines):
        # Track section headings (lines starting with digits like "4.2 Table Cell")
        if re.match(r'^\d+[\.\d]* ', line.strip()):
            current_section = f"section-{line.strip()[:40].replace(' ', '-').lower()}"

        for pattern in _ODF_ELEMENT_PATTERNS:
            for match in pattern.finditer(line):
                qname = match.group(1)
                ns = qname.split(":")[0]
                if ns not in _ODF_NAMESPACES:
                    continue

                # Extract surrounding context (current line + next line)
                context_lines = lines[max(0, i):min(len(lines), i + 3)]
                text_fragment = " ".join(ln.strip() for ln in context_lines if ln.strip())
                text_fragment = text_fragment[:300]

                if text_fragment in seen_fragments:
                    continue
                seen_fragments.add(text_fragment)

                candidates.append({
                    "req_id": f"REQ-ODF-EX-{uuid.uuid4().hex[:8]}",
                    "section_id": current_section,
                    "heading": current_section.replace("-", " ").title(),
                    "text_fragment": text_fragment,
                    "keyword": qname,
                    "status": "candidate",
                    "extracted_at": _now_iso(),
                    "extra": {"pattern": pattern.pattern[:50]},
                })

                if len(candidates) >= _MAX_CANDIDATES_PER_FORMAT:
                    return candidates

    return candidates


def _extract_rfc2119(format_id: str, text_path: Path) -> List[Dict[str, Any]]:
    """
    For non-ODF formats with RFC 2119 language (e.g. ZST/RFC 8878).
    Scan flat text for MUST/SHALL/SHOULD/MAY patterns directly.
    """
    RFC2119_RE = re.compile(
        r'(MUST|SHALL|SHOULD|MAY|REQUIRED|OPTIONAL|must|shall|should)',
        re.IGNORECASE
    )
    candidates: List[Dict[str, Any]] = []
    seen: set = set()

    lines = text_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    current_section = "section-unknown"

    for i, line in enumerate(lines):
        if re.match(r'^\d+[\.\d]* ', line.strip()):
            current_section = f"section-{line.strip()[:40].replace(' ', '-').lower()}"

        for m in RFC2119_RE.finditer(line):
            context = " ".join(
                ln.strip() for ln in lines[max(0, i - 1):min(len(lines), i + 2)] if ln.strip()
            )
            fragment = context[:300]
            if fragment in seen:
                continue
            seen.add(fragment)

            candidates.append({
                "req_id": f"REQ-{format_id.upper()[:4]}-EX-{uuid.uuid4().hex[:8]}",
                "section_id": current_section,
                "heading": current_section.replace("-", " ").title(),
                "text_fragment": fragment,
                "keyword": m.group(1),
                "status": "candidate",
                "extracted_at": _now_iso(),
                "extra": {},
            })

            if len(candidates) >= _MAX_CANDIDATES_PER_FORMAT:
                return candidates

    return candidates


def run_pipeline(format_id: str, dry_run: bool = False) -> Dict[str, Any]:
    """Run full extraction pipeline for one format. Returns result dict."""
    print(f"\n[pipeline] format={format_id} dry_run={dry_run}")

    # Step 1: Discovery
    spec_index = _load_spec_index(format_id)
    if spec_index is None:
        return {"format_id": format_id, "status": "no_spec_index", "appended": 0}

    if spec_index.get("normalized_text_cached") is False:
        reason = spec_index.get("no_spec_text_reason", "unknown")
        print(f"  [SKIP] {format_id}: normalized_text_cached=false — {reason}")
        return {"format_id": format_id, "status": "no_spec_text", "reason": reason, "appended": 0}

    # Check for text.txt
    text_path = _find_normalized_text(format_id)
    if text_path is None:
        print(f"  [SKIP] {format_id}: no normalized/text.txt found")
        return {"format_id": format_id, "status": "no_text_file", "appended": 0}

    print(f"  [OK] Spec text found: {text_path} ({text_path.stat().st_size // 1024}KB)")

    # Step 2: Section index (optional — build if missing)
    index_file = _ARTIFACTS_DIR / f"{format_id}-spec-index.json"
    if not index_file.exists():
        print(f"  [INFO] Section index not found at {index_file}; skipping indexer step")

    # Step 3: Extraction (format-aware dispatch)
    if format_id in _ODF_FORMATS:
        print("  [EXTRACT] ODF format — using XML element/attribute scanner")
        candidates = _scan_odf_xml_elements(text_path)
    else:
        print("  [EXTRACT] Non-ODF format — using RFC 2119 scanner")
        candidates = _extract_rfc2119(format_id, text_path)

    print(f"  [EXTRACT] Found {len(candidates)} raw candidates")

    if not candidates:
        return {"format_id": format_id, "status": "no_candidates", "appended": 0}

    # Step 4: Load workbench and dedup
    workbench_path = _find_workbench_yaml(format_id)
    if workbench_path is None:
        version_dir = _SPEC_CACHE / format_id / "extracted" / "workbench"
        workbench_path = version_dir / "verified-facts-review.yaml"
        print(f"  [WARN] No workbench found; will create at {workbench_path}")

    workbench_data = _load_workbench(workbench_path)
    existing_ids = _existing_claim_ids(workbench_data)
    existing_claims = {f.get("claim", "")[:100] for f in workbench_data.get("facts", [])}

    # Step 5: Write candidates (dedup by text_fragment prefix)
    next_num = _next_ex_number(existing_ids, format_id)
    appended = 0
    skipped_dup = 0
    new_facts = []
    now_iso = _now_iso()

    for cand in candidates:
        fragment_key = cand["text_fragment"][:100]
        if fragment_key in existing_claims:
            skipped_dup += 1
            continue

        claim_id = f"FACT-{format_id.upper()}-EX-{next_num:04d}"
        fact = {
            "claim_id": claim_id,
            "claim": cand["text_fragment"],
            "verification_status": "pending_verification",
            "extraction_method": "automated_extraction",
            "validated_by": None,
            "validated_at": None,
            "provenance": {
                "section_id": cand["section_id"],
                "spec_id": f"{format_id}-normalized",
                "format_id": format_id,
                "section_heading": cand["heading"],
                "extraction_method": "xml_element_scan" if format_id in _ODF_FORMATS else "rfc2119_keyword_match",
                "extracted_at": cand["extracted_at"],
                "extra": {
                    "keyword": cand["keyword"],
                    "original_req_id": cand["req_id"],
                    **(cand.get("extra") or {}),
                },
            },
        }

        if dry_run:
            print(f"  [DRY-RUN] {claim_id}: {cand['keyword']} — {cand['text_fragment'][:80]}...")
        else:
            new_facts.append(fact)
            existing_ids.add(claim_id)
            existing_claims.add(fragment_key)

        appended += 1
        next_num += 1

    if not dry_run and new_facts:
        workbench_data["facts"].extend(new_facts)
        _save_workbench(workbench_path, workbench_data)
        print(f"  [OK] Appended {len(new_facts)} new facts to {workbench_path}")

    print(f"  [SUMMARY] appended={appended} skipped_dup={skipped_dup}")

    # Step 6: Trigger verification on new facts
    if not dry_run and appended > 0:
        print(f"  [VERIFY] Triggering run_fact_verification.py --format {format_id}")
        import subprocess
        verifier = Path(__file__).parent / "run_fact_verification.py"
        if verifier.exists():
            result = subprocess.run(
                [sys.executable, str(verifier), "--format", format_id],
                capture_output=True, text=True, cwd=str(_REPO)
            )
            if result.returncode == 0:
                print("  [VERIFY] Verification complete")
            else:
                print(f"  [VERIFY] Verification exited {result.returncode}: {result.stderr[:200]}")
        else:
            print("  [VERIFY] run_fact_verification.py not found; skipping")

    return {
        "format_id": format_id,
        "status": "ok",
        "text_path": str(text_path),
        "workbench_file": str(workbench_path),
        "candidates_found": len(candidates),
        "appended": appended,
        "skipped_dup": skipped_dup,
        "dry_run": dry_run,
    }


def _formats_with_spec_text() -> List[str]:
    """Return format_ids that have normalized/text.txt."""
    results = []
    for txt in _SPEC_CACHE.glob("*/*/normalized/text.txt"):
        format_id = txt.parts[-4]  # .local/spec-cache/{format_id}/{version}/normalized/text.txt
        results.append(format_id)
    return sorted(set(results))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="SAL extraction pipeline orchestrator."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--format", dest="format_id", help="Format ID to extract (e.g. fods)")
    group.add_argument("--all", action="store_true", help="Run for all formats with spec text")
    parser.add_argument("--dry-run", action="store_true", help="Print candidates without writing")
    args = parser.parse_args()

    _SAL_OUTPUT.mkdir(parents=True, exist_ok=True)

    if args.all:
        formats = _formats_with_spec_text()
        print(f"[pipeline] Running for formats with spec text: {formats}")
    else:
        formats = [args.format_id]

    results = []
    for fmt in formats:
        r = run_pipeline(fmt, dry_run=args.dry_run)
        results.append(r)

    report = {
        "generated_at": _now_iso(),
        "dry_run": args.dry_run,
        "formats_processed": len(formats),
        "results": results,
        "total_appended": sum(r.get("appended", 0) for r in results),
    }

    report_path = _SAL_OUTPUT / "extraction-pipeline-report.json"
    if not args.dry_run:
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"\n[pipeline] Report written to {report_path}")

    print(f"\n[pipeline] Total appended: {report['total_appended']}")
    print(json.dumps(report, indent=2))

    # Exit non-zero if no formats succeeded
    if not any(r.get("status") == "ok" for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
