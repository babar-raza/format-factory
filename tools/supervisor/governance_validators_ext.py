"""governance_validators_ext.py — Extension validators for governance_validators.py

This file exists to keep governance_validators.py within its baseline_loc_cap.
New validators (V48+) are placed here and imported at the bottom of governance_validators.py.

Pattern mirrors analytics extraction pattern used for format codecs:
  governance_validators.py imports from governance_validators_ext at module bottom.
  governance_validator_runner.py registers both sets of validators in run_all_governance_validators().

TC-WHALE-GOVBLOCK-001 (2026-06-21): V48 extracted here per source baseline LOC cap policy.
TC-ANAL-SEG-HEAL-001 (2026-06-22): V50 added here — MODULE-NAME-001 forbidden module names.
TC-QHARD-001 (2026-06-22): V51 validate_spec_qname_coverage — exported classes must have spec_qname.
TC-QHARD-002 (2026-06-22): V52 validate_compat_import_integrity — Compat/ facades import from real spec/ classes.
TC-QHARD-003 (2026-06-22): V53 validate_spec_authority_class_completeness — registry python_file entries exist.
"""

from __future__ import annotations

import ast
import re as _re
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def validate_architecture_only_stub_gate(
    declaration: dict, repo_root: Path | None = None
) -> dict:
    """V48 (TC-ZS-001): RELEASE_GATE and Gate 11 items must not cite architecture_only stubs.

    Scans evidence_paths for all RELEASE_GATE items. If any cited file contains the
    'GENERATED — architecture_only' marker, the sprint is blocked.
    For PRODUCT_SOURCE items: WARN only (blocks_sprint=False).

    Prevents architectural skeleton stubs from being accepted as behavioral proof
    at commercial gate checkpoints (Gate 11, RELEASE_GATE).
    Implemented 2026-06-21 (ZERO-STUB-AUDIT-20260621, TC-ZS-001).
    Extracted to governance_validators_ext.py (TC-WHALE-GOVBLOCK-001, 2026-06-21).
    """
    repo = repo_root or _REPO_ROOT
    _ARCH_MARKER = "GENERATED \u2014 architecture_only"
    _ARCH_MARKER2 = "architecture_only"
    gate_violations = []
    product_warnings = []

    for item in declaration.get("planned_work_items", []):
        itype = item.get("item_type", "")
        is_gate = itype in ("RELEASE_GATE", "READINESS")
        is_product = itype in ("PRODUCT_SOURCE", "PRODUCT_TEST")
        if not (is_gate or is_product):
            continue
        item_id = item.get("item_id", "UNKNOWN")
        for path_str in item.get("evidence_paths", []):
            if not (path_str.endswith(".py") or path_str.endswith(".cs")):
                continue
            p = (repo / path_str) if not Path(path_str).is_absolute() else Path(path_str)
            if not p.exists():
                continue
            try:
                first_lines = p.read_text(encoding="utf-8", errors="replace")[:500]
            except OSError:
                continue
            if _ARCH_MARKER in first_lines or (
                _ARCH_MARKER2 in first_lines and "TODO" in first_lines
            ):
                entry = {
                    "item_id": item_id,
                    "evidence_path": path_str,
                    "issue": "Evidence file is an architecture_only stub \u2014 not behavioral proof",
                }
                if is_gate:
                    gate_violations.append(entry)
                else:
                    product_warnings.append(entry)

    all_issues = gate_violations + product_warnings
    result = "FAIL" if gate_violations else ("WARN" if product_warnings else "PASS")
    return {
        "validator": "validate_architecture_only_stub_gate",
        "result": result,
        "items": all_issues,
        "summary": (
            f"V48: {len(gate_violations)} RELEASE_GATE item(s) cite architecture_only stubs (blocked); "
            f"{len(product_warnings)} PRODUCT item(s) cite stubs (warned)"
            if all_issues else "V48: No architecture_only stubs cited as evidence"
        ),
        "blocks_sprint": bool(gate_violations),
    }


def validate_forbidden_module_names(
    declaration: dict, repo_root: Path | None = None
) -> dict:
    """V50 — MODULE-NAME-001: Forbid generic analytics-bucket module names.

    Blocks creation of NEW files matching:
      *_analytics_extra.py, *_extra.py, *_misc.py
      *_helpers.py / *_utils.py containing format-prefixed spec behavior

    Deletion of these files (where file does NOT exist on disk) is ALWAYS allowed.
    The validator checks Path(repo / path).exists() before flagging — so deleting
    a forbidden-named file in a sprint does NOT cause this validator to self-block.

    These names indicate code grouped by convenience, not spec hierarchy.
    Every product module must map to a spec section, element, or domain concept.

    Added 2026-06-22 (TC-ANAL-SEG-HEAL-001) as part of spec-level segregation healing.
    """
    import re

    repo = repo_root or _REPO_ROOT
    FORBIDDEN = re.compile(
        r"src/python/[^/]+/[^/]+_(analytics_extra|extra|misc)\.py$"
    )
    CONDITIONAL = re.compile(
        r"src/python/[^/]+/[^/]+_(helpers|utils)\.py$"
    )
    FORMAT_FN = re.compile(
        r"def (?:abw|csv|dif|fodg|fods|fodt|fodp|gnumeric|ndjson|"
        r"ods|odt|pbm|pgm|ppm|qoi|sylk|toml|tsv|xcf|zst)_"
    )

    violations = []
    changed = declaration.get("changed_files", [])
    for path in changed:
        # CRITICAL: skip files being DELETED (they don't exist on disk).
        # Allows deletion sprints to remove forbidden-named files without self-blocking.
        full_path = repo / path
        if not full_path.exists():
            continue
        if FORBIDDEN.search(path):
            violations.append({
                "path": path,
                "rule": "MODULE-NAME-001",
                "type": "forbidden_suffix",
                "message": f"Forbidden analytics-bucket module suffix in {path!r}",
            })
        elif CONDITIONAL.search(path):
            try:
                content = full_path.read_text(encoding="utf-8", errors="replace")
                if FORMAT_FN.search(content):
                    violations.append({
                        "path": path,
                        "rule": "MODULE-NAME-001",
                        "type": "conditional_forbidden",
                        "message": (
                            f"Format-prefixed spec behavior found in conditionally-forbidden "
                            f"module {path!r}"
                        ),
                    })
            except OSError:
                pass

    blocks = len(violations) > 0
    return {
        "validator": "validate_forbidden_module_names",
        "rule_id": "MODULE-NAME-001",
        "result": "FAIL" if blocks else "PASS",
        "blocks_sprint": blocks,
        "items": violations,
        "summary": (
            f"V50: {len(violations)} forbidden module name(s) found"
            if blocks else "V50: No forbidden module names"
        ),
    }


# ---------------------------------------------------------------------------
# V51 — TC-QHARD-001: spec_qname_coverage_validator
# ---------------------------------------------------------------------------

_FORMATS = [
    "abw", "csv", "dif", "fodg", "fodp", "fods", "fodt",
    "gnumeric", "ndjson", "ods", "odt", "pbm", "pgm", "ppm",
    "qoi", "sylk", "toml", "tsv", "xcf", "zst",
]
_FACADE_ONLY_FORMATS = {"zst"}  # codec-only formats with no domain model class

_ERROR_SUFFIXES = (
    "Error", "Exception", "SizeError", "ParseError", "InputError",
    "WriteError", "DecodeError", "InvalidFormatError",
    "InvalidMagicError", "InvalidHeaderError", "InvalidContainerError",
)
_CONSTANTS = {"FORMAT_ID", "SPEC_VERSION", "PACKAGE_VERSION", "MAX_FILE_BYTES"}


def _has_spec_qname(class_name: str, src_root: Path) -> bool:
    """Return True if any .py file under src_root defines class_name with spec_qname.

    Handles both plain assignments (spec_qname = "...") and annotated assignments
    (spec_qname: str = "..."), which produce ast.Assign vs ast.AnnAssign respectively.
    """
    for py_file in src_root.rglob("*.py"):
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for stmt in node.body:
                    # Plain assignment: spec_qname = "..."
                    if (
                        isinstance(stmt, ast.Assign)
                        and any(
                            isinstance(t, ast.Name) and t.id == "spec_qname"
                            for t in stmt.targets
                        )
                    ):
                        return True
                    # Annotated assignment: spec_qname: str = "..."
                    if (
                        isinstance(stmt, ast.AnnAssign)
                        and isinstance(stmt.target, ast.Name)
                        and stmt.target.id == "spec_qname"
                    ):
                        return True
    return False


def _all_symbols_for_format(fmt: str, src_root: Path) -> list[str]:
    """Extract __all__ symbols from src/python/{fmt}/__init__.py."""
    init_path = src_root / f"src/python/{fmt}/__init__.py"
    if not init_path.exists():
        return []
    text = init_path.read_text(encoding="utf-8", errors="replace")
    syms = []
    in_all = False
    for line in text.splitlines():
        stripped = line.strip()
        if not in_all and "__all__" in line and "[" in line:
            in_all = True
        if in_all:
            for m in _re.findall(r'"([^"]+)"|\'([^\']+)\'', line):
                sym = m[0] or m[1]
                if sym and not sym.startswith("_") and sym not in syms:
                    syms.append(sym)
            if "]" in line and stripped not in ("__all__ = [", "__all__ = []"):
                in_all = False
    return syms


def validate_spec_qname_coverage(
    declaration: dict | None = None,
    repo_root: Path | None = None,
) -> dict:
    """V51 (TC-QHARD-001): WARN if any class exported from a format __init__.py lacks spec_qname.

    Scans all 20 Python format packages. For each exported symbol that is a class
    (non-Error, non-constant), checks whether any .py file in the format package
    defines that class with a spec_qname attribute. Produces WARN violations; never
    blocks sprint (blocks_sprint=False).

    Exceptions:
    - Error/Exception subclasses are exempt.
    - Constants (FORMAT_ID, SPEC_VERSION etc.) are exempt.
    - Formats in _FACADE_ONLY_FORMATS (e.g. zst) are skipped when they have no ClassDef.
    """
    repo = repo_root or _REPO_ROOT
    warnings = []

    for fmt in _FORMATS:
        if fmt in _FACADE_ONLY_FORMATS:
            continue
        fmt_root = repo / f"src/python/{fmt}"
        if not fmt_root.exists():
            continue
        for sym in _all_symbols_for_format(fmt, repo):
            if sym in _CONSTANTS:
                continue
            if any(sym.endswith(s) for s in _ERROR_SUFFIXES):
                continue
            # Is it a class? Check by looking for ClassDef in format package.
            is_class = False
            for py_file in fmt_root.rglob("*.py"):
                try:
                    tree = ast.parse(py_file.read_text(encoding="utf-8", errors="replace"))
                except SyntaxError:
                    continue
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name == sym:
                        is_class = True
                        break
                if is_class:
                    break
            if not is_class:
                continue
            # Check spec_qname
            if not _has_spec_qname(sym, fmt_root):
                warnings.append({
                    "format": fmt,
                    "class": sym,
                    "issue": f"Exported class {sym!r} in {fmt} lacks spec_qname attribute",
                })

    result = "WARN" if warnings else "PASS"
    return {
        "validator": "validate_spec_qname_coverage",
        "result": result,
        "blocks_sprint": False,
        "items": warnings,
        "summary": (
            f"V51: {len(warnings)} exported class(es) lack spec_qname"
            if warnings else "V51: All exported classes have spec_qname (or none applicable)"
        ),
    }


# ---------------------------------------------------------------------------
# V52 — TC-QHARD-002: compat_import_integrity_validator
# ---------------------------------------------------------------------------


def validate_compat_import_integrity(
    declaration: dict | None = None,
    repo_root: Path | None = None,
) -> dict:
    """V52 (TC-QHARD-002): WARN if any Compat/ facade cannot import its spec authority class.

    Scans all src/python/{format}/Compat/*.py files. For each file, finds
    'from ..spec.{path} import {Class}' patterns (AST-based, not runtime).
    Checks whether the target .py file exists AND contains a ClassDef named {Class}.

    Severity: WARN (blocks_sprint=False). This fires for FODS/FODT currently because
    spec/ classes don't exist yet. It becomes PASS after Phase 1 completes.
    """
    repo = repo_root or _REPO_ROOT
    warnings = []

    for fmt in _FORMATS:
        compat_dir = repo / f"src/python/{fmt}/Compat"
        if not compat_dir.exists():
            continue
        for compat_file in compat_dir.glob("*.py"):
            if compat_file.name == "__init__.py":
                continue
            try:
                text = compat_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            # Find relative imports: from ..spec.{sub.path} import {ClassName}
            # Also detect absolute: from src.python.{fmt}.spec.{sub.path} import {ClassName}
            patterns = [
                _re.finditer(r"from \.\.(spec(?:\.\w+)+) import (\w+)", text),
                _re.finditer(
                    r"from src\.python\.\w+\.(spec(?:\.\w+)+) import (\w+)", text
                ),
            ]
            for matches in patterns:
              for m in matches:
                import_path, class_name = m.group(1), m.group(2)
                # Convert dotted path to filesystem: spec.office.document -> spec/office/document.py
                rel_path = import_path.replace(".", "/") + ".py"
                target = repo / f"src/python/{fmt}" / rel_path
                if not target.exists():
                    warnings.append({
                        "facade_file": str(compat_file.relative_to(repo)),
                        "import": f"from ..{import_path} import {class_name}",
                        "issue": f"Target file {rel_path!r} does not exist in {fmt}/",
                        "severity": "WARN",
                    })
                    continue
                # File exists — check class defined inside
                try:
                    tree = ast.parse(target.read_text(encoding="utf-8", errors="replace"))
                except SyntaxError:
                    continue
                defined_classes = {
                    node.name
                    for node in ast.walk(tree)
                    if isinstance(node, ast.ClassDef)
                }
                if class_name not in defined_classes:
                    warnings.append({
                        "facade_file": str(compat_file.relative_to(repo)),
                        "import": f"from ..{import_path} import {class_name}",
                        "issue": f"Class {class_name!r} not found in {target.name}",
                        "severity": "ERROR",
                    })

    result = "WARN" if warnings else "PASS"
    return {
        "validator": "validate_compat_import_integrity",
        "result": result,
        "blocks_sprint": False,
        "items": warnings,
        "summary": (
            f"V52: {len(warnings)} Compat/ import integrity issue(s) found"
            if warnings else "V52: All Compat/ facades have resolvable spec/ imports"
        ),
    }


# ---------------------------------------------------------------------------
# V53 — TC-QHARD-003: spec_authority_class_completeness
# ---------------------------------------------------------------------------


def validate_spec_authority_class_completeness(
    declaration: dict | None = None,
    repo_root: Path | None = None,
    formats_filter: list[str] | None = None,
) -> dict:
    """V53 (TC-QHARD-003): WARN for each QName registry entry whose python_file is missing or lacks the spec class.

    Reads all shared/qname-registry/*.yaml files. For entries where python_file != null:
    1. If the file does not exist on disk: WARN "file missing".
    2. If the file exists but no ClassDef has spec_qname == qname: WARN "class missing".

    Severity: WARN (blocks_sprint=False). All FODS entries produce WARN at Phase 0;
    they become PASS after Phase 1 creates the spec authority classes.
    """
    import yaml as _yaml  # stdlib-compatible; pyyaml required

    repo = repo_root or _REPO_ROOT
    warnings = []

    registry_dir = repo / "shared/qname-registry"
    if not registry_dir.exists():
        return {
            "validator": "validate_spec_authority_class_completeness",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V53: No QName registry directory found — skipped",
        }

    for yaml_path in sorted(registry_dir.glob("*.yaml")):
        if yaml_path.name == "schema.yaml":
            continue
        try:
            entries = _yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or []
        except Exception:
            continue
        fmt_name = yaml_path.stem
        if formats_filter and fmt_name not in formats_filter:
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            python_file = entry.get("python_file")
            if not python_file:
                continue
            qname = entry.get("qname", "")
            target = repo / python_file
            if not target.exists():
                warnings.append({
                    "format": fmt_name,
                    "qname": qname,
                    "python_file": python_file,
                    "issue": "python_file does not exist on disk",
                })
                continue
            # File exists — verify it contains a class with spec_qname == qname
            try:
                tree = ast.parse(target.read_text(encoding="utf-8", errors="replace"))
            except SyntaxError:
                continue
            found_qname = False
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for stmt in node.body:
                        # Plain assignment: spec_qname = "..."
                        if (
                            isinstance(stmt, ast.Assign)
                            and any(
                                isinstance(t, ast.Name) and t.id == "spec_qname"
                                for t in stmt.targets
                            )
                            and isinstance(stmt.value, ast.Constant)
                            and stmt.value.value == qname
                        ):
                            found_qname = True
                            break
                        # Annotated assignment: spec_qname: str = "..."
                        if (
                            isinstance(stmt, ast.AnnAssign)
                            and isinstance(stmt.target, ast.Name)
                            and stmt.target.id == "spec_qname"
                            and isinstance(stmt.value, ast.Constant)
                            and stmt.value.value == qname
                        ):
                            found_qname = True
                            break
                if found_qname:
                    break
            if not found_qname:
                warnings.append({
                    "format": fmt_name,
                    "qname": qname,
                    "python_file": python_file,
                    "issue": f"File exists but no class with spec_qname == {qname!r}",
                })

    result = "WARN" if warnings else "PASS"
    return {
        "validator": "validate_spec_authority_class_completeness",
        "result": result,
        "blocks_sprint": False,
        "items": warnings,
        "summary": (
            f"V53: {len(warnings)} registry entry(ies) missing spec authority class"
            if warnings else "V53: All registry python_file entries have valid spec authority classes"
        ),
    }
