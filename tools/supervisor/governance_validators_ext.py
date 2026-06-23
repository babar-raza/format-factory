"""governance_validators_ext.py — Extension validators for governance_validators.py

This file exists to keep governance_validators.py within its baseline_loc_cap.
New validators (V48+) are placed here and imported at the bottom of governance_validators.py.

Pattern mirrors analytics extraction pattern used for format codecs:
  governance_validators.py imports from governance_validators_ext at module bottom.
  governance_validator_runner.py registers both sets of validators in run_all_governance_validators().

TC-WHALE-GOVBLOCK-001 (2026-06-21): V48 extracted here per source baseline LOC cap policy.
TC-PG-006 (2026-06-23): V56 validate_hardening_target_identity — plan hardening must write to native plan.
TC-ANAL-SEG-HEAL-001 (2026-06-22): V50 added here — MODULE-NAME-001 forbidden module names.
zesty-conjuring-peacock (2026-06-23): V50 extended — *_analytics.py + bare analytics.py added to FORBIDDEN.
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


def validate_hardening_target_identity(
    declaration: dict | None = None,
    repo_root: Path | None = None,
) -> dict:
    """V56 (TC-PG-006): Verify plan hardening writes to the native plan, not a fallback.

    Scans evidence_paths in all work items for .md files under plans/ or .claude/plans/.
    If any cited plan file is:
      - plans/snoopy-juggling-seal.md AND snoopy is NOT the active plan → FAIL
      - any plan file other than the active plan → WARN

    Active plan is resolved from .local/supervisor/plan-locks/ (IN_PROGRESS locks).
    Falls back to no-op PASS if no plan lock exists (no per-chat plan active).

    Severity: FAIL for snoopy as wrong-target; WARN for other wrong-target plans.
    blocks_sprint: True only on FAIL.

    Added 2026-06-23 (TC-PG-006, keen-snacking-quiche plan governance healing).
    """
    import json

    repo = repo_root or _REPO_ROOT

    # Resolve active plan path from IN_PROGRESS lock files
    active_plan_path: str | None = None
    locks_dir = repo / ".local" / "supervisor" / "plan-locks"
    if locks_dir.is_dir():
        for lf in sorted(locks_dir.glob("*.json")):
            try:
                lock = json.loads(lf.read_text(encoding="utf-8"))
                if lock.get("status") == "IN_PROGRESS":
                    active_plan_path = str(lock.get("plan_path", "")).replace("\\", "/")
                    break
            except Exception:
                continue

    # Also try shared lock
    if not active_plan_path:
        shared = repo / ".local" / "supervisor" / "active-plan-lock.json"
        if shared.exists():
            try:
                lock = json.loads(shared.read_text(encoding="utf-8"))
                if lock.get("status") == "IN_PROGRESS":
                    active_plan_path = str(lock.get("plan_path", "")).replace("\\", "/")
            except Exception:
                pass

    if not active_plan_path:
        # No active plan — nothing to enforce
        return {
            "validator": "validate_hardening_target_identity",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V49: No active per-chat plan lock — hardening target check skipped",
        }

    # Normalise the active plan path for comparison
    active_norm = active_plan_path.rstrip("/")

    # Scan all work item evidence_paths for .md files in plans/ or .claude/plans/
    _PLAN_PATTERNS = _re.compile(
        r"((?:plans/|\.claude/plans/|C:[/\\]Users[/\\][^/\\]+[/\\]\.claude[/\\]plans[/\\])[^/\s]+\.md)"
    )
    fail_items = []
    warn_items = []

    all_items = []
    if declaration:
        all_items = (
            declaration.get("completed_work_items", [])
            + declaration.get("planned_work_items", [])
        )
        # Scan global evidence_paths (hardening sprint evidence)
        for ep in declaration.get("evidence_paths", []):
            all_items.append({"item_id": "DECLARATION_LEVEL", "evidence_paths": [ep]})
        # evidence_artifacts are modified-file records, not hardening targets.
        # Skip plan_file type entries — those are governance corrections (e.g. adding
        # plan_identity front-matter to a plan, which is not a hardening-target mismatch).
        for ea in declaration.get("evidence_artifacts", []):
            if isinstance(ea, dict) and ea.get("type") not in ("plan_file", "governance_ledger"):
                all_items.append({
                    "item_id": "DECLARATION_LEVEL",
                    "evidence_paths": [ea.get("path", "")],
                })

    for item in all_items:
        if not isinstance(item, dict):
            continue
        item_id = item.get("item_id", "<unknown>")
        for path_str in item.get("evidence_paths", []):
            path_norm = str(path_str).replace("\\", "/")
            # Only check plan-like paths
            if not _PLAN_PATTERNS.search(path_norm):
                continue
            # Normalise
            if path_norm == active_norm or path_norm.endswith("/" + active_norm.split("/")[-1]):
                continue  # This IS the active plan — correct
            if "master-plan-memory.md" in path_norm:
                continue  # Ledger — not a hardening target mismatch
            # snoopy specifically cited while NOT being the active plan → FAIL
            if "snoopy-juggling-seal.md" in path_norm:
                fail_items.append({
                    "item_id": item_id,
                    "evidence_path": path_str,
                    "active_plan": active_plan_path,
                    "issue": (
                        "snoopy-juggling-seal.md cited as hardening target "
                        "but it is NOT the active per-chat plan"
                    ),
                    "severity": "FAIL",
                })
            else:
                warn_items.append({
                    "item_id": item_id,
                    "evidence_path": path_str,
                    "active_plan": active_plan_path,
                    "issue": (
                        f"Plan file {path_str!r} cited as hardening evidence "
                        f"but active plan is {active_plan_path!r}"
                    ),
                    "severity": "WARN",
                })

    all_issues = fail_items + warn_items
    result = "FAIL" if fail_items else ("WARN" if warn_items else "PASS")
    return {
        "validator": "validate_hardening_target_identity",
        "result": result,
        "blocks_sprint": bool(fail_items),
        "items": all_issues,
        "summary": (
            f"V56: {len(fail_items)} FAIL item(s) (wrong plan cited as hardening target); "
            f"{len(warn_items)} WARN item(s)"
            if all_issues
            else f"V56: Hardening evidence targets active plan ({active_plan_path})"
        ),
    }


def validate_forbidden_module_names(
    declaration: dict, repo_root: Path | None = None
) -> dict:
    """V50 — MODULE-NAME-001: Forbid generic analytics-bucket module names.

    Blocks creation of or modification of files matching:
      *_analytics.py, *_analytics_extra.py, *_extra.py, *_misc.py, bare analytics.py
      *_helpers.py / *_utils.py containing format-prefixed spec behavior

    Deletion of these files (where file does NOT exist on disk) is ALWAYS allowed.
    The validator checks Path(repo / path).exists() before flagging — so deleting
    a forbidden-named file in a sprint does NOT cause this validator to self-block.

    These names indicate code grouped by convenience, not spec hierarchy.
    Every product module must map to a spec section, element, or domain concept.

    Added 2026-06-22 (TC-ANAL-SEG-HEAL-001) as part of spec-level segregation healing.
    Extended 2026-06-23 (zesty-conjuring-peacock): *_analytics.py and bare analytics.py
    added to FORBIDDEN — all analytics-bucket patterns now blocked, not just overflow files.
    """
    import re

    repo = repo_root or _REPO_ROOT
    FORBIDDEN = re.compile(
        r"src/python/[^/]+/"
        r"(?:[^/]+_(?:analytics_extra|analytics|extra|misc)|analytics)\.py$"
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


# ---------------------------------------------------------------------------
# V54 — Cross-lane: product item mutating supervisor machinery files
# ---------------------------------------------------------------------------

_PRODUCT_SOURCE_ITEM_TYPES = frozenset({
    "PRODUCT_SOURCE", "TEST", "REQUIREMENT", "READINESS", "RELEASE_GATE",
    "PRODUCT_IMPLEMENTATION", "PRODUCT_TESTING",
    "PRODUCT_CAPABILITY_EXPANSION", "PRODUCT_EXPORT_OR_DOGFOOD",
})

_MACHINERY_SUPERVISOR_PREFIXES = (
    "tools/supervisor/",
    "tools/validators/",
    "tools/requirements_authority/",
)


def validate_cross_lane_product_touching_machinery(
    declaration: dict | None = None,
    repo_root: Path | None = None,
) -> dict:
    """V54: WARN if a product-track item declares changed_files under tools/supervisor/.

    Product sprints should not mutate supervisor machinery files. Cross-lane mutations
    indicate architectural drift — work that belongs to the MACHINERY track is being
    bundled with PRODUCT_SOURCE items.

    Severity: WARN-only (blocks_sprint=False). Promotes to blocking after 3 clean sprints
    with no false positives. Exception: items with lane_exception='MACHINERY_HEALING' bypass.

    Added 2026-06-23 (FF-FORENSIC-AUDIT-20260623 / A4) as part of lane boundary hardening.
    """
    if declaration is None:
        return {
            "validator": "validate_cross_lane_product_touching_machinery",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V54: No declaration provided — skipped",
        }

    warnings = []
    all_items = (
        declaration.get("completed_work_items", [])
        + declaration.get("planned_work_items", [])
    )

    # Also check at declaration level (some declarations list changed_files globally)
    global_changed = declaration.get("changed_files", [])

    for item in all_items:
        if not isinstance(item, dict):
            continue
        itype = item.get("item_type", "")
        if itype not in _PRODUCT_SOURCE_ITEM_TYPES:
            continue
        # Exception: MACHINERY_HEALING hybrid items are legitimately cross-lane
        if item.get("lane_exception") == "MACHINERY_HEALING":
            continue

        changed = item.get("changed_files", []) or global_changed
        for path in changed:
            path_str = str(path).replace("\\", "/")
            if any(path_str.startswith(pfx) for pfx in _MACHINERY_SUPERVISOR_PREFIXES):
                warnings.append({
                    "item_id": item.get("item_id", "<unknown>"),
                    "item_type": itype,
                    "changed_file": path_str,
                    "issue": (
                        f"Product-track item ({itype}) declares change to machinery file "
                        f"{path_str!r} — potential cross-lane contamination"
                    ),
                    "severity": "WARN",
                })

    result = "WARN" if warnings else "PASS"
    return {
        "validator": "validate_cross_lane_product_touching_machinery",
        "result": result,
        "blocks_sprint": False,
        "items": warnings,
        "summary": (
            f"V54: {len(warnings)} product item(s) mutating machinery files"
            if warnings else "V54: No cross-lane product→machinery contamination detected"
        ),
    }


# ---------------------------------------------------------------------------
# V55 — Cross-lane: machinery item mutating product src/ files
# ---------------------------------------------------------------------------

_MACHINERY_ITEM_TYPES = frozenset({
    "GOVERNANCE_TASKCARD", "GOVERNANCE_DOC", "GOVERNANCE_REVIEW",
    "SPEC_AUTHORITY_MACHINERY", "REQUIREMENT_CAPABILITY_MACHINERY",
    "ACTION_QUEUE_MACHINERY", "AUTONOMY_ORCHESTRATOR_MACHINERY",
    "SUPERVISOR_VERDICT_MACHINERY", "VALIDATOR_OR_EVIDENCE_MACHINERY",
    "PROMPT_GENERATION_MACHINERY", "GOVERNED_SKILL_OR_GENERATOR_MACHINERY",
})

_PRODUCT_SRC_PREFIXES = (
    "src/python/",
    "src/net/",
)


def validate_cross_lane_machinery_touching_product(
    declaration: dict | None = None,
    repo_root: Path | None = None,
) -> dict:
    """V55: WARN if a machinery-track item declares changed_files under src/.

    Machinery sprints should not mutate product source files. Cross-lane mutations
    risk destabilizing product behavior during infrastructure work.

    Severity: WARN-only (blocks_sprint=False). Exception: items with
    lane_exception='MACHINERY_HEALING' bypass (analytics separation sprints that
    necessarily extract src/ code to analytics files are legitimately cross-lane).

    Added 2026-06-23 (FF-FORENSIC-AUDIT-20260623 / A4) as part of lane boundary hardening.
    """
    if declaration is None:
        return {
            "validator": "validate_cross_lane_machinery_touching_product",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V55: No declaration provided — skipped",
        }

    warnings = []
    all_items = (
        declaration.get("completed_work_items", [])
        + declaration.get("planned_work_items", [])
    )
    global_changed = declaration.get("changed_files", [])

    for item in all_items:
        if not isinstance(item, dict):
            continue
        itype = item.get("item_type", "")
        if itype not in _MACHINERY_ITEM_TYPES:
            continue
        # Exception: MACHINERY_HEALING items are legitimately cross-lane
        if item.get("lane_exception") == "MACHINERY_HEALING":
            continue

        changed = item.get("changed_files", []) or global_changed
        for path in changed:
            path_str = str(path).replace("\\", "/")
            if any(path_str.startswith(pfx) for pfx in _PRODUCT_SRC_PREFIXES):
                warnings.append({
                    "item_id": item.get("item_id", "<unknown>"),
                    "item_type": itype,
                    "changed_file": path_str,
                    "issue": (
                        f"Machinery-track item ({itype}) declares change to product source "
                        f"{path_str!r} — potential cross-lane contamination"
                    ),
                    "severity": "WARN",
                })

    result = "WARN" if warnings else "PASS"
    return {
        "validator": "validate_cross_lane_machinery_touching_product",
        "result": result,
        "blocks_sprint": False,
        "items": warnings,
        "summary": (
            f"V55: {len(warnings)} machinery item(s) mutating product src/ files"
            if warnings else "V55: No cross-lane machinery→product contamination detected"
        ),
    }


_LEDGER_SRC_PREFIXES = ("src/python/", "src/net/")


def validate_changed_files_in_ledger(
    declaration: dict | None = None,
    repo_root: Path | None = None,
) -> dict:
    """V57: WARN if src/python/ or src/net/ changed files have no product-code-change-ledger entry.

    Cross-validates declaration changed_files against reports/r90/product-code-change-ledger.json.
    Every src/ file modified after governance tracking began should have a ledger entry.

    Severity: WARN-only (blocks_sprint=False) until ledger is fully backfilled.
    Activation cutoff: sprint where 90% of src/ entries have ledger coverage.

    Added 2026-06-23 (TC-VNK-003) as V57.
    """
    import json as _json

    if declaration is None:
        return {
            "validator": "validate_changed_files_in_ledger",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V57: No declaration provided — skipped",
        }

    _root = repo_root or Path(__file__).resolve().parents[2]
    ledger_path = _root / "reports" / "r90" / "product-code-change-ledger.json"

    # Build set of ledger-tracked paths
    ledger_paths: set[str] = set()
    if ledger_path.exists():
        try:
            ledger_data = _json.loads(ledger_path.read_text(encoding="utf-8"))
            entries = ledger_data if isinstance(ledger_data, list) else ledger_data.get("entries", [])
            for entry in entries:
                for sf in entry.get("source_files", []):
                    raw = str(sf.get("path", "")).replace("\\", "/")
                    if raw:
                        ledger_paths.add(raw)
        except Exception:
            pass  # If ledger is unreadable, skip — WARN-only validator

    # Collect declaration changed_files
    changed_files = declaration.get("changed_files", [])
    warnings = []
    for path in changed_files:
        path_str = str(path).replace("\\", "/")
        if not any(path_str.startswith(pfx) for pfx in _LEDGER_SRC_PREFIXES):
            continue
        if path_str not in ledger_paths:
            warnings.append({
                "path": path_str,
                "issue": f"src/ file {path_str!r} has no product-code-change-ledger entry",
                "severity": "WARN",
            })

    result = "WARN" if warnings else "PASS"
    return {
        "validator": "validate_changed_files_in_ledger",
        "result": result,
        "blocks_sprint": False,
        "items": warnings,
        "summary": (
            f"V57: {len(warnings)} src/ file(s) missing ledger entry"
            if warnings else "V57: All src/ changed files have ledger entries (or no src/ files changed)"
        ),
    }


def validate_expansion_fallback_refs(declaration: dict) -> dict:
    """V58 (FALLBACK-REF-001): Detect EXPANSION-FALLBACK-* synthetic gap references.

    autonomous_task_generator.py injects gap_ledger_ref="EXPANSION-FALLBACK-{FORMAT}-{fn}"
    for functions not in the real gap-ledger. These pass TC-GUARD-001's non-empty check but
    are NOT real GAP-* entries. This validator surfaces them for review.

    WARN-only (blocks_sprint=False) to allow transitional use without hard-blocking existing
    deepening work. Classifies as LEDGER_ENTRY_CLAIMED_UNPROVEN.
    """
    _FALLBACK_PREFIX = "EXPANSION-FALLBACK-"
    _CHECKED = {"PRODUCT_SOURCE", "PRODUCT_TEST"}
    violations = []
    total_checked = 0
    for item in declaration.get("planned_work_items", []):
        if item.get("item_type") not in _CHECKED:
            continue
        total_checked += 1
        ref = item.get("gap_ledger_ref", "")
        if isinstance(ref, str) and ref.startswith(_FALLBACK_PREFIX):
            violations.append({
                "item_id": item.get("item_id", "UNKNOWN"),
                "gap_ledger_ref": ref,
                "classification": "LEDGER_ENTRY_CLAIMED_UNPROVEN",
            })
    pct = (len(violations) / total_checked * 100) if total_checked > 0 else 0.0
    result = "WARN" if violations else "PASS"
    return {
        "validator": "validate_expansion_fallback_refs",
        "result": result,
        "blocks_sprint": False,
        "violations": violations,
        "total_checked": total_checked,
        "fallback_count": len(violations),
        "fallback_pct": round(pct, 1),
        "detail": (
            f"{len(violations)}/{total_checked} PRODUCT_SOURCE/TEST items use "
            f"EXPANSION-FALLBACK synthetic gap refs ({pct:.0f}%). "
            "These are not real gap-ledger entries. "
            "Replace with real GAP-{FORMAT}-* IDs from gap-ledger.json when available."
        ) if violations else "No EXPANSION-FALLBACK refs detected.",
    }


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
# V60 — TC-TCF-010: validate_terminal_closure_completeness
# ---------------------------------------------------------------------------


def validate_terminal_closure_completeness(
    declaration: dict | None = None,
    repo_root: Path | None = None,
) -> dict:
    """V60 (TC-TCF-010): WARN if RELEASE_GATE/READINESS items cite a plan with open taskcards.

    Scans evidence_paths for plan files (.md in plans/ or .claude/plans/). If any
    cited plan has open taskcards (not CLOSED/SUPERSEDED/EXCLUDED), produces WARN.

    This prevents declaring release readiness when underlying plans still have
    incomplete work.

    Severity: WARN-only (blocks_sprint=False). Advisory at gate level.
    Added 2026-06-23 (TC-FORENSICS-TERMINAL-20260623, TC-TCF-010).
    """
    if declaration is None:
        return {
            "validator": "validate_terminal_closure_completeness",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V60: No declaration provided -- skipped",
        }

    repo = repo_root or _REPO_ROOT
    _GATE_TYPES = {"RELEASE_GATE", "READINESS"}
    _PLAN_RE = _re.compile(
        r"((?:plans/|\.claude/plans/)[^\s]+\.md)"
    )
    warnings = []

    for item in declaration.get("planned_work_items", []):
        if item.get("item_type") not in _GATE_TYPES:
            continue
        item_id = item.get("item_id", "UNKNOWN")
        for path_str in item.get("evidence_paths", []):
            if not _PLAN_RE.search(str(path_str)):
                continue
            p = (repo / path_str) if not Path(path_str).is_absolute() else Path(path_str)
            if not p.exists():
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            # Use the same taskcard regex patterns as lifecycle_audit.py
            tc_table = _re.findall(
                r"\|\s*(TC-[A-Z0-9]+-[A-Z0-9-]+)\s*\|\s*"
                r"(CLOSED|OPEN|IN_PROGRESS|PENDING|SUPERSEDED|EXCLUDED)\s*\|",
                text, _re.IGNORECASE,
            )
            tc_block = _re.findall(
                r"^#{1,4}\s+(TC-[A-Z0-9]+-[A-Z0-9-]+)\b[^\n]*\n"
                r"(?:[^\n]*\n){0,4}?"
                r"[^\n]*\*{0,2}Status:?\*{0,2}\s*(CLOSED|OPEN|IN_PROGRESS|PENDING|SUPERSEDED|EXCLUDED)",
                text, _re.IGNORECASE | _re.MULTILINE,
            )
            all_tcs = {}
            for tc_id, status in tc_table + tc_block:
                all_tcs.setdefault(tc_id.upper(), status.upper())
            open_tcs = [
                tc for tc, st in all_tcs.items()
                if st not in ("CLOSED", "SUPERSEDED", "EXCLUDED")
            ]
            if open_tcs:
                warnings.append({
                    "item_id": item_id,
                    "plan_path": str(path_str),
                    "open_taskcards": open_tcs,
                    "issue": (
                        f"RELEASE_GATE/READINESS item cites plan with "
                        f"{len(open_tcs)} open taskcard(s): {', '.join(open_tcs[:5])}"
                    ),
                })

    result = "WARN" if warnings else "PASS"
    return {
        "validator": "validate_terminal_closure_completeness",
        "result": result,
        "blocks_sprint": False,
        "items": warnings,
        "summary": (
            f"V60: {len(warnings)} gate item(s) cite plans with open taskcards"
            if warnings else "V60: No gate items cite plans with open taskcards"
        ),
    }


# ---------------------------------------------------------------------------
# V61 — TC-TCF-010: validate_error_fallback_safety
# ---------------------------------------------------------------------------


def validate_error_fallback_safety(
    declaration: dict | None = None,
    repo_root: Path | None = None,
) -> dict:
    """V61 (TC-TCF-010): Verify write_plan_lock.py error fallback writes ITERATION_REQUIRED.

    Structural smoke test: reads write_plan_lock.py and verifies that error fallback
    paths (except ImportError / except Exception blocks) write ITERATION_REQUIRED,
    not TERMINAL_CLOSED. This prevents regression of defect D6.

    Severity: FAIL if TERMINAL_CLOSED found in error fallback. blocks_sprint=True.
    Added 2026-06-23 (TC-FORENSICS-TERMINAL-20260623, TC-TCF-010).
    """
    repo = repo_root or _REPO_ROOT
    target = repo / "tools" / "supervisor" / "write_plan_lock.py"

    if not target.exists():
        return {
            "validator": "validate_error_fallback_safety",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V61: write_plan_lock.py not found -- skipped",
        }

    try:
        text = target.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {
            "validator": "validate_error_fallback_safety",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V61: Could not read write_plan_lock.py -- skipped",
        }

    # Look for except blocks that ASSIGN status = "TERMINAL_CLOSED"
    # Only flag direct assignments like: status = "TERMINAL_CLOSED"
    # Do NOT flag comparisons, conditionals, or string mentions
    _ASSIGN_RE = _re.compile(r'^\s*status\s*=\s*["\']TERMINAL_CLOSED["\']')
    violations = []
    lines = text.splitlines()
    in_except = False
    except_line = 0
    except_indent = 0
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        if stripped.startswith("except ") or stripped.startswith("except:"):
            in_except = True
            except_line = i
            except_indent = indent
        elif in_except and indent <= except_indent and stripped and not stripped.startswith("#"):
            # Dedented past except block
            if not stripped.startswith("except"):
                in_except = False
        if in_except and _ASSIGN_RE.match(line):
            violations.append({
                "line": i,
                "except_start": except_line,
                "content": stripped,
                "issue": (
                    f"Error fallback at line {i} assigns status='TERMINAL_CLOSED' "
                    f"(D6 regression) -- should be ITERATION_REQUIRED"
                ),
            })

    result = "FAIL" if violations else "PASS"
    return {
        "validator": "validate_error_fallback_safety",
        "result": result,
        "blocks_sprint": bool(violations),
        "items": violations,
        "summary": (
            f"V61: {len(violations)} error fallback path(s) still write TERMINAL_CLOSED (D6 regression!)"
            if violations else "V61: Error fallback paths correctly write ITERATION_REQUIRED"
        ),
    }


# ---------------------------------------------------------------------------
# V62 — TC-MACH-VAL-001: spec_fact_refs density validator
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# V63 — TC-MACH-SRC-001: public API surface ratio validator
# ---------------------------------------------------------------------------


def validate_public_api_surface_ratio(
    declaration: dict, repo_root: Path | None = None
) -> dict:
    """V63 (TC-MACH-SRC-001): WARN when __init__.py has >50 exports with <20% tested.

    Forward governance only — does not retroactively clean up existing exports.
    WARN-only mode (not BLOCK).
    """
    root = repo_root or _REPO_ROOT
    items = declaration.get("completed_work_items", [])
    if isinstance(items, list) and items and isinstance(items[0], str):
        items = declaration.get("planned_work_items", [])
    if not items:
        return {
            "validator": "validate_public_api_surface_ratio",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V63: No work items to check",
        }

    warnings = []
    for item in items:
        if not isinstance(item, dict):
            continue
        item_type = item.get("item_type", "")
        if item_type != "PRODUCT_SOURCE":
            continue

        changed = item.get("changed_files", [])
        for f in changed:
            if not isinstance(f, str):
                continue
            if not f.endswith("__init__.py"):
                continue
            if not (f.startswith("src/python/") or f.startswith("src/net/")):
                continue

            init_path = root / f.replace("/", "\\") if "\\" in str(root) else root / f
            if not init_path.exists():
                continue

            try:
                content = init_path.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(content)
            except Exception:
                continue

            # Count exports: look for __all__ or top-level names
            export_count = 0
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "__all__":
                            if isinstance(node.value, (ast.List, ast.Tuple)):
                                export_count = len(node.value.elts)
                elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if not node.name.startswith("_"):
                        export_count += 1

            if export_count > 50:
                # Check test coverage ratio (best-effort)
                fmt_parts = f.replace("\\", "/").split("/")
                if len(fmt_parts) >= 3:
                    fmt_name = fmt_parts[2]  # e.g., "ndjson" from "src/python/ndjson/__init__.py"
                    test_dir = root / "tests" / "python" / fmt_name
                    test_count = 0
                    if test_dir.exists():
                        test_count = sum(1 for p in test_dir.rglob("test_*.py") if "analytics" not in p.name)
                    coverage_ratio = test_count / export_count if export_count else 1.0
                    if coverage_ratio < 0.2:
                        item_id = item.get("item_id", item.get("id", "unknown"))
                        warnings.append({
                            "item_id": item_id,
                            "file": f,
                            "export_count": export_count,
                            "test_count": test_count,
                            "coverage_ratio": round(coverage_ratio, 2),
                            "issue": f"__init__.py has {export_count} exports but only {test_count} non-analytics test files ({coverage_ratio:.0%})",
                            "severity": "WARN",
                        })

    result = "WARN" if warnings else "PASS"
    return {
        "validator": "validate_public_api_surface_ratio",
        "result": result,
        "blocks_sprint": False,  # WARN-only mode
        "items": warnings,
        "summary": (
            f"V63: {len(warnings)} __init__.py file(s) have low test coverage ratio"
            if warnings else "V63: All modified __init__.py files have acceptable test coverage"
        ),
    }
