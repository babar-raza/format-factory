"""
check_boundary.py — Commercial exclusion boundary checker for format-factory.

Verifies that:
1. No commercial artifact appears in an OSS manifest
2. No FOSS source file (src/python/{format}/ or src/net/{format}/) references
   any commercial namespace, class, or tier-5/6 identifier

Policy source: docs/release-control.md §Commercial Exclusion Rules

Usage:
    python tools/validation/check_boundary.py
    python tools/validation/check_boundary.py --manifest manifests/oss-manifest.yaml
    python tools/validation/check_boundary.py --src-only
    python tools/validation/check_boundary.py --output boundary-report.json

Exit codes:
    0 — boundary clean (no violations)
    1 — boundary violations found
    2 — tool error
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Patterns that indicate commercial-ONLY content in FOSS source
# NOTE: comments saying "no commercial" or "FOSS only" are NOT violations.
COMMERCIAL_PATTERNS: list[re.Pattern] = [
    # Explicit commercial tier labels
    re.compile(r"\bcommercial[_\s-]only\b", re.IGNORECASE),
    re.compile(r"\bTier[_ -]?[56]\b", re.IGNORECASE),
    re.compile(r"\bEnterpriseOnly\b"),
    # Front matter fields
    re.compile(r"\bvisibility\s*:\s*commercial\b", re.IGNORECASE),
    re.compile(r"\bcommercial_allowed\s*:\s*true\b", re.IGNORECASE),
    # Import of commercial namespaces
    re.compile(r"\bfrom\s+\w+\.commercial\b"),
    re.compile(r"\bimport\s+\w+\.commercial\b"),
    # .NET commercial markers
    re.compile(r"DEC-033\s+Option\s+B", re.IGNORECASE),
    re.compile(r"Commercial\s+\.NET", re.IGNORECASE),
]

FOSS_SOURCE_DIRS = [
    "src/python",
    "src/net",
]

FOSS_SOURCE_EXTENSIONS = {".py", ".cs", ".fs", ".vb", ".ts", ".js"}

SKIP_DIRS = {".git", ".venv", "__pycache__", ".local", "node_modules", "build", "dist"}


def _has_commercial_frontmatter(text: str) -> bool:
    """Return True if the file's front matter declares commercial visibility."""
    stripped = text.lstrip()
    if not stripped.startswith("---"):
        return False
    rest = stripped[3:]
    end = rest.find("\n---")
    if end == -1:
        return False
    fm_text = rest[:end]
    # Quick pattern check (avoid full parse for speed)
    return bool(re.search(r"\bvisibility\s*:\s*commercial\b", fm_text, re.IGNORECASE))


def check_foss_source_boundary(root: Path) -> list[dict]:
    """
    Scan FOSS source directories for commercial namespace references.

    Returns list of dicts with keys: path, line, pattern, snippet.
    """
    violations: list[dict] = []

    for src_dir in FOSS_SOURCE_DIRS:
        scan_path = root / src_dir
        if not scan_path.exists():
            continue
        for path in sorted(scan_path.rglob("*")):
            if not path.is_file():
                continue
            parts = set(path.relative_to(root).parts)
            if parts & SKIP_DIRS:
                continue
            if path.suffix.lower() not in FOSS_SOURCE_EXTENSIONS:
                continue
            try:
                lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            for lineno, line in enumerate(lines, start=1):
                for pat in COMMERCIAL_PATTERNS:
                    if pat.search(line):
                        violations.append({
                            "path": str(path.relative_to(root)),
                            "line": lineno,
                            "pattern": pat.pattern,
                            "snippet": line.strip()[:200],
                        })
                        break  # Only one violation per line

    return violations


def check_manifest_boundary(manifest_path: Path) -> list[dict]:
    """
    Check a generated OSS manifest for any commercial artifacts.

    Returns list of violations.
    """
    if not manifest_path.exists():
        return [{"error": f"Manifest not found: {manifest_path}"}]

    try:
        text = manifest_path.read_text(encoding="utf-8")
    except OSError as exc:
        return [{"error": f"Cannot read manifest: {exc}"}]

    if yaml is not None:
        try:
            manifest = yaml.safe_load(text)
        except Exception:
            manifest = None
    else:
        manifest = None

    if manifest is None:
        try:
            manifest = json.loads(text)
        except Exception:
            return [{"error": "Cannot parse manifest as YAML or JSON"}]

    violations: list[dict] = []
    artifacts = manifest.get("artifacts", [])
    for artifact in artifacts:
        visibility = artifact.get("visibility", "")
        if visibility == "commercial":
            violations.append({
                "path": artifact.get("path", "<unknown>"),
                "reason": "commercial artifact in OSS manifest",
                "visibility": visibility,
            })
        commercial_allowed = artifact.get("commercial_allowed")
        if commercial_allowed is True and visibility != "public":
            violations.append({
                "path": artifact.get("path", "<unknown>"),
                "reason": "commercial_allowed=true in OSS manifest",
                "visibility": visibility,
            })

    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Commercial exclusion boundary checker")
    parser.add_argument(
        "--manifest",
        default=None,
        help="OSS release manifest to check (YAML or JSON). If not provided, skips manifest check.",
    )
    parser.add_argument(
        "--path",
        default=str(REPO_ROOT),
        help=f"Repo root to scan (default: {REPO_ROOT})",
    )
    parser.add_argument(
        "--src-only",
        action="store_true",
        help="Only check FOSS source boundary (skip manifest check)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Write JSON report to this path",
    )
    args = parser.parse_args(argv)

    root = Path(args.path)
    if not root.exists():
        print(f"ERROR: Path does not exist: {root}", file=sys.stderr)
        return 2

    src_violations = check_foss_source_boundary(root)

    manifest_violations: list[dict] = []
    if not args.src_only and args.manifest:
        manifest_violations = check_manifest_boundary(Path(args.manifest))

    total = len(src_violations) + len(manifest_violations)

    report = {
        "schema_version": "1.0",
        "scanned_root": str(root),
        "manifest_checked": args.manifest,
        "boundary_clean": total == 0,
        "foss_source_violations": src_violations,
        "manifest_violations": manifest_violations,
        "total_violations": total,
    }

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"Boundary report written: {args.output}")
        print(f"  Boundary clean: {report['boundary_clean']}")
        print(f"  Total violations: {total}")
    else:
        if total == 0:
            print("PASS: Commercial boundary clean — no violations found.")
        else:
            print(f"FAIL: {total} boundary violation(s) found:")
            if src_violations:
                print(f"\n  FOSS source violations ({len(src_violations)}):")
                for v in src_violations[:20]:
                    snippet = v.get('snippet', '')[:80].encode('ascii', errors='replace').decode('ascii')
                print(f"    {v.get('path')}:{v.get('line')} -- {snippet}")
            if manifest_violations:
                print(f"\n  Manifest violations ({len(manifest_violations)}):")
                for v in manifest_violations:
                    print(f"    {v}")
            if total > 20:
                print(f"  ... and {total - 20} more. Use --output to see full report.")

    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
