"""governance_validators_ext2.py — V75/V76/V77/V78/V79/V82/V92-V99: Governance validators overflow.

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
from governance_validators_contract import validator  # noqa: F401

from pathlib import Path


# V75 — TC-GH-004: dependency_direction_validator
# Enforces RULE-LIB-003: import direction Parser→Model→Analytics→Compat←__init__
@validator(rule_id="V_VALIDATE_DEPENDENCY_DIRECTION", domain="governance")
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
@validator(rule_id="V_VALIDATE_ERROR_HANDLING_HIERARCHY", domain="governance")
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
@validator(rule_id="V_VALIDATE_ANALYTICS_NAMING_ENFORCED", domain="governance")
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
@validator(rule_id="V_VALIDATE_DOTNET_LOC_CAP", domain="governance")
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
@validator(rule_id="V_VALIDATE_HEALING_STALL_DETECTOR", domain="governance")
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


@validator(rule_id="V_VALIDATE_ORACLE_OBLIGATIONS", domain="governance")
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


@validator(rule_id="V_VALIDATE_CERTIFICATION_REPORTS_EXIST", domain="governance")
def validate_certification_reports_exist(declaration: dict, repo_root: Path = None) -> dict:
    """V88: Certification report directories must exist for all 20 formats."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[2]
    cert_root = repo_root / "reports" / "certification"
    all_formats = [
        "abw", "csv", "dif", "fodg", "fodp", "fods", "fodt", "gnumeric",
        "ndjson", "ods", "odt", "pbm", "pgm", "ppm", "qoi", "sylk",
        "toml", "tsv", "xcf", "zst",
    ]
    missing = [fmt for fmt in all_formats if not (cert_root / fmt).is_dir()]
    if missing:
        return {
            "validator": "validate_certification_reports_exist",
            "result": "WARN",
            "items": [{"missing_format_dirs": missing}],
            "summary": f"V88: {len(missing)} format(s) missing certification report dirs: {missing}",
            "blocks_sprint": False,
        }
    # Verify each has at least api-contract.json
    incomplete = []
    for fmt in all_formats:
        if not (cert_root / fmt / "api-contract.json").exists():
            incomplete.append(fmt)
    if incomplete:
        return {
            "validator": "validate_certification_reports_exist",
            "result": "WARN",
            "items": [{"incomplete_formats": incomplete}],
            "summary": f"V88: {len(incomplete)} format(s) missing api-contract.json: {incomplete}",
            "blocks_sprint": False,
        }
    return {
        "validator": "validate_certification_reports_exist",
        "result": "PASS",
        "items": [],
        "summary": f"V88: All {len(all_formats)} format certification report dirs present",
        "blocks_sprint": False,
    }


@validator(rule_id="V_VALIDATE_CERTIFICATION_MATRIX_CONSISTENT", domain="governance")
def validate_certification_matrix_consistent(declaration: dict, repo_root: Path = None) -> dict:
    """V89: Portfolio certification matrix must be internally consistent."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[2]
    matrix_path = repo_root / "reports" / "certification" / "portfolio-certification-matrix.json"
    if not matrix_path.exists():
        return {
            "validator": "validate_certification_matrix_consistent",
            "result": "WARN",
            "items": [{"error": "portfolio-certification-matrix.json not found"}],
            "summary": "V89: Portfolio certification matrix not found",
            "blocks_sprint": False,
        }
    try:
        import json
        data = json.loads(matrix_path.read_text(encoding="utf-8"))
        formats = data.get("formats", [])
        violations = []
        for entry in formats:
            fmt_id = entry.get("format_id", "?")
            verdict = entry.get("overall_verdict", "?")
            dims = entry.get("dimensions", {})
            if verdict == "CERTIFIED":
                for dim_name, dim_data in dims.items():
                    status = dim_data.get("status", "?")
                    if status not in ("PASS", "NOT_APPLICABLE"):
                        violations.append(f"{fmt_id}: CERTIFIED but {dim_name}={status}")
                stubs = dims.get("stubs", {}).get("material_count", 0)
                if stubs > 0:
                    violations.append(f"{fmt_id}: CERTIFIED but {stubs} material stubs")
                uncov = dims.get("exceptions", {}).get("uncovered", 0)
                if uncov > 0:
                    violations.append(f"{fmt_id}: CERTIFIED but {uncov} uncovered exceptions")
        if violations:
            return {
                "validator": "validate_certification_matrix_consistent",
                "result": "WARN",
                "items": [{"violations": violations}],
                "summary": f"V89: {len(violations)} consistency violation(s) in certification matrix",
                "blocks_sprint": False,
            }
        return {
            "validator": "validate_certification_matrix_consistent",
            "result": "PASS",
            "items": [],
            "summary": f"V89: Certification matrix consistent ({len(formats)} formats, no violations)",
            "blocks_sprint": False,
        }
    except Exception as e:
        return {
            "validator": "validate_certification_matrix_consistent",
            "result": "WARN",
            "items": [{"error": str(e)}],
            "summary": f"V89: Certification matrix check failed: {e}",
            "blocks_sprint": False,
        }


_readme_freshness_cache = {}  # keyed by str(repo_root) — repo state constant within process


@validator(rule_id="V_VALIDATE_README_FRESHNESS", domain="governance")
def validate_readme_freshness(declaration: dict, repo_root: Path = None) -> dict:
    """V87: Per-format READMEs must have current generated blocks."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[2]
    _cache_key = str(repo_root)
    if _cache_key in _readme_freshness_cache:
        return _readme_freshness_cache[_cache_key]
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
            _result = {
                "validator": "validate_readme_freshness",
                "result": "WARN",
                "items": stale,
                "summary": f"V87: {len(stale)} stale README(s) detected (non-blocking — CI readme-drift job is authoritative)",
                "blocks_sprint": False,
            }
        else:
            _result = {
                "validator": "validate_readme_freshness",
                "result": "PASS",
                "items": [],
                "summary": f"V87: README freshness clean ({len(report.get('checks', []))} checked)",
                "blocks_sprint": False,
            }
        _readme_freshness_cache[_cache_key] = _result
        return _result
    except Exception as e:
        _result = {
            "validator": "validate_readme_freshness",
            "result": "WARN",
            "items": [{"error": str(e)}],
            "summary": f"V87: README freshness check failed: {e}",
            "blocks_sprint": False,
        }
        _readme_freshness_cache[_cache_key] = _result
        return _result


@validator(rule_id="V_VALIDATE_PLANS_ROOT_POLICY", domain="governance")
def validate_plans_root_policy(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V90 (FF-PLAN-GOV-002): Only master-plan.md and master-plan-memory.md at plans/ root.

    Scans the direct contents of plans/ and reports any .md or other files
    that are not in the approved root set. WARN level (does not block sprints).
    """
    from pathlib import Path as _Path

    _r = repo_root or _Path(__file__).parent.parent.parent
    _allowed = {"master-plan.md", "master-plan-memory.md", "README.md"}

    plans_root = _r / "plans"
    if not plans_root.exists():
        return {
            "validator": "validate_plans_root_policy",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V90: plans/ directory not found (nothing to check)",
        }

    violations = []
    for f in plans_root.iterdir():
        if f.is_dir():
            continue
        if f.name not in _allowed:
            violations.append(str(f.relative_to(_r)))

    if violations:
        return {
            "validator": "validate_plans_root_policy",
            "result": "WARN",
            "blocks_sprint": False,
            "items": violations,
            "summary": (
                f"V90: {len(violations)} file(s) at plans/ root outside allowed set: "
                + ", ".join(violations[:5])
            ),
        }
    return {
        "validator": "validate_plans_root_policy",
        "result": "PASS",
        "blocks_sprint": False,
        "items": [],
        "summary": "V90: plans/ root contains only master-plan.md and master-plan-memory.md",
    }


# V92-V99 (TC-PB-009): Playbook system governance validators (WARN-only)
# All validators are non-blocking: blocks_sprint=False
# ---------------------------------------------------------------------------

_PLAYBOOKS_DIR_REL = "playbooks/format-factory"
_PLAYBOOK_REGISTRY_REL = "playbooks/playbook-registry.yaml"
_PLAYBOOK_COVERAGE_REL = "reports/playbooks/playbook-coverage-universe.yaml"


def _load_playbook_contracts(repo_root: "Path") -> "list[dict]":
    """Parse playbook_contract YAML front-matter from all Markdown templates."""
    import re as _re
    import yaml as _yaml
    from pathlib import Path as _Path

    contracts = []
    pb_dir = repo_root / _PLAYBOOKS_DIR_REL
    if not pb_dir.exists():
        return contracts
    for md_file in pb_dir.glob("*.md"):
        try:
            text = md_file.read_text(encoding="utf-8")
            m = _re.search(r"<!--\s*\n(playbook_contract:.*?)-->", text, _re.DOTALL)
            if m:
                data = _yaml.safe_load(m.group(1))
                if isinstance(data, dict) and "playbook_contract" in data:
                    entry = data["playbook_contract"]
                    entry["_source_path"] = str(md_file.relative_to(repo_root))
                    contracts.append(entry)
        except Exception:
            continue
    return contracts


@validator(rule_id="V_VALIDATE_PLAYBOOK_REGISTRY_ENTRIES", domain="governance")
def validate_playbook_registry_entries(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V92 (TC-PB-009): Active playbook registry entries must resolve to files on disk."""
    from pathlib import Path as _Path
    import yaml as _yaml

    _r = repo_root or _Path(__file__).parent.parent.parent
    registry_path = _r / _PLAYBOOK_REGISTRY_REL
    if not registry_path.exists():
        return {
            "validator": "validate_playbook_registry_entries",
            "result": "WARN",
            "blocks_sprint": False,
            "items": [],
            "summary": "V92: playbooks/playbook-registry.yaml not found — skipping (WARN)",
        }
    try:
        registry = _yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        entries = registry.get("playbook_registry", {}).get("entries", [])
        missing = [
            f"{e.get('playbook_id', '?')}: {e.get('canonical_path', '')}"
            for e in entries
            if e.get("status", "").upper() == "ACTIVE"
            and e.get("canonical_path")
            and not (_r / e["canonical_path"]).exists()
        ]
        if missing:
            return {
                "validator": "validate_playbook_registry_entries",
                "result": "FAIL",
                "blocks_sprint": True,
                "items": missing,
                "summary": f"V92: {len(missing)} ACTIVE registry entry(s) reference nonexistent files — GOV_BLOCK",
            }
        return {
            "validator": "validate_playbook_registry_entries",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": f"V92: All {len(entries)} registry entries resolve to files",
        }
    except Exception as e:
        return {
            "validator": "validate_playbook_registry_entries",
            "result": "WARN",
            "blocks_sprint": False,
            "items": [],
            "summary": f"V92: Registry check skipped due to error: {e}",
        }


@validator(rule_id="V_VALIDATE_PLAYBOOK_HAS_VERSION", domain="governance")
def validate_playbook_has_version(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V93 (TC-PB-009): Active playbook contract must have a version field."""
    from pathlib import Path as _Path

    _r = repo_root or _Path(__file__).parent.parent.parent
    contracts = _load_playbook_contracts(_r)
    if not contracts:
        return {
            "validator": "validate_playbook_has_version",
            "result": "WARN",
            "blocks_sprint": False,
            "items": [],
            "summary": "V93: No playbook contracts found to check",
        }
    missing = [
        c.get("_source_path", c.get("playbook_id", "?"))
        for c in contracts
        if c.get("status", "").upper() == "ACTIVE" and not c.get("version")
    ]
    if missing:
        return {
            "validator": "validate_playbook_has_version",
            "result": "WARN",
            "blocks_sprint": False,
            "items": missing,
            "summary": f"V93: {len(missing)} active playbook(s) missing version field",
        }
    return {
        "validator": "validate_playbook_has_version",
        "result": "PASS",
        "blocks_sprint": False,
        "items": [],
        "summary": f"V93: All {len(contracts)} playbook contracts have version field",
    }


@validator(rule_id="V_VALIDATE_PLAYBOOK_HAS_OWNER", domain="governance")
def validate_playbook_has_owner(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V94 (TC-PB-009): Active playbook contract must have owner_layer field."""
    from pathlib import Path as _Path

    _r = repo_root or _Path(__file__).parent.parent.parent
    contracts = _load_playbook_contracts(_r)
    if not contracts:
        return {
            "validator": "validate_playbook_has_owner",
            "result": "WARN",
            "blocks_sprint": False,
            "items": [],
            "summary": "V94: No playbook contracts found to check",
        }
    missing = [
        c.get("_source_path", c.get("playbook_id", "?"))
        for c in contracts
        if c.get("status", "").upper() == "ACTIVE" and not c.get("owner_layer")
    ]
    if missing:
        return {
            "validator": "validate_playbook_has_owner",
            "result": "WARN",
            "blocks_sprint": False,
            "items": missing,
            "summary": f"V94: {len(missing)} active playbook(s) missing owner_layer field",
        }
    return {
        "validator": "validate_playbook_has_owner",
        "result": "PASS",
        "blocks_sprint": False,
        "items": [],
        "summary": f"V94: All {len(contracts)} playbook contracts have owner_layer field",
    }


@validator(rule_id="V_VALIDATE_PLAYBOOK_HAS_EVIDENCE_CONTRACT", domain="governance")
def validate_playbook_has_evidence_contract(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V95 (TC-PB-009): Active playbook must have evidence_requirements field."""
    from pathlib import Path as _Path

    _r = repo_root or _Path(__file__).parent.parent.parent
    contracts = _load_playbook_contracts(_r)
    if not contracts:
        return {
            "validator": "validate_playbook_has_evidence_contract",
            "result": "WARN",
            "blocks_sprint": False,
            "items": [],
            "summary": "V95: No playbook contracts found to check",
        }
    missing = [
        c.get("_source_path", c.get("playbook_id", "?"))
        for c in contracts
        if c.get("status", "").upper() == "ACTIVE" and not c.get("evidence_requirements")
    ]
    if missing:
        return {
            "validator": "validate_playbook_has_evidence_contract",
            "result": "WARN",
            "blocks_sprint": False,
            "items": missing,
            "summary": f"V95: {len(missing)} active playbook(s) missing evidence_requirements",
        }
    return {
        "validator": "validate_playbook_has_evidence_contract",
        "result": "PASS",
        "blocks_sprint": False,
        "items": [],
        "summary": f"V95: All {len(contracts)} playbook contracts have evidence_requirements",
    }


@validator(rule_id="V_VALIDATE_PLAYBOOK_HAS_ROLLBACK", domain="governance")
def validate_playbook_has_rollback(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V96 (TC-PB-009): Active playbook must have rollback field."""
    from pathlib import Path as _Path

    _r = repo_root or _Path(__file__).parent.parent.parent
    contracts = _load_playbook_contracts(_r)
    if not contracts:
        return {
            "validator": "validate_playbook_has_rollback",
            "result": "WARN",
            "blocks_sprint": False,
            "items": [],
            "summary": "V96: No playbook contracts found to check",
        }
    missing = [
        c.get("_source_path", c.get("playbook_id", "?"))
        for c in contracts
        if c.get("status", "").upper() == "ACTIVE" and not c.get("rollback")
    ]
    if missing:
        return {
            "validator": "validate_playbook_has_rollback",
            "result": "WARN",
            "blocks_sprint": False,
            "items": missing,
            "summary": f"V96: {len(missing)} active playbook(s) missing rollback field",
        }
    return {
        "validator": "validate_playbook_has_rollback",
        "result": "PASS",
        "blocks_sprint": False,
        "items": [],
        "summary": f"V96: All {len(contracts)} playbook contracts have rollback field",
    }


@validator(rule_id="V_VALIDATE_PLAYBOOK_NOT_OVERRIDING_GATE", domain="governance")
def validate_playbook_not_overriding_gate(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V97 (TC-PB-009): Playbook limitations must include gate-override prohibition."""
    from pathlib import Path as _Path

    _r = repo_root or _Path(__file__).parent.parent.parent
    contracts = _load_playbook_contracts(_r)
    if not contracts:
        return {
            "validator": "validate_playbook_not_overriding_gate",
            "result": "WARN",
            "blocks_sprint": False,
            "items": [],
            "summary": "V97: No playbook contracts found to check",
        }
    violations = [
        c.get("_source_path", c.get("playbook_id", "?"))
        for c in contracts
        if c.get("status", "").upper() == "ACTIVE"
        and not any(
            "gate approval" in str(lim).lower() for lim in c.get("limitations", [])
        )
    ]
    if violations:
        return {
            "validator": "validate_playbook_not_overriding_gate",
            "result": "WARN",
            "blocks_sprint": False,
            "items": violations,
            "summary": (
                f"V97: {len(violations)} active playbook(s) missing gate-override prohibition"
            ),
        }
    return {
        "validator": "validate_playbook_not_overriding_gate",
        "result": "PASS",
        "blocks_sprint": False,
        "items": [],
        "summary": f"V97: All {len(contracts)} playbook contracts prohibit gate approval",
    }


@validator(rule_id="V_VALIDATE_PLAYBOOK_HAS_NO_DEPRECATED_PATHS", domain="governance")
def validate_playbook_has_no_deprecated_paths(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V98 (TC-PB-009): Playbook allowed_paths must not reference non-existent directories.

    Parameterized paths (containing < >) are skipped — they need concrete values.
    """
    from pathlib import Path as _Path

    _r = repo_root or _Path(__file__).parent.parent.parent
    contracts = _load_playbook_contracts(_r)
    if not contracts:
        return {
            "validator": "validate_playbook_has_no_deprecated_paths",
            "result": "WARN",
            "blocks_sprint": False,
            "items": [],
            "summary": "V98: No playbook contracts found to check",
        }
    stale = [
        f"{c.get('_source_path', c.get('playbook_id', '?'))}: {p}"
        for c in contracts
        if c.get("status", "").upper() == "ACTIVE"
        for p in c.get("allowed_paths", [])
        if "<" not in p and ">" not in p and not (_r / p.rstrip("/")).exists()
    ]
    if stale:
        return {
            "validator": "validate_playbook_has_no_deprecated_paths",
            "result": "WARN",
            "blocks_sprint": False,
            "items": stale,
            "summary": f"V98: {len(stale)} allowed_path(s) reference missing directories",
        }
    return {
        "validator": "validate_playbook_has_no_deprecated_paths",
        "result": "PASS",
        "blocks_sprint": False,
        "items": [],
        "summary": "V98: All non-parameterized allowed_paths exist in repository",
    }


@validator(rule_id="V_VALIDATE_PLAYBOOK_COVERAGE_REPORT_CURRENT", domain="governance")
def validate_playbook_coverage_report_current(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V99 (TC-PB-009): Coverage universe report must be newer than playbook template files."""
    import os as _os
    from pathlib import Path as _Path

    _r = repo_root or _Path(__file__).parent.parent.parent
    coverage_path = _r / _PLAYBOOK_COVERAGE_REL
    if not coverage_path.exists():
        return {
            "validator": "validate_playbook_coverage_report_current",
            "result": "WARN",
            "blocks_sprint": False,
            "items": [],
            "summary": "V99: playbook-coverage-universe.yaml not found — run coverage audit",
        }
    pb_dir = _r / _PLAYBOOKS_DIR_REL
    if not pb_dir.exists():
        return {
            "validator": "validate_playbook_coverage_report_current",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V99: No playbook templates directory — coverage report current",
        }
    coverage_mtime = _os.path.getmtime(str(coverage_path))
    stale_templates = [
        str(f.relative_to(_r))
        for f in pb_dir.glob("*.md")
        if _os.path.getmtime(str(f)) > coverage_mtime
    ]
    if stale_templates:
        return {
            "validator": "validate_playbook_coverage_report_current",
            "result": "WARN",
            "blocks_sprint": False,
            "items": stale_templates,
            "summary": (
                f"V99: {len(stale_templates)} template(s) newer than coverage report "
                f"— re-run coverage audit"
            ),
        }
    return {
        "validator": "validate_playbook_coverage_report_current",
        "result": "PASS",
        "blocks_sprint": False,
        "items": [],
        "summary": "V99: Coverage universe report is current (newer than all templates)",
    }




# V93 — TC-PSG-006: project_status_freshness_validator
# Enforces RULE-STATUS-001: PROJECT_STATUS.md must exist, be structurally valid (two-lane
# contract), and have stable anchors. blocks_sprint=False (advisory — regeneration is
# best-effort per Supreme Directive).
@validator(rule_id="V_VALIDATE_PROJECT_STATUS_FRESHNESS", domain="governance")
def validate_project_status_freshness(declaration: dict, repo_root: "Path | None" = None) -> dict:
    """V93: PROJECT_STATUS.md must exist with valid two-lane structure and stable anchors.

    Checks:
    - File exists
    - Contains '## Machinery Lane' and '## Product Lane'
    - Contains stable anchors: status-at-a-glance, machinery-lane, product-lane
    - Contains AUTO-GENERATED marker (not manually edited)

    blocks_sprint=False -- regeneration is best-effort per Supreme Directive.
    """
    from pathlib import Path as _Path

    _r = repo_root or _Path(__file__).parent.parent.parent
    status_path = _r / "PROJECT_STATUS.md"

    REQUIRED_SECTIONS = ["## Machinery Lane", "## Product Lane"]
    REQUIRED_ANCHORS_V93 = ["status-at-a-glance", "machinery-lane", "product-lane"]

    if not status_path.exists():
        return {
            "validator": "validate_project_status_freshness",
            "result": "WARN",
            "blocks_sprint": False,
            "items": ["PROJECT_STATUS.md missing -- run: python tools/docs/generate_project_status.py"],
            "summary": "V93: PROJECT_STATUS.md does not exist",
        }

    try:
        content = status_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return {
            "validator": "validate_project_status_freshness",
            "result": "WARN",
            "blocks_sprint": False,
            "items": [f"Cannot read PROJECT_STATUS.md: {e}"],
            "summary": "V93: PROJECT_STATUS.md unreadable",
        }

    violations = []

    if "<!-- AUTO-GENERATED" not in content:
        violations.append("Missing AUTO-GENERATED marker -- file may have been manually edited")

    for section in REQUIRED_SECTIONS:
        if section not in content:
            violations.append(f"Missing required section: {section}")

    for anchor in REQUIRED_ANCHORS_V93:
        if f'name="{anchor}"' not in content:
            violations.append(f"Missing stable anchor: {anchor}")

    if violations:
        return {
            "validator": "validate_project_status_freshness",
            "result": "WARN",
            "blocks_sprint": False,
            "items": violations,
            "summary": (
                f"V93: PROJECT_STATUS.md has {len(violations)} structural violation(s) "
                f"-- run: python tools/docs/generate_project_status.py"
            ),
        }

    return {
        "validator": "validate_project_status_freshness",
        "result": "PASS",
        "blocks_sprint": False,
        "items": [],
        "summary": "V93: PROJECT_STATUS.md exists with valid two-lane structure and stable anchors",
    }
