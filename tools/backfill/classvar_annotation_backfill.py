"""Add ClassVar type annotations to spec_qname and companion class attributes.

GAP-FORENSIC-013: Transforms bare class-level assignments like
    spec_qname = "csv:record"
into properly annotated ClassVar declarations:
    spec_qname: ClassVar[str] = "csv:record"

Only touches class-level attributes. Module-level attributes (analytics files) are skipped.
Already-annotated files are left unchanged (idempotent).
"""
from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_PYTHON = REPO_ROOT / "src" / "python"

SKIP_DIRS = {"build", "__pycache__", ".git", "__pypackages__"}

STR_ATTRS = {"spec_qname", "spec_fact_ref", "namespace_uri", "local_name", "spec_source"}
LIST_ATTRS = {"facade_names"}
BOOL_ATTRS = {"authority_only"}
ALL_ATTRS = STR_ATTRS | LIST_ATTRS | BOOL_ATTRS

TYPE_MAP = {}
for _a in STR_ATTRS:
    TYPE_MAP[_a] = "str"
for _a in LIST_ATTRS:
    TYPE_MAP[_a] = "list"
for _a in BOOL_ATTRS:
    TYPE_MAP[_a] = "bool"


def _find_class_attr_lines(source: str) -> dict[int, str]:
    """Return {line_number: attr_name} for bare class-level attribute assignments."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {}

    results = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for stmt in node.body:
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name) and target.id in ALL_ATTRS:
                        results[stmt.lineno] = target.id
            elif isinstance(stmt, ast.AnnAssign):
                if (
                    isinstance(stmt.target, ast.Name)
                    and stmt.target.id in ALL_ATTRS
                ):
                    ann_src = ast.dump(stmt.annotation)
                    if "ClassVar" in ann_src:
                        continue
                    results[stmt.lineno] = stmt.target.id
    return results


def _has_classvar_import(lines: list[str]) -> bool:
    for line in lines:
        if re.match(r"from\s+typing\s+import\s+.*\bClassVar\b", line):
            return True
    return False


def _add_classvar_import(lines: list[str]) -> list[str]:
    """Mutate lines to add ClassVar to typing imports. Returns modified lines."""
    if _has_classvar_import(lines):
        return lines

    for i, line in enumerate(lines):
        m = re.match(r"(from\s+typing\s+import\s+)(.*)", line)
        if m:
            prefix, imports_part = m.group(1), m.group(2)
            stripped = imports_part.rstrip()
            if stripped.endswith(")"):
                lines[i] = line.rstrip()[:-1] + ", ClassVar)\n"
            else:
                lines[i] = prefix + imports_part.rstrip() + ", ClassVar\n"
            return lines

    future_idx = None
    last_import_idx = None
    first_class_idx = None
    docstring_end_idx = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("from __future__"):
            future_idx = i
        if stripped.startswith(("import ", "from ")) and not stripped.startswith("from __future__"):
            last_import_idx = i
        if stripped.startswith("class ") and first_class_idx is None:
            first_class_idx = i

    if future_idx is not None:
        insert_at = future_idx + 1
        lines.insert(insert_at, "from typing import ClassVar\n")
        return lines

    if last_import_idx is not None:
        insert_at = last_import_idx + 1
        lines.insert(insert_at, "from typing import ClassVar\n")
        return lines

    if first_class_idx is not None:
        insert_at = first_class_idx
        while insert_at > 0 and lines[insert_at - 1].strip() == "":
            insert_at -= 1
        lines.insert(insert_at, "from typing import ClassVar\n")
        if insert_at > 0 and lines[insert_at - 1].strip() != "":
            lines.insert(insert_at, "\n")
        return lines

    lines.insert(0, "from typing import ClassVar\n")
    return lines


def _annotate_attr_line(line: str, attr_name: str) -> str:
    """Transform a bare assignment line into a ClassVar-annotated one."""
    cv_type = TYPE_MAP[attr_name]

    ann_pattern = re.compile(
        rf"^(\s*){re.escape(attr_name)}\s*:\s*\w+\s*=\s*(.*)"
    )
    m_ann = ann_pattern.match(line)
    if m_ann:
        indent = m_ann.group(1)
        value = m_ann.group(2).rstrip()
        return f"{indent}{attr_name}: ClassVar[{cv_type}] = {value}\n"

    bare_pattern = re.compile(
        rf"^(\s*){re.escape(attr_name)}\s*=\s*(.*)"
    )
    m = bare_pattern.match(line)
    if m:
        indent = m.group(1)
        value = m.group(2).rstrip()
        return f"{indent}{attr_name}: ClassVar[{cv_type}] = {value}\n"

    return line


def process_file(filepath: Path, dry_run: bool = False) -> int:
    """Process a single file. Returns count of attribute lines changed."""
    source = filepath.read_text(encoding="utf-8", errors="replace")
    class_attrs = _find_class_attr_lines(source)
    if not class_attrs:
        return 0

    lines = source.splitlines(keepends=True)
    if not lines[-1].endswith("\n"):
        lines[-1] += "\n"

    changed = 0
    for lineno, attr_name in class_attrs.items():
        idx = lineno - 1
        if 0 <= idx < len(lines):
            old_line = lines[idx]
            new_line = _annotate_attr_line(old_line, attr_name)
            if new_line != old_line:
                lines[idx] = new_line
                changed += 1

    if changed == 0:
        return 0

    if not _has_classvar_import(lines):
        lines = _add_classvar_import(lines)

    if not dry_run:
        filepath.write_text("".join(lines), encoding="utf-8")

    return changed


def find_py_files(fmt: str) -> list[Path]:
    """Find all .py files for a format, skipping build/pycache dirs."""
    fmt_dir = SRC_PYTHON / fmt
    if not fmt_dir.is_dir():
        print(f"ERROR: {fmt_dir} not found", file=sys.stderr)
        return []

    results = []
    for py_file in sorted(fmt_dir.rglob("*.py")):
        parts = py_file.relative_to(fmt_dir).parts
        if any(p in SKIP_DIRS for p in parts):
            continue
        results.append(py_file)
    return results


def run(fmt: str, dry_run: bool = False) -> dict:
    """Run the backfill for a single format. Returns summary dict."""
    files = find_py_files(fmt)

    total_changed = 0
    files_changed = 0
    details = []

    for py_file in files:
        count = process_file(py_file, dry_run=dry_run)
        if count > 0:
            files_changed += 1
            total_changed += count
            rel = py_file.relative_to(REPO_ROOT)
            details.append((str(rel), count))

    return {
        "format": fmt,
        "files_scanned": len(files),
        "files_changed": files_changed,
        "attrs_changed": total_changed,
        "dry_run": dry_run,
        "details": details,
    }


def main():
    parser = argparse.ArgumentParser(description="Add ClassVar annotations to spec_qname attributes")
    parser.add_argument("--format", required=True, help="Format package name (e.g., csv, abw)")
    parser.add_argument("--dry-run", action="store_true", help="Report changes without writing")
    args = parser.parse_args()

    result = run(args.format, dry_run=args.dry_run)

    mode = "DRY RUN" if result["dry_run"] else "APPLIED"
    print(f"\n[{mode}] Format: {result['format']}")
    print(f"  Files scanned:  {result['files_scanned']}")
    print(f"  Files changed:  {result['files_changed']}")
    print(f"  Attrs annotated: {result['attrs_changed']}")

    if result["details"]:
        print("\n  Changed files:")
        for path, count in result["details"]:
            print(f"    {path} ({count} attrs)")

    return 0 if result["attrs_changed"] >= 0 else 1


if __name__ == "__main__":
    sys.exit(main())
