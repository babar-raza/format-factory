"""governance_validators_dotnet.py — V73 (.NET SpecQName) + V78_AGG (partial class aggregate LOC).

V73 (TC-DOTNET-QNAME-001): For PRODUCT_SOURCE or RELEASE_GATE items that modify
src/net/*/Spec/*.cs files, verify:
  1. Each modified Spec/*.cs file contains a SpecQName constant.
  2. The SpecQName value matches the registered qname in shared/qname-registry/.

WARN-only (blocks_sprint=False) — enables gradual adoption without blocking
existing sprints that may add .NET spec classes incrementally.

Severity guidance:
  - RELEASE_GATE items citing .NET Spec/ files → FAIL if SpecQName missing/wrong
  - All other items → WARN only

V78_AGG (TC-SPW-001): Enforce LOC at per-class-aggregate granularity across partial class files.
  Complements V78 per-file enforcement with class-level aggregate tracking.
  Exclusion config: .supervisor/schemas/partial-class-exclusions.json
"""
from __future__ import annotations
from governance_validators_contract import validator  # noqa: F401

import json
import re
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_REGISTRY_DIR = _REPO_ROOT / "shared" / "qname-registry"
_EXCLUSIONS_CONFIG = _REPO_ROOT / ".supervisor" / "schemas" / "partial-class-exclusions.json"
_BASELINE_PATH = _REPO_ROOT / "registry" / "source-structure-baseline.json"

# Partial class detection regex (TC-SPW-001-02 confirmed pattern)
_PARTIAL_CLASS_PATTERN = re.compile(r"\bpartial\s+class\s+(\w+)")

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


def _load_exclusion_config() -> dict:
    """Load partial-class-exclusions.json; return defaults on any error."""
    defaults: dict = {
        "suffix_exclusions": ["*.g.cs", "*.designer.cs", "*.generated.cs"],
        "directory_exclusions": ["test", "tests", "build", "obj", "bin"],
        "class_name_exclusions": [],
    }
    try:
        return json.loads(_EXCLUSIONS_CONFIG.read_text(encoding="utf-8"))
    except Exception:
        return defaults


def collect_partial_class_aggregates(
    src_net_root: "Path",
    exclusion_config: "dict | None" = None,
) -> "dict[str, list[tuple[Path, int]]]":
    """Group .cs files by partial class name and compute LOC per group.

    Returns {class_name: [(file_path, loc), ...]} for classes with ≥2 partial files.
    Excludes generated code (*.g.cs, *.designer.cs) and build directories.
    TC-SPW-001-03 (REQ-MEAS-001).
    """
    if exclusion_config is None:
        exclusion_config = _load_exclusion_config()

    suffix_exclusions: list[str] = exclusion_config.get("suffix_exclusions", [])
    dir_exclusions: set[str] = set(exclusion_config.get("directory_exclusions", []))
    # Normalize suffixes — strip leading '*'
    suffix_set: set[str] = {s.lstrip("*") for s in suffix_exclusions}

    class_map: dict[str, list[tuple[Path, int]]] = {}
    # Track (class_name, file) pairs already added — a file may declare multiple
    # partial classes, but should only appear once per class in the group.
    seen: set[tuple[str, Path]] = set()

    src_root = Path(src_net_root)
    if not src_root.is_dir():
        return {}

    for cs_file in sorted(src_root.rglob("*.cs")):
        # Skip excluded directories
        if any(part.lower() in dir_exclusions for part in cs_file.parts):
            continue
        # Skip excluded suffixes (*.g.cs etc.)
        name_lower = cs_file.name.lower()
        if any(name_lower.endswith(suf.lower()) for suf in suffix_set):
            continue

        try:
            content = cs_file.read_text(encoding="utf-8", errors="replace")
            loc = content.count("\n") + (1 if content and not content.endswith("\n") else 0)
        except Exception:
            continue

        for m in _PARTIAL_CLASS_PATTERN.finditer(content):
            class_name = m.group(1)
            key = (class_name, cs_file)
            if key in seen:
                continue
            seen.add(key)
            if class_name not in class_map:
                class_map[class_name] = []
            class_map[class_name].append((cs_file, loc))

    # Return only classes appearing in ≥2 files (true partial classes)
    return {cn: files for cn, files in class_map.items() if len(files) >= 2}


def _load_aggregate_baselines() -> dict:
    """Load partial_class_aggregates section from source-structure-baseline.json."""
    try:
        data = json.loads(_BASELINE_PATH.read_text(encoding="utf-8"))
        return data.get("partial_class_aggregates", {})
    except Exception:
        return {}


def _get_aggregate_cap(class_name: str, file_count: int, baselines: dict) -> int:
    """Return aggregate LOC cap for a class.

    If class is in baselines, use its aggregate_cap.
    Otherwise: 2000 for classes with >3 files, 2000 for 2-3 files (partial design).
    """
    if class_name in baselines:
        return int(baselines[class_name].get("aggregate_cap", 2000))
    return 2000


@validator(rule_id="V78_AGG", domain="dotnet")
def validate_dotnet_aggregate_loc_cap(
    declaration: dict,
    repo_root: "Path | None" = None,
) -> dict:
    """V78_AGG (TC-SPW-001): Enforce per-class-aggregate LOC cap across partial class files.

    Complements V78 (per-file) by summing LOC across all partial class files.
    Known aggregate violations are WARN (blocks_sprint=False).
    New violations exceeding cap → FAIL (blocks_sprint=True).
    Trajectory check: sprint touching known aggregate group must not grow aggregate.
    """
    _r = repo_root or _REPO_ROOT
    src_net = _r / "src" / "net"

    exclusion_config = _load_exclusion_config()
    baselines = _load_aggregate_baselines()

    aggregates = collect_partial_class_aggregates(src_net, exclusion_config)

    if not aggregates:
        return {
            "validator": "validate_dotnet_aggregate_loc_cap",
            "rule_id": "V78_AGG",
            "result": "PASS",
            "items": [],
            "summary": "V78_AGG: No partial class aggregates found — skip",
            "blocks_sprint": False,
        }

    changed_files: list[str] = declaration.get("changed_files", [])
    changed_normalized = {f.replace("\\", "/") for f in changed_files}

    violations: list[dict] = []
    known_violation_warns: list[dict] = []

    for class_name, files in aggregates.items():
        aggregate_loc = sum(loc for _, loc in files)
        cap = _get_aggregate_cap(class_name, len(files), baselines)
        is_known = class_name in baselines

        # Check if any file in this group was touched this sprint
        file_paths_normalized = {f.as_posix().replace("\\", "/") for f, _ in files}
        sprint_touched = bool(changed_normalized & file_paths_normalized)

        if is_known:
            known_cap = int(baselines[class_name].get("aggregate_cap", cap))
            if sprint_touched and aggregate_loc > known_cap:
                # Trajectory failure: known violation grew beyond frozen cap
                violations.append({
                    "class_name": class_name,
                    "issue": "TRAJECTORY_FAIL",
                    "aggregate_loc": aggregate_loc,
                    "aggregate_cap": known_cap,
                    "file_count": len(files),
                    "detail": (
                        f"{class_name} aggregate {aggregate_loc} LOC exceeded frozen cap "
                        f"{known_cap} LOC — sprint touched this class group and it grew"
                    ),
                })
            else:
                # Known violation, stable or not touched → WARN only
                known_violation_warns.append({
                    "class_name": class_name,
                    "issue": "KNOWN_VIOLATION",
                    "aggregate_loc": aggregate_loc,
                    "aggregate_cap": known_cap,
                    "file_count": len(files),
                    "detail": (
                        f"{class_name}: {aggregate_loc} LOC aggregate (known violation, "
                        f"cap={known_cap})"
                    ),
                })
        elif aggregate_loc > cap:
            # New violation — not in baselines, exceeds default cap
            violations.append({
                "class_name": class_name,
                "issue": "NEW_AGGREGATE_VIOLATION",
                "aggregate_loc": aggregate_loc,
                "aggregate_cap": cap,
                "file_count": len(files),
                "detail": (
                    f"{class_name}: {aggregate_loc} LOC aggregate exceeds {cap} LOC cap "
                    f"across {len(files)} partial class files"
                ),
            })

    if violations:
        return {
            "validator": "validate_dotnet_aggregate_loc_cap",
            "rule_id": "V78_AGG",
            "result": "FAIL",
            "items": violations + known_violation_warns,
            "summary": (
                f"V78_AGG: {len(violations)} aggregate violation(s) "
                f"(+ {len(known_violation_warns)} known). blocks_sprint=True"
            ),
            "blocks_sprint": True,
        }

    if known_violation_warns:
        return {
            "validator": "validate_dotnet_aggregate_loc_cap",
            "rule_id": "V78_AGG",
            "result": "WARN",
            "items": known_violation_warns,
            "summary": (
                f"V78_AGG: {len(known_violation_warns)} known aggregate violation(s) — "
                f"stable/untouched. Advisory only."
            ),
            "blocks_sprint": False,
        }

    return {
        "validator": "validate_dotnet_aggregate_loc_cap",
        "rule_id": "V78_AGG",
        "result": "PASS",
        "items": [],
        "summary": f"V78_AGG: {len(aggregates)} partial class group(s) within aggregate caps",
        "blocks_sprint": False,
    }


_FORMAT_REGISTRY_PATH = _REPO_ROOT / "registry" / "format-registry.yaml"
_TESTS_NET_ROOT = _REPO_ROOT / "tests" / "net"

# Round-trip detection patterns: a file qualifies if it contains BOTH a write token AND a read token
_RT_WRITE = re.compile(r"\b(?:Save|Write)\s*\(", re.IGNORECASE)
_RT_READ = re.compile(r"\b(?:Load|Parse)\s*\(", re.IGNORECASE)


def _gate1_formats_from_registry() -> set[str]:
    """Return set of format IDs whose gate_1.status == 'passed' in format-registry.yaml."""
    try:
        import yaml as _yaml
        data = _yaml.safe_load(_FORMAT_REGISTRY_PATH.read_text(encoding="utf-8")) or {}
        formats = data.get("formats", [])
        gate1 = set()
        for fmt in (formats if isinstance(formats, list) else []):
            fmt_id = fmt.get("format_id") or fmt.get("id") or ""
            gates = fmt.get("gates", {})
            if isinstance(gates, dict) and gates.get("gate_1", {}).get("status") == "passed":
                gate1.add(str(fmt_id).lower())
        return gate1
    except Exception:
        return set()


def _has_roundtrip_test(format_id: str) -> bool:
    """Return True if tests/net/{format_id}/ contains ≥1 .cs file with both write and read calls."""
    test_dir = _TESTS_NET_ROOT / format_id
    if not test_dir.is_dir():
        return False
    for cs_file in test_dir.rglob("*.cs"):
        try:
            content = cs_file.read_text(encoding="utf-8", errors="replace")
            if _RT_WRITE.search(content) and _RT_READ.search(content):
                return True
        except Exception:
            continue
    return False


def _infer_formats_from_declaration(declaration: dict) -> set[str]:
    """Infer format IDs from format_targets or src/net/{format}/ paths in changed_files."""
    targets = declaration.get("format_targets", [])
    if isinstance(targets, list) and targets:
        return {str(t).lower() for t in targets}
    # Fallback: parse from changed_files
    changed = declaration.get("changed_files", [])
    formats: set[str] = set()
    _src_net = re.compile(r"src[/\\]net[/\\]([^/\\]+)[/\\]")
    for f in changed:
        m = _src_net.search(str(f).replace("\\", "/"))
        if m:
            formats.add(m.group(1).lower())
    return formats


@validator(rule_id="V152", domain="dotnet")
def validate_format_roundtrip_coverage(
    declaration: dict,
    repo_root: "Path | None" = None,
) -> dict:
    """V152 (TC-SPW-003B): Gate-1 formats must have a .NET round-trip test.

    A round-trip test is any .cs file in tests/net/{format}/ containing BOTH
    a write call (Save/Write) AND a read call (Load/Parse).

    Returns FAIL+blocks_sprint=True (GOV_BLOCK) when any Gate-1 format has no round-trip test.
    Returns PASS when all Gate-1 formats in scope have coverage.
    Non-blocking if format-registry.yaml is unavailable.
    """
    gate1 = _gate1_formats_from_registry()
    if not gate1:
        return {
            "validator": "validate_format_roundtrip_coverage",
            "rule_id": "V152",
            "result": "PASS",
            "items": [],
            "summary": "V152: format-registry.yaml unavailable — skip (non-blocking)",
            "blocks_sprint": False,
        }

    format_targets = _infer_formats_from_declaration(declaration)
    # Only check formats that are in scope for this declaration AND are Gate-1
    in_scope = format_targets & gate1
    if not in_scope:
        return {
            "validator": "validate_format_roundtrip_coverage",
            "rule_id": "V152",
            "result": "PASS",
            "items": [],
            "summary": "V152: No Gate-1 formats in scope for this declaration",
            "blocks_sprint": False,
        }

    missing: list[dict] = []
    for fmt in sorted(in_scope):
        if not _has_roundtrip_test(fmt):
            missing.append({"format": fmt, "issue": "NO_ROUNDTRIP_TEST",
                            "test_dir": str(_TESTS_NET_ROOT / fmt)})

    if missing:
        return {
            "validator": "validate_format_roundtrip_coverage",
            "rule_id": "V152",
            "result": "FAIL",
            "items": missing,
            "summary": (
                f"V152: {len(missing)} Gate-1 format(s) have no .NET round-trip test: "
                + ", ".join(i["format"] for i in missing)
            ),
            "blocks_sprint": True,
        }

    return {
        "validator": "validate_format_roundtrip_coverage",
        "rule_id": "V152",
        "result": "PASS",
        "items": [],
        "summary": f"V152: {len(in_scope)} Gate-1 format(s) have round-trip test coverage",
        "blocks_sprint": False,
    }


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
