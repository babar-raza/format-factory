"""Plan and repair duplicate Python format exception definitions.

The command is dry-run by default. It removes only shadow class definitions
whose names are already defined by the package's canonical ``exceptions.py``.
The canonical hierarchy is validated before any write, and all writes are
atomic.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = REPO_ROOT / "src" / "python"


class RepairError(RuntimeError):
    """Raised when a safe deterministic repair cannot be constructed."""


@dataclass(frozen=True)
class Duplicate:
    path: str
    names: tuple[str, ...]


def _parse(path: Path) -> tuple[str, ast.Module]:
    text = path.read_text(encoding="utf-8")
    try:
        return text, ast.parse(text, filename=str(path))
    except SyntaxError as error:
        raise RepairError(f"cannot parse {path}: {error}") from error


def _class_bases(node: ast.ClassDef) -> tuple[str, ...]:
    values: list[str] = []
    for base in node.bases:
        if isinstance(base, ast.Name):
            values.append(base.id)
        elif isinstance(base, ast.Attribute):
            values.append(base.attr)
    return tuple(values)


def canonical_exceptions(package_dir: Path) -> dict[str, tuple[str, ...]]:
    path = package_dir / "exceptions.py"
    if not path.is_file():
        raise RepairError(f"canonical exception module is missing: {path}")
    _, tree = _parse(path)
    classes = {
        node.name: _class_bases(node)
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name.endswith("Error")
    }
    if not classes:
        raise RepairError(f"no exception classes found in {path}")

    def reaches_root(name: str, seen: frozenset[str] = frozenset()) -> bool:
        if name == "FormatFactoryError":
            return True
        if name in seen or name not in classes:
            return False
        return any(
            reaches_root(base, seen | {name})
            for base in classes[name]
        )

    invalid = sorted(name for name in classes if not reaches_root(name))
    if invalid:
        raise RepairError(
            "canonical exception hierarchy is not rooted at FormatFactoryError: "
            + ", ".join(invalid)
        )
    return classes


def find_duplicates(package_dir: Path) -> list[Duplicate]:
    canonical = canonical_exceptions(package_dir)
    duplicates: list[Duplicate] = []
    for path in sorted(package_dir.rglob("*.py")):
        if path == package_dir / "exceptions.py" or "__pycache__" in path.parts:
            continue
        _, tree = _parse(path)
        names = tuple(
            sorted(
                node.name
                for node in tree.body
                if isinstance(node, ast.ClassDef) and node.name in canonical
            )
        )
        if names:
            duplicates.append(
                Duplicate(path=path.relative_to(package_dir).as_posix(), names=names)
            )
    return duplicates


def _relative_import(path: Path, package_dir: Path, names: tuple[str, ...]) -> str:
    depth = len(path.relative_to(package_dir).parts) - 1
    dots = "." * (depth + 1)
    return f"from {dots}exceptions import {', '.join(names)}"


def _insertion_line(tree: ast.Module) -> int:
    line = 0
    body = list(tree.body)
    if (
        body
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, str)
    ):
        line = body.pop(0).end_lineno or body[0].lineno
    for node in body:
        if isinstance(node, ast.ImportFrom) and node.module == "__future__":
            line = node.end_lineno or node.lineno
        else:
            break
    return line


def repair_file(path: Path, package_dir: Path, names: tuple[str, ...]) -> str:
    text, tree = _parse(path)
    nodes = [
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name in names
    ]
    if len(nodes) != len(names):
        raise RepairError(f"duplicate plan drifted before apply: {path}")
    if any(node.decorator_list for node in nodes):
        raise RepairError(f"decorated duplicate exception is unsafe to remove: {path}")

    lines = text.splitlines(keepends=True)
    for node in sorted(nodes, key=lambda item: item.lineno, reverse=True):
        start = node.lineno - 1
        end = node.end_lineno or node.lineno
        del lines[start:end]

    remaining = "".join(lines)
    _, remaining_tree = _parse_text(path, remaining)
    import_line = _relative_import(path, package_dir, names)
    if import_line not in remaining.splitlines():
        insert_at = _insertion_line(remaining_tree)
        lines = remaining.splitlines(keepends=True)
        addition = import_line + "\n"
        if insert_at and insert_at < len(lines) and lines[insert_at].strip():
            addition += "\n"
        lines.insert(insert_at, addition)
        remaining = "".join(lines)
    return _normalize_blank_lines(remaining)


def _parse_text(path: Path, text: str) -> tuple[str, ast.Module]:
    try:
        return text, ast.parse(text, filename=str(path))
    except SyntaxError as error:
        raise RepairError(f"repair would produce invalid Python for {path}: {error}") from error


def _normalize_blank_lines(text: str) -> str:
    while "\n\n\n\n" in text:
        text = text.replace("\n\n\n\n", "\n\n\n")
    return text.rstrip() + "\n"


def _atomic_write(path: Path, text: str) -> None:
    fd, raw_temp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temp = Path(raw_temp)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def run(package_dir: Path, *, apply: bool = False) -> dict[str, object]:
    package_dir = package_dir.resolve()
    duplicates = find_duplicates(package_dir)
    changed = [item.path for item in duplicates]
    if apply:
        for item in duplicates:
            path = package_dir / item.path
            _atomic_write(path, repair_file(path, package_dir, item.names))
        if find_duplicates(package_dir):
            raise RepairError("postcondition failed: duplicate exceptions remain")
    return {
        "result": "PASS",
        "mode": "apply" if apply else "dry-run",
        "canonical_module": "exceptions.py",
        "changed_files": changed,
        "duplicates": [asdict(item) for item in duplicates],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", required=True, dest="format_id")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    package_dir = SOURCE_ROOT / args.format_id
    try:
        result = run(package_dir, apply=args.apply)
    except RepairError as error:
        print(json.dumps({"result": "FAIL", "error": str(error)}, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
