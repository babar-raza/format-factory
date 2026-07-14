"""run_manager.py — Atomic certification run concept.

TC-002 (precious-wandering-lighthouse, 2026-07-13)

A certification run groups all 9 dimension reports for a format under a single
run_id, preventing hybrid verdicts caused by partial reruns at different source
revisions. The dashboard reads run manifests to determine which reports are "current"
for each format.

Functions:
  generate_run_id() -> str
  compute_source_revision() -> str
  write_run_manifest(run_id, format_id, source_revision, tools_run, reports_written) -> Path
  get_latest_run_manifest(format_id) -> dict | None
  create_synthetic_initial_manifest(format_id) -> Path
"""
from __future__ import annotations

import json
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_CERT_ROOT = _REPO_ROOT / "reports" / "certification"
_RUNS_ROOT = _CERT_ROOT / "runs"

_DIMENSION_REPORT_NAMES = [
    "api-contract.json",
    "traceability-audit.json",
    "stub-audit.json",
    "exception-audit.json",
    "oracle-alignment.json",
    "assertion-quality.json",
    "roundtrip-audit.json",
    "package-proof.json",
    "consumer-proof.json",
]


def generate_run_id() -> str:
    """Generate a unique, sortable run ID per invocation."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    short_uuid = uuid.uuid4().hex[:8]
    return f"cert-run-{ts}-{short_uuid}"


def compute_source_revision(source_paths: "list[Path] | None" = None) -> str:
    """Return the current git HEAD SHA or UNAVAILABLE as fallback."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=_REPO_ROOT,
            timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "UNAVAILABLE"


def write_run_manifest(
    run_id: str,
    format_id: str,
    source_revision: str,
    tools_run: list[str],
    reports_written: list[str],
) -> Path:
    """Write a run manifest JSON to reports/certification/runs/{run_id}/{format_id}-manifest.json.

    Args:
        run_id: Unique ID for this certification run (from generate_run_id())
        format_id: Format being certified (e.g. "fods", "csv")
        source_revision: git SHA at time of run
        tools_run: List of certification tool names invoked in this run
        reports_written: List of relative paths to reports written in this run

    Returns:
        Path to the written manifest file.
    """
    manifest: dict[str, Any] = {
        "run_id": run_id,
        "format_id": format_id,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "source_revision": source_revision,
        "tools_run": tools_run,
        "reports_written": reports_written,
        "is_synthetic": False,
    }
    dest = _RUNS_ROOT / run_id / f"{format_id}-manifest.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return dest


def get_latest_run_manifest(format_id: str) -> "dict | None":
    """Find the most recent complete run manifest for a given format.

    "Complete" means all reports_written paths exist on disk.
    Returns the manifest dict, or None if no runs exist for this format.
    """
    if not _RUNS_ROOT.exists():
        return None

    candidates: list[tuple[str, Path]] = []
    for run_dir in _RUNS_ROOT.iterdir():
        if not run_dir.is_dir():
            continue
        mf_path = run_dir / f"{format_id}-manifest.json"
        if mf_path.exists():
            candidates.append((run_dir.name, mf_path))

    if not candidates:
        return None

    # Sort by run_id (which is timestamp-prefixed, so lexicographic = chronological)
    candidates.sort(key=lambda x: x[0], reverse=True)

    for run_id, mf_path in candidates:
        try:
            manifest = json.loads(mf_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        # Check completeness: all reported paths must exist on disk
        all_present = all(
            (_REPO_ROOT / rp).exists() for rp in manifest.get("reports_written", [])
        )
        if all_present:
            return manifest

    return None


def create_synthetic_initial_manifest(format_id: str) -> Path:
    """Group all existing reports for a format into a synthetic initial run manifest.

    This prevents immediate breakage when run_manager is introduced — existing
    reports predate the run model and would otherwise appear as MISSING_EVIDENCE.
    The synthetic run is marked with run_id="cert-initial-crispy-jingling-snail"
    and source_revision="pre-run-model".

    Returns the path to the synthetic manifest.
    """
    _INITIAL_RUN_ID = "cert-initial-crispy-jingling-snail"
    fmt_dir = _CERT_ROOT / format_id
    reports_written: list[str] = []

    if fmt_dir.is_dir():
        for report_name in _DIMENSION_REPORT_NAMES:
            rp = fmt_dir / report_name
            if rp.exists():
                reports_written.append(f"reports/certification/{format_id}/{report_name}")

    manifest: dict[str, Any] = {
        "run_id": _INITIAL_RUN_ID,
        "format_id": format_id,
        "started_at": "2026-07-01T00:00:00Z",
        "source_revision": "pre-run-model",
        "tools_run": list({r.split("/")[-1].replace(".json", "") for r in reports_written}),
        "reports_written": reports_written,
        "is_synthetic": True,
        "note": "Synthetic manifest grouping reports that predate the run model. "
                "Regenerate with a full certification run to obtain a real manifest.",
    }
    dest = _RUNS_ROOT / _INITIAL_RUN_ID / f"{format_id}-manifest.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return dest


def bootstrap_initial_manifests(formats: "list[str] | None" = None) -> list[Path]:
    """Create synthetic initial manifests for all (or specified) formats.

    Safe to re-run — skips manifests that already exist.
    """
    if formats is None:
        # Discover formats from reports/certification/ directory
        formats = [
            d.name for d in _CERT_ROOT.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]

    created: list[Path] = []
    for fmt in sorted(formats):
        existing = get_latest_run_manifest(fmt)
        if existing is not None:
            continue  # Already has a manifest
        dest = create_synthetic_initial_manifest(fmt)
        created.append(dest)
    return created


if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "bootstrap":
        fmts = sys.argv[2:] or None
        paths = bootstrap_initial_manifests(fmts)
        print(f"Created {len(paths)} synthetic initial manifests")
        for p in paths:
            print(f"  {p}")
    elif cmd == "generate-run-id":
        print(generate_run_id())
    elif cmd == "source-revision":
        print(compute_source_revision())
    elif cmd == "latest":
        fmt = sys.argv[2] if len(sys.argv) > 2 else ""
        if not fmt:
            print("Usage: run_manager.py latest <format_id>", file=sys.stderr)
            sys.exit(1)
        m = get_latest_run_manifest(fmt)
        print(json.dumps(m, indent=2) if m else "null")
    else:
        print("Commands: bootstrap [fmt...] | generate-run-id | source-revision | latest <fmt>")
