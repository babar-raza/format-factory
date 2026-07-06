"""governance_validators_spec.py — Spec/QName validators extracted from governance_validators_ext.py.

Extracted to keep governance_validators_ext.py within its baseline_loc_cap (1423 LOC).
Contains V51, V52, V53 (TC-QHARD spec/qname validators) and V59, V62 (parity/density validators).

TC-GOVBLOCK-SPEC-001 (2026-06-26): extraction sprint s78 — reduces ext.py by ~540 LOC.

Validators:
  V51: validate_spec_qname_coverage — exported classes must have spec_qname (TC-QHARD-001, WARN-only)
  V52: validate_compat_import_integrity — Compat/ facades can resolve spec/ imports (TC-QHARD-002, WARN-only)
  V53: validate_spec_authority_class_completeness — registry python_file entries exist (TC-QHARD-003)
  V59: validate_cross_language_parity — dual-language format parity awareness (TC-MGHEAL-005, WARN-only)
  V62: validate_spec_fact_refs_density — spec_fact_refs per new class in PRODUCT_SOURCE (TC-MACH-VAL-001)
"""

from __future__ import annotations
from governance_validators_contract import validator  # noqa: F401

import ast
import re as _re
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


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


@validator(rule_id="V_VALIDATE_SPEC_QNAME_COVERAGE", domain="spec")
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


@validator(rule_id="V_VALIDATE_COMPAT_IMPORT_INTEGRITY", domain="spec")
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


@validator(rule_id="V_VALIDATE_SPEC_AUTHORITY_CLASS_COMPLETENESS", domain="spec")
def validate_spec_authority_class_completeness(
    declaration: dict | None = None,
    repo_root: Path | None = None,
    formats_filter: list[str] | None = None,
) -> dict:
    """V53 (TC-QHARD-003): Validate QName registry python_file entries.

    Reads all shared/qname-registry/*.yaml files.

    Pass 1 (WARN): For entries where python_file != null:
    1. If the file does not exist on disk: WARN "file missing".
    2. If the file exists but no ClassDef has spec_qname == qname: WARN "class missing".

    Pass 2 (FAIL): For entries where status IN (implementing, implemented, stable)
    AND python_file is null: FAIL with blocks_sprint=True.
    Seeded and architecture_only entries with null python_file remain WARN-only.

    TC-QNAME-VALIDATORS-001 (cheerful-floating-glade): upgraded to FAIL mode 2026-06-23.
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

    # Pass 2: FAIL for implementing/implemented/stable entries with null python_file
    _FAIL_STATUSES = {"implementing", "implemented", "stable"}
    blockers = []
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
            status = entry.get("status", "seeded")
            python_file = entry.get("python_file")
            qname = entry.get("qname", "")
            if not python_file and status in _FAIL_STATUSES:
                blockers.append({
                    "format": fmt_name,
                    "qname": qname,
                    "status": status,
                    "issue": f"status={status} but python_file is null — must be populated",
                })

    if blockers:
        return {
            "validator": "validate_spec_authority_class_completeness",
            "result": "FAIL",
            "blocks_sprint": True,
            "items": blockers + warnings,
            "summary": (
                f"V53: {len(blockers)} registry entry(ies) with status "
                f"implementing/implemented/stable have null python_file (BLOCKS SPRINT)"
            ),
        }

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


# ---------------------------------------------------------------------------
# V59 — TC-MGHEAL-005: cross_language_parity
# ---------------------------------------------------------------------------


@validator(rule_id="V_VALIDATE_CROSS_LANGUAGE_PARITY", domain="spec")
def validate_cross_language_parity(
    declaration: dict,
    repo_root: "Path | None" = None,
) -> dict:
    """V59 (TC-MGHEAL-005): Cross-language parity awareness for dual-language formats.

    For PRODUCT_SOURCE items targeting a format with both .NET and Python implementations,
    WARN if no cross-language parity evidence or acknowledgment is present.

    WARN-only (blocks_sprint=False) to allow transitional use while parity matrices are built.
    """
    import json as _json

    if repo_root is None:
        repo_root = Path(__file__).resolve().parent.parent.parent
    else:
        repo_root = Path(repo_root)

    # Formats with both .NET and Python implementations
    _DUAL_FORMATS = {
        "fods", "fodt", "csv", "tsv", "ndjson", "zst",
        "pbm", "pgm", "ppm",  # NetPBM family
    }

    violations = []
    total_checked = 0

    for item in declaration.get("planned_work_items", []):
        if item.get("item_type") != "PRODUCT_SOURCE":
            continue

        # Try to determine format from item metadata
        item_id = item.get("item_id", "UNKNOWN")
        fmt = item.get("format", "").lower()
        if not fmt:
            # Try to infer format from evidence_paths or changed_files
            for path_field in ("evidence_paths", "changed_files"):
                for p in item.get(path_field, []):
                    p_str = str(p).replace("\\", "/").lower()
                    for f in _DUAL_FORMATS:
                        if f"/python/{f}/" in p_str or f"/net/{f}/" in p_str:
                            fmt = f
                            break
                    if fmt:
                        break
                if fmt:
                    break

        if fmt not in _DUAL_FORMATS:
            continue

        total_checked += 1

        # Check if parity is acknowledged in item metadata
        has_parity = (
            item.get("cross_language_parity_checked")
            or item.get("parity_deferred")
            or any("parity" in str(v).lower() for v in item.get("notes", []))
        )
        if not has_parity:
            violations.append({
                "item_id": item_id,
                "format": fmt,
                "issue": "PRODUCT_SOURCE for dual-language format without parity acknowledgment",
            })

    result = "WARN" if violations else "PASS"
    return {
        "validator": "validate_cross_language_parity",
        "result": result,
        "blocks_sprint": False,
        "violations": violations,
        "total_dual_format_items": total_checked,
        "detail": (
            f"V59: {len(violations)}/{total_checked} dual-format PRODUCT_SOURCE items "
            f"lack cross-language parity acknowledgment. "
            "Add cross_language_parity_checked or parity_deferred to item metadata."
        ) if violations else f"V59: {total_checked} dual-format items checked, all have parity awareness.",
    }


# ---------------------------------------------------------------------------
# V62 — TC-MACH-VAL-001: spec_fact_refs density validator
# ---------------------------------------------------------------------------


@validator(rule_id="V_VALIDATE_SPEC_FACT_REFS_DENSITY", domain="spec")
def validate_spec_fact_refs_density(
    declaration: dict, repo_root: Path | None = None
) -> dict:
    """V62 (TC-MACH-VAL-001): Require >=1 spec_fact_ref per new non-Compat class in PRODUCT_SOURCE items.

    REWORK_REQUIRED mode (not hard block) — ramp to BLOCK after 3 sprints.
    Compat/ classes are facades — excluded from this check.
    spec/ classes are architecture markers — excluded from this check.
    """
    root = repo_root or _REPO_ROOT
    items = declaration.get("completed_work_items", [])
    if isinstance(items, list) and items and isinstance(items[0], str):
        items = declaration.get("planned_work_items", [])
    if not items:
        return {
            "validator": "validate_spec_fact_refs_density",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V62: No work items to check",
        }

    warnings = []
    for item in items:
        if not isinstance(item, dict):
            continue
        item_type = item.get("item_type", "")
        if item_type != "PRODUCT_SOURCE":
            continue

        # Check evidence for spec_fact_refs
        evidence = item.get("evidence_artifacts", [])
        spec_refs = item.get("spec_fact_refs", [])

        # Also check in evidence_artifacts for spec_fact_ref fields
        if not spec_refs:
            for ev in evidence:
                if isinstance(ev, dict) and ev.get("spec_fact_refs"):
                    spec_refs = ev["spec_fact_refs"]
                    break

        # Check changed files for new classes under src/python/ or src/net/
        # excluding Compat/ and spec/ directories
        changed = item.get("changed_files", [])
        has_new_class_file = False
        for f in changed:
            if isinstance(f, str) and (f.startswith("src/python/") or f.startswith("src/net/")):
                parts = f.replace("\\", "/").split("/")
                if "Compat" in parts or "spec" in parts:
                    continue
                if f.endswith(".py") or f.endswith(".cs"):
                    has_new_class_file = True
                    break

        if has_new_class_file and not spec_refs:
            item_id = item.get("item_id", item.get("id", "unknown"))
            warnings.append({
                "item_id": item_id,
                "issue": "PRODUCT_SOURCE item modifies non-Compat/non-spec source without spec_fact_refs",
                "severity": "REWORK_REQUIRED",
            })

    result = "WARN" if warnings else "PASS"
    return {
        "validator": "validate_spec_fact_refs_density",
        "result": result,
        "blocks_sprint": False,  # REWORK_REQUIRED mode, not hard block
        "items": warnings,
        "summary": (
            f"V62: {len(warnings)} PRODUCT_SOURCE item(s) lack spec_fact_refs (REWORK_REQUIRED)"
            if warnings else "V62: All PRODUCT_SOURCE items have spec_fact_refs"
        ),
    }
