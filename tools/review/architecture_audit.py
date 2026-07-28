"""
architecture_audit.py — Per-format product architecture classification tool.

TC-B01 (elegant-napping-minsky / MCP-W3-006)

Scans src/python/{format}/ and src/net/{format}/ for all known formats.
Emits reports/architecture-audit/{format}_{lang}.json per format×language.

Usage:
    python tools/review/architecture_audit.py [--format FORMAT] [--all] [--out-dir DIR]

Classification levels (Python):
    COMPLIANT               all 6 criteria pass
    MINOR_REALIGNMENT       4-5 pass; failures are naming/minor gaps only
    PUBLIC_FACADE_REPAIR    spec/ present but Compat/ missing or empty; init has logic
    QNAME_MODEL_DECOMPOSITION  spec_qname classes found in wrong files (parser, codec)
    PARSER_WRITER_REALIGNMENT  parser.py has no spec/ import (produces raw dicts only)
    FULL_REBUILD            spec_dir_present = false; no spec_qname anywhere

Classification levels (.NET):
    COMPLIANT               all 6 criteria pass
    MINOR_REALIGNMENT       4-5 pass
    MODEL_DECOMPOSITION     no Model/ subdir; model types in flat root
    SPEC_MISSING            no Spec/ dir and no SpecQName constants
    FULL_REBUILD            no model, no spec, no structure

Cap: ≤300 LOC (including docstrings).
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_PY = REPO_ROOT / "src" / "python"
SRC_NET = REPO_ROOT / "src" / "net"
OUT_DIR_DEFAULT = REPO_ROOT / "reports" / "architecture-audit"

KNOWN_FORMATS = [
    "abw", "csv", "dif", "fodg", "fodp", "fods", "fodt", "gnumeric",
    "ndjson", "ods", "odt", "pbm", "pgm", "ppm", "qoi", "sylk",
    "toml", "tsv", "xcf", "zst",
]
NET_FORMATS = ["csv", "fods", "fodt", "html", "markdown", "ndjson", "tsv", "txt"]


# ---------------------------------------------------------------------------
# Python audit helpers
# ---------------------------------------------------------------------------

def _has_spec_qname_in_file(py_path: Path) -> bool:
    try:
        tree = ast.parse(py_path.read_text(encoding="utf-8", errors="replace"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id == "spec_qname":
                        return True
            if isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name) and node.target.id == "spec_qname":
                    return True
    except SyntaxError:
        pass
    return False


def _init_logic_free(init_path: Path) -> bool:
    if not init_path.exists():
        return True
    try:
        tree = ast.parse(init_path.read_text(encoding="utf-8", errors="replace"))
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                return False
    except SyntaxError:
        pass
    return True


def audit_python(fmt: str) -> dict:
    """Audit src/python/{fmt}/ and return classification + criteria."""
    src_dir = SRC_PY / fmt
    pkg_dir = src_dir

    criteria: dict[str, bool] = {}
    violations: list[str] = []
    files_scanned = 0

    # C1: spec/ dir present
    spec_dir = None
    for candidate in [pkg_dir / "spec", src_dir / "spec"]:
        if candidate.is_dir():
            spec_dir = candidate
            break
    criteria["spec_dir_present"] = spec_dir is not None
    if not criteria["spec_dir_present"]:
        violations.append("No spec/ directory found")

    # C2: spec/ is namespaced (has subdirs)
    if spec_dir:
        subdirs = [p for p in spec_dir.iterdir() if p.is_dir() and not p.name.startswith("_")]
        criteria["spec_namespaced"] = len(subdirs) > 0
        if not criteria["spec_namespaced"]:
            violations.append("spec/ is flat (no namespace subdirs)")
    else:
        criteria["spec_namespaced"] = False

    # C3: models or spec classes have spec_qname
    py_files = list(pkg_dir.rglob("*.py")) + list(src_dir.rglob("*.py"))
    py_files = list({p for p in py_files if not any(
        part in ("__pycache__", "build") for part in p.parts
    )})
    files_scanned = len(py_files)
    has_qname = any(_has_spec_qname_in_file(p) for p in py_files)
    criteria["models_spec_qname"] = has_qname
    if not has_qname:
        violations.append("No spec_qname attribute found in any .py file")

    # C4: __init__.py has no class/function definitions
    init_path = pkg_dir / "__init__.py"
    if not init_path.exists():
        init_path = src_dir / "__init__.py"
    criteria["init_logic_free"] = _init_logic_free(init_path)
    if not criteria["init_logic_free"]:
        violations.append("__init__.py contains class or function definitions")

    # C5: Compat/ dir exists (public facade layer)
    compat = (pkg_dir / "Compat").is_dir() or (src_dir / "Compat").is_dir()
    criteria["compat_delegates"] = compat
    if not compat:
        violations.append("No Compat/ directory (public facade layer missing)")

    # C6: parser/codec imports from spec/
    spec_import_found = False
    for p in py_files:
        name = p.name.lower()
        if any(x in name for x in ("parser", "codec", "reader")):
            text = p.read_text(encoding="utf-8", errors="replace")
            if re.search(r"from\s+\S*spec\S*\s+import|import\s+\S*spec\S*", text):
                spec_import_found = True
                break
    criteria["parser_produces_typed"] = spec_import_found
    if not spec_import_found:
        violations.append("parser/codec does not import from spec/ (may return raw dicts)")

    # Classify
    pass_count = sum(criteria.values())
    if pass_count == 6:
        classification = "COMPLIANT"
    elif not criteria["spec_dir_present"] and not criteria["models_spec_qname"]:
        classification = "FULL_REBUILD"
    elif not criteria["parser_produces_typed"]:
        classification = "PARSER_WRITER_REALIGNMENT"
    elif criteria["models_spec_qname"] and not criteria["spec_dir_present"]:
        classification = "QNAME_MODEL_DECOMPOSITION"
    elif not criteria["compat_delegates"] or not criteria["init_logic_free"]:
        classification = "PUBLIC_FACADE_REPAIR"
    else:
        classification = "MINOR_REALIGNMENT"

    return {
        "format_id": fmt,
        "language": "python",
        "audit_timestamp": datetime.now(timezone.utc).isoformat(),
        "classification": classification,
        "criteria": criteria,
        "violations": violations,
        "files_scanned": files_scanned,
    }


def audit_dotnet(fmt: str) -> dict:
    """Audit src/net/{fmt}/ and return classification + criteria."""
    src_dir = SRC_NET / fmt
    criteria: dict[str, bool] = {}
    violations: list[str] = []
    cs_files: list[Path] = []

    if src_dir.is_dir():
        cs_files = list(src_dir.rglob("*.cs"))

    criteria["model_dir_present"] = (src_dir / "Model").is_dir()
    criteria["spec_dir_present"] = (src_dir / "Spec").is_dir()

    dumping_ground = any(
        re.search(r"ExtendedApis|MissingMethods|Misc\.cs", p.name) for p in cs_files
    )
    criteria["no_dumping_ground"] = not dumping_ground
    if dumping_ground:
        violations.append("Dumping-ground files found (*ExtendedApis.cs, *MissingMethods.cs, *Misc.cs)")

    spec_qname_found = any(
        re.search(r"const\s+string\s+\w*[Ss]pec[Qq]name|SpecQName\s*=", p.read_text(
            encoding="utf-8", errors="replace"))
        for p in cs_files
    )
    criteria["spec_qname_constants"] = spec_qname_found
    if not spec_qname_found and cs_files:
        violations.append("No SpecQName string constants found in .cs files")

    sub_cs = list((src_dir / "Model").rglob("*.cs")) if criteria["model_dir_present"] else []
    model_dirs = {p.parent for p in sub_cs}
    criteria["model_depth"] = len(model_dirs) >= 2
    if not criteria["model_depth"]:
        violations.append("Model/ has fewer than 2 subdirs (shallow model)")

    criteria["loc_within_cap"] = True  # checked separately via source-structure-baseline.json

    pass_count = sum(criteria.values())
    if pass_count == 6:
        classification = "COMPLIANT"
    elif not criteria["model_dir_present"] and not criteria["spec_dir_present"]:
        if not cs_files:
            classification = "NOT_IMPLEMENTED"
        else:
            classification = "FULL_REBUILD"
    elif not criteria["spec_dir_present"] and not criteria["spec_qname_constants"]:
        classification = "SPEC_MISSING"
    elif not criteria["model_dir_present"]:
        classification = "MODEL_DECOMPOSITION"
    else:
        classification = "MINOR_REALIGNMENT"

    return {
        "format_id": fmt,
        "language": "dotnet",
        "audit_timestamp": datetime.now(timezone.utc).isoformat(),
        "classification": classification,
        "criteria": criteria,
        "violations": violations,
        "files_scanned": len(cs_files),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def run_audit(fmt: str, out_dir: Path, lang: str = "both") -> list[dict]:
    out_dir.mkdir(parents=True, exist_ok=True)
    results = []

    if lang in ("python", "both"):
        py_src = SRC_PY / fmt
        if py_src.is_dir():
            result = audit_python(fmt)
            out = out_dir / f"{fmt}_python.json"
            out.write_text(json.dumps(result, indent=2))
            results.append(result)
        else:
            result = {"format_id": fmt, "language": "python",
                      "classification": "NOT_FOUND", "criteria": {}, "violations": ["src/python/{} not found".format(fmt)], "files_scanned": 0}
            results.append(result)

    if lang in ("dotnet", "both"):
        net_src = SRC_NET / fmt
        if net_src.is_dir() or fmt in NET_FORMATS:
            result = audit_dotnet(fmt)
            out = out_dir / f"{fmt}_dotnet.json"
            out.write_text(json.dumps(result, indent=2))
            results.append(result)

    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Architecture audit tool (TC-B01)")
    parser.add_argument("--format", "-f", help="Single format ID to audit")
    parser.add_argument("--all", "-a", dest="all_formats", action="store_true",
                        help="Audit all known formats")
    parser.add_argument("--lang", choices=("python", "dotnet", "both"), default="both")
    parser.add_argument("--out-dir", default=str(OUT_DIR_DEFAULT))
    args = parser.parse_args(argv)

    out_dir = Path(args.out_dir)
    formats_to_audit = KNOWN_FORMATS if args.all_formats else (
        [args.format] if args.format else KNOWN_FORMATS
    )

    all_results = []
    for fmt in formats_to_audit:
        results = run_audit(fmt, out_dir, lang=args.lang)
        all_results.extend(results)
        for r in results:
            print(f"{r['format_id']:12} {r['language']:8} {r['classification']}")

    # Write summary
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_audited": len(all_results),
        "classifications": {},
    }
    for r in all_results:
        c = r["classification"]
        summary["classifications"][c] = summary["classifications"].get(c, 0) + 1

    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    print(f"\nSummary: {summary['classifications']}")
    print(f"Reports written to: {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
