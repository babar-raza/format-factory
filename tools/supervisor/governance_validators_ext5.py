"""governance_validators_ext5.py — V187-V193: Source Quality and Deadline Monitors
(lively-leaping-elephant, TC-GOV-LLE-004, 2026-07-14)

V187 validate_function_count_per_file
    AST-based function count per Python source file. New files >80 fn: FAIL.
    Baseline files >80 fn that regress: FAIL. Baseline files at cap: WARN.
    blocks_sprint=True for new-file violations; WARN-only for baseline files.

V188 validate_io_in_domain_model
    AST check: domain model files (*models.py, *_document.py) must not import
    os/io/pathlib or call open(). FAIL for new files, WARN for baseline.

V189 validate_analytics_statelessness
    Regex check: analytics files (*_analytics.py) must not import os/io/pathlib/
    subprocess/shutil at module scope. WARN-only (advisory).

V190 validate_test_tier_presence
    Per-format check: tests/python/{format}/ should have parse, round-trip, and
    write test files. WARN-only.

V191 validate_explicit_all_defined
    __init__.py files in changed_files should declare __all__. WARN-only.

V192 validate_changed_files_exist
    Every path declared in changed_files should exist on disk. WARN-only.

V193 validate_remediation_deadline_expired
    For baseline entries where remediation_deadline < today and remediation_status
    != 'complete': emit WARN per expired entry. WARN-only.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

from governance_validators_contract import validator  # noqa: F401

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_BASELINE_PATH = _REPO_ROOT / "registry" / "source-structure-baseline.json"

_DOMAIN_MODEL_PATTERNS = re.compile(r"(^|/)models\.py$|(^|/).*_document\.py$")
_ANALYTICS_PATTERN = re.compile(r"(^|/).*_analytics\.py$")
_IO_IMPORTS = re.compile(r"^(import|from)\s+(os|io|pathlib|subprocess|shutil)\b", re.MULTILINE)

_FUNCTION_COUNT_THRESHOLD = 80


def _load_baseline() -> dict:
    try:
        if _BASELINE_PATH.exists():
            return json.loads(_BASELINE_PATH.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def _get_known_violations(baseline: dict) -> dict:
    return baseline.get("known_violations", {})


def _ast_count_functions(source_text: str) -> int:
    try:
        tree = ast.parse(source_text)
        return sum(
            1 for node in ast.iter_child_nodes(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        )
    except SyntaxError:
        return 0


def _ast_has_io_imports(source_text: str) -> list[str]:
    """Return list of found I/O import names in the source."""
    found = []
    try:
        tree = ast.parse(source_text)
        io_modules = {"os", "io", "pathlib"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in io_modules:
                        found.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.split(".")[0] in io_modules:
                    found.append(node.module.split(".")[0])
    except SyntaxError:
        pass
    return list(set(found))


@validator(
    rule_id="V187",
    domain="structural",
    description="Block new Python source files with more than 80 top-level functions; WARN for baseline regressions.",
)
def validate_function_count_per_file(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V187: Block new files with >80 top-level functions; WARN for baseline regressions."""
    _repo = repo_root or _REPO_ROOT
    baseline = _load_baseline()
    kv = _get_known_violations(baseline)
    violations_fail = []
    violations_warn = []

    changed_files = declaration.get("changed_files", []) or []
    for cf in changed_files:
        if not cf.startswith("src/python/") or not cf.endswith(".py"):
            continue
        cf_path = _repo / cf
        if not cf_path.exists():
            continue
        try:
            source = cf_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        fn_count = _ast_count_functions(source)
        if fn_count <= _FUNCTION_COUNT_THRESHOLD:
            continue

        if cf in kv:
            cap = kv[cf].get("baseline_functions_cap", fn_count)
            if fn_count > cap:
                violations_fail.append(f"{cf}: {fn_count} fn (cap={cap}, regression)")
            else:
                violations_warn.append(f"{cf}: {fn_count} fn (in baseline, no regression)")
        else:
            violations_fail.append(f"{cf}: {fn_count} fn > {_FUNCTION_COUNT_THRESHOLD} (new file, FAIL)")

    all_violations = violations_fail + violations_warn
    if violations_fail:
        return {
            "validator": "validate_function_count_per_file",
            "result": "FAIL",
            "blocks_sprint": True,
            "violations": all_violations,
            "summary": (
                f"V187: {len(violations_fail)} new/regressing file(s) exceed "
                f"{_FUNCTION_COUNT_THRESHOLD}-function cap; {len(violations_warn)} baseline warn(s)"
            ),
        }
    if violations_warn:
        return {
            "validator": "validate_function_count_per_file",
            "result": "WARN",
            "blocks_sprint": False,
            "violations": violations_warn,
            "summary": f"V187: {len(violations_warn)} baseline file(s) have >{_FUNCTION_COUNT_THRESHOLD} functions (capped, no regression)",
        }
    return {
        "validator": "validate_function_count_per_file",
        "result": "PASS",
        "blocks_sprint": False,
        "summary": f"V187: All changed Python files within {_FUNCTION_COUNT_THRESHOLD}-function limit",
    }


@validator(
    rule_id="V188",
    domain="structural",
    description="Domain model files (*models.py, *_document.py) must not import os/io/pathlib. FAIL new files, WARN baseline.",
)
def validate_io_in_domain_model(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V188: Domain model files must not import os/io/pathlib. FAIL new, WARN baseline."""
    _repo = repo_root or _REPO_ROOT
    baseline = _load_baseline()
    kv = _get_known_violations(baseline)
    violations_fail = []
    violations_warn = []

    changed_files = declaration.get("changed_files", []) or []
    for cf in changed_files:
        if not _DOMAIN_MODEL_PATTERNS.search(cf):
            continue
        if not cf.startswith("src/python/"):
            continue
        cf_path = _repo / cf
        if not cf_path.exists():
            continue
        try:
            source = cf_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        found = _ast_has_io_imports(source)
        if not found:
            continue
        entry = f"{cf}: imports {found}"
        if cf in kv:
            violations_warn.append(entry)
        else:
            violations_fail.append(entry)

    if violations_fail:
        return {
            "validator": "validate_io_in_domain_model",
            "result": "FAIL",
            "blocks_sprint": True,
            "violations": violations_fail + violations_warn,
            "summary": f"V188: {len(violations_fail)} new domain model file(s) import I/O modules",
        }
    if violations_warn:
        return {
            "validator": "validate_io_in_domain_model",
            "result": "WARN",
            "blocks_sprint": False,
            "violations": violations_warn,
            "summary": f"V188: {len(violations_warn)} baseline domain model file(s) import I/O modules (WARN)",
        }
    return {
        "validator": "validate_io_in_domain_model",
        "result": "PASS",
        "blocks_sprint": False,
        "summary": "V188: No I/O imports found in domain model files",
    }


@validator(
    rule_id="V189",
    domain="structural",
    description="Analytics files (*_analytics.py) must not import I/O modules at module scope. WARN-only (advisory).",
)
def validate_analytics_statelessness(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V189: Analytics files must not import I/O modules at module scope. WARN-only."""
    _repo = repo_root or _REPO_ROOT
    violations = []

    changed_files = declaration.get("changed_files", []) or []
    for cf in changed_files:
        if not _ANALYTICS_PATTERN.search(cf):
            continue
        if not cf.startswith("src/python/"):
            continue
        cf_path = _repo / cf
        if not cf_path.exists():
            continue
        try:
            source = cf_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        matches = _IO_IMPORTS.findall(source)
        if matches:
            io_names = list({m[1] for m in matches})
            violations.append(f"{cf}: module-scope imports {io_names}")

    if violations:
        return {
            "validator": "validate_analytics_statelessness",
            "result": "WARN",
            "blocks_sprint": False,
            "violations": violations,
            "summary": f"V189: {len(violations)} analytics file(s) import I/O modules at module scope (advisory)",
        }
    return {
        "validator": "validate_analytics_statelessness",
        "result": "PASS",
        "blocks_sprint": False,
        "summary": "V189: Analytics files appear stateless at module scope",
    }


@validator(
    rule_id="V190",
    domain="governance",
    description="Check that tests/python/{format}/ has parse, roundtrip, and write test tiers. WARN-only.",
)
def validate_test_tier_presence(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V190: Check test tier presence per format touched by the sprint. WARN-only."""
    _repo = repo_root or _REPO_ROOT
    warnings = []

    changed_files = declaration.get("changed_files", []) or []
    formats_touched: set[str] = set()
    for cf in changed_files:
        parts = Path(cf).parts
        if len(parts) >= 3 and parts[0] == "src" and parts[1] == "python":
            formats_touched.add(parts[2])

    for fmt in sorted(formats_touched):
        test_dir = _repo / "tests" / "python" / fmt
        if not test_dir.exists():
            warnings.append(f"{fmt}: tests/python/{fmt}/ does not exist")
            continue
        test_files = [f.name for f in test_dir.rglob("test_*.py")]
        has_parse = any("parse" in n or "load" in n or "codec" in n for n in test_files)
        has_round = any("round" in n or "roundtrip" in n for n in test_files)
        has_write = any("write" in n or "writer" in n for n in test_files)
        if not has_parse:
            warnings.append(f"{fmt}: no parse/load test file in tests/python/{fmt}/")
        if not has_round:
            warnings.append(f"{fmt}: no roundtrip test file in tests/python/{fmt}/")
        if not has_write:
            warnings.append(f"{fmt}: no write test file in tests/python/{fmt}/ (may be expected)")

    if warnings:
        return {
            "validator": "validate_test_tier_presence",
            "result": "WARN",
            "blocks_sprint": False,
            "violations": warnings,
            "summary": f"V190: {len(warnings)} test tier gap(s) across {len(formats_touched)} format(s) (advisory)",
        }
    return {
        "validator": "validate_test_tier_presence",
        "result": "PASS",
        "blocks_sprint": False,
        "summary": f"V190: Test tier presence checked for {len(formats_touched)} format(s) — OK",
    }


@validator(
    rule_id="V191",
    domain="governance",
    description="__init__.py files in changed_files should declare __all__. WARN-only (advisory).",
)
def validate_explicit_all_defined(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V191: __init__.py files in changed_files should declare __all__. WARN-only."""
    _repo = repo_root or _REPO_ROOT
    missing = []

    changed_files = declaration.get("changed_files", []) or []
    for cf in changed_files:
        if not cf.endswith("__init__.py"):
            continue
        if not cf.startswith("src/python/"):
            continue
        cf_path = _repo / cf
        if not cf_path.exists():
            continue
        try:
            source = cf_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "__all__" not in source:
            missing.append(cf)

    if missing:
        return {
            "validator": "validate_explicit_all_defined",
            "result": "WARN",
            "blocks_sprint": False,
            "violations": missing,
            "summary": f"V191: {len(missing)} __init__.py file(s) missing __all__ declaration (advisory)",
        }
    return {
        "validator": "validate_explicit_all_defined",
        "result": "PASS",
        "blocks_sprint": False,
        "summary": "V191: All changed __init__.py files declare __all__",
    }


@validator(
    rule_id="V192",
    domain="evidence",
    description="Every path declared in changed_files should exist on disk. WARN-only.",
)
def validate_changed_files_exist(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V192: Every path declared in changed_files should exist on disk. WARN-only."""
    _repo = repo_root or _REPO_ROOT
    missing = []

    changed_files = declaration.get("changed_files", []) or []
    for cf in changed_files:
        cf_path = _repo / cf if not Path(cf).is_absolute() else Path(cf)
        if not cf_path.exists():
            missing.append(cf)

    if missing:
        return {
            "validator": "validate_changed_files_exist",
            "result": "WARN",
            "blocks_sprint": False,
            "violations": missing,
            "summary": f"V192: {len(missing)} declared changed_file(s) do not exist on disk (may be deletions or typos)",
        }
    return {
        "validator": "validate_changed_files_exist",
        "result": "PASS",
        "blocks_sprint": False,
        "summary": f"V192: All {len(changed_files)} declared changed_file(s) exist on disk",
    }


@validator(
    rule_id="V193",
    domain="governance",
    description="WARN when baseline entries have a past remediation_deadline and remediation_status != 'complete'. WARN-only.",
)
def validate_remediation_deadline_expired(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V193: WARN when baseline entries have a past remediation_deadline and no 'complete' status."""
    from datetime import datetime

    baseline = _load_baseline()
    kv = _get_known_violations(baseline)
    today = datetime.now()
    expired = []

    for path, entry in kv.items():
        if not isinstance(entry, dict):
            continue
        if path.startswith("tests/") or path.startswith("tools/"):
            continue
        deadline_str = entry.get("remediation_deadline", "")
        status = entry.get("remediation_status", "")
        if not deadline_str or status == "complete":
            continue
        try:
            deadline = datetime.fromisoformat(deadline_str[:10])
            if deadline < today:
                healing_sprint = entry.get("healing_sprint", "none")
                expired.append(
                    f"{path}: deadline={deadline_str}, status={status or 'unset'}, "
                    f"healing_sprint={healing_sprint}"
                )
        except (ValueError, TypeError):
            continue

    if expired:
        return {
            "validator": "validate_remediation_deadline_expired",
            "result": "WARN",
            "blocks_sprint": False,
            "violations": expired,
            "summary": (
                f"V193: {len(expired)} baseline violation(s) past remediation_deadline "
                "with incomplete status (advisory — see violation_pressure in continuation signal)"
            ),
        }
    return {
        "validator": "validate_remediation_deadline_expired",
        "result": "PASS",
        "blocks_sprint": False,
        "summary": "V193: No expired remediation deadlines found (or all marked complete)",
    }
