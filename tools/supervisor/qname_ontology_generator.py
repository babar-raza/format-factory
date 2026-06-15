"""QName ontology generator — executable implementation.

Generates QName-to-code mappings, namespace trees, and unmapped QName ledgers
from format source files. This is the executable version of the QName pilot.

Usage:
    python tools/supervisor/qname_ontology_generator.py \
        --format FODP \
        --output-dir .local/evidences/<run_id>/pilot-results/
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# ODF namespace registry
# ---------------------------------------------------------------------------

ODF_NAMESPACES = {
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "presentation": "urn:oasis:names:tc:opendocument:xmlns:presentation:1.0",
    "draw": "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "style": "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
    "fo": "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0",
    "svg": "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0",
    "meta": "urn:oasis:names:tc:opendocument:xmlns:meta:1.0",
    "number": "urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0",
}

# Format to expected QNames
FORMAT_QNAME_EXPECTATIONS = {
    "FODP": [
        "office:document", "office:body", "office:presentation",
        "draw:page", "draw:frame", "draw:text-box",
        "text:p", "text:span", "presentation:notes",
        "draw:page@draw:name", "svg:width", "svg:height",
    ],
    "FODS": [
        "office:document", "office:body", "office:spreadsheet",
        "table:table", "table:table-row", "table:table-cell",
        "text:p", "table:table@table:name",
        "table:table-cell@office:value-type",
        "table:table-cell@office:value",
    ],
    "FODT": [
        "office:document", "office:body", "office:text",
        "text:p", "text:span", "text:h", "text:list",
        "text:list-item", "text:section",
        "style:style", "style:text-properties",
    ],
    "FODG": [
        "office:document", "office:body", "office:drawing",
        "draw:page", "draw:frame", "draw:text-box",
        "draw:rect", "draw:ellipse", "draw:line",
        "text:p", "draw:page@draw:name",
    ],
}


def _reverse_ns_lookup(uri: str) -> str | None:
    """Reverse-map a namespace URI to its ODF prefix."""
    for prefix, ns_uri in ODF_NAMESPACES.items():
        if ns_uri == uri:
            return prefix
    return None


def scan_source_for_qnames(source_path: Path) -> list[dict]:
    """Scan a Python source file for QName references in string literals.

    Handles three patterns found in ODF codec source files:
    1. Literal prefix:element strings (e.g., ``"draw:page"``)
    2. Clark notation ``{namespace_uri}element`` in string literals
    3. f-string / format expressions using NS dict lookups:
       ``f"{{{NS['draw']}}}page"`` or ``NS['draw']`` near element names
    """
    if not source_path.is_file():
        return []

    content = source_path.read_text(encoding="utf-8")
    found = []

    # --- Strategy 1: literal prefix:element strings ---
    for match in re.finditer(r'["\']\.?//(\w+:\w[\w-]*)["\']', content):
        _add_prefix_match(found, match.group(1), content, match.start())
    for match in re.finditer(r'["\'](\w+:\w[\w-]*)["\']', content):
        _add_prefix_match(found, match.group(1), content, match.start())

    # --- Strategy 2: Clark notation in string literals ---
    for match in re.finditer(r'\{(urn:[^}]+)\}(\w[\w-]*)', content):
        uri, local = match.group(1), match.group(2)
        prefix = _reverse_ns_lookup(uri)
        if prefix:
            line_num = content[:match.start()].count("\n") + 1
            found.append({
                "qname": f"{prefix}:{local}",
                "prefix": prefix,
                "local_name": local,
                "namespace": uri,
                "line_number": line_num,
            })

    # --- Strategy 3: NS dict + f-string element extraction ---
    # Matches patterns like: NS['draw']}}}page  or  NS["office"]}}}document
    # These come from f-strings: f"{{{NS['draw']}}}page"
    for match in re.finditer(
        r"""NS\[['"](\w+)['"]\]\}*\}+(\w[\w-]*)""", content
    ):
        prefix, local = match.group(1), match.group(2)
        if prefix in ODF_NAMESPACES:
            line_num = content[:match.start()].count("\n") + 1
            found.append({
                "qname": f"{prefix}:{local}",
                "prefix": prefix,
                "local_name": local,
                "namespace": ODF_NAMESPACES[prefix],
                "line_number": line_num,
            })

    # --- Strategy 4: NS dict attribute access patterns ---
    # Matches: .get(f"{{{NS['draw']}}}name"  →  draw:name (attribute)
    for match in re.finditer(
        r"""\.(?:get|set)\(f["']\{+NS\[['"](\w+)['"]\]\}+(\w[\w-]*)["']""",
        content,
    ):
        prefix, local = match.group(1), match.group(2)
        if prefix in ODF_NAMESPACES:
            line_num = content[:match.start()].count("\n") + 1
            found.append({
                "qname": f"{prefix}:{local}",
                "prefix": prefix,
                "local_name": local,
                "namespace": ODF_NAMESPACES[prefix],
                "line_number": line_num,
            })

    # Deduplicate by qname
    seen: set[str] = set()
    unique = []
    for item in found:
        if item["qname"] not in seen:
            seen.add(item["qname"])
            unique.append(item)

    return unique


def _add_prefix_match(
    found: list[dict], qname: str, content: str, offset: int
) -> None:
    """Helper: add a prefix:local match if the prefix is a known ODF namespace."""
    if ":" not in qname:
        return
    prefix, local = qname.split(":", 1)
    if prefix in ODF_NAMESPACES:
        line_num = content[:offset].count("\n") + 1
        found.append({
            "qname": qname,
            "prefix": prefix,
            "local_name": local,
            "namespace": ODF_NAMESPACES[prefix],
            "line_number": line_num,
        })


def scan_source_for_functions(source_path: Path) -> list[dict]:
    """Extract all public function definitions from a source file."""
    if not source_path.is_file():
        return []

    content = source_path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return []

    functions = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_"):
                functions.append({
                    "name": node.name,
                    "line_number": node.lineno,
                    "end_line": node.end_lineno,
                    "args": [a.arg for a in node.args.args],
                    "docstring": ast.get_docstring(node) or "",
                })

    return functions


def generate_qname_to_code_map(format_id: str, source_path: Path) -> dict:
    """Generate a QName-to-code mapping for a format."""
    qnames_found = scan_source_for_qnames(source_path)
    functions = scan_source_for_functions(source_path)
    expected = FORMAT_QNAME_EXPECTATIONS.get(format_id, [])

    # Build mapping: which functions reference which QNames
    content = source_path.read_text(encoding="utf-8") if source_path.is_file() else ""
    lines = content.splitlines()

    mappings = []
    for qname_info in qnames_found:
        qname = qname_info["qname"]
        qname_line = qname_info["line_number"]
        # Find which function contains this line
        containing_function = None
        for func in functions:
            if func["line_number"] <= qname_line <= (func.get("end_line") or 9999):
                containing_function = func["name"]
                break

        mappings.append({
            "qname": qname,
            "namespace": qname_info["namespace"],
            "prefix": qname_info["prefix"],
            "local_name": qname_info["local_name"],
            "code_references": [{
                "module": str(source_path),
                "function": containing_function or "module_level",
                "line": qname_line,
            }],
        })

    # Find unmapped expected QNames
    mapped_qnames = {m["qname"] for m in mappings}
    unmapped = [q for q in expected if q not in mapped_qnames]

    total_expected = len(expected) if expected else len(qnames_found)
    mapped_count = len(mappings)
    coverage = (mapped_count / total_expected * 100) if total_expected > 0 else 0

    return {
        "format_id": format_id,
        "source_path": str(source_path),
        "spec_ref": FORMAT_QNAME_EXPECTATIONS.get(format_id, ["unknown"])[0] if expected else "unknown",
        "mappings": mappings,
        "unmapped_qnames": unmapped,
        "functions": [f["name"] for f in functions],
        "coverage_summary": {
            "total_expected": total_expected,
            "mapped": mapped_count,
            "unmapped": len(unmapped),
            "coverage_percent": round(coverage, 1),
        },
    }


def generate_namespace_tree(format_id: str) -> dict:
    """Generate namespace containment tree for a format."""
    # This is format-specific knowledge encoded as data
    trees = {
        "FODP": {
            "element": "office:document",
            "children": [{
                "element": "office:body",
                "children": [{
                    "element": "office:presentation",
                    "children": [{
                        "element": "draw:page",
                        "attributes": ["draw:name", "draw:style-name"],
                        "children": [
                            {"element": "draw:frame", "children": [
                                {"element": "draw:text-box", "children": [
                                    {"element": "text:p", "children": [
                                        {"element": "text:span", "leaf": True}
                                    ]}
                                ]}
                            ]},
                            {"element": "presentation:notes", "children": [
                                {"element": "draw:frame", "children": [
                                    {"element": "draw:text-box", "children": [
                                        {"element": "text:p", "leaf": True}
                                    ]}
                                ]}
                            ]},
                        ],
                    }],
                }],
            }],
        },
        "FODS": {
            "element": "office:document",
            "children": [{
                "element": "office:body",
                "children": [{
                    "element": "office:spreadsheet",
                    "children": [{
                        "element": "table:table",
                        "attributes": ["table:name"],
                        "children": [{
                            "element": "table:table-row",
                            "children": [{
                                "element": "table:table-cell",
                                "attributes": ["office:value-type", "office:value"],
                                "children": [
                                    {"element": "text:p", "leaf": True}
                                ],
                            }],
                        }],
                    }],
                }],
            }],
        },
    }

    tree = trees.get(format_id, {"element": "unknown", "note": "No tree defined for this format"})
    return {
        "format_id": format_id,
        "containment_tree": tree,
    }


def generate_ontology(format_id: str, source_path: Path, output_dir: Path) -> dict:
    """Generate complete ontology for a format."""
    output_dir.mkdir(parents=True, exist_ok=True)

    qname_map = generate_qname_to_code_map(format_id, source_path)
    ns_tree = generate_namespace_tree(format_id)

    # Write outputs
    map_path = output_dir / f"qname-to-code-map-{format_id.lower()}.json"
    map_path.write_text(json.dumps(qname_map, indent=2), encoding="utf-8")

    tree_path = output_dir / f"namespace-tree-{format_id.lower()}.json"
    tree_path.write_text(json.dumps(ns_tree, indent=2), encoding="utf-8")

    # Write unmapped ledger
    ledger_path = output_dir / f"unmapped-qnames-{format_id.lower()}.json"
    ledger_path.write_text(json.dumps({
        "format_id": format_id,
        "unmapped": qname_map["unmapped_qnames"],
        "count": len(qname_map["unmapped_qnames"]),
    }, indent=2), encoding="utf-8")

    return {
        "format_id": format_id,
        "qname_map_path": str(map_path),
        "namespace_tree_path": str(tree_path),
        "unmapped_ledger_path": str(ledger_path),
        "coverage": qname_map["coverage_summary"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="QName ontology generator")
    parser.add_argument("--format", required=True, help="Format ID (e.g., FODP)")
    parser.add_argument("--source", help="Source file path (auto-detected if omitted)")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    args = parser.parse_args()

    fmt = args.format.upper()
    if args.source:
        source = Path(args.source)
    else:
        family = FORMAT_FAMILIES.get(fmt, {})
        module_base = family.get("module_base", f"src/python/{fmt.lower()}")
        module_file = MODULE_FILE_MAP.get(fmt, f"{fmt.lower()}_codec.py")
        source = Path(module_base) / module_file

    result = generate_ontology(fmt, source, Path(args.output_dir))
    print(json.dumps(result, indent=2))
    return 0


# Reuse from compiler
FORMAT_FAMILIES = {
    "FODP": {"family": "ODF", "module_base": "src/python/fodp"},
    "FODS": {"family": "ODF", "module_base": "src/python/fods"},
    "FODT": {"family": "ODF", "module_base": "src/python/fodt"},
    "FODG": {"family": "ODF", "module_base": "src/python/fodg"},
}

MODULE_FILE_MAP = {
    "FODP": "fodp_codec.py", "FODS": "fods_codec.py",
    "FODT": "fodt_codec.py", "FODG": "fodg_codec.py",
}

if __name__ == "__main__":
    sys.exit(main())
