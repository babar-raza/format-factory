"""
run_fact_verification.py — Deterministic spec text search verification runner.

Processes all pending_verification and needs_review facts that have a cached
normalized spec text, runs deterministic section-window text search against
that text, and updates their verification_status in-place.

Usage:
    python run_fact_verification.py [--format <id>] [--dry-run] [--calibrate]

Flags:
    --format <id>   Only process one format (e.g. fods, fodt)
    --dry-run       Print proposed changes without writing anything
    --calibrate     Only run against already-verified facts to measure precision
                    (must show ≥12/14 for FODS before batch is safe)

Exit codes:
    0   Success
    1   Calibration precision too low (<10 found out of known-verified set)
    2   Verified count decreased for any format after a batch run
    3   No spec text found for any format (all skipped)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SPEC_CACHE = _REPO_ROOT / ".local" / "spec-cache"
_SAL_OUTPUT = _REPO_ROOT / ".local" / "sal-output"

_PENDING_STATUSES = frozenset(["pending_verification", "needs_review"])
_VERIFIED_STATUSES = frozenset(["verified", "verified_with_note"])

# Stop words to skip when tokenizing claims
_STOP_WORDS = frozenset([
    "the", "and", "for", "that", "this", "with", "from", "are", "has",
    "have", "not", "into", "can", "will", "its", "which", "when",
    "each", "they", "their", "than", "only", "also",
])

# Minimum key term length
_MIN_TERM_LEN = 4

# Window size (lines) around found section header
_WINDOW_HALF = 50

# Score thresholds
_VERIFIED_THRESHOLD = 3       # ≥N key terms → verified
_PARTIAL_THRESHOLD = 1        # 1-2 key terms → verified_with_note


def _tokenize_claim(claim: str) -> list[str]:
    """Extract key terms from a claim string."""
    raw = re.split(r"[\s\(\),;:./\\]", claim)
    terms = []
    seen = set()
    for w in raw:
        w = w.strip().lower().rstrip(".])")
        if len(w) >= _MIN_TERM_LEN and w not in _STOP_WORDS and w not in seen:
            terms.append(w)
            seen.add(w)
    return terms


def _find_section_line(lines: list[str], section_id: str) -> int | None:
    """Find the first line index where section_id appears as a section header."""
    if not section_id:
        return None
    # Pattern: line starts with the section_id followed by whitespace or form feed only.
    # Do NOT include dot — "9.4.1 ..." should not match when searching for section "9.4".
    pattern = re.compile(r"^" + re.escape(section_id) + r"[\s\x0c]")
    # Search for the LAST occurrence (often better quality than TOC entries at start)
    found_idx = None
    for i, line in enumerate(lines):
        if pattern.match(line):
            found_idx = i
    return found_idx


def _score_claim(lines: list[str], section_line: int, terms: list[str]) -> tuple[str, list[str]]:
    """
    Score a claim against the text window around section_line.
    Returns (status_string, matched_terms).
    """
    start = max(0, section_line - _WINDOW_HALF)
    end = min(len(lines), section_line + _WINDOW_HALF + 1)
    window_text = " ".join(l.strip() for l in lines[start:end]).lower()

    matched = [t for t in terms if t in window_text]
    n = len(matched)

    if n >= _VERIFIED_THRESHOLD:
        return "verified", matched
    elif n >= _PARTIAL_THRESHOLD:
        return "verified_with_note", matched
    else:
        return "not_found_in_normalized_text", matched


def _load_review_yaml(path: Path) -> dict[str, Any]:
    """Load a verified-facts-review.yaml (JSON or YAML format)."""
    text = path.read_text(encoding="utf-8")
    if text.lstrip().startswith("{"):
        return json.loads(text)
    # YAML fallback
    try:
        import yaml  # type: ignore
        return yaml.safe_load(text) or {}
    except ImportError:
        raise RuntimeError(f"PyYAML required to parse YAML file: {path}")


def _save_review_yaml(path: Path, data: dict[str, Any]) -> None:
    """Save back in the original format (JSON if originally JSON)."""
    original_text = path.read_text(encoding="utf-8")
    if original_text.lstrip().startswith("{"):
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    else:
        try:
            import yaml  # type: ignore
            path.write_text(yaml.dump(data, allow_unicode=True, default_flow_style=False), encoding="utf-8")
        except ImportError:
            raise RuntimeError(f"PyYAML required to save YAML file: {path}")


def _find_normalized_text(cache_version_dir: Path) -> Path | None:
    """Find text.txt under the version directory.

    Checks in order:
      1. {version_dir}/normalized/text.txt  (FODS layout)
      2. {version_dir}/text.txt             (text directly in version dir)
      3. spec-index.yaml normalized_text_path field (cross-format shared specs, e.g. FODT→FODS)
      4. Walk up 3 parent levels checking both locations (fallback)
    """
    # Primary: FODS-style layout
    candidate = cache_version_dir / "normalized" / "text.txt"
    if candidate.is_file():
        return candidate
    # Secondary: text.txt directly in the version directory
    candidate = cache_version_dir / "text.txt"
    if candidate.is_file():
        return candidate
    # Tertiary: check spec-index.yaml for a normalized_text_path cross-reference
    spec_index = cache_version_dir / "spec-index.yaml"
    if spec_index.is_file():
        try:
            import yaml  # type: ignore
            index_data = yaml.safe_load(spec_index.read_text(encoding="utf-8")) or {}
        except Exception:
            index_data = {}
        ntp = index_data.get("normalized_text_path")
        if ntp:
            candidate = (cache_version_dir / ntp).resolve()
            if candidate.is_file():
                return candidate
    # Walk up parents
    parent = cache_version_dir.parent
    for _ in range(3):
        candidate = parent / "normalized" / "text.txt"
        if candidate.is_file():
            return candidate
        candidate = parent / "text.txt"
        if candidate.is_file():
            return candidate
        parent = parent.parent
    return None


def _workbench_dir_to_version_dir(workbench_file: Path) -> Path:
    """Given .../workbench/verified-facts-review.yaml, return the version dir."""
    return workbench_file.parent.parent


def _count_verified(facts: list[dict]) -> int:
    """Count facts with verified or verified_with_note status."""
    count = 0
    for f in facts:
        prov = f.get("provenance", {}) or {}
        vstat = f.get("verification_status") or prov.get("verification_status", "")
        if vstat in _VERIFIED_STATUSES:
            count += 1
    return count


def _process_format(
    review_file: Path,
    format_id: str,
    dry_run: bool,
    calibrate: bool,
    lines_cache: dict[Path, list[str]],
) -> dict[str, Any]:
    """
    Process one verified-facts-review.yaml file.
    Returns a result dict with counts.
    """
    data = _load_review_yaml(review_file)
    facts = data.get("facts", [])

    version_dir = _workbench_dir_to_version_dir(review_file)
    text_path = _find_normalized_text(version_dir)

    result: dict[str, Any] = {
        "format_id": format_id,
        "review_file": str(review_file),
        "text_path": str(text_path) if text_path else None,
        "total_facts": len(facts),
        "pre_verified": _count_verified(facts),
        "checked": 0,
        "promoted_verified": 0,
        "promoted_verified_with_note": 0,
        "not_found": 0,
        "skipped_no_text": 0,
        "skipped_no_section_id": 0,
        "skipped_no_terms": 0,
        "calibration_found": 0,
        "calibration_total": 0,
        "changes": [],
    }

    if text_path is None:
        result["skipped_no_text"] = len(facts)
        print(f"  [{format_id}] No normalized text.txt found at {version_dir / 'normalized'} — skipping",
              file=sys.stderr)
        return result

    # Load text lines (cache by path)
    if text_path not in lines_cache:
        with open(text_path, encoding="utf-8", errors="replace") as fh:
            lines_cache[text_path] = fh.readlines()
    lines = lines_cache[text_path]

    if calibrate:
        # Only evaluate already-verified facts; don't modify anything
        target_facts = [f for f in facts
                        if (f.get("provenance", {}) or {}).get("verification_status") in _VERIFIED_STATUSES
                        or f.get("verification_status") in _VERIFIED_STATUSES]
        result["calibration_total"] = len(target_facts)
    else:
        target_facts = [f for f in facts
                        if ((f.get("provenance", {}) or {}).get("verification_status") in _PENDING_STATUSES
                            or f.get("verification_status") in _PENDING_STATUSES)]

    for fact in target_facts:
        prov = fact.get("provenance", {}) or {}
        section_id = prov.get("section_id", "") or fact.get("section_id", "")
        claim = fact.get("claim", "")
        claim_id = fact.get("claim_id", "?")

        if not section_id:
            result["skipped_no_section_id"] += 1
            continue

        terms = _tokenize_claim(claim)
        if not terms:
            result["skipped_no_terms"] += 1
            continue

        section_line = _find_section_line(lines, section_id)
        if section_line is None:
            if calibrate:
                print(f"    CALIBRATE MISS {claim_id}: section {section_id!r} not found in text",
                      file=sys.stderr)
            else:
                result["not_found"] += 1
            continue

        status, matched = _score_claim(lines, section_line, terms)
        result["checked"] += 1

        if calibrate:
            if status in _VERIFIED_STATUSES or status == "verified":
                result["calibration_found"] += 1
                print(f"    CALIBRATE HIT  {claim_id}: {len(matched)}/{len(terms)} terms matched", file=sys.stderr)
            else:
                print(f"    CALIBRATE MISS {claim_id}: {len(matched)}/{len(terms)} terms, status={status}",
                      file=sys.stderr)
            continue

        if status == "not_found_in_normalized_text":
            result["not_found"] += 1
            continue

        # Record change
        today = date.today().isoformat()
        change = {
            "claim_id": claim_id,
            "old_status": prov.get("verification_status") or fact.get("verification_status", "?"),
            "new_status": status,
            "matched_terms": matched,
            "term_count": len(matched),
            "total_terms": len(terms),
            "section_line": section_line + 1,
        }
        result["changes"].append(change)

        if status == "verified":
            result["promoted_verified"] += 1
        else:
            result["promoted_verified_with_note"] += 1

        if not dry_run:
            # Apply update in-place to provenance
            prov["verification_status"] = status
            prov["validated_by"] = "deterministic_spec_text_search"
            prov["validated_at"] = today
            prov["verification_evidence"] = (
                f"Section {section_id} found at text line {section_line + 1}; "
                f"{len(matched)}/{len(terms)} key terms matched: {matched}"
            )

    if calibrate:
        return result

    if not dry_run and result["changes"]:
        _save_review_yaml(review_file, data)

    result["post_verified"] = _count_verified(
        _load_review_yaml(review_file).get("facts", []) if not dry_run else facts
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic SAL fact verification runner")
    parser.add_argument("--format", dest="format_id", help="Only process one format (e.g. fods)")
    parser.add_argument("--dry-run", action="store_true", help="Print changes without writing")
    parser.add_argument("--calibrate", action="store_true",
                        help="Run against already-verified facts to measure precision")
    args = parser.parse_args()

    _SAL_OUTPUT.mkdir(parents=True, exist_ok=True)

    # Discover all workbench review files
    if args.format_id:
        pattern = f"{args.format_id.lower()}/*/workbench/verified-facts-review.yaml"
    else:
        pattern = "*/*/workbench/verified-facts-review.yaml"

    review_files = sorted(_SPEC_CACHE.glob(pattern))
    if not review_files:
        print(f"No verified-facts-review.yaml files found under {_SPEC_CACHE} with pattern: {pattern}",
              file=sys.stderr)
        return 3

    lines_cache: dict[Path, list[str]] = {}
    all_results = []
    any_text_found = False

    for review_file in review_files:
        # Infer format_id from path: .local/spec-cache/{format_id}/{version}/workbench/...
        fmt = review_file.parts[-4]  # format_id is 4 levels up from filename
        print(f"\n[{fmt}] Processing {review_file.name} ...", file=sys.stderr)

        res = _process_format(review_file, fmt, args.dry_run, args.calibrate, lines_cache)
        all_results.append(res)

        if res["text_path"] is not None:
            any_text_found = True

        if args.calibrate:
            total = res["calibration_total"]
            found = res["calibration_found"]
            print(f"  [{fmt}] Calibration: {found}/{total} verified facts found in spec text", file=sys.stderr)
        else:
            print(f"  [{fmt}] Checked: {res['checked']}, "
                  f"Promoted verified: {res['promoted_verified']}, "
                  f"Verified_with_note: {res['promoted_verified_with_note']}, "
                  f"Not found: {res['not_found']}, "
                  f"No text: {res['skipped_no_text']}",
                  file=sys.stderr)
            if args.dry_run:
                for ch in res["changes"]:
                    print(f"    DRY-RUN {ch['claim_id']}: {ch['old_status']} → {ch['new_status']} "
                          f"({ch['term_count']}/{ch['total_terms']} terms)", file=sys.stderr)

    if not any_text_found:
        print("ERROR: No normalized spec text found for any format.", file=sys.stderr)
        return 3

    # Write report
    if args.calibrate:
        report_path = _SAL_OUTPUT / "fact-verification-calibration.json"
        report = {
            "mode": "calibration",
            "dry_run": False,
            "formats": [
                {
                    "format_id": r["format_id"],
                    "calibration_total": r["calibration_total"],
                    "calibration_found": r["calibration_found"],
                    "precision": (
                        round(r["calibration_found"] / r["calibration_total"], 3)
                        if r["calibration_total"] > 0 else 0
                    ),
                }
                for r in all_results
            ],
        }
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"\nCalibration report: {report_path}", file=sys.stderr)

        # Check precision gate
        for r in all_results:
            if r["calibration_total"] > 0:
                found = r["calibration_found"]
                total = r["calibration_total"]
                fmt = r["format_id"]
                print(f"\n[{fmt}] Calibration precision: {found}/{total} "
                      f"({100*found/total:.0f}%)", file=sys.stderr)
                if found < 10:
                    print(f"ERROR: Calibration precision too low for {fmt} ({found}/{total} < 10). "
                          "Do NOT run batch verification. Tune algorithm first.", file=sys.stderr)
                    return 1
        return 0

    # Non-calibrate: write full report
    report_path = _SAL_OUTPUT / "fact-verification-report.json"
    report = {
        "mode": "batch",
        "dry_run": args.dry_run,
        "formats": [
            {
                "format_id": r["format_id"],
                "total_facts": r["total_facts"],
                "pre_verified": r["pre_verified"],
                "post_verified": r.get("post_verified", r["pre_verified"]),
                "checked": r["checked"],
                "promoted_verified": r["promoted_verified"],
                "promoted_verified_with_note": r["promoted_verified_with_note"],
                "not_found": r["not_found"],
                "skipped_no_text": r["skipped_no_text"],
                "changes": r["changes"],
            }
            for r in all_results
        ],
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nReport: {report_path}", file=sys.stderr)

    # Check for decreased verified counts
    if not args.dry_run:
        for r in all_results:
            pre = r["pre_verified"]
            post = r.get("post_verified", pre)
            fmt = r["format_id"]
            if post < pre:
                print(f"ERROR: Verified count DECREASED for {fmt}: {pre} → {post}. "
                      "Something went wrong — check YAML integrity.", file=sys.stderr)
                return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
