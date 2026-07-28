"""Deterministically expose a format analytics module from its package root."""
from __future__ import annotations

import argparse
import ast
import json
import os
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = REPO_ROOT / "src" / "python"
BEGIN = "# BEGIN FORMAT FACTORY ANALYTICS EXPORTS"
END = "# END FORMAT FACTORY ANALYTICS EXPORTS"


class WiringError(RuntimeError):
    """Raised when analytics exports cannot be determined safely."""


def _literal_all(tree: ast.Module) -> tuple[str, ...] | None:
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if not any(isinstance(target, ast.Name) and target.id == "__all__" for target in targets):
            continue
        value = node.value
        if not isinstance(value, (ast.List, ast.Tuple)):
            raise WiringError("analytics __all__ must be a literal list or tuple")
        if not all(
            isinstance(item, ast.Constant) and isinstance(item.value, str)
            for item in value.elts
        ):
            raise WiringError("analytics __all__ must contain only string literals")
        return tuple(sorted({str(item.value) for item in value.elts}))
    return None


def discover_exports(module_path: Path) -> tuple[str, ...]:
    try:
        tree = ast.parse(module_path.read_text(encoding="utf-8"), filename=str(module_path))
    except SyntaxError as error:
        raise WiringError(f"cannot parse analytics module: {error}") from error
    explicit = _literal_all(tree)
    if explicit is not None:
        return explicit
    return tuple(
        sorted(
            {
                node.name
                for node in tree.body
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                and not node.name.startswith("_")
            }
        )
    )


def find_module(package_dir: Path) -> Path:
    candidates = [
        package_dir / f"{package_dir.name}_analytics.py",
        package_dir / "analytics.py",
    ]
    found = [path for path in candidates if path.is_file()]
    if len(found) != 1:
        raise WiringError(
            f"expected exactly one analytics module, found {[path.name for path in found]}"
        )
    return found[0]


def _block(module_name: str, exports: tuple[str, ...], has_all: bool) -> str:
    if not exports:
        raise WiringError("analytics module has no public exports")
    names = ", ".join(exports)
    all_statement = (
        f"__all__ += {exports!r}" if has_all else f"__all__ = {exports!r}"
    )
    return (
        f"{BEGIN}\n"
        f"from .{module_name} import {names}\n\n"
        f"{all_statement}\n"
        f"{END}"
    )


def _has_all(tree: ast.Module) -> bool:
    return any(
        (
            isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets)
        )
        or (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "__all__"
        )
        for node in tree.body
    )


def render(package_dir: Path) -> tuple[Path, tuple[str, ...], str]:
    module = find_module(package_dir)
    exports = discover_exports(module)
    init = package_dir / "__init__.py"
    current = init.read_text(encoding="utf-8") if init.is_file() else ""
    prefix = current
    suffix = ""
    if BEGIN in current or END in current:
        if current.count(BEGIN) != 1 or current.count(END) != 1:
            raise WiringError("analytics export markers are unbalanced")
        start = current.index(BEGIN)
        finish = current.index(END, start) + len(END)
        prefix = current[:start]
        suffix = current[finish:]
    source_without_owned_block = prefix + suffix
    try:
        tree = ast.parse(source_without_owned_block or "", filename=str(init))
    except SyntaxError as error:
        raise WiringError(f"cannot parse package initializer: {error}") from error
    block = _block(module.stem, exports, _has_all(tree))
    if BEGIN in current or END in current:
        updated = prefix + block + suffix
    else:
        updated = current.rstrip() + ("\n\n" if current.strip() else "") + block + "\n"
    try:
        ast.parse(updated, filename=str(init))
    except SyntaxError as error:
        raise WiringError(f"generated initializer is invalid: {error}") from error
    return init, exports, updated


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
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
    init, exports, updated = render(package_dir)
    current = init.read_text(encoding="utf-8") if init.is_file() else ""
    change_required = current != updated
    if apply and change_required:
        _atomic_write(init, updated)
        _, _, replay = render(package_dir)
        if replay != updated:
            raise WiringError("postcondition failed: analytics wiring is not idempotent")
    return {
        "result": "PASS",
        "mode": "apply" if apply else "dry-run",
        "analytics_module": find_module(package_dir).name,
        "exports": list(exports),
        "change_required": change_required,
        "changed_files": [init.name] if change_required else [],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", required=True, dest="format_id")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        result = run(SOURCE_ROOT / args.format_id, apply=args.apply)
    except WiringError as error:
        print(json.dumps({"result": "FAIL", "error": str(error)}, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
