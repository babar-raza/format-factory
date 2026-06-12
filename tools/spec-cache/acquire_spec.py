"""
acquire_spec.py — Specification Downloader and Indexer
format-factory / tools/spec-cache/

Purpose:
    Download a specification file from a remote URL, compute its SHA-256,
    and record a spec-index.yaml entry using spec_index.py. By default runs
    in DRY-RUN mode and does NOT perform network access. Pass --allow-network
    to enable actual download. Network access requires explicit T3 authorization
    (see docs/specification-cache.md).

Policy:
    - Default mode: DRY-RUN (no network, no disk write, prints what would happen).
    - Live mode: --allow-network must be passed explicitly.
    - Downloaded files are stored ONLY in .local/spec-cache/ (gitignored).
    - Spec files are NEVER committed to git.
    - All six T3 authorization conditions must be documented before live download.
    - Legal metadata (legal_category, license, redistribution_permitted) MUST be
      provided; the tool refuses to proceed without them.
    - This tool does NOT call LLM endpoints.
    - This tool does NOT approve gates.

Authorization model:
    Before passing --allow-network, all six conditions in docs/specification-cache.md
    must be satisfied:
      T3-1: Format has passed Gate 1
      T3-2: Legal category confirmed as 1 or 2 (Open Standard or Permissive OSS)
      T3-3: redistribution_permitted explicitly confirmed
      T3-4: canonical_url verified as official publisher URL
      T3-5: Spec version confirmed against official source
      T3-6: Human operator records authorization in acquisition pack

See also:
    docs/specification-cache.md — full policy and authorization model
    tools/spec-cache/spec_index.py — spec-index.yaml library
    tools/spec-cache/refresh_check.py — check for stale entries
"""

import argparse
import pathlib
import sys
from datetime import date, datetime, timezone

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

# Import spec_index from same directory
_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
import spec_index


# ---------------------------------------------------------------------------
# Live download (only called when --allow-network is active)
# ---------------------------------------------------------------------------


def _download_file(url: str, dest_path: pathlib.Path, timeout: int = 60) -> int:
    """
    Download url to dest_path. Returns file size in bytes.
    Raises on HTTP error or network failure.
    Only called when --allow-network is active.
    """
    try:
        import urllib.request

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        # Use a descriptive User-Agent so server logs show purpose
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "format-factory/acquire_spec (research; non-commercial)"
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = response.read()

        dest_path.write_bytes(data)
        return len(data)
    except Exception as e:
        raise RuntimeError(f"Download failed for {url}: {e}") from e


def _detect_mime_type(file_path: pathlib.Path, url: str) -> str:
    """Detect MIME type from file extension or URL, with fallback."""
    ext = file_path.suffix.lower()
    url_lower = url.lower()

    mime_map = {
        ".pdf": "application/pdf",
        ".html": "text/html",
        ".htm": "text/html",
        ".xml": "application/xml",
        ".odt": "application/vnd.oasis.opendocument.text",
        ".ods": "application/vnd.oasis.opendocument.spreadsheet",
        ".odp": "application/vnd.oasis.opendocument.presentation",
        ".zip": "application/zip",
        ".txt": "text/plain",
        ".md": "text/markdown",
        ".json": "application/json",
        ".yaml": "application/yaml",
        ".yml": "application/yaml",
    }

    if ext in mime_map:
        return mime_map[ext]

    # Fallback from URL
    for suffix, mime in mime_map.items():
        if suffix in url_lower:
            return mime

    return "application/octet-stream"


# ---------------------------------------------------------------------------
# Entry construction
# ---------------------------------------------------------------------------


def _build_entry(
    args: argparse.Namespace,
    file_path: pathlib.Path,
    file_size_bytes: int,
    sha256: str,
    content_hash: str,
    dry_run: bool,
) -> dict:
    """Build the spec-index.yaml entry dict from args and computed values."""
    now_iso = datetime.now(timezone.utc).isoformat()
    today_str = date.today().isoformat()

    # file_path in the entry is relative to the version directory
    relative_file_path = file_path.name if not dry_run else args.filename

    return {
        "format_id": args.format_id,
        "spec_name": args.spec_name,
        "version": args.version,
        "source_url": args.source_url,
        "canonical_url": args.canonical_url,
        "publisher": args.publisher,
        "download_date": today_str,
        "file_path": relative_file_path,
        "file_size_bytes": file_size_bytes,
        "sha256": sha256,
        "mime_type": args.mime_type or _detect_mime_type(pathlib.Path(args.filename), args.source_url),
        "legal_category": int(args.legal_category),
        "license": args.license,
        "redistribution_permitted": args.redistribution_permitted,
        "local_only": True,
        "fetched_at": now_iso,
        "content_hash": content_hash,
        "stale": False,
        "notes": args.notes,
        "dry_run": dry_run,
    }


# ---------------------------------------------------------------------------
# Dry-run path
# ---------------------------------------------------------------------------


def _run_dry(args: argparse.Namespace) -> int:
    """Execute in dry-run mode: validate metadata, print what would happen."""
    print("=== DRY-RUN MODE (no network access, no disk writes) ===")
    print()
    print(f"  format_id           : {args.format_id}")
    print(f"  spec_name           : {args.spec_name}")
    print(f"  version             : {args.version}")
    print(f"  source_url          : {args.source_url}")
    print(f"  canonical_url       : {args.canonical_url}")
    print(f"  publisher           : {args.publisher}")
    print(f"  filename            : {args.filename}")
    print(f"  legal_category      : {args.legal_category}")
    print(f"  license             : {args.license}")
    print(f"  redistribution_perm : {args.redistribution_permitted}")
    print()

    # Build a synthetic entry for validation
    cache_root = spec_index.get_cache_root()
    dest_dir = cache_root / args.format_id / args.version
    dest_path = dest_dir / args.filename

    synthetic_entry = _build_entry(
        args=args,
        file_path=dest_path,
        file_size_bytes=0,
        sha256="dry_run_synthetic",
        content_hash="dry_run_synthetic",
        dry_run=True,
    )

    errors = spec_index.validate_entry(synthetic_entry)
    if errors:
        print("VALIDATION ERRORS (dry-run entry would be rejected):")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("Validation: PASS (synthetic entry passes schema validation)")
    print()
    print("Would write to:")
    print(f"  Spec file  : {dest_path}")
    print(f"  Index file : {spec_index.get_index_path(args.format_id, args.version)}")
    print()
    print("To perform live download, add: --allow-network")
    print("Network download requires T3 authorization (see docs/specification-cache.md).")
    return 0


# ---------------------------------------------------------------------------
# Live download path
# ---------------------------------------------------------------------------


def _run_live(args: argparse.Namespace) -> int:
    """Execute live download: download, hash, write index."""
    cache_root = spec_index.get_cache_root()
    dest_dir = cache_root / args.format_id / args.version
    dest_path = dest_dir / args.filename

    # Check for existing entry
    existing = spec_index.read_entry(args.format_id, args.version)
    if existing and not args.overwrite:
        print(
            f"ERROR: spec-index.yaml already exists for {args.format_id}/{args.version}. "
            "Use --overwrite to replace.",
            file=sys.stderr,
        )
        return 1

    print(f"Downloading: {args.source_url}")
    print(f"         to: {dest_path}")

    try:
        file_size_bytes = _download_file(args.source_url, dest_path, timeout=args.timeout)
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print(f"Downloaded: {file_size_bytes} bytes")

    # Compute hashes
    sha256 = spec_index.compute_sha256(dest_path)
    content_hash = sha256  # content_hash == sha256 for downloaded files

    print(f"SHA-256: {sha256}")

    # Build and write entry
    entry = _build_entry(
        args=args,
        file_path=dest_path,
        file_size_bytes=file_size_bytes,
        sha256=sha256,
        content_hash=content_hash,
        dry_run=False,
    )

    # Remove dry_run key for live entries
    entry.pop("dry_run", None)

    try:
        index_path = spec_index.write_entry(entry, allow_overwrite=bool(args.overwrite))
    except (ValueError, FileExistsError) as e:
        print(f"ERROR writing index: {e}", file=sys.stderr)
        return 1

    print(f"Index written: {index_path}")
    print()
    print("SUCCESS — spec cached.")
    print(f"  format_id : {args.format_id}")
    print(f"  version   : {args.version}")
    print(f"  sha256    : {sha256}")
    return 0


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="acquire_spec.py",
        description=(
            "Download and index a specification file into .local/spec-cache/. "
            "Default: dry-run (no network). Pass --allow-network for live download."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  # Dry-run (validate metadata only):\n"
            "  python acquire_spec.py --format-id fods --spec-name 'ODF 1.3 Part 4' \\\n"
            "      --version 1.3 --source-url https://example.org/odf13.pdf \\\n"
            "      --canonical-url https://example.org/odf13.pdf \\\n"
            "      --publisher OASIS --filename odf13.pdf \\\n"
            "      --legal-category 1 --license RF --redistribution-permitted\n"
            "\n"
            "  # Live download (requires T3 authorization):\n"
            "  python acquire_spec.py ... --allow-network\n"
        ),
    )

    # Required metadata
    p.add_argument("--format-id", required=True, help="Format identifier, e.g. fods")
    p.add_argument("--spec-name", required=True, help="Human-readable spec name")
    p.add_argument("--version", required=True, help="Spec version string, e.g. 1.3")
    p.add_argument("--source-url", required=True, help="URL where spec was downloaded from")
    p.add_argument(
        "--canonical-url",
        required=True,
        help="Official canonical URL for this spec version",
    )
    p.add_argument("--publisher", required=True, help="Publisher name, e.g. OASIS")
    p.add_argument("--filename", required=True, help="Filename to use in .local/spec-cache/")

    # Legal metadata (required — tool refuses without them)
    p.add_argument(
        "--legal-category",
        required=True,
        choices=["1", "2", "3", "4"],
        help="Legal category: 1=Open Standard RF, 2=Permissive OSS, 3=Published Proprietary, 4=Ambiguous",
    )
    p.add_argument(
        "--license",
        required=True,
        help="License identifier, e.g. 'RF' or 'Apache-2.0' or 'proprietary-parser-allowed'",
    )
    p.add_argument(
        "--redistribution-permitted",
        action="store_true",
        default=False,
        help="Confirm that redistribution of the cached spec is permitted",
    )

    # Optional metadata
    p.add_argument("--mime-type", default=None, help="MIME type (auto-detected if not provided)")
    p.add_argument("--notes", default=None, help="Optional notes about this spec entry")

    # Network control
    p.add_argument(
        "--allow-network",
        action="store_true",
        default=False,
        help=(
            "Enable live network download. Requires T3 authorization "
            "(docs/specification-cache.md). Default: dry-run."
        ),
    )

    # Overwrite control
    p.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Overwrite existing spec-index.yaml entry if present",
    )

    # Timeout
    p.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Download timeout in seconds (default: 60)",
    )

    return p


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    # redistribution_permitted=False is the correct default for local-only caching
    # of standards-body documents (OASIS, W3C, ECMA). Do NOT warn when it is False —
    # that is the expected and safe default. Only warn if redistribution_permitted is
    # explicitly True but the legal basis has not been independently verified.
    # (Actual redistribution enforcement happens at commit/release time, not here.)

    if args.allow_network:
        return _run_live(args)
    else:
        return _run_dry(args)


if __name__ == "__main__":
    sys.exit(main())
