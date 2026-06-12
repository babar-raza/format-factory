#!/usr/bin/env python3
"""
validate_oracle_environment.py — Check the oracle execution environment
against the provider registry.

Usage:
    python validate_oracle_environment.py [--format FODS] [--registry provider_registry.yaml]
    python validate_oracle_environment.py --list-formats

Reads tools/oracle/provider_registry.yaml to determine which provider is
approved for the requested format gate, then checks whether that provider is
discoverable on the local machine.

Outputs a machine-readable status report and exits:
  0 — all required providers are present and functional
  1 — one or more required providers are missing or not functional
"""

import argparse
import subprocess
import sys
from pathlib import Path

try:
    import yaml
    _YAML = True
except ImportError:
    _YAML = False

# ---------------------------------------------------------------------------
# Registry loading
# ---------------------------------------------------------------------------

_DEFAULT_REGISTRY = Path(__file__).parent / "provider_registry.yaml"


def load_registry(registry_path: Path) -> dict:
    """Load the provider registry YAML."""
    if not registry_path.exists():
        print(f"ERROR: Registry not found: {registry_path}")
        sys.exit(1)
    text = registry_path.read_text(encoding="utf-8")
    if _YAML:
        return yaml.safe_load(text)
    # Minimal fallback: just return empty structure
    print("WARNING: PyYAML not installed; using minimal fallback parser")
    return {}


def get_provider_def(registry: dict, provider_id: str) -> dict | None:
    """Look up a provider definition by ID."""
    for p in registry.get("providers", []):
        if p.get("provider_id") == provider_id:
            return p
    return None


def get_format_assignment(registry: dict, format_id: str) -> dict | None:
    """Look up a format's provider assignment."""
    return registry.get("format_provider_assignments", {}).get(format_id.lower())


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

def discover_provider(provider_def: dict) -> tuple[str | None, str | None]:
    """Try to find the oracle binary on the local machine.

    Checks (in order):
      1. Environment variable specified in provider_def.discovery.env_var
      2. Binary names via PATH (standard_paths checked directly)

    Returns (path_str, version_str) or (None, None) if not found.
    """
    import os
    import shutil

    discovery = provider_def.get("discovery", {})
    env_var = discovery.get("env_var", "")
    binary_names = discovery.get("binary_names", [])
    standard_paths = discovery.get("standard_paths", [])
    version_flag = provider_def.get("version_flag", "--version")

    # 1. Environment variable override
    if env_var:
        override = os.environ.get(env_var, "")
        if override:
            p = Path(override)
            if p.exists():
                ver = _get_version(str(p), version_flag)
                return str(p), ver

    # 2. Binary names in PATH
    for name in binary_names:
        found = shutil.which(name)
        if found:
            ver = _get_version(found, version_flag)
            return found, ver

    # 3. Standard paths
    for path_str in standard_paths:
        p = Path(path_str)
        if p.exists():
            ver = _get_version(str(p), version_flag)
            return str(p), ver

    return None, None


def _get_version(binary: str, version_flag: str) -> str | None:
    """Run binary --version and return first line, or None on failure."""
    try:
        result = subprocess.run(
            [binary, version_flag],
            capture_output=True,
            text=True,
            timeout=10,
        )
        out = (result.stdout or result.stderr or "").strip()
        if out:
            return out.splitlines()[0]
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_format(format_id: str, registry: dict) -> bool:
    """Validate that the oracle environment is ready for the given format.

    Returns True if ready, False if blocked.
    """
    assignment = get_format_assignment(registry, format_id)
    if not assignment:
        print(f"ERROR: Format '{format_id}' not found in provider registry.")
        return False

    gate = assignment.get("gate", "?")
    approved = assignment.get("approved_providers", [])
    current_status = assignment.get("current_status", "unknown")

    print("=" * 60)
    print(f"Oracle Environment Validation: {format_id.upper()} Gate {gate}")
    print("=" * 60)
    print(f"Current status: {current_status}")
    print(f"Approved providers: {', '.join(approved)}")
    print()

    all_ok = True

    for provider_id in approved:
        provider_def = get_provider_def(registry, provider_id)
        if not provider_def:
            print(f"  WARN: Provider '{provider_id}' listed in assignment but not defined in registry.")
            all_ok = False
            continue

        print(f"Provider: {provider_def.get('display_name', provider_id)}")
        print(f"  Required minimum version: {provider_def.get('version_minimum', 'unspecified')}")
        print(f"  Recommended version: {provider_def.get('version_recommended', 'unspecified')}")

        path, version = discover_provider(provider_def)
        if path:
            print("  Status: FOUND")
            print(f"  Path: {path}")
            print(f"  Version: {version or 'could not determine'}")
        else:
            print("  Status: NOT FOUND")
            print(f"  Checked env var: {provider_def.get('discovery', {}).get('env_var', 'none')}")
            n_paths = len(provider_def.get("discovery", {}).get("standard_paths", []))
            print(f"  Checked {n_paths} standard path(s)")
            checklist = provider_def.get("acquisition_pack", "")
            if checklist:
                print(f"  Installation guide: {checklist}")
            all_ok = False
        print()

    if all_ok:
        print(f"ORACLE_ENV: READY — all required providers present for {format_id.upper()} Gate {gate}")
    else:
        print(f"ORACLE_ENV: BLOCKED — required provider(s) missing for {format_id.upper()} Gate {gate}")
        blocker = assignment.get("blocker_report", "")
        if blocker:
            print(f"Blocker report: {blocker}")

    return all_ok


def list_formats(registry: dict) -> None:
    """Print all registered format assignments."""
    assignments = registry.get("format_provider_assignments", {})
    if not assignments:
        print("No format assignments registered.")
        return
    print("Registered format assignments:")
    for fmt, info in assignments.items():
        providers = ", ".join(info.get("approved_providers", []))
        gate = info.get("gate", "?")
        status = info.get("current_status", "unknown")
        print(f"  {fmt.upper()}: Gate {gate}, providers=[{providers}], status={status}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Validate oracle execution environment against provider registry"
    )
    parser.add_argument("--format", default="fods",
                        help="Format ID to validate (default: fods)")
    parser.add_argument("--registry",
                        default=str(_DEFAULT_REGISTRY),
                        help="Path to provider_registry.yaml")
    parser.add_argument("--list-formats", action="store_true",
                        help="List all registered formats and exit")
    args = parser.parse_args()

    registry = load_registry(Path(args.registry))

    if args.list_formats:
        list_formats(registry)
        sys.exit(0)

    ok = validate_format(args.format, registry)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
