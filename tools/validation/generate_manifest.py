"""
generate_manifest.py — Release manifest generator for format-factory.

Scans all artifact files with front matter, filters by release type (oss | commercial),
and outputs a release manifest YAML listing all eligible artifacts.

Policy source: docs/governance/release-control.md

Usage:
    python tools/validation/generate_manifest.py
    python tools/validation/generate_manifest.py --release-type oss
    python tools/validation/generate_manifest.py --release-type commercial
    python tools/validation/generate_manifest.py --output manifests/oss-manifest.yaml

Exit codes:
    0 — manifest generated successfully
    1 — no eligible artifacts found
    2 — tool error
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

SKIP_DIRS = {
    ".git", ".venv", "__pycache__", ".local", "node_modules",
    "build", "dist", ".eggs", ".tox",
}
ARTIFACT_EXTENSIONS = {".md", ".yaml", ".yml", ".py", ".json"}


def _extract_frontmatter(text: str) -> dict | None:
    """Extract and parse YAML front matter. Returns None if no front matter."""
    stripped = text.lstrip()
    if not stripped.startswith("---"):
        return None
    rest = stripped[3:]
    end = rest.find("\n---")
    if end == -1:
        return None
    fm_text = rest[:end].strip()
    if yaml is None:
        fm: dict = {}
        for line in fm_text.splitlines():
            if ":" in line and not line.startswith(" "):
                k, _, v = line.partition(":")
                raw = v.strip()
                if raw.lower() == "true":
                    v_parsed: object = True
                elif raw.lower() == "false":
                    v_parsed = False
                elif raw.lower() in ("null", "~", ""):
                    v_parsed = None
                else:
                    v_parsed = raw
                fm[k.strip()] = v_parsed
        return fm
    try:
        parsed = yaml.safe_load(fm_text)
        return parsed if isinstance(parsed, dict) else None
    except Exception:
        return None


def is_oss_eligible(fm: dict) -> bool:
    """Return True if an artifact is eligible for OSS release per release-control.md."""
    return (
        fm.get("visibility") == "public"
        and fm.get("publish_allowed") is True
        and fm.get("open_source_allowed") is True
        and not fm.get("release_blockers")
        and fm.get("commercial_allowed") is not True
    )


def is_commercial_eligible(fm: dict) -> bool:
    """Return True if an artifact is eligible for commercial release."""
    return (
        fm.get("visibility") in ("public", "commercial")
        and fm.get("publish_allowed") is True
        and fm.get("commercial_allowed") is True
        and not fm.get("release_blockers")
    )


def scan_artifacts(root: Path, release_type: str) -> list[dict]:
    """
    Scan all artifacts under root and return those eligible for the given release type.

    release_type: "oss" | "commercial" | "all"
    """
    eligible: list[dict] = []

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        parts = set(path.relative_to(root).parts[:-1])
        if parts & SKIP_DIRS:
            continue
        if path.suffix.lower() not in ARTIFACT_EXTENSIONS:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        fm = _extract_frontmatter(text)
        if fm is None:
            continue

        include = False
        if release_type == "oss":
            include = is_oss_eligible(fm)
        elif release_type == "commercial":
            include = is_commercial_eligible(fm)
        elif release_type == "all":
            include = fm.get("publish_allowed") is True

        if include:
            eligible.append({
                "path": str(path.relative_to(root)),
                "artifact_id": fm.get("artifact_id"),
                "artifact_type": fm.get("artifact_type"),
                "visibility": fm.get("visibility"),
                "license": fm.get("license"),
                "format_id": fm.get("format_id"),
                "product_family": fm.get("product_family"),
                "provenance_required": fm.get("provenance_required", False),
                "provenance_status": fm.get("provenance_status"),
            })

    return eligible


def build_manifest(artifacts: list[dict], release_type: str, root: Path) -> dict:
    """Build the release manifest dict."""
    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "release_type": release_type,
        "scanned_root": str(root),
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Release manifest generator")
    parser.add_argument(
        "--release-type",
        choices=["oss", "commercial", "all"],
        default="oss",
        help="Release type to generate manifest for (default: oss)",
    )
    parser.add_argument(
        "--path",
        default=str(REPO_ROOT),
        help=f"Root directory to scan (default: {REPO_ROOT})",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Write manifest to this path (YAML or JSON based on extension)",
    )
    parser.add_argument(
        "--format",
        choices=["yaml", "json"],
        default="yaml",
        dest="output_format",
        help="Output format: yaml or json (default: yaml)",
    )
    args = parser.parse_args(argv)

    root = Path(args.path)
    if not root.exists():
        print(f"ERROR: Path does not exist: {root}", file=sys.stderr)
        return 2

    artifacts = scan_artifacts(root, args.release_type)
    manifest = build_manifest(artifacts, args.release_type, root)

    if args.output_format == "json" or (args.output and args.output.endswith(".json")):
        content = json.dumps(manifest, indent=2) + "\n"
    elif yaml is not None:
        content = yaml.dump(manifest, sort_keys=False, allow_unicode=True)
    else:
        # Fallback: JSON when yaml not available
        content = json.dumps(manifest, indent=2) + "\n"

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")
        print(f"Manifest written: {args.output}")
        print(f"  Release type: {args.release_type}")
        print(f"  Eligible artifacts: {len(artifacts)}")
    else:
        print(content)
        print(f"# Release type: {args.release_type} | Eligible artifacts: {len(artifacts)}", file=sys.stderr)

    return 0 if artifacts else 1


if __name__ == "__main__":
    sys.exit(main())
