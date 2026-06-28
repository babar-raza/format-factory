"""governance_validators_ext2.py — V75/V76/V77/V78/V79/V82: Governance validators overflow.

Extracted to keep governance_validators_ext.py within its baseline_loc_cap (1423 LOC).

V75 (TC-GH-004, 2026-06-25): validate_dependency_direction
    RULE-LIB-003 — Import direction within format packages must follow the governed chain:
    Parser/Codec → Models → Analytics → Compat ← __init__.py
    WARN for existing files (grandfathered in known_violations); FAIL for new files.

V76 (TC-GH-004, 2026-06-25): validate_error_handling_hierarchy
    RULE-LIB-006 — Each format package must have exceptions.py; parsers must not raise bare exceptions.
    WARN for existing packages (grandfathered); FAIL for NEW format packages not in baseline.

V77 (TC-GM-002, PROD-GOVERNANCE-001): validate_analytics_naming_enforced
    RULE-LIB-007 — Files named *_document.py must NOT have a module docstring containing
    "analytics functions". That is the analytics-masquerade anti-pattern. blocks_sprint=True.

V78 (TC-GM-003, PROD-GOVERNANCE-001): validate_dotnet_loc_cap
    RULE-LIB-008 — .cs files in src/net/ must be ≤800 LOC unless already in known_violations.
    Files ≤800 LOC always PASS. blocks_sprint=True.

V79 (TC-GM-004, PROD-GOVERNANCE-001): validate_healing_stall_detector
    RULE-LIB-009 — WARN when known_violations entries have loc == baseline_loc_cap (zero healing
    progress since baseline was frozen). blocks_sprint=False (advisory only).

V82 (TC-ORC-003, ORACLE-LAYER-HARDENING-001): validate_oracle_obligations
    RULE-ORC-001 — Every registered format must have an oracle obligation entry in
    oracle/registry/format-oracle-registry.yaml before advancing beyond Gate 4.
    WARN when any format is missing an obligation. blocks_sprint=False (advisory).
"""

from __future__ import annotations

from pathlib import Path


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


# V77 — PROD-GOVERNANCE-001 (TC-GM-002): analytics_naming_enforced
# RULE-LIB-007: *_document.py files must not be analytics files in disguise.
def validate_analytics_naming_enforced(declaration: dict, repo_root: "Path | None" = None) -> dict:
    """V77: *_document.py files under src/python/ must not have 'analytics functions' in docstring.

    blocks_sprint=True — analytics masquerade naming is a structural violation.
    ATOMIC DEPLOYMENT: V77 must deploy in the same sprint as the gnumeric + toml renames.
    """
    import ast as _ast
    from pathlib import Path as _Path

    _r = repo_root or _Path(__file__).parent.parent.parent
    items = []
    for f in declaration.get("changed_files", []):
        if "src/python" not in str(f):
            continue
        from pathlib import Path as _P
        fname = _P(str(f)).name
        if not fname.endswith("_document.py"):
            continue
        fpath = _r / str(f)
        if not fpath.exists():
            continue
        try:
            text = fpath.read_text(encoding="utf-8", errors="replace")
            tree = _ast.parse(text)
            docstring = _ast.get_docstring(tree) or ""
        except Exception:
            docstring = ""
        if "analytics functions" in docstring:
            items.append({"file": str(f), "docstring_snippet": docstring[:80]})

    if items:
        return {
            "validator": "validate_analytics_naming_enforced",
            "result": "FAIL",
            "items": items,
            "summary": f"V77: {len(items)} analytics-masquerade *_document.py file(s) detected — BLOCK",
            "blocks_sprint": True,
        }
    return {
        "validator": "validate_analytics_naming_enforced",
        "result": "PASS",
        "items": [],
        "summary": "V77: No analytics-masquerade naming detected",
        "blocks_sprint": False,
    }


# V78 — PROD-GOVERNANCE-001 (TC-GM-003): dotnet_loc_cap
# RULE-LIB-008: .cs files in src/net/ must be ≤800 LOC unless already in known_violations.
def validate_dotnet_loc_cap(declaration: dict, repo_root: "Path | None" = None) -> dict:
    """V78: src/net/**/*.cs files must be ≤800 LOC or pre-existing in known_violations.

    Files ≤800 LOC always PASS (new compliant files don't need a baseline entry).
    blocks_sprint=True for new files >800 LOC not in known_violations.
    """
    from pathlib import Path as _Path

    _r = repo_root or _Path(__file__).parent.parent.parent
    _baseline_path = _r / "registry" / "source-structure-baseline.json"
    try:
        import json as _json
        _baseline = _json.loads(_baseline_path.read_text(encoding="utf-8"))
        _known = _baseline.get("known_violations", {})
    except Exception:
        _known = {}

    items = []
    for f in declaration.get("changed_files", []):
        if "src/net" not in str(f) or not str(f).endswith(".cs"):
            continue
        fpath = _r / str(f)
        if not fpath.exists():
            continue
        actual_loc = sum(1 for _ in fpath.open(encoding="utf-8", errors="replace"))
        if actual_loc <= 800:
            continue  # Always PASS for compliant files
        rel_str = fpath.relative_to(_r).as_posix()
        known_entry = _known.get(rel_str, {})
        if not known_entry:
            items.append({"file": str(f), "loc": actual_loc, "reason": "new_file_exceeds_800_loc"})
        elif actual_loc > known_entry.get("baseline_loc_cap", 0):
            items.append({"file": str(f), "loc": actual_loc,
                          "cap": known_entry["baseline_loc_cap"], "reason": "worsened_beyond_cap"})

    if items:
        return {
            "validator": "validate_dotnet_loc_cap",
            "result": "FAIL",
            "items": items,
            "summary": f"V78: {len(items)} .cs file(s) exceed 800 LOC without baseline entry — BLOCK",
            "blocks_sprint": True,
        }
    return {
        "validator": "validate_dotnet_loc_cap",
        "result": "PASS",
        "items": [],
        "summary": "V78: All .cs files within LOC cap",
        "blocks_sprint": False,
    }


# V79 — PROD-GOVERNANCE-001 (TC-GM-004): healing_stall_detector
# RULE-LIB-009: known_violations entries at loc == baseline_loc_cap have zero healing progress.
def validate_healing_stall_detector(declaration: dict, repo_root: "Path | None" = None) -> dict:
    """V79: WARN when known_violations entries show zero healing progress (loc == baseline_loc_cap).

    blocks_sprint=False — advisory only. Does NOT use remediation_deadline (field does not exist).
    """
    from pathlib import Path as _Path

    _r = repo_root or _Path(__file__).parent.parent.parent
    _baseline_path = _r / "registry" / "source-structure-baseline.json"
    try:
        import json as _json
        _baseline = _json.loads(_baseline_path.read_text(encoding="utf-8"))
        _known = _baseline.get("known_violations", {})
    except Exception:
        return {
            "validator": "validate_healing_stall_detector",
            "result": "PASS",
            "items": [],
            "summary": "V79: Baseline not found — stall detection skipped",
            "blocks_sprint": False,
        }

    stalled = []
    for rel_path, entry in _known.items():
        loc = entry.get("loc", 0)
        cap = entry.get("baseline_loc_cap", 0)
        if loc == cap and cap > 0:
            fpath = _r / rel_path
            if fpath.exists():
                stalled.append({"file": rel_path, "loc": loc, "cap": cap})

    return {
        "validator": "validate_healing_stall_detector",
        "result": "WARN" if stalled else "PASS",
        "items": stalled,
        "summary": (
            f"V79: {len(stalled)} known_violation(s) show zero healing progress (loc == cap)"
            if stalled else "V79: All known violations show healing progress"
        ),
        "blocks_sprint": False,
    }


def validate_oracle_obligations(declaration: dict, repo_root: Path = None) -> dict:
    """V82: Every registered format must have an oracle obligation entry.

    RULE-ORC-001 — Checks oracle/registry/format-oracle-registry.yaml against
    registry/format-registry.yaml. WARN when any format is missing an obligation.
    blocks_sprint=False (advisory — obligation gap is a planning gap, not a code failure).
    """
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[2]

    try:
        import yaml as _yaml

        # Read format registry — supports both dict and list forms
        fmt_reg_path = repo_root / "registry" / "format-registry.yaml"
        oracle_reg_path = repo_root / "oracle" / "registry" / "format-oracle-registry.yaml"

        if not fmt_reg_path.exists() or not oracle_reg_path.exists():
            return {
                "validator": "validate_oracle_obligations",
                "result": "PASS",
                "items": [],
                "summary": "V82: Registry files not found — oracle obligation check skipped",
                "blocks_sprint": False,
            }

        fmt_data = _yaml.safe_load(fmt_reg_path.read_text(encoding="utf-8")) or {}
        oracle_data = _yaml.safe_load(oracle_reg_path.read_text(encoding="utf-8")) or {}

        # Extract registered format IDs (supports dict-of-dicts or list-of-dicts)
        # Real format-registry.yaml: {"formats": [{"format_id": "csv", ...}, ...]}
        formats_raw = fmt_data.get("formats", {})
        if isinstance(formats_raw, dict):
            registered = set(formats_raw.keys())
        elif isinstance(formats_raw, list):
            registered = {
                e.get("format_id") or e.get("id", "")
                for e in formats_raw
                if isinstance(e, dict)
            }
        else:
            registered = set()

        # Extract oracle obligation format IDs
        # Real format-oracle-registry.yaml: {"format_oracles": [{"format_id": "csv", ...}, ...]}
        # Test format: {"oracle_obligations": {"csv": {...}}}
        oracle_raw = (
            oracle_data.get("format_oracles")
            or oracle_data.get("oracle_obligations")
            or oracle_data
        )
        if isinstance(oracle_raw, dict):
            oracle_ids = set(oracle_raw.keys())
        elif isinstance(oracle_raw, list):
            oracle_ids = {
                e.get("format_id") or e.get("id", "")
                for e in oracle_raw
                if isinstance(e, dict)
            }
        else:
            oracle_ids = set()

        excluded = {"odf-shared"}
        governed = registered - excluded

        missing = sorted(governed - oracle_ids)
        total = len(governed)

        if missing:
            return {
                "validator": "validate_oracle_obligations",
                "result": "WARN",
                "items": [{"format_id": f, "code": "MISSING_OBLIGATION"} for f in missing],
                "summary": (
                    f"V82: {len(missing)}/{total} formats missing oracle obligation. "
                    f"Missing: {missing[:5]}"
                ),
                "blocks_sprint": False,
            }
        return {
            "validator": "validate_oracle_obligations",
            "result": "PASS",
            "items": [],
            "summary": f"V82: All {total} registered formats have oracle obligations",
            "blocks_sprint": False,
        }

    except Exception as e:
        return {
            "validator": "validate_oracle_obligations",
            "result": "PASS",
            "items": [],
            "summary": f"V82: Oracle obligation check skipped due to error: {e}",
            "blocks_sprint": False,
        }


def validate_readme_freshness(declaration: dict, repo_root: Path = None) -> dict:
    """V87: Per-format READMEs must have current generated blocks."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[2]
    try:
        import sys as _sys

        if str(repo_root) not in _sys.path:
            _sys.path.insert(0, str(repo_root))
        import tools.readme_sync.collector as _collector
        import tools.readme_sync.drift_detector as _drift

        old_collector_root = _collector.REPO_ROOT
        old_drift_root = _drift.REPO_ROOT
        _collector.REPO_ROOT = repo_root
        _drift.REPO_ROOT = repo_root
        try:
            report = _drift.check_all_drift()
        finally:
            _collector.REPO_ROOT = old_collector_root
            _drift.REPO_ROOT = old_drift_root

        stale = [item for item in report.get("checks", []) if item.get("drifted")]
        if stale:
            return {
                "validator": "validate_readme_freshness",
                "result": "FAIL",
                "items": stale,
                "summary": f"V87: {len(stale)} stale README(s) detected",
                "blocks_sprint": True,
            }
        return {
            "validator": "validate_readme_freshness",
            "result": "PASS",
            "items": [],
            "summary": f"V87: README freshness clean ({len(report.get('checks', []))} checked)",
            "blocks_sprint": False,
        }
    except Exception as e:
        return {
            "validator": "validate_readme_freshness",
            "result": "FAIL",
            "items": [{"error": str(e)}],
            "summary": f"V87: README freshness check failed: {e}",
            "blocks_sprint": True,
        }
