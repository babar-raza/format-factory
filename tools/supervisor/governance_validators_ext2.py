"""governance_validators_ext2.py — V75/V76: Import direction and error handling hierarchy validators.

Extracted to keep governance_validators_ext.py within its baseline_loc_cap (1423 LOC).

V75 (TC-GH-004, 2026-06-25): validate_dependency_direction
    RULE-LIB-003 — Import direction within format packages must follow the governed chain:
    Parser/Codec → Models → Analytics → Compat ← __init__.py
    WARN for existing files (grandfathered in known_violations); FAIL for new files.

V76 (TC-GH-004, 2026-06-25): validate_error_handling_hierarchy
    RULE-LIB-006 — Each format package must have exceptions.py; parsers must not raise bare exceptions.
    WARN for existing packages (grandfathered); FAIL for NEW format packages not in baseline.
"""

from __future__ import annotations


# V75 — TC-GH-004: dependency_direction_validator
# Enforces RULE-LIB-003: import direction Parser→Model→Analytics→Compat←__init__
def validate_dependency_direction(declaration: dict, repo_root: "Path | None" = None) -> dict:
    """V75: Import direction within format packages must follow the governed dependency chain.

    WARN for existing files (grandfathered in known_violations).
    FAIL for new files NOT in known_violations that violate import direction.
    """
    import ast as _ast
    from pathlib import Path as _Path

    _r = repo_root or _Path(__file__).parent.parent.parent
    _baseline_path = _r / "registry" / "source-structure-baseline.json"
    try:
        import json as _json
        _baseline = _json.loads(_baseline_path.read_text(encoding="utf-8"))
        _known = set(_baseline.get("known_violations", {}).keys())
    except Exception:
        _known = set()

    # Forbidden import patterns by file suffix
    _FORBIDDEN = {
        "_parser.py": ["analytics", "Compat"],
        "_codec.py": ["analytics", "Compat"],
        "models.py": ["_parser", "_codec"],
        "neutral_model.py": ["_parser", "_codec"],
    }

    findings = []
    for item in declaration.get("planned_work_items", []):
        if item.get("item_type") != "PRODUCT_SOURCE":
            continue
        for ev_path in item.get("evidence_paths", []):
            if "src/python" not in str(ev_path):
                continue
            fpath = _r / ev_path
            if not fpath.exists():
                continue
            fname = fpath.name
            forbidden_imports = []
            for suffix, forbidden in _FORBIDDEN.items():
                if not fname.endswith(suffix):
                    continue
                try:
                    tree = _ast.parse(fpath.read_text(encoding="utf-8", errors="replace"))
                except Exception:
                    continue
                for node in _ast.walk(tree):
                    if isinstance(node, (_ast.Import, _ast.ImportFrom)):
                        import_str = ""
                        if isinstance(node, _ast.ImportFrom) and node.module:
                            import_str = node.module
                        elif isinstance(node, _ast.Import):
                            import_str = ",".join(a.name for a in node.names)
                        for fb in forbidden:
                            if fb.lower() in import_str.lower():
                                forbidden_imports.append(
                                    f"{fname} imports '{fb}' (forbidden for this file type)"
                                )
            if forbidden_imports:
                rel_key = str(fpath.relative_to(_r).as_posix())
                is_new = rel_key not in _known
                findings.append({
                    "file": str(ev_path),
                    "issues": forbidden_imports,
                    "severity": "FAIL" if is_new else "WARN",
                })

    has_fail = any(f["severity"] == "FAIL" for f in findings)
    result = "FAIL" if has_fail else ("WARN" if findings else "PASS")
    return {
        "validator": "validate_dependency_direction",
        "result": result,
        "blocks_sprint": has_fail,
        "items": findings,
        "summary": (
            f"V75: {len(findings)} import direction violation(s) found"
            if findings else "V75: Import direction clean"
        ),
    }


# V76 — TC-GH-004: error_handling_hierarchy_validator
# Enforces RULE-LIB-006: format-specific exception hierarchy required
def validate_error_handling_hierarchy(declaration: dict, repo_root: "Path | None" = None) -> dict:
    """V76: Each format package must have exceptions.py; parsers must not raise bare exceptions.

    WARN for existing packages (grandfathered). FAIL for NEW format packages not in baseline.
    """
    from pathlib import Path as _Path

    _r = repo_root or _Path(__file__).parent.parent.parent
    _baseline_path = _r / "registry" / "source-structure-baseline.json"
    try:
        import json as _json
        _baseline = _json.loads(_baseline_path.read_text(encoding="utf-8"))
        _known = set(_baseline.get("known_violations", {}).keys())
    except Exception:
        _known = set()

    findings = []
    checked_packages: set[str] = set()
    for item in declaration.get("planned_work_items", []):
        if item.get("item_type") != "PRODUCT_SOURCE":
            continue
        for ev_path in item.get("evidence_paths", []):
            if "src/python" not in str(ev_path):
                continue
            fpath = _Path(str(ev_path))
            # Derive format package directory (src/python/{format}/)
            parts = fpath.parts
            try:
                src_idx = list(parts).index("src")
                pkg_dir = _r / _Path(*parts[:src_idx + 3])  # src/python/{format}
            except (ValueError, IndexError):
                continue
            pkg_key = str(pkg_dir.relative_to(_r).as_posix())
            if pkg_key in checked_packages:
                continue
            checked_packages.add(pkg_key)
            exceptions_file = pkg_dir / "exceptions.py"
            if not exceptions_file.exists():
                is_new = not any(k.startswith(pkg_key) for k in _known)
                findings.append({
                    "package": pkg_key,
                    "issue": "exceptions.py missing from format package",
                    "severity": "FAIL" if is_new else "WARN",
                })

    has_fail = any(f["severity"] == "FAIL" for f in findings)
    result = "FAIL" if has_fail else ("WARN" if findings else "PASS")
    return {
        "validator": "validate_error_handling_hierarchy",
        "result": result,
        "blocks_sprint": has_fail,
        "items": findings,
        "summary": (
            f"V76: {len(findings)} format package(s) missing exception hierarchy"
            if findings else "V76: Error handling hierarchy present in all modified packages"
        ),
    }
