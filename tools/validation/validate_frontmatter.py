"""
validate_frontmatter.py — Artifact front matter validator for format-factory.

Scans all committed artifacts for YAML front matter (between --- delimiters),
validates required fields, and reports violations.

Policy source: docs/release-control.md

Usage:
    python tools/validation/validate_frontmatter.py
    python tools/validation/validate_frontmatter.py --path src/
    python tools/validation/validate_frontmatter.py --fix
    python tools/validation/validate_frontmatter.py --output report.json

Exit codes:
    0 — all artifacts valid
    1 — violations found
    2 — tool error (bad arguments, unreadable directory, etc.)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Required front matter fields per release-control.md
REQUIRED_FIELDS = [
    "artifact_id",
    "artifact_type",
    "visibility",
    "publish_allowed",
]

# Optional but tracked fields
TRACKED_FIELDS = [
    "format_id",
    "product_family",
    "license",
    "release_blockers",
    "open_source_allowed",
    "commercial_allowed",
    "provenance_required",
    "provenance_status",
    "generated_by",
    "generated_at",
    "reusable",
]

VALID_VISIBILITY = {"public", "internal", "commercial", "evidence-only", "generated", "blocked"}

ARTIFACT_EXTENSIONS = {".md", ".yaml", ".yml", ".py", ".json", ".txt", ".toml"}

# Directories to skip entirely
SKIP_DIRS = {
    ".git", ".venv", "__pycache__", ".local", "node_modules",
    "build", "dist", ".eggs", ".tox",
}


def _has_frontmatter(text: str) -> bool:
    """Return True if the text starts with a YAML front matter block (---)."""
    stripped = text.lstrip()
    return stripped.startswith("---")


def _extract_frontmatter(text: str) -> tuple[dict, str | None]:
    """
    Extract and parse the YAML front matter from text.

    Returns (parsed_dict, error_str). If no front matter, returns ({}, None).
    If parse error, returns ({}, error_message).
    """
    stripped = text.lstrip()
    if not stripped.startswith("---"):
        return {}, None

    # Find the closing ---
    rest = stripped[3:]
    end = rest.find("\n---")
    if end == -1:
        return {}, "Unclosed front matter block (missing closing ---)"

    fm_text = rest[:end].strip()
    if yaml is None:
        # Fallback: minimal key extraction without yaml
        fm: dict = {}
        for line in fm_text.splitlines():
            if ":" in line and not line.startswith(" "):
                k, _, v = line.partition(":")
                fm[k.strip()] = v.strip()
        return fm, None

    try:
        parsed = yaml.safe_load(fm_text)
        if not isinstance(parsed, dict):
            return {}, "Front matter did not parse to a dict"
        return parsed, None
    except Exception as exc:
        return {}, f"YAML parse error: {exc}"


def validate_file(path: Path) -> list[str]:
    """
    Validate a single file's front matter.

    Returns a list of violation strings (empty = valid).
    """
    violations: list[str] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return [f"Cannot read file: {exc}"]

    if not _has_frontmatter(text):
        # Not all files require front matter — skip silently
        return []

    fm, err = _extract_frontmatter(text)
    if err:
        violations.append(f"Front matter parse error: {err}")
        return violations

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in fm:
            violations.append(f"Missing required field: {field}")

    # Validate visibility value
    visibility = fm.get("visibility")
    if visibility is not None and visibility not in VALID_VISIBILITY:
        violations.append(f"Invalid visibility value: {visibility!r} (must be one of {sorted(VALID_VISIBILITY)})")

    # Check boolean fields
    for bool_field in ("publish_allowed", "open_source_allowed", "commercial_allowed", "provenance_required"):
        val = fm.get(bool_field)
        if val is not None and not isinstance(val, bool):
            violations.append(f"Field {bool_field!r} must be boolean, got {type(val).__name__}")

    return violations


def scan_directory(
    root: Path,
    *,
    extensions: set[str] | None = None,
    skip_dirs: set[str] | None = None,
) -> dict[str, list[str]]:
    """
    Scan all files under root for front matter violations.

    Returns dict mapping relative file path → list of violation strings.
    Only files with violations are included.
    """
    if extensions is None:
        extensions = ARTIFACT_EXTENSIONS
    if skip_dirs is None:
        skip_dirs = SKIP_DIRS

    results: dict[str, list[str]] = {}

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        # Skip files in excluded directories
        parts = set(path.relative_to(root).parts[:-1])
        if parts & skip_dirs:
            continue
        if path.suffix.lower() not in extensions:
            continue
        violations = validate_file(path)
        if violations:
            results[str(path.relative_to(root))] = violations

    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Artifact front matter validator")
    parser.add_argument(
        "--path",
        default=str(REPO_ROOT),
        help=f"Root directory to scan (default: repo root {REPO_ROOT})",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Write JSON report to this path instead of stdout",
    )
    parser.add_argument(
        "--extensions",
        default=None,
        help="Comma-separated file extensions to check (default: .md,.yaml,.yml,.py,.json,.txt,.toml)",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print only summary counts, not per-file violations",
    )
    args = parser.parse_args(argv)

    root = Path(args.path)
    if not root.exists():
        print(f"ERROR: Path does not exist: {root}", file=sys.stderr)
        return 2

    extensions: set[str] | None = None
    if args.extensions:
        extensions = {e.strip() if e.strip().startswith(".") else f".{e.strip()}" for e in args.extensions.split(",")}

    violations = scan_directory(root, extensions=extensions)

    report = {
        "schema_version": "1.0",
        "scanned_root": str(root),
        "files_with_violations": len(violations),
        "total_violations": sum(len(v) for v in violations.values()),
        "violations": violations,
    }

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"Report written: {args.output}")
        print(f"  Files with violations: {report['files_with_violations']}")
        print(f"  Total violations: {report['total_violations']}")
    elif args.summary:
        print(f"Files with violations: {report['files_with_violations']}")
        print(f"Total violations: {report['total_violations']}")
    else:
        if not violations:
            print("PASS: No front matter violations found.")
        else:
            print(f"FAIL: {len(violations)} file(s) with violations:")
            for fpath, viols in sorted(violations.items()):
                print(f"\n  {fpath}")
                for v in viols:
                    print(f"    - {v}")

    return 0 if not violations else 1


if __name__ == "__main__":
    sys.exit(main())
