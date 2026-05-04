"""
spec_index.py — Specification Cache Index Library
format-factory / tools/spec-cache/

Purpose:
    Read, write, and validate spec-index.yaml entries for the specification
    cache under .local/spec-cache/. This module is used by acquire_spec.py
    and refresh_check.py.

Policy:
    - All cached specs live under .local/spec-cache/ (gitignored).
    - Spec files are NEVER committed to git.
    - Every cached spec version must have a spec-index.yaml entry.
    - This module does NOT perform network access.
    - This module does NOT call LLM endpoints.

See also:
    docs/specification-cache.md — full policy and schema reference
    tools/spec-cache/acquire_spec.py — download and index a spec file
    tools/spec-cache/refresh_check.py — check for stale entries
"""

import hashlib
import os
import pathlib
import sys
from datetime import date, datetime, timezone
from typing import Any, Optional

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Schema definition
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = {
    # Always required — must be present with non-null values.
    "format_id",
    "spec_name",
    "version",
    "source_url",
    "canonical_url",
    "publisher",
    "legal_category",
    "license",
    "redistribution_permitted",
    "local_only",
    "stale",
}

# Post-download fields: present in the dict but may be None/null before download.
# acquire_spec.py populates these on live download (or synthetic values on dry-run).
# Pre-download / metadata-only entries may omit or set these to null.
NULLABLE_DOWNLOAD_FIELDS = {
    "download_date",
    "file_path",
    "file_size_bytes",
    "sha256",
    "mime_type",
    "content_hash",
    "fetched_at",
}

OPTIONAL_FIELDS = {
    # Identity metadata
    "spec_id",
    "source_type",
    "date_published",
    "date_accessed",
    "local_path",
    "fetched_by",
    # Refresh / HTTP metadata
    "last_verified",
    "etag",
    "last_modified",
    "refresh_policy",
    # Release control
    "release_blockers",
    # Misc
    "notes",
    "dry_run",
}

VALID_LEGAL_CATEGORIES = {1, 2, 3, 4}

# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_entry(entry: dict) -> list[str]:
    """
    Validate a spec-index.yaml entry against the schema.

    Returns a list of error strings. Empty list means valid.
    """
    errors = []

    if not isinstance(entry, dict):
        return ["Entry must be a YAML mapping/dict"]

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in entry:
            errors.append(f"Missing required field: {field}")

    if errors:
        return errors  # Stop early if required fields are missing

    # Type checks
    if not isinstance(entry.get("format_id"), str) or not entry["format_id"].strip():
        errors.append("format_id must be a non-empty string")

    if not isinstance(entry.get("spec_name"), str) or not entry["spec_name"].strip():
        errors.append("spec_name must be a non-empty string")

    if not isinstance(entry.get("version"), str) or not entry["version"].strip():
        errors.append("version must be a non-empty string")

    if not isinstance(entry.get("source_url"), str) or not entry["source_url"].startswith("http"):
        errors.append("source_url must be an http/https URL string")

    if not isinstance(entry.get("canonical_url"), str) or not entry["canonical_url"].startswith("http"):
        errors.append("canonical_url must be an http/https URL string")

    if not isinstance(entry.get("publisher"), str) or not entry["publisher"].strip():
        errors.append("publisher must be a non-empty string")

    legal_cat = entry.get("legal_category")
    if legal_cat not in VALID_LEGAL_CATEGORIES:
        errors.append(f"legal_category must be one of {VALID_LEGAL_CATEGORIES}, got: {legal_cat}")

    if not isinstance(entry.get("redistribution_permitted"), bool):
        errors.append("redistribution_permitted must be a boolean")

    if not isinstance(entry.get("local_only"), bool):
        errors.append("local_only must be a boolean")

    if entry.get("local_only") is not True:
        errors.append("local_only must be true — spec files must never be committed")

    if not isinstance(entry.get("stale"), bool):
        errors.append("stale must be a boolean")

    # sha256 / content_hash format check
    sha256_val = entry.get("sha256")
    if sha256_val is not None and sha256_val != "dry_run_synthetic":
        if not isinstance(sha256_val, str) or not sha256_val.startswith("sha256:"):
            errors.append("sha256 must be 'sha256:<hex>' or null or 'dry_run_synthetic'")

    content_hash_val = entry.get("content_hash")
    if content_hash_val is not None and content_hash_val != "dry_run_synthetic":
        if not isinstance(content_hash_val, str) or not content_hash_val.startswith("sha256:"):
            errors.append("content_hash must be 'sha256:<hex>' or null or 'dry_run_synthetic'")

    return errors


# ---------------------------------------------------------------------------
# File I/O
# ---------------------------------------------------------------------------


def get_cache_root() -> pathlib.Path:
    """Return the .local/spec-cache/ root path relative to the repo root."""
    # Walk up from this file's directory to find repo root (.gitignore presence)
    here = pathlib.Path(__file__).resolve().parent
    for candidate in [here, here.parent, here.parent.parent, here.parent.parent.parent]:
        if (candidate / ".gitignore").exists():
            return candidate / ".local" / "spec-cache"
    # Fallback: use current working directory
    return pathlib.Path.cwd() / ".local" / "spec-cache"


def get_index_path(format_id: str, version: str) -> pathlib.Path:
    """Return the path to the spec-index.yaml for a given format/version."""
    return get_cache_root() / format_id / version / "spec-index.yaml"


def read_entry(format_id: str, version: str) -> Optional[dict]:
    """
    Read a spec-index.yaml entry for format_id/version.

    Returns the parsed YAML dict or None if not found.
    """
    index_path = get_index_path(format_id, version)
    if not index_path.exists():
        return None
    with open(index_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_entry(entry: dict, allow_overwrite: bool = False) -> pathlib.Path:
    """
    Write a spec-index.yaml entry to the cache.

    Validates the entry before writing. Raises ValueError on validation failure.
    Raises FileExistsError if the entry exists and allow_overwrite=False.

    Returns the path to the written file.
    """
    errors = validate_entry(entry)
    if errors:
        raise ValueError(f"Entry validation failed:\n" + "\n".join(f"  - {e}" for e in errors))

    format_id = entry["format_id"]
    version = entry["version"]
    index_path = get_index_path(format_id, version)

    if index_path.exists() and not allow_overwrite:
        raise FileExistsError(
            f"spec-index.yaml already exists at {index_path}. "
            "Pass allow_overwrite=True to update."
        )

    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "w", encoding="utf-8") as f:
        yaml.dump(entry, f, default_flow_style=False, allow_unicode=True, sort_keys=True)

    return index_path


def list_all_entries() -> list[dict]:
    """
    Scan .local/spec-cache/ and return all valid spec-index.yaml entries.
    Skips entries that fail to parse.
    """
    cache_root = get_cache_root()
    entries = []
    if not cache_root.exists():
        return entries

    for index_file in sorted(cache_root.rglob("spec-index.yaml")):
        try:
            with open(index_file, "r", encoding="utf-8") as f:
                entry = yaml.safe_load(f)
            if isinstance(entry, dict):
                entry["_index_path"] = str(index_file)
                entries.append(entry)
        except Exception as e:
            print(f"WARNING: Could not parse {index_file}: {e}", file=sys.stderr)

    return entries


# ---------------------------------------------------------------------------
# Hash utilities
# ---------------------------------------------------------------------------


def compute_sha256(file_path: pathlib.Path) -> str:
    """Compute sha256 of a file. Returns 'sha256:<hex>'."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"


def verify_hash(file_path: pathlib.Path, expected_hash: str) -> bool:
    """Verify a file's SHA-256 against the expected 'sha256:<hex>' string."""
    if expected_hash in (None, "dry_run_synthetic"):
        return True  # Dry-run entries always pass
    actual = compute_sha256(file_path)
    return actual == expected_hash


# ---------------------------------------------------------------------------
# Staleness check
# ---------------------------------------------------------------------------


def is_stale(entry: dict, cache_root: Optional[pathlib.Path] = None) -> tuple[bool, str]:
    """
    Check whether a spec-index.yaml entry is stale.

    Returns (is_stale: bool, reason: str).
    Reasons:
        - 'stale_flag': entry has stale: true
        - 'missing_file': the cached file does not exist on disk
        - 'hash_mismatch': SHA-256 of cached file does not match entry
        - 'not_stale': entry appears current
    """
    if entry.get("stale") is True:
        return True, "stale_flag"

    if cache_root is None:
        cache_root = get_cache_root()

    file_path_rel = entry.get("file_path")
    if file_path_rel:
        # file_path is relative to the version directory
        format_id = entry.get("format_id", "")
        version = entry.get("version", "")
        file_path = cache_root / format_id / version / file_path_rel
        if not file_path.exists():
            return True, "missing_file"

        expected_hash = entry.get("content_hash") or entry.get("sha256")
        if expected_hash and expected_hash != "dry_run_synthetic":
            if not verify_hash(file_path, expected_hash):
                return True, "hash_mismatch"

    return False, "not_stale"


# ---------------------------------------------------------------------------
# CLI for validation
# ---------------------------------------------------------------------------


def _cmd_validate(args: list[str]) -> int:
    """validate [format_id [version]] — validate existing index entries."""
    entries = list_all_entries()
    if not entries:
        print("No spec-index.yaml entries found in .local/spec-cache/")
        return 0

    all_valid = True
    for entry in entries:
        path = entry.pop("_index_path", "unknown")
        errors = validate_entry(entry)
        if errors:
            print(f"INVALID: {path}")
            for err in errors:
                print(f"  - {err}")
            all_valid = False
        else:
            stale_flag, reason = is_stale(entry)
            status = f"STALE ({reason})" if stale_flag else "CURRENT"
            print(f"VALID [{status}]: {entry.get('format_id')}/{entry.get('version')} — {path}")

    return 0 if all_valid else 1


def _cmd_list(args: list[str]) -> int:
    """list — list all cached spec entries."""
    entries = list_all_entries()
    if not entries:
        print("No spec-index.yaml entries found.")
        return 0
    for entry in entries:
        path = entry.pop("_index_path", "unknown")
        stale_flag, reason = is_stale(entry)
        status = f"STALE({reason})" if stale_flag else "current"
        print(f"{entry.get('format_id'):12} {entry.get('version'):8} [{status}]  {path}")
    return 0


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print("Usage: spec_index.py <command> [args]")
        print("Commands:")
        print("  validate    — validate all spec-index.yaml entries")
        print("  list        — list all cached spec entries")
        return 1

    cmd = args[0].lower()
    if cmd == "validate":
        return _cmd_validate(args[1:])
    elif cmd == "list":
        return _cmd_list(args[1:])
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
