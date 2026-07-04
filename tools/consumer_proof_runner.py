"""consumer_proof_runner.py — Run all 20 consumer roundtrip scripts and capture evidence.

TC-CPR-004 (sparkling-waddling-narwhal): Captures dated execution output so that
consumer proof obligations cite real script output, not just script file existence.

Usage:
    python tools/consumer_proof_runner.py [--formats fmt1,fmt2,...] [--output-dir PATH]

Outputs:
    .local/evidences/consumer-proof-{fmt}.txt   — stdout/stderr for each format
    .local/evidences/consumer-proof-manifest.json — per-format state, timestamp, pass/fail
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]

_ALL_FORMATS = [
    "abw", "csv", "dif", "fodg", "fodp", "fods", "fodt", "gnumeric",
    "ndjson", "ods", "odt", "pbm", "pgm", "ppm", "qoi", "sylk",
    "toml", "tsv", "xcf", "zst",
]

_SCRIPT_NAME = "consumer_roundtrip.py"


def _run_format(fmt: str, output_dir: Path, python: str) -> dict:
    """Run one consumer roundtrip script; capture stdout/stderr to file; return manifest entry."""
    script = _REPO / "examples" / "python" / fmt / _SCRIPT_NAME
    if not script.exists():
        result = {
            "pass": False,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": f"script not found: {script.relative_to(_REPO)}",
            "output_file": None,
        }
        return result

    out_file = output_dir / f"consumer-proof-{fmt}.txt"
    ts = datetime.now(timezone.utc).isoformat()

    try:
        proc = subprocess.run(
            [python, str(script)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(_REPO),
        )
        combined = proc.stdout + (("\n--- STDERR ---\n" + proc.stderr) if proc.stderr.strip() else "")
        out_file.write_text(combined, encoding="utf-8")

        passed = (
            proc.returncode == 0
            and "CONSUMER_PROOF: PASS" in proc.stdout
        )
        return {
            "pass": passed,
            "timestamp": ts,
            "returncode": proc.returncode,
            "output_file": str(out_file.relative_to(_REPO)),
            "error": None if passed else f"returncode={proc.returncode} or PASS sentinel missing",
        }
    except subprocess.TimeoutExpired:
        out_file.write_text(f"TIMEOUT after 60s\n", encoding="utf-8")
        return {
            "pass": False,
            "timestamp": ts,
            "error": "timeout after 60s",
            "output_file": str(out_file.relative_to(_REPO)),
        }
    except Exception as exc:
        return {
            "pass": False,
            "timestamp": ts,
            "error": str(exc),
            "output_file": None,
        }


def run(formats: list[str] | None = None, output_dir: Path | None = None, python: str | None = None) -> dict:
    """Run all (or selected) formats; return manifest dict."""
    fmts = formats or _ALL_FORMATS
    out_dir = output_dir or (_REPO / ".local" / "evidences")
    out_dir.mkdir(parents=True, exist_ok=True)

    py = python or sys.executable

    manifest: dict[str, dict] = {}
    total = len(fmts)
    passed = 0

    for fmt in fmts:
        entry = _run_format(fmt, out_dir, py)
        manifest[fmt] = entry
        status = "PASS" if entry["pass"] else "FAIL"
        print(f"  [{status}] {fmt}: {entry.get('error') or entry.get('output_file', '')}")
        if entry["pass"]:
            passed += 1

    manifest_path = out_dir / "consumer-proof-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"\nConsumer proof: {passed}/{total} PASS")
    print(f"Manifest: {manifest_path}")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Run consumer roundtrip proofs for all 20 formats.")
    parser.add_argument("--formats", help="Comma-separated format list (default: all 20)")
    parser.add_argument("--output-dir", help="Directory for output files (default: .local/evidences/)")
    parser.add_argument("--python", help="Python interpreter to use (default: current interpreter)")
    args = parser.parse_args()

    fmts = [f.strip() for f in args.formats.split(",")] if args.formats else None
    out_dir = Path(args.output_dir) if args.output_dir else None
    py = args.python

    manifest = run(formats=fmts, output_dir=out_dir, python=py)
    failures = [fmt for fmt, entry in manifest.items() if not entry["pass"]]
    if failures:
        print(f"FAILED formats: {failures}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
