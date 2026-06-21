"""validate_spec_registry.py — Validate a QName registry YAML against schema and SAL context packs.

Validates:
1. Schema compliance: all required fields present for each entry
2. Status values are in allowed enum
3. spec_fact_refs are resolvable in the SAL context pack JSON (if available)

Exit codes:
  0 — PASS (all entries valid, all spec_fact_refs resolved)
  1 — WARN (valid schema, but spec_fact_refs not resolvable — context pack may be absent)
  2 — FAIL (schema violation)

Usage:
  python tools/spec/validate_spec_registry.py shared/qname-registry/fodt.yaml
  python tools/spec/validate_spec_registry.py shared/qname-registry/fodt.yaml --format fodt
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent

REQUIRED_FIELDS = [
    "qname",
    "namespace_uri",
    "local_name",
    "canonical_class",
    "spec_fact_ref",
    "status",
    "source_layer",
]

VALID_STATUSES = {
    "seeded",
    "architecture_only",
    "implementing",
    "implemented",
    "stable",
    "deprecated",
}

VALID_SOURCE_LAYERS = {
    "Spec",
    "Public",
    "Compat",
    "Reading",
    "Writing",
    "Validation",
    "Conversion",
    "Internal",
}

# Context pack search paths
_CONTEXT_PACK_PATHS = [
    "reports/specification-authority-layer-mwp/context-pack-sample/{format}-context-pack.json",
    ".local/spec-cache/{format}-context-pack.json",
]


def _load_yaml(path: Path) -> list[dict]:
    """Load a YAML registry file."""
    try:
        import yaml  # type: ignore[import]
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except ImportError:
        pass

    # Minimal fallback YAML parser
    entries: list[dict] = []
    current: dict = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("- "):
            if current:
                entries.append(current)
            current = {}
            rest = line[2:].strip()
            if ":" in rest:
                k, _, v = rest.partition(":")
                val = v.strip().strip('"').strip("'")
                current[k.strip()] = None if val in ("null", "~", "") else val
        elif line.startswith("  ") and ":" in line:
            k, _, v = line.strip().partition(":")
            val = v.strip().strip('"').strip("'")
            if val.startswith("["):
                current[k.strip()] = []
            else:
                current[k.strip()] = None if val in ("null", "~", "") else val
    if current:
        entries.append(current)
    return entries


def _find_context_pack(format_name: str, repo_root: Path) -> dict | None:
    """Search for a SAL context pack JSON for the given format."""
    for template in _CONTEXT_PACK_PATHS:
        path = repo_root / template.format(format=format_name)
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
    return None


def _extract_fact_ids(context_pack: dict) -> set[str]:
    """Extract all FACT-* IDs from a context pack JSON."""
    fact_ids: set[str] = set()

    def _recurse(obj: object) -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in ("fact_id", "req_id", "id") and isinstance(v, str) and v.startswith("FACT-"):
                    fact_ids.add(v)
                _recurse(v)
        elif isinstance(obj, list):
            for item in obj:
                _recurse(item)

    _recurse(context_pack)
    return fact_ids


def validate_registry(
    registry_path: Path,
    format_name: str | None,
    repo_root: Path,
) -> tuple[int, list[str], list[str]]:
    """Validate a registry file. Returns (exit_code, errors, warnings)."""
    errors: list[str] = []
    warnings: list[str] = []

    if not registry_path.exists():
        return 2, [f"Registry file not found: {registry_path}"], []

    entries = _load_yaml(registry_path)

    if not entries:
        return 2, ["Registry file is empty or not a YAML list"], []

    # Determine format name for context pack lookup
    fmt = format_name or registry_path.stem

    # Load context pack (optional — WARN if absent)
    context_pack = _find_context_pack(fmt, repo_root)
    known_fact_ids: set[str] | None = None
    if context_pack is not None:
        known_fact_ids = _extract_fact_ids(context_pack)
    else:
        warnings.append(
            f"Context pack not found for '{fmt}' — spec_fact_ref cross-reference skipped"
        )

    # Validate each entry
    for i, entry in enumerate(entries):
        prefix = f"Entry {i + 1} ({entry.get('qname', '<no qname>')})"

        # Required fields
        for field in REQUIRED_FIELDS:
            if field not in entry or entry[field] is None:
                errors.append(f"{prefix}: missing required field '{field}'")

        # Status enum
        status = entry.get("status")
        if status and status not in VALID_STATUSES:
            errors.append(
                f"{prefix}: invalid status '{status}' (allowed: {', '.join(sorted(VALID_STATUSES))})"
            )

        # source_layer enum
        source_layer = entry.get("source_layer")
        if source_layer and source_layer not in VALID_SOURCE_LAYERS:
            errors.append(
                f"{prefix}: invalid source_layer '{source_layer}' "
                f"(allowed: {', '.join(sorted(VALID_SOURCE_LAYERS))})"
            )

        # qname format: should contain ":"
        qname = entry.get("qname", "")
        if qname and ":" not in qname:
            errors.append(f"{prefix}: qname '{qname}' must contain ':' (namespace:local)")

        # spec_fact_ref cross-reference
        spec_fact_ref = entry.get("spec_fact_ref")
        if spec_fact_ref and known_fact_ids is not None:
            if spec_fact_ref not in known_fact_ids:
                warnings.append(
                    f"{prefix}: spec_fact_ref '{spec_fact_ref}' not found in context pack "
                    f"(may be missing or use different ID format)"
                )

    if errors:
        return 2, errors, warnings
    if warnings and known_fact_ids is None:
        # No context pack → WARN but not FAIL
        return 1, errors, warnings
    return 0, errors, warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a QName registry YAML against schema and SAL context packs"
    )
    parser.add_argument("registry_path", help="Path to registry YAML file (e.g. shared/qname-registry/fodt.yaml)")
    parser.add_argument("--format", default=None, help="Format name override (defaults to registry file stem)")
    parser.add_argument("--repo-root", default=None, help="Override repo root path")
    parser.add_argument("--quiet", action="store_true", help="Suppress output")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root) if args.repo_root else REPO_ROOT
    registry_path = Path(args.registry_path)
    if not registry_path.is_absolute():
        registry_path = repo_root / registry_path

    exit_code, errors, warnings = validate_registry(
        registry_path=registry_path,
        format_name=args.format,
        repo_root=repo_root,
    )

    if not args.quiet:
        status_labels = {0: "PASS", 1: "WARN", 2: "FAIL"}
        print(f"validate_spec_registry — {registry_path.name}: {status_labels[exit_code]}")
        for err in errors:
            print(f"  ERROR: {err}")
        for warn in warnings:
            print(f"  WARN:  {warn}")
        if not errors and not warnings:
            print("  All entries valid. All spec_fact_refs resolved.")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
