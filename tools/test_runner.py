#!/usr/bin/env python3
"""Format Factory layered test runner.

Selects and runs the appropriate pytest layer for a given change scope.
Outputs structured JSON compatible with evidence-declaration.yaml.

Usage:
    python tools/test_runner.py --layer 0                  # explicit layer
    python tools/test_runner.py --auto                     # auto-detect from git diff
    python tools/test_runner.py --auto --format tsv        # hint: specific format
    python tools/test_runner.py --layer 6 --shard 1/4      # sharded full suite
    python tools/test_runner.py --layer 1 --dry-run        # print command only
    python tools/test_runner.py --layer 3 --json-out r.json
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from fnmatch import fnmatch
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "registry" / "test-layer-manifest.yaml"

LAYER_NAMES = {
    0: "structural",
    1: "focused",
    2: "family",
    3: "integration",
    4: "golden",
    5: "broad",
    6: "full",
}

SHARD_MAP = {
    1: {"path": "tests/python/", "ignore": []},
    2: {"path": "tests/supervisor/", "ignore": []},
    3: {"path": "tests/evidence/", "ignore": []},
    4: {
        "path": "tests/",
        "ignore": ["tests/python", "tests/supervisor", "tests/evidence"],
    },
}


def load_manifest(path: Path | None = None) -> dict:
    """Load the test-layer-manifest.yaml."""
    path = path or MANIFEST_PATH
    try:
        import yaml
        with open(path) as f:
            return yaml.safe_load(f)
    except ImportError:
        # Fallback: parse just enough YAML for change_impact rules
        # If PyYAML is missing, use a minimal hardcoded default
        return _fallback_manifest()


def _fallback_manifest() -> dict:
    """Minimal manifest when PyYAML is unavailable."""
    return {
        "layers": {f"layer{i}": {"name": LAYER_NAMES[i]} for i in range(7)},
        "format_families": {
            "netpbm": ["pbm", "pgm", "ppm"],
            "opendocument_spreadsheet": ["fods", "ods"],
            "opendocument_text": ["fodt", "odt", "abw"],
            "opendocument_graphics": ["fodg"],
            "tabular": ["csv", "tsv", "sylk", "dif", "gnumeric"],
            "image": ["pbm", "pgm", "ppm", "qoi", "xcf"],
            "archive": ["zst"],
            "structured": ["ndjson", "toml"],
        },
        "change_impact": [
            {"pattern": "docs/**", "min_layer": 0},
            {"pattern": "reports/**", "min_layer": 0},
            {"pattern": "plans/**", "min_layer": 0},
            {"pattern": "*.md", "min_layer": 0},
            {"pattern": "src/python/**", "min_layer": 1},
            {"pattern": "tests/python/*/test_*.py", "min_layer": 1},
            {"pattern": "tools/supervisor/**", "min_layer": 3},
            {"pattern": "tools/ai/**", "min_layer": 3},
            {"pattern": "tests/supervisor/**", "min_layer": 3},
            {"pattern": "tests/evidence/**", "min_layer": 3},
            {"pattern": "tests/capability_layer/**", "min_layer": 3},
            {"pattern": "registry/**", "min_layer": 3},
            {"pattern": "schemas/**", "min_layer": 3},
            {"pattern": "tools/*", "min_layer": 5},
            {"pattern": "tests/python/conftest.py", "min_layer": 5},
            {"pattern": "src/net/**", "min_layer": 5},
            {"pattern": "pyproject.toml", "min_layer": 6},
            {"pattern": ".github/**", "min_layer": 6},
            {"pattern": "tests/conftest.py", "min_layer": 6},
            {"pattern": "_default", "min_layer": 6},
        ],
    }


def detect_changed_files(base_ref: str = "HEAD") -> list[str]:
    """Detect changed files via git diff."""
    # Try staged + unstaged vs base_ref
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", base_ref],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        files = [f.strip() for f in result.stdout.strip().splitlines() if f.strip()]
    except (subprocess.SubprocessError, FileNotFoundError):
        files = []

    # Also include untracked files
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--cached"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        staged = [f.strip() for f in result.stdout.strip().splitlines() if f.strip()]
        files = list(set(files + staged))
    except (subprocess.SubprocessError, FileNotFoundError):
        pass

    # Also get unstaged changes
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        unstaged = [f.strip() for f in result.stdout.strip().splitlines() if f.strip()]
        files = list(set(files + unstaged))
    except (subprocess.SubprocessError, FileNotFoundError):
        pass

    return sorted(files)


def resolve_formats_from_paths(changed_files: list[str]) -> set[str]:
    """Extract format names from changed file paths."""
    formats = set()
    for f in changed_files:
        parts = f.replace("\\", "/").split("/")
        # src/python/{format}/... or tests/python/{format}/...
        if len(parts) >= 3 and parts[0] in ("src", "tests") and parts[1] == "python":
            fmt = parts[2]
            if fmt not in ("conftest.py", "__pycache__") and not fmt.startswith("test_"):
                formats.add(fmt)
    return formats


def resolve_family(fmt: str, manifest: dict) -> set[str]:
    """Expand a format to its family members."""
    families = manifest.get("format_families", {})
    result = {fmt}
    for _family_name, members in families.items():
        if fmt in members:
            result.update(members)
    return result


def compute_min_layer(
    changed_files: list[str], manifest: dict
) -> tuple[int, str]:
    """Walk change-impact rules, return (max_min_layer, reason)."""
    rules = manifest.get("change_impact", [])
    max_layer = -1
    reason = "no changed files detected"

    if not changed_files:
        return 0, reason

    for f in changed_files:
        f_norm = f.replace("\\", "/")
        matched = False
        for rule in rules:
            pat = rule["pattern"]
            if pat == "_default":
                if not matched:
                    layer = rule["min_layer"]
                    if layer > max_layer:
                        max_layer = layer
                        reason = f"{f_norm} matched default rule"
                break
            if fnmatch(f_norm, pat):
                layer = rule["min_layer"]
                if layer > max_layer:
                    max_layer = layer
                    reason = f"{f_norm} matched pattern '{pat}'"
                matched = True
                break
        if not matched:
            # No pattern matched — use default (layer 6)
            if 6 > max_layer:
                max_layer = 6
                reason = f"{f_norm} matched no pattern (default: layer 6)"

    return max(0, max_layer), reason


def build_marker_expr(layer: int) -> str:
    """Build cumulative marker expression for the given layer."""
    if layer >= 6:
        return ""  # No filter needed — run everything
    parts = [f"layer{i}" for i in range(layer + 1)]
    return " or ".join(parts)


_LAYER0_FILES = [
    "tests/test_health_check.py",
    "tests/python/test_pige_public_api_smoke.py",
]


def build_pytest_cmd(
    layer: int,
    formats: set[str] | None = None,
    shard: tuple[int, int] | None = None,
    verbose: bool = False,
    junitxml_path: str | None = None,
) -> list[str]:
    """Construct the pytest command for the given layer and options."""
    python_exe = sys.executable
    cmd = [python_exe, "-m", "pytest"]

    # Fast-path: L0 uses explicit file paths (no marker, avoids full-tree collection)
    if layer == 0:
        for f in _LAYER0_FILES:
            cmd.append(str(REPO_ROOT / f))
    # Fast-path: L1/L2 with format hint uses directory paths + L0 files (cumulative)
    elif layer <= 2 and formats:
        # Include L0 files first (cumulativity: layer N includes layers 0..N)
        for f in _LAYER0_FILES:
            cmd.append(str(REPO_ROOT / f))
        for fmt in sorted(formats):
            test_dir = REPO_ROOT / "tests" / "python" / fmt
            if test_dir.is_dir():
                cmd.append(str(test_dir))
    else:
        # Standard path: use cumulative marker expression
        marker_expr = build_marker_expr(layer)
        if marker_expr:
            cmd.extend(["-m", marker_expr])

    # Shard scoping for L6
    if shard:
        shard_num, _shard_total = shard
        shard_info = SHARD_MAP.get(shard_num)
        if shard_info:
            cmd.append(str(REPO_ROOT / shard_info["path"]))
            for ign in shard_info.get("ignore", []):
                cmd.extend(["--ignore", str(REPO_ROOT / ign)])

    # Output
    if junitxml_path:
        cmd.extend(["--junitxml", junitxml_path])

    if verbose:
        cmd.append("-v")

    cmd.append("-q")

    return cmd


def parse_junitxml(path: str) -> dict:
    """Parse junitxml output into test_results dict."""
    try:
        tree = ET.parse(path)
        root = tree.getroot()
        # Handle both <testsuites> and <testsuite> root
        if root.tag == "testsuites":
            suites = root.findall("testsuite")
        else:
            suites = [root]

        total = 0
        failures = 0
        errors = 0
        skipped = 0
        for suite in suites:
            total += int(suite.get("tests", 0))
            failures += int(suite.get("failures", 0))
            errors += int(suite.get("errors", 0))
            skipped += int(suite.get("skipped", 0))

        passed = total - failures - errors - skipped
        return {
            "passed": max(0, passed),
            "failed": failures,
            "skipped": skipped,
            "errors": errors,
        }
    except FileNotFoundError:
        return {"passed": 0, "failed": 0, "skipped": 0, "errors": 0,
                "_parse_error": "junitxml file not found"}
    except (ET.ParseError, ValueError):
        return {"passed": 0, "failed": 0, "skipped": 0, "errors": 0,
                "_parse_error": "junitxml parse failed"}


def run_and_collect(
    cmd: list[str],
    layer: int,
    layer_reason: str,
    formats: set[str] | None = None,
    shard: tuple[int, int] | None = None,
    json_out_path: str | None = None,
) -> dict:
    """Run pytest command and collect structured results."""
    start = time.monotonic()
    start_ts = datetime.now(timezone.utc).isoformat()

    # Create temp junitxml if not already in cmd
    junitxml_in_cmd = any("--junitxml" in c for c in cmd)
    junitxml_path = None
    if not junitxml_in_cmd:
        tmp = tempfile.NamedTemporaryFile(suffix=".xml", delete=False, prefix="ff-test-")
        junitxml_path = tmp.name
        tmp.close()
        cmd.extend(["--junitxml", junitxml_path])
    else:
        for i, c in enumerate(cmd):
            if c == "--junitxml" and i + 1 < len(cmd):
                junitxml_path = cmd[i + 1]
                break

    proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
    elapsed = time.monotonic() - start

    test_results = parse_junitxml(junitxml_path) if junitxml_path else {
        "passed": 0, "failed": 0, "skipped": 0, "errors": 0,
    }

    # Extract parse error sentinel (if any) before exposing test_results
    parse_error = test_results.pop("_parse_error", None)

    # Determine result reliability
    total_tests = sum(test_results[k] for k in ("passed", "failed", "skipped", "errors"))
    results_reliable = True
    if parse_error:
        results_reliable = False
    elif proc.returncode != 0 and total_tests == 0:
        results_reliable = False

    if not results_reliable:
        print(
            f"WARNING: pytest exited {proc.returncode} but test results are "
            f"unreliable (0 tests recorded). Check pytest output for errors.",
            file=sys.stderr,
        )

    # Clean up temp file
    if junitxml_path and not junitxml_in_cmd:
        try:
            os.unlink(junitxml_path)
        except OSError:
            pass

    marker_expr = build_marker_expr(layer)
    result = {
        "layer": layer,
        "layer_name": LAYER_NAMES.get(layer, f"layer{layer}"),
        "layer_reason": layer_reason,
        "formats_detected": sorted(formats) if formats else [],
        "marker_expr": marker_expr or "(no filter - full suite)",
        "command": " ".join(cmd),
        "test_results": test_results,
        "test_results_reliable": results_reliable,
        "duration_seconds": round(elapsed, 2),
        "shard": f"{shard[0]}/{shard[1]}" if shard else None,
        "timestamp": start_ts,
        "pytest_exit_code": proc.returncode,
    }

    if json_out_path:
        out_path = Path(json_out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w") as f:
            json.dump(result, f, indent=2)

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Format Factory layered test runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--layer", type=int, choices=range(7), metavar="N",
        help="Explicit layer (0-6)",
    )
    group.add_argument(
        "--auto", action="store_true",
        help="Auto-detect layer from git diff",
    )
    parser.add_argument(
        "--base-ref", default="HEAD",
        help="Git ref for diff comparison (default: HEAD)",
    )
    parser.add_argument(
        "--format", dest="format_hint", metavar="FMT",
        help="Hint: specific format name (e.g., tsv)",
    )
    parser.add_argument(
        "--shard", metavar="M/N",
        help="Shard specification for layer 6 (e.g., 1/4)",
    )
    parser.add_argument(
        "--json-out", metavar="PATH",
        help="Write JSON results to file",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print command without running")
    parser.add_argument("--verbose", "-v", action="store_true", help="Pass -v to pytest")

    args = parser.parse_args()

    manifest = load_manifest()

    # Determine layer
    formats: set[str] = set()
    if args.auto:
        changed = detect_changed_files(args.base_ref)
        layer, reason = compute_min_layer(changed, manifest)
        formats = resolve_formats_from_paths(changed)
    else:
        layer = args.layer
        reason = f"explicitly set to layer {layer}"

    # Apply format hint
    if args.format_hint:
        formats.add(args.format_hint)

    # Expand to family for layer 2
    if layer == 2 and formats:
        expanded = set()
        for fmt in formats:
            expanded.update(resolve_family(fmt, manifest))
        formats = expanded

    # Parse shard
    shard = None
    if args.shard:
        parts = args.shard.split("/")
        if len(parts) == 2:
            shard = (int(parts[0]), int(parts[1]))

    # Build junitxml path
    junitxml_path = None
    if not args.dry_run:
        results_dir = REPO_ROOT / ".local" / "test-results"
        results_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        shard_suffix = f"-shard{shard[0]}" if shard else ""
        junitxml_path = str(results_dir / f"layer{layer}{shard_suffix}-{ts}.xml")

    cmd = build_pytest_cmd(
        layer=layer,
        formats=formats if layer <= 2 else None,
        shard=shard,
        verbose=args.verbose,
        junitxml_path=junitxml_path,
    )

    if args.dry_run:
        print(json.dumps({
            "layer": layer,
            "layer_name": LAYER_NAMES.get(layer, f"layer{layer}"),
            "layer_reason": reason,
            "formats_detected": sorted(formats),
            "marker_expr": build_marker_expr(layer) or "(no filter - full suite)",
            "command": " ".join(cmd),
            "shard": f"{shard[0]}/{shard[1]}" if shard else None,
            "dry_run": True,
        }, indent=2))
        return

    result = run_and_collect(
        cmd=cmd,
        layer=layer,
        layer_reason=reason,
        formats=formats,
        shard=shard,
        json_out_path=args.json_out,
    )

    # Print summary
    tr = result["test_results"]
    status = "PASS" if tr["failed"] == 0 and tr["errors"] == 0 else "FAIL"
    print(f"\n[Layer {layer} ({result['layer_name']})] {status}")
    print(f"  Reason: {reason}")
    print(f"  Passed: {tr['passed']}, Failed: {tr['failed']}, "
          f"Skipped: {tr['skipped']}, Errors: {tr['errors']}")
    print(f"  Duration: {result['duration_seconds']}s")
    if args.json_out:
        print(f"  Results: {args.json_out}")

    sys.exit(result["pytest_exit_code"])


if __name__ == "__main__":
    main()
