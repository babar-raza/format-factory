"""Automated, reproducible forensic inventory of the Python portfolio under src/python.

Implements TC-PA-002 of plans/.claude/primary-purpose-the-python-starry-cupcake.md
(mission PORTFOLIO-AUDIT-2026-07-16).

READ-ONLY: this tool never writes to src/. It parses every package with `ast` and
emits a machine-readable inventory that TC-PA-003 (portfolio_issue_ledger.py)
consumes to build the occurrence-level issue ledger. That programmatic
inventory -> ledger binding is the fix for finding PF-008 ("forensic artifacts
have no consumer; the forensics-to-fix pipeline was manual").

Usage:
    python tools/audit/portfolio_forensic_inventory.py \
        --out .local/evidences/portfolio-audit-2026-07-16/full-inventory.yaml

Determinism: all collections are sorted; the only nondeterministic field is
`generated_at`, which is excluded from `inventory_digest`.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "src" / "python"
SAL_FACTS_DIR = REPO / "shared" / "sal-facts"
SAL_MERGED = REPO / ".local" / "spec-cache" / "sal-facts-latest.json"
TESTS = REPO / "tests" / "python"

# --- Information-model taxonomy -------------------------------------------------
# Basis for converter classification (TC-PA-002 requires every converter to carry a
# classification; TC-PA-008/V251 will enforce this as a gate).
INFORMATION_MODEL: dict[str, str] = {
    "csv": "TABULAR", "tsv": "TABULAR", "dif": "TABULAR", "sylk": "TABULAR",
    "gnumeric": "TABULAR", "ods": "TABULAR", "fods": "TABULAR",
    "abw": "TEXT_DOC", "odt": "TEXT_DOC", "fodt": "TEXT_DOC",
    "fodp": "PRESENTATION",
    "fodg": "DRAWING",
    "pbm": "RASTER", "pgm": "RASTER", "ppm": "RASTER", "qoi": "RASTER", "xcf": "RASTER",
    "safetensors": "TENSOR",
    "nrrd": "VOLUMETRIC",
    "mtlx": "MATERIAL_GRAPH",
    "ipynb": "NOTEBOOK",
    "ubl": "BUSINESS_DOC",
    "xliff": "TRANSLATION",
    "ndjson": "SEMI_STRUCTURED", "toml": "SEMI_STRUCTURED",
    "zst": "COMPRESSION",
}

# Directed compatibility. Absent pair => MEANINGLESS_PROJECTION.
# FAITHFUL      : same information model; round-trippable in principle.
# MEANINGFUL    : distinct models, but a defensible, information-preserving mapping exists.
# LOSSY         : mapping exists but structurally discards source information.
# MEANINGLESS_PROJECTION : no defensible information-model mapping; output is a
#                 mechanical projection (e.g. a spreadsheet rendered as a bitmap).
_MEANINGFUL: set[tuple[str, str]] = {
    ("TABULAR", "SEMI_STRUCTURED"), ("SEMI_STRUCTURED", "TABULAR"),
    ("TABULAR", "TEXT_DOC"),
    ("TABULAR", "PRESENTATION"),
    ("BUSINESS_DOC", "TABULAR"), ("TABULAR", "BUSINESS_DOC"),
    ("TRANSLATION", "TABULAR"), ("TABULAR", "TRANSLATION"),
    ("NOTEBOOK", "TEXT_DOC"),
    ("NOTEBOOK", "SEMI_STRUCTURED"), ("SEMI_STRUCTURED", "NOTEBOOK"),
    ("TEXT_DOC", "PRESENTATION"), ("PRESENTATION", "TEXT_DOC"),
    ("MATERIAL_GRAPH", "SEMI_STRUCTURED"),
    ("VOLUMETRIC", "RASTER"), ("RASTER", "VOLUMETRIC"),
    ("TENSOR", "SEMI_STRUCTURED"),
}
_LOSSY: set[tuple[str, str]] = {
    ("TEXT_DOC", "TABULAR"),
    ("PRESENTATION", "TABULAR"),
    ("DRAWING", "TABULAR"),
    ("TEXT_DOC", "SEMI_STRUCTURED"), ("SEMI_STRUCTURED", "TEXT_DOC"),
    ("DRAWING", "RASTER"),
    ("PRESENTATION", "RASTER"),
    ("TEXT_DOC", "RASTER"),
    ("RASTER", "SEMI_STRUCTURED"), ("SEMI_STRUCTURED", "RASTER"),
    ("TENSOR", "VOLUMETRIC"), ("VOLUMETRIC", "TENSOR"),
    ("TENSOR", "RASTER"), ("RASTER", "TENSOR"),
}


def classify_conversion(src_fmt: str, tgt_fmt: str) -> tuple[str, str]:
    """Return (classification, rationale) for a src->tgt converter."""
    s = INFORMATION_MODEL.get(src_fmt)
    t = INFORMATION_MODEL.get(tgt_fmt)
    if s is None or t is None:
        return "UNKNOWN_MODEL", f"no information model registered for {src_fmt if s is None else tgt_fmt}"
    if s == t:
        return "FAITHFUL", f"both {src_fmt} and {tgt_fmt} are {s}; mapping is model-preserving"
    if t == "COMPRESSION" or s == "COMPRESSION":
        return "CONTAINER", f"{s}->{t} is a compression/container wrapper, not a model translation"
    if (s, t) in _MEANINGFUL:
        return "MEANINGFUL", f"{s}->{t} has a defensible information-preserving mapping"
    if (s, t) in _LOSSY:
        return "LOSSY", f"{s}->{t} mapping exists but structurally discards source information"
    return (
        "MEANINGLESS_PROJECTION",
        f"{s}->{t} has no defensible information-model mapping; output is a mechanical projection",
    )


# --- Symbol categorisation ------------------------------------------------------
def categorize_symbol(module_name: str, symbol: str) -> str:
    m = module_name.lower()
    if re.search(r"_to_[a-z0-9]+$", m):
        return "conversion"
    if "analytics" in m or m.endswith("_stats"):
        return "analytics"
    if m.endswith("exceptions") or symbol.endswith("Error"):
        return "exception"
    if "model" in m or "document" in m:
        return "model"
    if m.endswith("cli") or m.endswith("workflow"):
        return "cli"
    if "compat" in m:
        return "compat"
    if any(k in m for k in ("parser", "writer", "codec", "reader", "probe")):
        return "core"
    return "other"


def _sig(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    try:
        args = [a.arg for a in node.args.posonlyargs + node.args.args]
        if node.args.vararg:
            args.append("*" + node.args.vararg.arg)
        args += [a.arg for a in node.args.kwonlyargs]
        if node.args.kwarg:
            args.append("**" + node.args.kwarg.arg)
        return f"({', '.join(args)})"
    except Exception:
        return "(?)"


def _is_stub_body(node: ast.AST) -> str | None:
    """Return stub kind if the function body is a stub, else None."""
    body = [n for n in getattr(node, "body", []) if not isinstance(n, ast.Expr) or not isinstance(getattr(n, "value", None), ast.Constant)]
    if not body:
        return "docstring_or_empty_only"
    if len(body) == 1:
        only = body[0]
        if isinstance(only, ast.Pass):
            return "pass_only"
        if isinstance(only, ast.Raise):
            exc = only.exc
            name = None
            if isinstance(exc, ast.Call) and isinstance(exc.func, ast.Name):
                name = exc.func.id
            elif isinstance(exc, ast.Name):
                name = exc.id
            if name == "NotImplementedError":
                return "raises_NotImplementedError"
        if isinstance(only, ast.Return) and (only.value is None or (isinstance(only.value, ast.Constant) and only.value.value is None)):
            return "returns_none_only"
    return None


def _abstract(node: ast.AST) -> bool:
    for d in getattr(node, "decorator_list", []):
        src = ast.unparse(d) if hasattr(ast, "unparse") else ""
        if "abstract" in src.lower():
            return True
    return False


# --- Per-file analysis ----------------------------------------------------------
def analyze_file(path: Path, pkg: str) -> dict[str, Any]:
    rel = path.relative_to(REPO).as_posix()
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    out: dict[str, Any] = {
        "path": rel,
        "loc": len(lines),
        "sha256": hashlib.sha256(text.encode("utf-8", "replace")).hexdigest(),
        "symbols": [],
        "sys_path_calls": [],
        "stubs": [],
        "markers": [],
        "imports": [],
        "exception_classes": [],
        "parse_error": None,
    }
    module_name = path.stem

    # TODO/FIXME markers are text-level, not AST-level.
    for i, line in enumerate(lines, 1):
        if re.search(r"#\s*(TODO|FIXME|XXX|HACK)\b", line):
            out["markers"].append({"line": i, "text": line.strip()[:160]})

    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError as e:
        out["parse_error"] = f"{type(e).__name__}: {e}"
        return out

    # Resolve local aliases of the `sys` module. A naive check for the literal
    # name `sys` produces FALSE NEGATIVES: src/python/dif/interchange_document.py
    # uses `import sys as _sys` then `_sys.path.insert(...)`. Any validator built
    # on this detection (TC-PA-005 / V249) MUST resolve aliases the same way or
    # it will silently miss alias-based evasions.
    sys_aliases: set[str] = {"sys"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name == "sys" and a.asname:
                    sys_aliases.add(a.asname)
    out["sys_aliases"] = sorted(sys_aliases)

    for node in ast.walk(tree):
        # sys.path.insert / sys.path.append  (exact file:line)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in ("insert", "append", "extend"):
                v = node.func.value
                if (
                    isinstance(v, ast.Attribute)
                    and v.attr == "path"
                    and isinstance(v.value, ast.Name)
                    and v.value.id in sys_aliases
                ):
                    try:
                        snippet = ast.unparse(node)
                    except Exception:
                        snippet = "sys.path." + node.func.attr
                    out["sys_path_calls"].append(
                        {"line": node.lineno, "op": node.func.attr, "snippet": snippet[:200]}
                    )
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.Import):
                for a in node.names:
                    out["imports"].append({"module": a.name.split(".")[0], "line": node.lineno, "relative": False})
            else:
                rel_lvl = node.level or 0
                mod = node.module or ""
                out["imports"].append(
                    {
                        "module": (mod.split(".")[0] if mod else ""),
                        "line": node.lineno,
                        "relative": rel_lvl > 0,
                        "level": rel_lvl,
                    }
                )

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out["symbols"].append(
                {
                    "name": node.name,
                    "kind": "function",
                    "module": f"{pkg}.{module_name}",
                    "signature": _sig(node),
                    "public": not node.name.startswith("_"),
                    "category": categorize_symbol(module_name, node.name),
                    "line": node.lineno,
                }
            )
            kind = _is_stub_body(node)
            if kind and not _abstract(node):
                out["stubs"].append(
                    {"symbol": node.name, "line": node.lineno, "kind": kind, "abstract": False}
                )
        elif isinstance(node, ast.ClassDef):
            bases = []
            for b in node.bases:
                try:
                    bases.append(ast.unparse(b))
                except Exception:
                    pass
            out["symbols"].append(
                {
                    "name": node.name,
                    "kind": "class",
                    "module": f"{pkg}.{module_name}",
                    "signature": f"({', '.join(bases)})",
                    "public": not node.name.startswith("_"),
                    "category": categorize_symbol(module_name, node.name),
                    "line": node.lineno,
                }
            )
            if node.name.endswith("Error") or any("Error" in b or "Exception" in b for b in bases):
                out["exception_classes"].append(
                    {"name": node.name, "bases": sorted(bases), "line": node.lineno}
                )
    out["symbols"].sort(key=lambda s: (s["module"], s["name"], s["line"]))
    out["sys_path_calls"].sort(key=lambda s: s["line"])
    out["stubs"].sort(key=lambda s: s["line"])
    return out


# --- SAL fact counts ------------------------------------------------------------
def sal_fact_counts() -> dict[str, dict[str, Any]]:
    counts: dict[str, dict[str, Any]] = {}
    for f in sorted(SAL_FACTS_DIR.glob("*.yaml")):
        try:
            d = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
            counts[f.stem] = {"canonical_facts": len(d.get("facts") or [])}
        except Exception as e:  # pragma: no cover
            counts[f.stem] = {"canonical_facts": -1, "error": str(e)}
    if SAL_MERGED.exists():
        try:
            d = json.loads(SAL_MERGED.read_text(encoding="utf-8"))
            for r in d.get("results", []):
                fid = r.get("format_id")
                sf = r.get("spec_facts")
                n = len(sf) if isinstance(sf, list) else (sf if isinstance(sf, int) else -1)
                counts.setdefault(fid, {})["merged_spec_facts"] = n
                counts[fid]["workbench_verified"] = r.get("workbench_verified_fact_count")
        except Exception:
            pass
    return counts


def test_file_counts() -> dict[str, int]:
    counts: dict[str, int] = {}
    if not TESTS.exists():
        return counts
    for p in TESTS.rglob("test_*.py"):
        if "__pycache__" in p.parts:
            continue
        text = p.name
        for pkg in INFORMATION_MODEL:
            if re.search(rf"(^|[_/]){re.escape(pkg)}([_/.]|$)", text):
                counts[pkg] = counts.get(pkg, 0) + 1
    return counts


def parse_pyproject(pkg_dir: Path) -> dict[str, Any]:
    pp = pkg_dir / "pyproject.toml"
    if not pp.exists():
        return {"exists": False}
    try:
        import tomllib

        d = tomllib.loads(pp.read_text(encoding="utf-8"))
    except Exception as e:
        return {"exists": True, "parse_error": str(e)}
    proj = d.get("project", {})
    return {
        "exists": True,
        "name": proj.get("name"),
        "version": proj.get("version"),
        "declared_dependencies": sorted(proj.get("dependencies") or []),
    }


def readme_claims(pkg_dir: Path) -> dict[str, Any]:
    rm = pkg_dir / "README.md"
    if not rm.exists():
        return {"exists": False}
    text = rm.read_text(encoding="utf-8", errors="replace")
    # Symbols the README claims, via `code spans` that look like calls/identifiers.
    claimed = sorted(set(re.findall(r"`([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", text)))
    return {"exists": True, "loc": len(text.splitlines()), "claimed_symbols": claimed}


def main() -> int:
    ap = argparse.ArgumentParser(description="Automated forensic inventory of src/python (TC-PA-002).")
    ap.add_argument("--out", default=".local/evidences/portfolio-audit-2026-07-16/full-inventory.yaml")
    ap.add_argument("--src", default=str(SRC))
    args = ap.parse_args()

    src_root = Path(args.src)
    pkgs = sorted(p for p in src_root.iterdir() if p.is_dir() and p.name != "__pycache__")
    sal = sal_fact_counts()
    tests_per_fmt = test_file_counts()

    packages: dict[str, Any] = {}
    totals = {
        "packages": 0, "py_files": 0, "symbols": 0, "public_symbols": 0,
        "sys_path_files": 0, "sys_path_occurrences": 0, "converters": 0,
        "stub_functions": 0, "markers": 0, "pycache_files": 0, "parse_errors": 0,
    }
    converter_class_totals: dict[str, int] = {}

    for pkg_dir in pkgs:
        pkg = pkg_dir.name
        files = sorted(
            p for p in pkg_dir.rglob("*.py") if "__pycache__" not in p.parts
        )
        file_reports = [analyze_file(p, pkg) for p in files]

        pycache = sum(1 for _ in pkg_dir.rglob("__pycache__/*.pyc"))
        sys_path_files = [f for f in file_reports if f["sys_path_calls"]]
        sys_path_occ = [
            {"path": f["path"], "line": c["line"], "op": c["op"], "snippet": c["snippet"]}
            for f in file_reports
            for c in f["sys_path_calls"]
        ]

        converters = []
        for p in files:
            # Source format is the leading token; target is the trailing token.
            # The optional middle group matches qualified converters such as
            # `abw_typed_children_to_ndjson` (a plain `([a-z0-9]+)_to_([a-z0-9]+)`
            # fullmatch silently drops it -> undercounts converters by 1).
            m = re.fullmatch(r"(?P<src>[a-z0-9]+)(?:_[a-z0-9_]+?)??_to_(?P<tgt>[a-z0-9]+)", p.stem)
            if not m:
                continue
            s_fmt, t_fmt = m.group("src"), m.group("tgt")
            rep = next(f for f in file_reports if f["path"] == p.relative_to(REPO).as_posix())
            classification, rationale = classify_conversion(s_fmt, t_fmt)
            body = p.read_text(encoding="utf-8", errors="replace")
            converters.append(
                {
                    "path": rep["path"],
                    "module": p.stem,
                    "source_format": s_fmt,
                    "target_format": t_fmt,
                    "source_model": INFORMATION_MODEL.get(s_fmt, "UNKNOWN"),
                    "target_model": INFORMATION_MODEL.get(t_fmt, "UNKNOWN"),
                    "classification": classification,
                    "rationale": rationale,
                    "loc": rep["loc"],
                    "conversion_logic_sha256": hashlib.sha256(body.encode("utf-8", "replace")).hexdigest(),
                    "public_symbols": sorted(s["name"] for s in rep["symbols"] if s["public"]),
                }
            )
            converter_class_totals[classification] = converter_class_totals.get(classification, 0) + 1

        all_syms = [s for f in file_reports for s in f["symbols"]]
        pub = [s for s in all_syms if s["public"]]
        by_cat: dict[str, int] = {}
        for s in pub:
            by_cat[s["category"]] = by_cat.get(s["category"], 0) + 1

        exc_classes = [e for f in file_reports for e in f["exception_classes"]]
        exc_names = {e["name"] for e in exc_classes}
        roots = [
            e for e in exc_classes
            if not any(b in exc_names for b in e["bases"])
        ]
        chains_ff = any("FormatFactoryError" in b for e in exc_classes for b in e["bases"])

        init_all: list[str] = []
        init = pkg_dir / "__init__.py"
        if init.exists():
            try:
                t = ast.parse(init.read_text(encoding="utf-8", errors="replace"))
                for node in ast.walk(t):
                    if isinstance(node, ast.Assign):
                        for tgt in node.targets:
                            if isinstance(tgt, ast.Name) and tgt.id == "__all__":
                                if isinstance(node.value, ast.List):
                                    init_all = [
                                        el.value for el in node.value.elts
                                        if isinstance(el, ast.Constant) and isinstance(el.value, str)
                                    ]
            except Exception:
                pass

        pyproj = parse_pyproject(pkg_dir)
        rm = readme_claims(pkg_dir)

        # Dependency reality check: third-party imports not declared in pyproject.
        local_names = {p.name for p in pkgs} | {"_shared"}
        stdlib = set(sys.stdlib_module_names)
        imported = {
            i["module"] for f in file_reports for i in f["imports"]
            if i["module"] and not i["relative"]
        }
        third_party = sorted(
            m for m in imported
            if m not in stdlib and m not in local_names and not m.startswith("_")
        )
        declared = {re.split(r"[<>=!\[ ]", d)[0].strip().lower() for d in (pyproj.get("declared_dependencies") or [])}
        undeclared = sorted(m for m in third_party if m.lower() not in declared)

        readme_missing = []
        if rm.get("exists"):
            pubnames = {s["name"] for s in pub}
            readme_missing = sorted(c for c in rm["claimed_symbols"] if c not in pubnames)

        packages[pkg] = {
            "package": pkg,
            "path": pkg_dir.relative_to(REPO).as_posix(),
            "information_model": INFORMATION_MODEL.get(pkg, "N/A" if pkg == "_shared" else "UNKNOWN"),
            "py_file_count": len(files),
            "total_loc": sum(f["loc"] for f in file_reports),
            "pycache_file_count": pycache,
            "symbol_count": len(all_syms),
            "public_symbol_count": len(pub),
            "public_symbols_by_category": dict(sorted(by_cat.items())),
            "init_all_count": len(init_all),
            "init_all_is_dynamic": init.exists() and not init_all,
            "sys_path_file_count": len(sys_path_files),
            "sys_path_occurrences": sorted(sys_path_occ, key=lambda x: (x["path"], x["line"])),
            "converter_count": len(converters),
            "converters": sorted(converters, key=lambda c: c["path"]),
            "stub_count": sum(len(f["stubs"]) for f in file_reports),
            "stubs": sorted(
                [{"path": f["path"], **s} for f in file_reports for s in f["stubs"]],
                key=lambda x: (x["path"], x["line"]),
            ),
            "marker_count": sum(len(f["markers"]) for f in file_reports),
            "markers": sorted(
                [{"path": f["path"], **m} for f in file_reports for m in f["markers"]],
                key=lambda x: (x["path"], x["line"]),
            ),
            "exception_class_count": len(exc_classes),
            "exception_roots": sorted({e["name"] for e in roots}),
            "exception_chains_to_FormatFactoryError": chains_ff,
            "monolith_files": sorted(
                [{"path": f["path"], "loc": f["loc"]} for f in file_reports if f["loc"] > 800],
                key=lambda x: -x["loc"],
            ),
            "parse_errors": sorted(
                [{"path": f["path"], "error": f["parse_error"]} for f in file_reports if f["parse_error"]],
                key=lambda x: x["path"],
            ),
            "pyproject": pyproj,
            "readme": {
                "exists": rm.get("exists", False),
                "claimed_symbol_count": len(rm.get("claimed_symbols", [])),
                "claimed_but_not_public": readme_missing,
            },
            "third_party_imports": third_party,
            "undeclared_third_party_imports": undeclared,
            "sal_facts": sal.get(pkg, {}),
            "test_file_count": tests_per_fmt.get(pkg, 0),
        }

        totals["packages"] += 1
        totals["py_files"] += len(files)
        totals["symbols"] += len(all_syms)
        totals["public_symbols"] += len(pub)
        totals["sys_path_files"] += len(sys_path_files)
        totals["sys_path_occurrences"] += len(sys_path_occ)
        totals["converters"] += len(converters)
        totals["stub_functions"] += packages[pkg]["stub_count"]
        totals["markers"] += packages[pkg]["marker_count"]
        totals["pycache_files"] += pycache
        totals["parse_errors"] += len(packages[pkg]["parse_errors"])

    doc = {
        "schema_version": "1.0",
        "taskcard": "TC-PA-002",
        "mission_id": "PORTFOLIO-AUDIT-2026-07-16",
        "generator": "tools/audit/portfolio_forensic_inventory.py",
        "src_root": src_root.relative_to(REPO).as_posix(),
        "totals": totals,
        "converter_classification_totals": dict(sorted(converter_class_totals.items())),
        "packages": dict(sorted(packages.items())),
    }
    payload = yaml.safe_dump(doc, sort_keys=False, width=120, allow_unicode=True)
    doc["inventory_digest"] = hashlib.sha256(payload.encode("utf-8")).hexdigest()

    out = Path(args.out)
    if not out.is_absolute():
        out = REPO / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        yaml.safe_dump(doc, sort_keys=False, width=120, allow_unicode=True), encoding="utf-8"
    )

    print(f"wrote {out}")
    for k, v in totals.items():
        print(f"  {k}: {v}")
    print("  converter classifications:")
    for k, v in sorted(converter_class_totals.items(), key=lambda x: -x[1]):
        print(f"    {k}: {v}")
    print(f"  inventory_digest: {doc['inventory_digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
