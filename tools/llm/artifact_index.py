"""
tools/llm/artifact_index.py — Artifact Index Bootstrapper
TC-0005 (Phase 1, 2026-06-18)

Bootstraps .local/artifact-index.yaml from the committed repo state and
updates it when new artifacts are created.

The artifact index provides reuse tooling: before generating any artifact,
check if a compatible artifact already exists using this index.
See docs/ai/llm-endpoint-strategy.md Section G (artifact reuse).
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

_REPO_ROOT = Path(__file__).parents[2]
_LOCAL_DIR = _REPO_ROOT / ".local"
_INDEX_PATH = _LOCAL_DIR / "artifact-index.yaml"

# Directories to scan for artifacts (relative to repo root)
_ARTIFACT_DIRS = [
    "reports/capability-layer",
    "reports/supervisor",
    "reports/gate11",
    "taskcards",
    "docs",
    "plans",
    "schemas",
    "registry",
]

# Artifact file extensions to index
_ARTIFACT_EXTENSIONS = {".md", ".yaml", ".json", ".txt"}


def _make_entry(path: Path, repo_root: Path) -> dict[str, Any]:
    rel = path.relative_to(repo_root)
    stat = path.stat()
    return {
        "path": rel.as_posix(),
        "size_bytes": stat.st_size,
        "mtime": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        "format_id": _infer_format_id(rel),
        "artifact_type": _infer_artifact_type(rel),
    }


def _infer_format_id(rel: Path) -> str | None:
    """Infer format_id from path components if possible."""
    parts = rel.parts
    known_formats = {
        "fods", "fodt", "fodg", "fodp", "ods", "odt", "csv", "tsv",
        "dif", "sylk", "abw", "ndjson", "gnumeric", "pbm", "pgm",
        "ppm", "qoi", "xcf", "zst", "toml",
    }
    for part in parts:
        if part.lower() in known_formats:
            return part.lower()
    return None


def _infer_artifact_type(rel: Path) -> str:
    """Infer artifact type from path prefix."""
    first = rel.parts[0] if rel.parts else ""
    if first == "reports":
        return "report"
    if first == "taskcards":
        return "taskcard"
    if first in ("docs", "plans"):
        return "documentation"
    if first == "registry":
        return "registry"
    if first == "schemas":
        return "schema"
    return "other"


def bootstrap_index(force: bool = False) -> Path:
    """
    Scan the repo and write .local/artifact-index.yaml.
    If the file already exists and force=False, return without overwriting.

    Returns the path to the index file.
    """
    _LOCAL_DIR.mkdir(parents=True, exist_ok=True)

    if _INDEX_PATH.exists() and not force:
        return _INDEX_PATH

    entries = []
    for dir_rel in _ARTIFACT_DIRS:
        scan_dir = _REPO_ROOT / dir_rel
        if not scan_dir.is_dir():
            continue
        for p in scan_dir.rglob("*"):
            if p.suffix in _ARTIFACT_EXTENSIONS and p.is_file():
                entries.append(_make_entry(p, _REPO_ROOT))

    index = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": "tools/llm/artifact_index.py (TC-0005)",
        "total_artifacts": len(entries),
        "artifacts": entries,
    }

    if _HAS_YAML:
        _INDEX_PATH.write_text(
            yaml.dump(index, default_flow_style=False, allow_unicode=True),
            encoding="utf-8",
        )
    else:
        # Fallback: write as JSON with .yaml extension
        _INDEX_PATH.write_text(json.dumps(index, indent=2), encoding="utf-8")

    return _INDEX_PATH


def update_index_entry(artifact_path: str | Path) -> None:
    """
    Update or add a single artifact entry in the existing index.
    Creates the index if it doesn't exist.
    """
    if not _INDEX_PATH.exists():
        bootstrap_index()
        return

    abs_path = Path(artifact_path)
    if not abs_path.is_absolute():
        abs_path = _REPO_ROOT / abs_path

    if not abs_path.exists():
        return  # Nothing to index

    new_entry = _make_entry(abs_path, _REPO_ROOT)
    rel_str = new_entry["path"]

    if _HAS_YAML:
        data = yaml.safe_load(_INDEX_PATH.read_text(encoding="utf-8")) or {}
    else:
        data = json.loads(_INDEX_PATH.read_text(encoding="utf-8"))

    artifacts = data.get("artifacts", [])
    # Remove existing entry for this path
    artifacts = [a for a in artifacts if a.get("path") != rel_str]
    artifacts.append(new_entry)
    data["artifacts"] = artifacts
    data["total_artifacts"] = len(artifacts)
    data["last_updated"] = datetime.now(timezone.utc).isoformat()

    if _HAS_YAML:
        _INDEX_PATH.write_text(
            yaml.dump(data, default_flow_style=False, allow_unicode=True),
            encoding="utf-8",
        )
    else:
        _INDEX_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def find_artifact(
    format_id: str | None = None,
    artifact_type: str | None = None,
    path_contains: str | None = None,
) -> list[dict[str, Any]]:
    """
    Search the index for artifacts matching the given criteria.
    Returns matching entries sorted by mtime (newest first).
    """
    if not _INDEX_PATH.exists():
        return []

    if _HAS_YAML:
        data = yaml.safe_load(_INDEX_PATH.read_text(encoding="utf-8")) or {}
    else:
        data = json.loads(_INDEX_PATH.read_text(encoding="utf-8"))

    artifacts = data.get("artifacts", [])
    results = []
    for a in artifacts:
        if format_id and a.get("format_id") != format_id:
            continue
        if artifact_type and a.get("artifact_type") != artifact_type:
            continue
        if path_contains and path_contains not in a.get("path", ""):
            continue
        results.append(a)

    return sorted(results, key=lambda x: x.get("mtime", ""), reverse=True)


if __name__ == "__main__":
    import sys
    if "--bootstrap" in sys.argv:
        force = "--force" in sys.argv
        idx = bootstrap_index(force=force)
        print(f"Artifact index written: {idx}")
        if _HAS_YAML:
            data = yaml.safe_load(idx.read_text(encoding="utf-8")) or {}
        else:
            data = json.loads(idx.read_text(encoding="utf-8"))
        print(f"Total artifacts indexed: {data.get('total_artifacts', 0)}")
