"""Product inventory extraction for certification work.

generated_by: codex
mission_id: CERT-EXHAUST-20260628
visibility: internal
"""

from __future__ import annotations

import argparse
import ast
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = REPO_ROOT / "src" / "python"
DOTNET_ROOT = REPO_ROOT / "src" / "net"
REPORT_ROOT = REPO_ROOT / "reports" / "certification"


@dataclass(frozen=True)
class PythonSymbol:
    name: str
    kind: str
    file: str
    line: int
    role: str


def _rel(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT).as_posix()


def _read_ast(path: Path) -> ast.Module | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, UnicodeDecodeError):
        return None


def _line_count(path: Path) -> int:
    try:
        return len(path.read_text(encoding="utf-8").splitlines())
    except UnicodeDecodeError:
        return 0


def _classify_role(path: Path, name: str) -> str:
    text = f"{path.stem} {name}".lower()
    checks = [
        ("exception", ("error", "exception")),
        ("writer", ("write", "save", "export", "serialize", "to_")),
        ("parser", ("parse", "load", "read", "from_", "codec")),
        ("probe", ("probe", "detect", "validate", "is_valid")),
        ("analytics", ("stat", "metric", "count", "sum", "mean", "ratio", "analytics")),
        ("iterator", ("iter", "iterator")),
        ("model", ("model", "document", "row", "cell", "sheet", "paragraph")),
        ("workflow", ("workflow", "installed")),
        ("constant", ("constant", "default", "magic", "mime")),
    ]
    for role, needles in checks:
        if any(needle in text for needle in needles):
            return role
    return "api"


def _public_symbols_from_module(path: Path) -> list[PythonSymbol]:
    tree = _read_ast(path)
    if tree is None:
        return []
    symbols: list[PythonSymbol] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not node.name.startswith("_"):
                kind = "class" if isinstance(node, ast.ClassDef) else "function"
                symbols.append(
                    PythonSymbol(
                        name=node.name,
                        kind=kind,
                        file=_rel(path),
                        line=node.lineno,
                        role=_classify_role(path, node.name),
                    )
                )
    return symbols


def _literal_all(tree: ast.Module) -> list[str] | None:
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets):
            continue
        if isinstance(node.value, (ast.List, ast.Tuple)):
            values: list[str] = []
            for item in node.value.elts:
                if isinstance(item, ast.Constant) and isinstance(item.value, str):
                    values.append(item.value)
            return values
        return None
    return None


def _init_exports(package_dir: Path, module_symbols: dict[str, list[PythonSymbol]]) -> dict[str, Any]:
    init_path = package_dir / "__init__.py"
    tree = _read_ast(init_path)
    if tree is None:
        return {"exports": [], "dynamic_all": False, "export_sources": []}

    literal = _literal_all(tree)
    export_sources: list[str] = []
    inferred: set[str] = set()

    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module:
            source = node.module.lstrip(".")
            if node.level == 1:
                module_path = package_dir / f"{source}.py"
                export_sources.append(module_path.name)
                if len(node.names) == 1 and node.names[0].name == "*":
                    for symbol in module_symbols.get(module_path.name, []):
                        inferred.add(symbol.name)
                else:
                    for alias in node.names:
                        if alias.name != "*":
                            inferred.add(alias.asname or alias.name)

    if literal is not None:
        return {
            "exports": sorted(literal),
            "dynamic_all": False,
            "export_sources": sorted(set(export_sources)),
        }

    return {
        "exports": sorted(inferred),
        "dynamic_all": True,
        "export_sources": sorted(set(export_sources)),
    }


def _python_format_dirs(src_root: Path, only_format: str | None = None) -> list[Path]:
    dirs = []
    for child in sorted(src_root.iterdir()):
        if not child.is_dir():
            continue
        if child.name.startswith("_") or child.name.endswith(".egg-info"):
            continue
        if not (child / "__init__.py").exists():
            continue
        if only_format and child.name != only_format:
            continue
        dirs.append(child)
    return dirs


def extract_python_inventory(src_root: Path = PYTHON_ROOT, only_format: str | None = None) -> dict[str, Any]:
    formats: list[dict[str, Any]] = []
    total_files = 0
    total_exports = 0

    for package_dir in _python_format_dirs(src_root, only_format):
        py_files = sorted(p for p in package_dir.rglob("*.py") if "__pycache__" not in p.parts)
        module_symbols = {p.name: _public_symbols_from_module(p) for p in py_files}
        symbols = [symbol for per_file in module_symbols.values() for symbol in per_file]
        exports = _init_exports(package_dir, module_symbols)
        files = [
            {
                "path": _rel(path),
                "line_count": _line_count(path),
                "role": _classify_role(path, path.stem),
            }
            for path in py_files
        ]
        public_functions = [s.__dict__ for s in symbols if s.kind == "function"]
        public_classes = [s.__dict__ for s in symbols if s.kind == "class"]
        total_files += len(files)
        total_exports += len(exports["exports"])
        formats.append(
            {
                "format_id": package_dir.name,
                "package_path": _rel(package_dir),
                "file_count": len(files),
                "files": files,
                "export_count": len(exports["exports"]),
                "exports": exports["exports"],
                "dynamic_all": exports["dynamic_all"],
                "export_sources": exports["export_sources"],
                "public_function_count": len(public_functions),
                "public_functions": public_functions,
                "public_class_count": len(public_classes),
                "public_classes": public_classes,
            }
        )

    return {
        "metadata": {
            "authoritative_plan": "plans/.claude/crispy-jingling-snail.md",
            "generated_by": "codex",
            "mission_id": "CERT-EXHAUST-20260628",
            "visibility": "internal",
            "inventory_type": "python",
        },
        "format_count": len(formats),
        "total_file_count": total_files,
        "total_export_count": total_exports,
        "formats": formats,
    }


CS_CLASS_RE = re.compile(r"\bpublic\s+(?:sealed\s+|static\s+|partial\s+|abstract\s+)*class\s+([A-Za-z_][A-Za-z0-9_]*)")
CS_INTERFACE_RE = re.compile(r"\bpublic\s+interface\s+([A-Za-z_][A-Za-z0-9_]*)")
CS_METHOD_RE = re.compile(
    r"\bpublic\s+(?:static\s+|virtual\s+|override\s+|async\s+|sealed\s+|partial\s+)*"
    r"(?!class\b|interface\b|enum\b)([A-Za-z0-9_<>,\[\].?]+)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\("
)
CS_PROPERTY_RE = re.compile(
    r"\bpublic\s+(?:static\s+|virtual\s+|override\s+|required\s+|init\s+)*"
    r"([A-Za-z0-9_<>,\[\].?]+)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{\s*(?:get|set|init)"
)


def _dotnet_project_dirs(src_root: Path, only_format: str | None = None) -> list[Path]:
    dirs = []
    for child in sorted(src_root.iterdir()):
        if not child.is_dir():
            continue
        if only_format and child.name != only_format:
            continue
        if any(child.glob("*.csproj")) or list(child.rglob("*.cs")):
            dirs.append(child)
    return dirs


def _scan_cs_file(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    classes = []
    methods = []
    properties = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for pattern, target, kind in (
            (CS_CLASS_RE, classes, "class"),
            (CS_INTERFACE_RE, classes, "interface"),
            (CS_METHOD_RE, methods, "method"),
            (CS_PROPERTY_RE, properties, "property"),
        ):
            match = pattern.search(line)
            if not match:
                continue
            name = match.group(1) if kind in {"class", "interface"} else match.group(2)
            target.append(
                {
                    "name": name,
                    "kind": kind,
                    "file": _rel(path),
                    "line": lineno,
                    "signature": line.strip(),
                    "role": _classify_role(path, name),
                }
            )
    return {
        "classes": classes,
        "methods": methods,
        "properties": properties,
    }


def extract_dotnet_inventory(src_root: Path = DOTNET_ROOT, only_format: str | None = None) -> dict[str, Any]:
    projects: list[dict[str, Any]] = []
    total_files = 0
    total_public_members = 0
    for project_dir in _dotnet_project_dirs(src_root, only_format):
        cs_files = sorted(
            p
            for p in project_dir.rglob("*.cs")
            if "bin" not in p.parts and "obj" not in p.parts
        )
        scans = [_scan_cs_file(path) for path in cs_files]
        classes = [item for scan in scans for item in scan["classes"]]
        methods = [item for scan in scans for item in scan["methods"]]
        properties = [item for scan in scans for item in scan["properties"]]
        public_member_count = len(classes) + len(methods) + len(properties)
        total_files += len(cs_files)
        total_public_members += public_member_count
        projects.append(
            {
                "project_id": project_dir.name,
                "project_path": _rel(project_dir),
                "file_count": len(cs_files),
                "files": [
                    {
                        "path": _rel(path),
                        "line_count": _line_count(path),
                        "role": _classify_role(path, path.stem),
                    }
                    for path in cs_files
                ],
                "public_class_count": len(classes),
                "public_classes": classes,
                "public_method_count": len(methods),
                "public_methods": methods,
                "public_property_count": len(properties),
                "public_properties": properties,
                "public_member_count": public_member_count,
            }
        )
    return {
        "metadata": {
            "authoritative_plan": "plans/.claude/crispy-jingling-snail.md",
            "generated_by": "codex",
            "mission_id": "CERT-EXHAUST-20260628",
            "visibility": "internal",
            "inventory_type": "dotnet",
        },
        "project_count": len(projects),
        "total_file_count": total_files,
        "total_public_member_count": total_public_members,
        "projects": projects,
    }


DUAL_TRACK_ALIASES = {
    "netpbm": {"pbm", "pgm", "ppm", "netpbm"},
    "fods": {"fods"},
    "fodt": {"fodt", "odt"},
    "csv": {"csv"},
    "ndjson": {"ndjson"},
    "tsv": {"tsv"},
    "zst": {"zst"},
}


def _normalize_api_name(name: str) -> str:
    cleaned = re.sub(r"^(get|set|load|parse|write|save|export|to|from)_?", "", name.lower())
    return re.sub(r"[^a-z0-9]+", "", cleaned)


def extract_parity_matrix(
    py_inv: dict[str, Any] | None = None,
    net_inv: dict[str, Any] | None = None,
) -> dict[str, Any]:
    py_inv = py_inv or extract_python_inventory()
    net_inv = net_inv or extract_dotnet_inventory()
    py_by_format = {fmt["format_id"]: fmt for fmt in py_inv["formats"]}
    net_by_project = {proj["project_id"]: proj for proj in net_inv["projects"]}
    entries = []

    for dual_id, py_ids in DUAL_TRACK_ALIASES.items():
        if dual_id not in net_by_project:
            continue
        py_api_names: set[str] = set()
        for py_id in sorted(py_ids):
            fmt = py_by_format.get(py_id)
            if fmt:
                py_api_names.update(fmt["exports"])
        net_proj = net_by_project[dual_id]
        net_api_names = {
            item["name"]
            for item in (
                net_proj["public_classes"]
                + net_proj["public_methods"]
                + net_proj["public_properties"]
            )
        }
        py_norm = {_normalize_api_name(name): name for name in py_api_names}
        net_norm = {_normalize_api_name(name): name for name in net_api_names}
        matched_keys = sorted(set(py_norm) & set(net_norm))
        entries.append(
            {
                "format_id": dual_id,
                "python_formats": sorted(py_ids & set(py_by_format)),
                "dotnet_project": dual_id,
                "matched_apis": [
                    {"python": py_norm[key], "dotnet": net_norm[key], "normalized": key}
                    for key in matched_keys
                    if key
                ],
                "python_only_apis": sorted(
                    name for key, name in py_norm.items() if key not in net_norm
                ),
                "dotnet_only_apis": sorted(
                    name for key, name in net_norm.items() if key not in py_norm
                ),
                "intentional_gap_notes": [
                    ".NET products are currently parser/read-oriented; Python writer/export APIs are expected to appear as python_only until writer parity is authorized."
                ],
            }
        )

    return {
        "metadata": {
            "authoritative_plan": "plans/.claude/crispy-jingling-snail.md",
            "generated_by": "codex",
            "mission_id": "CERT-EXHAUST-20260628",
            "visibility": "internal",
            "inventory_type": "cross_product_parity",
        },
        "dual_track_count": len(entries),
        "entries": entries,
    }


def _write_json(data: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _default_output(args: argparse.Namespace) -> Path:
    if args.python:
        return REPORT_ROOT / "python-product-inventory.json"
    if args.dotnet:
        return REPORT_ROOT / "dotnet-product-inventory.json"
    if args.parity:
        return REPORT_ROOT / "cross-product-parity.json"
    raise ValueError("one inventory mode is required")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", action="store_true", dest="python")
    parser.add_argument("--dotnet", action="store_true")
    parser.add_argument("--parity", action="store_true")
    parser.add_argument("--format", dest="only_format", help="limit extraction to one format/project")
    parser.add_argument("--output", type=Path, help="JSON output path")
    parser.add_argument("--run-id", default=None, help="Certification run ID (from run_manager)")
    args = parser.parse_args()

    selected_modes = sum(bool(v) for v in (args.python, args.dotnet, args.parity))
    if selected_modes != 1:
        parser.error("select exactly one of --python, --dotnet, or --parity")

    if args.python:
        data = extract_python_inventory(only_format=args.only_format)
    elif args.dotnet:
        data = extract_dotnet_inventory(only_format=args.only_format)
    else:
        data = extract_parity_matrix()

    output = args.output or _default_output(args)
    if not output.is_absolute():
        output = REPO_ROOT / output
    if args.run_id:
        import subprocess as _sp
        _rev = "UNAVAILABLE"
        try:
            _r = _sp.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                         cwd=REPO_ROOT, timeout=10)
            if _r.returncode == 0:
                _rev = _r.stdout.strip()
        except Exception:
            pass
        data.setdefault("metadata", {}).update({
            "run_id": args.run_id,
            "source_revision": _rev,
            "generated_at": __import__("datetime").datetime.now(
                __import__("datetime").timezone.utc).isoformat(),
        })
    _write_json(data, output)
    print(json.dumps({"output": _rel(output), "mode": data["metadata"]["inventory_type"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
