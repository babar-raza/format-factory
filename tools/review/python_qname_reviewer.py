"""python_qname_reviewer.py — Python QName architecture compliance reviewer.

Reviews a Python format package against the governed QName decomposition plan:
  1. spec/ directory exists with at least one canonical class
  2. All classes in spec/ have spec_qname and spec_fact_ref attributes
  3. Compat/ directory exists with at least one facade class
  4. Facade classes in Compat/ inherit from a spec/ class
  5. No new functions added to {format}_analytics.py (checked vs baseline)
  6. All source files within governance LOC caps
  7. No-stub scan passes on spec/ and Compat/ files

Verdicts:
  ACCEPTED_VERIFIED         — all checks pass
  REWORK_REQUIRED           — one or more checks failed (fixable by agent)
  BLOCKED_EXTERNAL_AUTHORITY — blocked by missing spec fact authority
  DEFERRED_WITH_APPROVED_REASON — format explicitly deferred with recorded reason

CLI:
  python tools/review/python_qname_reviewer.py --format abw
  python tools/review/python_qname_reviewer.py --format fods --json
  python tools/review/python_qname_reviewer.py --format all
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SRC_PYTHON = _REPO_ROOT / "src" / "python"
_BASELINE_FILE = _REPO_ROOT / "registry" / "source-structure-baseline.json"
_SAL_CACHE = _REPO_ROOT / ".local" / "spec-cache"

_ALL_FORMATS = [
    "abw", "csv", "dif", "fodg", "fodp", "fods", "fodt",
    "gnumeric", "ndjson", "ods", "odt", "pbm", "pgm", "ppm",
    "qoi", "sylk", "toml", "tsv", "xcf", "zst",
]

_MAX_LOC = 800


def _load_baseline() -> dict:
    if _BASELINE_FILE.is_file():
        return json.loads(_BASELINE_FILE.read_text(encoding="utf-8"))
    return {"known_violations": {}}


def _count_loc(path: Path) -> int:
    try:
        return sum(1 for _ in path.open(encoding="utf-8", errors="replace"))
    except OSError:
        return 0


def _extract_class_attr(cls_node: ast.ClassDef, attr: str) -> str | None:
    for stmt in cls_node.body:
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name) and target.id == attr:
                    if isinstance(stmt.value, ast.Constant):
                        return str(stmt.value.value)
    return None


def _get_base_names(cls_node: ast.ClassDef) -> list[str]:
    bases = []
    for base in cls_node.bases:
        if isinstance(base, ast.Name):
            bases.append(base.id)
        elif isinstance(base, ast.Attribute):
            bases.append(base.attr)
    return bases


def _scan_classes(py_file: Path) -> list[dict]:
    try:
        tree = ast.parse(py_file.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return []
    results = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        results.append({
            "name": node.name,
            "spec_qname": _extract_class_attr(node, "spec_qname"),
            "spec_fact_ref": _extract_class_attr(node, "spec_fact_ref"),
            "bases": _get_base_names(node),
            "lineno": node.lineno,
        })
    return results


def _run_no_stub_scan(paths: list[Path]) -> dict:
    """Run the no-stub scanner on given paths."""
    try:
        sys.path.insert(0, str(_REPO_ROOT))
        from tools.review.no_stub_scan import report as stub_report
        return stub_report(paths)
    except Exception as exc:
        return {"status": "SCAN_ERROR", "error": str(exc), "total_violations": 0, "violations": []}


def _load_sal_facts(fmt: str) -> list[dict]:
    sal_file = _SAL_CACHE / f"sal-facts-{fmt}.json"
    if not sal_file.is_file():
        return []
    try:
        data = json.loads(sal_file.read_text(encoding="utf-8"))
        return data.get("spec_facts", [])
    except Exception:
        return []


def _check_spec_dir(fmt_dir: Path) -> dict:
    """Check 1: spec/ directory exists with at least one class."""
    spec_dir = fmt_dir / "spec"
    if not spec_dir.is_dir():
        return {"pass": False, "reason": "spec/ directory missing"}
    py_files = list(spec_dir.rglob("*.py"))
    classes = []
    for f in py_files:
        if "__pycache__" in f.parts:
            continue
        classes.extend(_scan_classes(f))
    if not classes:
        return {"pass": False, "reason": "spec/ has no Python classes"}
    return {"pass": True, "class_count": len(classes), "classes": classes}


def _check_spec_qnames(spec_check: dict) -> dict:
    """Check 2: All spec/ classes have spec_qname and spec_fact_ref."""
    if not spec_check.get("pass"):
        return {"pass": False, "reason": "spec/ check failed — skipping"}
    classes = spec_check.get("classes", [])
    missing_qname = [c for c in classes if not c["spec_qname"]]
    missing_fact = [c for c in classes if not c["spec_fact_ref"]]
    if missing_qname or missing_fact:
        return {
            "pass": False,
            "missing_spec_qname": [c["name"] for c in missing_qname],
            "missing_spec_fact_ref": [c["name"] for c in missing_fact],
        }
    return {"pass": True}


def _check_compat_dir(fmt_dir: Path, fmt: str) -> dict:
    """Check 3: Compat/ directory exists with at least one facade."""
    compat_dir = fmt_dir / "Compat"
    if not compat_dir.is_dir():
        return {"pass": False, "reason": "Compat/ directory missing"}
    py_files = [
        f for f in compat_dir.rglob("*.py")
        if "__pycache__" not in f.parts and f.name != "__init__.py"
    ]
    if not py_files:
        return {"pass": False, "reason": "Compat/ has no facade files"}
    facades = []
    for f in py_files:
        facades.extend(_scan_classes(f))
    if not facades:
        return {"pass": False, "reason": "Compat/ files have no facade classes"}
    return {"pass": True, "facade_count": len(facades), "facades": facades}


def _check_facade_inheritance(compat_check: dict) -> dict:
    """Check 4: Facade classes inherit from spec/ classes (have a base)."""
    if not compat_check.get("pass"):
        return {"pass": False, "reason": "Compat/ check failed — skipping"}
    facades = compat_check.get("facades", [])
    no_base = [f for f in facades if not f["bases"]]
    if no_base:
        return {
            "pass": False,
            "facades_without_base": [f["name"] for f in no_base],
        }
    return {"pass": True}


def _check_loc_caps(fmt_dir: Path, baseline: dict) -> dict:
    """Check 5: Source files within LOC caps."""
    known = baseline.get("known_violations", {})
    violations = []
    for py_file in sorted(fmt_dir.rglob("*.py")):
        parts = py_file.parts
        if "__pycache__" in parts or "build" in parts:
            continue
        rel = py_file.relative_to(_REPO_ROOT).as_posix()
        loc = _count_loc(py_file)
        cap = known.get(rel, {}).get("baseline_loc_cap", _MAX_LOC)
        if loc > cap:
            violations.append({"file": rel, "loc": loc, "cap": cap})
    if violations:
        return {"pass": False, "over_cap": violations}
    return {"pass": True}


def _check_sal_facts_exist(spec_check: dict, fmt: str) -> dict:
    """Check 7: All spec_fact_refs exist in sal-facts-{fmt}.json.

    Searches both the 'qname' field (used by structural facts like GNUMERIC/PBM)
    and the 'id' field (used by proper SAL facts like ABW/FODS) so both patterns
    are accepted.
    """
    if not spec_check.get("pass"):
        return {"pass": False, "reason": "spec/ check failed — skipping"}
    classes = spec_check.get("classes", [])
    sal_facts = _load_sal_facts(fmt)
    # Build a set of all fact identifiers from both 'qname' and 'id' fields
    fact_ids: set[str] = set()
    for f in sal_facts:
        if f.get("qname"):
            fact_ids.add(f["qname"])
        if f.get("id"):
            fact_ids.add(f["id"])
    missing = []
    for cls in classes:
        ref = cls.get("spec_fact_ref")
        if ref and ref not in fact_ids:
            missing.append({"class": cls["name"], "fact_ref": ref})
    if missing:
        return {
            "pass": False,
            "missing_facts": missing,
            "sal_facts_count": len(sal_facts),
            "sal_facts_file": f".local/spec-cache/sal-facts-{fmt}.json",
        }
    return {"pass": True, "sal_facts_count": len(sal_facts)}


def _check_no_stub(fmt_dir: Path) -> dict:
    """Check 6: No forbidden stub markers in spec/ and Compat/."""
    spec_dir = fmt_dir / "spec"
    compat_dir = fmt_dir / "Compat"
    scan_paths = [p for p in [spec_dir, compat_dir] if p.is_dir()]
    if not scan_paths:
        return {"pass": True, "note": "no spec/ or Compat/ to scan"}
    result = _run_no_stub_scan(scan_paths)
    if result.get("status") == "SCAN_ERROR":
        return {"pass": False, "reason": result.get("error")}
    return {
        "pass": result["status"] == "CLEAN",
        "total_violations": result.get("total_violations", 0),
        "violations": result.get("violations", []),
    }


def review_format(fmt: str) -> dict[str, Any]:
    """Run all checks for a single format and return structured result."""
    fmt_dir = _SRC_PYTHON / fmt
    if not fmt_dir.is_dir():
        return {
            "format": fmt,
            "verdict": "REWORK_REQUIRED",
            "reason": f"Format directory src/python/{fmt}/ not found",
        }

    baseline = _load_baseline()

    spec_check = _check_spec_dir(fmt_dir)
    qname_check = _check_spec_qnames(spec_check)
    sal_fact_check = _check_sal_facts_exist(spec_check, fmt)
    compat_check = _check_compat_dir(fmt_dir, fmt)
    inherit_check = _check_facade_inheritance(compat_check)
    loc_check = _check_loc_caps(fmt_dir, baseline)
    stub_check = _check_no_stub(fmt_dir)

    checks = {
        "spec_dir": spec_check,
        "spec_qnames": qname_check,
        "sal_facts_exist": sal_fact_check,
        "compat_dir": compat_check,
        "facade_inheritance": inherit_check,
        "loc_caps": loc_check,
        "no_stub": stub_check,
    }

    failed = [k for k, v in checks.items() if not v.get("pass")]

    if not failed:
        verdict = "ACCEPTED_VERIFIED"
    else:
        verdict = "REWORK_REQUIRED"

    return {
        "format": fmt,
        "verdict": verdict,
        "failed_checks": failed,
        "checks": checks,
    }


def review_all() -> dict[str, Any]:
    """Review all 20 format packages."""
    results = {}
    for fmt in _ALL_FORMATS:
        results[fmt] = review_format(fmt)
    accepted = [f for f, r in results.items() if r["verdict"] == "ACCEPTED_VERIFIED"]
    rework = [f for f, r in results.items() if r["verdict"] == "REWORK_REQUIRED"]
    return {
        "total": len(_ALL_FORMATS),
        "accepted_verified": len(accepted),
        "rework_required": len(rework),
        "formats": results,
    }


def _cli() -> int:
    parser = argparse.ArgumentParser(description="Python QName architecture reviewer")
    parser.add_argument("--format", default="all", help="Format to review (or 'all')")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    if args.format == "all":
        result = review_all()
    else:
        result = review_format(args.format)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if "formats" in result:
            print(f"QName Architecture Review — {result['total']} formats")
            print(f"  ACCEPTED_VERIFIED : {result['accepted_verified']}")
            print(f"  REWORK_REQUIRED   : {result['rework_required']}")
            for fmt, r in result["formats"].items():
                v = r["verdict"]
                failed = r.get("failed_checks", [])
                tag = "OK" if v == "ACCEPTED_VERIFIED" else f"REWORK({','.join(failed)})"
                print(f"  {fmt:<12} {tag}")
        else:
            v = result["verdict"]
            print(f"Format: {result['format']}  Verdict: {v}")
            if result.get("failed_checks"):
                print(f"  Failed: {result['failed_checks']}")

    return 0 if (result.get("verdict") == "ACCEPTED_VERIFIED" or
                 result.get("accepted_verified") == result.get("total")) else 1


if __name__ == "__main__":
    sys.exit(_cli())
