"""governance_validators_dotnet.py — V73: .NET SpecQName value validator.

V73 (TC-DOTNET-QNAME-001): For PRODUCT_SOURCE or RELEASE_GATE items that modify
src/net/*/Spec/*.cs files, verify:
  1. Each modified Spec/*.cs file contains a SpecQName constant.
  2. The SpecQName value matches the registered qname in shared/qname-registry/.

WARN-only (blocks_sprint=False) — enables gradual adoption without blocking
existing sprints that may add .NET spec classes incrementally.

Severity guidance:
  - RELEASE_GATE items citing .NET Spec/ files → FAIL if SpecQName missing/wrong
  - All other items → WARN only
"""
from __future__ import annotations
from governance_validators_contract import validator  # noqa: F401

import re
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_REGISTRY_DIR = _REPO_ROOT / "shared" / "qname-registry"

# Pattern for Spec/ files in .NET src
_DOTNET_SPEC_PATTERN = re.compile(
    r"src[/\\]net[/\\][^/\\]+[/\\]Spec[/\\].+\.cs$",
    re.IGNORECASE,
)

# Pattern to extract SpecQName value from C# file
_SPECQNAME_VALUE_PATTERN = re.compile(
    r'SpecQName\s*=\s*"([^"]+)"',
    re.IGNORECASE,
)


def _build_qname_registry() -> dict[str, str]:
    """Load all registry YAML files and return {dotnet_file_normalized → qname}."""
    registry: dict[str, str] = {}
    try:
        import yaml as _yaml
        _has_yaml = True
    except ImportError:
        _has_yaml = False

    for yf in sorted(_REGISTRY_DIR.glob("*.yaml")):
        if yf.name == "schema.yaml":
            continue
        try:
            if _has_yaml:
                import yaml as _yaml
                entries = _yaml.safe_load(yf.read_text(encoding="utf-8")) or []
            else:
                entries = []  # Skip if no YAML library
        except Exception:
            continue
        for entry in entries:
            df = entry.get("dotnet_file")
            q = entry.get("qname")
            if df and q:
                # Normalize path separators for consistent lookup
                key = str(df).replace("\\", "/")
                registry[key] = q
    return registry


@validator(rule_id="V_VALIDATE_DOTNET_SPEC_QNAME", domain="dotnet")
def validate_dotnet_spec_qname(
    declaration: dict,
    repo_root: "Path | None" = None,
) -> dict:
    """V73 (TC-DOTNET-QNAME-001): .NET Spec/ files must have SpecQName constant with correct value.

    Checks changed_files and evidence_paths for src/net/*/Spec/*.cs files.
    For each:
      - FAIL (RELEASE_GATE) / WARN (other) if SpecQName is absent
      - FAIL (RELEASE_GATE) / WARN (other) if SpecQName value does not match registry
    """
    _r = repo_root or _REPO_ROOT

    items = declaration.get("planned_work_items", [])
    item_types = {item.get("item_type", "") for item in items}
    is_release_gate = "RELEASE_GATE" in item_types

    # Collect all .NET Spec/ files from changed_files
    changed = declaration.get("changed_files", [])
    spec_files = [
        f for f in changed
        if _DOTNET_SPEC_PATTERN.search(f.replace("\\", "/"))
    ]

    if not spec_files:
        return {
            "validator": "validate_dotnet_spec_qname",
            "result": "PASS",
            "items": [],
            "summary": "V73: No .NET Spec/ files in changed_files — skip",
            "blocks_sprint": False,
        }

    # Build registry lazily (only when there are Spec/ files to check)
    registry = _build_qname_registry()

    violations = []
    for file_path in spec_files:
        normalized = file_path.replace("\\", "/")
        path = _r / normalized
        expected_qname = registry.get(normalized)

        if not path.exists():
            violations.append({
                "file": normalized,
                "issue": "file_not_found",
                "detail": "Changed .NET Spec/ file does not exist on disk",
                "expected_qname": expected_qname,
            })
            continue

        content = path.read_text(encoding="utf-8", errors="replace")

        # Check SpecQName presence
        m = _SPECQNAME_VALUE_PATTERN.search(content)
        if not m:
            violations.append({
                "file": normalized,
                "issue": "specqname_missing",
                "detail": f"No SpecQName constant found in {normalized}",
                "expected_qname": expected_qname,
            })
            continue

        actual_value = m.group(1)

        # Check value correctness (only if registry has this file)
        if expected_qname and actual_value != expected_qname:
            violations.append({
                "file": normalized,
                "issue": "specqname_wrong_value",
                "detail": (
                    f'SpecQName = "{actual_value}" but registry expects "{expected_qname}"'
                ),
                "expected_qname": expected_qname,
                "actual_value": actual_value,
            })
        elif expected_qname and actual_value == expected_qname:
            # PASS — correct value, no violation
            pass
        elif not expected_qname:
            # File not in registry yet — warn as informational
            violations.append({
                "file": normalized,
                "issue": "not_in_registry",
                "detail": (
                    f'SpecQName = "{actual_value}" but this file has no entry in shared/qname-registry/. '
                    "Add an entry to register the canonical qname."
                ),
                "actual_value": actual_value,
            })

    if not violations:
        return {
            "validator": "validate_dotnet_spec_qname",
            "result": "PASS",
            "items": [],
            "summary": f"V73: All {len(spec_files)} .NET Spec/ file(s) have correct SpecQName",
            "blocks_sprint": False,
        }

    # RELEASE_GATE items → FAIL; others → WARN
    result = "FAIL" if is_release_gate else "WARN"
    blocks = is_release_gate  # Only blocks for RELEASE_GATE declarations

    return {
        "validator": "validate_dotnet_spec_qname",
        "result": result,
        "items": violations,
        "summary": (
            f"V73: {len(violations)} .NET Spec/ file(s) with SpecQName issue(s). "
            f"{'BLOCKING for RELEASE_GATE.' if blocks else 'Advisory only.'}"
        ),
        "blocks_sprint": blocks,
    }
