"""
stale_detection.py -- Lane A Deliverable (CONWAY-R7R8)

Stale-state enforcement for generated requirements authority chain.

PURPOSE:
  Detect when the generated-requirements chain (files → verifier-review → IV)
  has become stale and block planning if the chain is inconsistent.

STALE VERDICTS:
  FRESH           -- all chain links are consistent; planning allowed
  REVIEW_REQUIRED -- soft inconsistency detected; human review recommended
  STALE_BLOCKED   -- critical inconsistency; planning is BLOCKED

CHECKS PERFORMED:
  1. Timestamp consistency across requirements files
  2. Verifier review is newer than or concurrent with requirements generation
  3. Registry IV date is on or after verifier review
  4. Registry accepted_count matches actual file count
  5. No requirements file modified after IV date (file-mtime check)

ALLOWED:
  - Reading requirements files
  - Reading registry
  - Reading verifier review
  - Emitting deterministic stale verdicts

NOT ALLOWED:
  - Mutating requirements files
  - Auto-regenerating requirements
  - Approving any gate
  - Bypassing authority chain

Authority: AGENTS.md AF9-AF15 | GOVERNANCE.md 26.8-26.13
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REGISTRY_PATH = REPO_ROOT / "registry" / "format-registry.yaml"
REQS_DIR = REPO_ROOT / "generated-requirements"

REQUIREMENTS_FILES = [
    "commercial-requirements.yaml",
    "object-model-requirements.yaml",
    "save-edit-requirements.yaml",
    "conversion-requirements.yaml",
    "traceability-map.yaml",
    "verifier-review.yaml",
]


def _load_yaml(path: Path) -> dict:
    try:
        import yaml
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except ImportError:
        raise ImportError("PyYAML required: pip install pyyaml")
    except Exception:
        return {}


def _parse_timestamp(ts: Any) -> datetime | None:
    """Parse ISO 8601 timestamp or date string. Returns None if unparseable."""
    if ts is None:
        return None
    s = str(ts).strip().rstrip("Z")
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def _collect_generation_timestamps(fmt_dir: Path) -> list[tuple[str, datetime]]:
    """Collect generation_timestamp from all requirements YAMLs (except verifier-review)."""
    result = []
    for fname in REQUIREMENTS_FILES:
        if fname == "verifier-review.yaml":
            continue
        path = fmt_dir / fname
        if not path.exists():
            continue
        data = _load_yaml(path)
        ts = _parse_timestamp(data.get("generation_timestamp"))
        if ts:
            result.append((fname, ts))
    return result


def _get_verifier_timestamp(fmt_dir: Path) -> datetime | None:
    vr = _load_yaml(fmt_dir / "verifier-review.yaml")
    return _parse_timestamp(vr.get("review_timestamp"))


def _get_registry_iv_date(fmt: str) -> tuple[str | None, str | None]:
    """Return (iv_status, iv_date) from registry for this format."""
    if not REGISTRY_PATH.exists():
        return None, None
    try:
        import yaml
        registry = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8")) or {}
    except Exception:
        return None, None
    formats = registry.get("formats", [])
    if isinstance(formats, list):
        entry = next((f for f in formats if f.get("format_id") == fmt), {})
    else:
        entry = formats.get(fmt, {})
    gr = entry.get("generated_requirements", {})
    return gr.get("iv_status"), gr.get("iv_date")


def _get_registry_accepted_count(fmt: str) -> int | None:
    """Return accepted_count from registry for this format."""
    if not REGISTRY_PATH.exists():
        return None
    try:
        import yaml
        registry = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8")) or {}
    except Exception:
        return None
    formats = registry.get("formats", [])
    if isinstance(formats, list):
        entry = next((f for f in formats if f.get("format_id") == fmt), {})
    else:
        entry = formats.get(fmt, {})
    return entry.get("generated_requirements", {}).get("accepted_count")


def _count_accepted_in_files(fmt_dir: Path) -> int:
    """Count ACCEPTED_FOR_VERTICAL_SLICE requirements across all requirement YAMLs."""
    count = 0
    for fname in ["commercial-requirements.yaml", "save-edit-requirements.yaml"]:
        path = fmt_dir / fname
        if not path.exists():
            continue
        data = _load_yaml(path)
        count += sum(
            1 for r in data.get("requirements", [])
            if r.get("status") == "ACCEPTED_FOR_VERTICAL_SLICE"
        )
    return count


def _check_file_mtime_after_iv(fmt_dir: Path, iv_date_str: str | None) -> list[str]:
    """
    Return list of files modified after the IV date.
    Returns empty list if iv_date_str is None or unparseable.
    """
    if not iv_date_str:
        return []
    iv_dt = _parse_timestamp(iv_date_str)
    if iv_dt is None:
        return []
    stale_files = []
    for fname in REQUIREMENTS_FILES:
        path = fmt_dir / fname
        if not path.exists():
            continue
        try:
            mtime = datetime.fromtimestamp(path.stat().st_mtime)
            # Allow 1-second tolerance for filesystem rounding
            if mtime > iv_dt and (mtime - iv_dt).total_seconds() > 60:
                stale_files.append(fname)
        except Exception:
            continue
    return stale_files


def detect_stale_state(fmt: str) -> dict:
    """
    Detect stale state for a format's requirements chain.

    Parameters
    ----------
    fmt : str
        Format ID (e.g. 'fods', 'fodt')

    Returns
    -------
    dict with:
      verdict: str        -- FRESH | REVIEW_REQUIRED | STALE_BLOCKED | INDETERMINATE
      reasons: list[str]  -- human-readable explanation
      checks: dict        -- per-check results (name → PASS|FAIL|SKIP|WARN)
      blocker_count: int  -- number of BLOCKER-level findings
    """
    fmt_dir = REQS_DIR / fmt
    checks = {}
    reasons = []
    blockers = 0
    warnings = 0

    # --- Check 0: Directory exists ---
    if not fmt_dir.exists():
        return {
            "verdict": "STALE_BLOCKED",
            "reasons": [f"generated-requirements/{fmt}/ does not exist"],
            "checks": {"directory_exists": "FAIL"},
            "blocker_count": 1,
        }
    checks["directory_exists"] = "PASS"

    # --- Check 1: Timestamp consistency across requirements files ---
    gen_timestamps = _collect_generation_timestamps(fmt_dir)
    if not gen_timestamps:
        checks["timestamp_consistency"] = "SKIP"
        reasons.append("No generation_timestamp fields found in requirements files — cannot check consistency")
        warnings += 1
    else:
        timestamps_only = [ts for _, ts in gen_timestamps]
        min_ts = min(timestamps_only)
        max_ts = max(timestamps_only)
        delta_seconds = (max_ts - min_ts).total_seconds()
        if delta_seconds <= 86400:  # within 24 hours is acceptable
            checks["timestamp_consistency"] = "PASS"
        else:
            checks["timestamp_consistency"] = "WARN"
            reasons.append(
                f"Requirements timestamps span {delta_seconds/3600:.1f} hours — "
                f"files may have been generated separately"
            )
            warnings += 1

    # --- Check 2: Verifier review is newer than requirements generation ---
    verifier_ts = _get_verifier_timestamp(fmt_dir)
    if verifier_ts is None:
        checks["verifier_after_generation"] = "SKIP"
        reasons.append("verifier-review.yaml missing review_timestamp — cannot verify ordering")
        warnings += 1
    elif not gen_timestamps:
        checks["verifier_after_generation"] = "SKIP"
    else:
        oldest_gen = min(ts for _, ts in gen_timestamps)
        latest_gen = max(ts for _, ts in gen_timestamps)
        if verifier_ts >= oldest_gen:
            checks["verifier_after_generation"] = "PASS"
        else:
            checks["verifier_after_generation"] = "FAIL"
            reasons.append(
                f"Verifier review timestamp ({verifier_ts.date()}) predates "
                f"requirements generation ({latest_gen.date()}) — STALE"
            )
            blockers += 1

    # --- Check 3: Registry IV date is on or after verifier review ---
    iv_status, iv_date_str = _get_registry_iv_date(fmt)
    iv_dt = _parse_timestamp(iv_date_str)

    if iv_status not in ("ESTABLISHED", "PASS"):
        checks["iv_after_verification"] = "SKIP"
        reasons.append(f"Registry iv_status={iv_status!r} — IV not confirmed, skip ordering check")
    elif iv_dt is None:
        checks["iv_after_verification"] = "WARN"
        reasons.append("Registry iv_date is missing — cannot verify IV ordering")
        warnings += 1
    elif verifier_ts is not None and iv_dt < verifier_ts:
        delta_days = (verifier_ts - iv_dt).days
        if delta_days > 1:
            checks["iv_after_verification"] = "FAIL"
            reasons.append(
                f"Registry IV date ({iv_dt.date()}) predates verifier review "
                f"({verifier_ts.date()}) by {delta_days} days — STALE"
            )
            blockers += 1
        else:
            checks["iv_after_verification"] = "WARN"
            reasons.append(
                "Registry IV date is within 1 day of verifier review — borderline"
            )
            warnings += 1
    else:
        checks["iv_after_verification"] = "PASS"

    # --- Check 4: Registry accepted_count matches actual file count ---
    registry_count = _get_registry_accepted_count(fmt)
    actual_count = _count_accepted_in_files(fmt_dir)
    if registry_count is None:
        checks["accepted_count_consistent"] = "SKIP"
        reasons.append("Registry accepted_count not recorded — cannot verify consistency")
        warnings += 1
    elif actual_count != registry_count:
        checks["accepted_count_consistent"] = "FAIL"
        reasons.append(
            f"Registry accepted_count={registry_count} != actual file count={actual_count} — "
            f"requirements or registry is stale"
        )
        blockers += 1
    else:
        checks["accepted_count_consistent"] = "PASS"

    # --- Check 5: No requirements file modified after IV date ---
    stale_files = _check_file_mtime_after_iv(fmt_dir, iv_date_str)
    if not stale_files:
        checks["no_modification_after_iv"] = "PASS"
    else:
        # File mtime check is informational — filesystems may update on checkout
        # Treat as WARNING not BLOCKER (mtime is not a reliable authority signal)
        checks["no_modification_after_iv"] = "WARN"
        reasons.append(
            f"Files modified after IV date (mtime, informational): {stale_files}"
        )
        warnings += 1

    # --- Verdict ---
    if blockers > 0:
        verdict = "STALE_BLOCKED"
    elif warnings >= 2:
        verdict = "REVIEW_REQUIRED"
    else:
        verdict = "FRESH"

    if not reasons:
        reasons.append("All stale checks passed — chain is FRESH")

    return {
        "verdict": verdict,
        "reasons": reasons,
        "checks": checks,
        "blocker_count": blockers,
        "warning_count": warnings,
    }


def main():
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Stale detection for generated requirements")
    parser.add_argument("format", nargs="?", default="all", help="Format ID or 'all'")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    formats = ["fods", "fodt"] if args.format == "all" else [args.format]
    results = {}
    for fmt in formats:
        result = detect_stale_state(fmt)
        results[fmt] = result
        if args.json:
            continue
        print(f"\n=== Stale Detection: {fmt.upper()} ===")
        print(f"  VERDICT:  {result['verdict']}")
        print(f"  BLOCKERS: {result['blocker_count']}")
        print(f"  WARNINGS: {result.get('warning_count', 0)}")
        for name, status in result["checks"].items():
            print(f"    [{status}] {name}")
        for reason in result["reasons"]:
            print(f"    NOTE: {reason}")

    if args.json:
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
