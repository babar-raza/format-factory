"""generate_canonical_stubs.py — Generate architecture_only spec skeleton files from registry.

Reads shared/qname-registry/<format>.yaml and generates:
- Python: src/python/<format>/spec/<ns>/<class>.py with spec_qname attribute
- .NET: src/net/<format>/Spec/<Ns>/<Class>.cs with QName constant
- All required __init__.py files for Python packages

Idempotent: re-running produces same output.
Does NOT overwrite files with status > seeded (architecture_only, implementing, implemented, stable).

Usage:
  python tools/spec/generate_canonical_stubs.py --format fodt
  python tools/spec/generate_canonical_stubs.py --format fodt --dry-run
"""

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent

# Status values that indicate the file is already beyond seeded and should NOT be overwritten
_BEYOND_SEEDED_STATUSES = {"architecture_only", "implementing", "implemented", "stable"}


def _load_yaml_registry(registry_path: Path) -> list[dict]:
    """Load a YAML registry file as a list of dicts."""
    try:
        import yaml  # type: ignore[import]
        return yaml.safe_load(registry_path.read_text(encoding="utf-8")) or []
    except ImportError:
        pass

    # Minimal fallback YAML parser for simple registry files
    entries: list[dict] = []
    current: dict = {}
    for line in registry_path.read_text(encoding="utf-8").splitlines():
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
            # Handle YAML lists (facade_names: [...])
            if val.startswith("["):
                current[k.strip()] = []
            else:
                current[k.strip()] = None if val in ("null", "~", "") else val
    if current:
        entries.append(current)
    return entries


def _python_path_for_entry(entry: dict, format_name: str) -> str | None:
    """Return the python_file path from the registry entry, or derive it if absent."""
    python_file = entry.get("python_file")
    if python_file in (None, "null"):
        return None  # No Python equivalent for this entry
    return python_file


def _dotnet_path_for_entry(entry: dict, format_name: str) -> str | None:
    """Return the dotnet_file path from the registry entry."""
    dotnet_file = entry.get("dotnet_file")
    if dotnet_file in (None, "null"):
        return None
    return dotnet_file


def _generate_python_stub(python_file: str, entry: dict, repo_root: Path, dry_run: bool) -> str:
    """Generate (or verify) a Python architecture_only stub file. Returns action taken."""
    file_path = repo_root / python_file
    qname = entry.get("qname", "")
    spec_fact_ref = entry.get("spec_fact_ref", "")
    canonical_class = entry.get("canonical_class", "")

    # Derive class name: last part of canonical (e.g. "Text.Paragraph" → "Paragraph")
    class_name = canonical_class.split(".")[-1] if canonical_class else "SpecClass"

    # Check if file already exists with status > seeded
    if file_path.exists():
        existing = file_path.read_text(encoding="utf-8", errors="replace")
        status = entry.get("status", "seeded")
        if status in _BEYOND_SEEDED_STATUSES:
            return f"SKIP (status={status})"
        # Even if seeded, don't overwrite if spec_qname is already correct
        if f'spec_qname = "{qname}"' in existing:
            return "SKIP (already correct)"

    content = f'''# GENERATED — architecture_only. Do not implement here until compat.py switch is ready.
# spec_fact_ref: {spec_fact_ref}
class {class_name}:
    spec_qname = "{qname}"
    spec_fact_ref = "{spec_fact_ref}"
    # TODO: implement to match legacy model class once compat.py switch is authorized
'''

    if not dry_run:
        # Create all required __init__.py files for Python package directories
        _ensure_python_packages(file_path, repo_root, dry_run)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return "CREATED"
    return "DRY_RUN"


def _ensure_python_packages(file_path: Path, repo_root: Path, dry_run: bool) -> None:
    """Create __init__.py in all parent directories up to src/python/<format>/spec."""
    # Find the spec/ directory boundary
    parts = file_path.parts
    spec_idx = None
    for i, part in enumerate(parts):
        if part == "spec":
            spec_idx = i
            break

    if spec_idx is None:
        return

    # Create __init__.py in spec/ and all subdirectories up to file's parent
    spec_dir = Path(*parts[: spec_idx + 1])
    current = spec_dir
    while current != file_path.parent:
        init_file = current / "__init__.py"
        if not init_file.exists() and not dry_run:
            current.mkdir(parents=True, exist_ok=True)
            init_file.write_text("", encoding="utf-8")
        current = current / parts[len(current.parts)]

    # Also create in file's parent
    init_file = file_path.parent / "__init__.py"
    if not init_file.exists() and not dry_run:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        init_file.write_text("", encoding="utf-8")


def _generate_dotnet_stub(dotnet_file: str, entry: dict, repo_root: Path, dry_run: bool) -> str:
    """Generate (or verify) a .NET architecture_only stub file. Returns action taken."""
    file_path = repo_root / dotnet_file
    qname = entry.get("qname", "")
    spec_fact_ref = entry.get("spec_fact_ref", "")
    canonical_class = entry.get("canonical_class", "")

    # Derive namespace and class from path and canonical_class
    class_name = canonical_class.split(".")[-1] if canonical_class else "SpecClass"
    # Build .NET namespace from file path: src/net/fodt/Spec/Text/Paragraph.cs → FormatFactory.Fodt.Spec.Text
    parts = file_path.parts
    try:
        net_idx = next(i for i, p in enumerate(parts) if p == "net")
        ns_parts = parts[net_idx + 1 : -1]  # e.g. ("fodt", "Spec", "Text")
        namespace = "FormatFactory." + ".".join(p.capitalize() for p in ns_parts)
    except (StopIteration, ValueError):
        namespace = "FormatFactory.Spec"

    # Check if file already exists with status > seeded
    if file_path.exists():
        existing = file_path.read_text(encoding="utf-8", errors="replace")
        status = entry.get("status", "seeded")
        if status in _BEYOND_SEEDED_STATUSES:
            return f"SKIP (status={status})"
        if f'QName = "{qname}"' in existing:
            return "SKIP (already correct)"

    content = f'''// GENERATED — architecture_only. Do not implement here until migration is authorized.
// spec_fact_ref: {spec_fact_ref}
namespace {namespace};

public static class {class_name}
{{
    public const string QName = "{qname}";
    public const string SpecFactRef = "{spec_fact_ref}";
    // TODO: implement once canonical migration plan is authorized
}}
'''

    if not dry_run:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return "CREATED"
    return "DRY_RUN"


def generate_stubs(
    format_name: str,
    repo_root: Path,
    dry_run: bool = False,
    verbose: bool = True,
) -> dict:
    """Generate all stubs for a format. Returns summary dict."""
    registry_path = repo_root / "shared" / "qname-registry" / f"{format_name}.yaml"

    if not registry_path.exists():
        return {
            "error": f"Registry not found: {registry_path}",
            "python_created": 0,
            "dotnet_created": 0,
            "skipped": 0,
        }

    entries = _load_yaml_registry(registry_path)
    results: list[dict] = []
    python_created = dotnet_created = skipped = 0

    for entry in entries:
        qname = entry.get("qname", "<unknown>")
        py_path = _python_path_for_entry(entry, format_name)
        dn_path = _dotnet_path_for_entry(entry, format_name)
        row: dict = {"qname": qname}

        if py_path:
            action = _generate_python_stub(py_path, entry, repo_root, dry_run)
            row["python"] = action
            if action == "CREATED":
                python_created += 1
            elif action.startswith("SKIP"):
                skipped += 1
        else:
            row["python"] = "NULL (no python_file)"

        if dn_path:
            action = _generate_dotnet_stub(dn_path, entry, repo_root, dry_run)
            row["dotnet"] = action
            if action == "CREATED":
                dotnet_created += 1
            elif action.startswith("SKIP"):
                skipped += 1
        else:
            row["dotnet"] = "NULL (no dotnet_file)"

        results.append(row)

    if verbose:
        label = "[DRY-RUN] " if dry_run else ""
        print(f"{label}generate_canonical_stubs — format: {format_name}")
        for row in results:
            print(f"  {row['qname']}")
            print(f"    python: {row.get('python', 'N/A')}")
            print(f"    dotnet: {row.get('dotnet', 'N/A')}")
        print(
            f"\nSummary: {python_created} Python created, "
            f"{dotnet_created} .NET created, {skipped} skipped"
        )

    return {
        "python_created": python_created,
        "dotnet_created": dotnet_created,
        "skipped": skipped,
        "results": results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate architecture_only spec stubs from canonical registry"
    )
    parser.add_argument("--format", required=True, help="Format name (e.g. fodt, fods)")
    parser.add_argument("--repo-root", default=None, help="Override repo root path")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be created without writing files")
    parser.add_argument("--quiet", action="store_true", help="Suppress output")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root) if args.repo_root else REPO_ROOT
    summary = generate_stubs(
        format_name=args.format,
        repo_root=repo_root,
        dry_run=args.dry_run,
        verbose=not args.quiet,
    )

    if "error" in summary:
        print(f"ERROR: {summary['error']}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
