r"""Import hygiene — AST-based sys.path mutation detector with alias resolution.

WHY AST AND NOT grep
--------------------
`sys.path` mutation is routinely written in forms that defeat naive matchers:

    import sys as _sys
    _sys.path.insert(0, ...)          # word-boundary regex \bsys\.path MISSES this
                                       # naive AST (Name.id == "sys") MISSES this

    from sys import path as _p
    _p.insert(0, ...)                 # no "sys.path" text at all

    _p = sys.path
    _p.append(...)                    # local rebinding

A detector that misses these reports FALSE CLEAN, which is worse than no
detector: it certifies the defect as absent. This module therefore resolves
import aliases and simple assignment rebindings before matching.

Real example at HEAD (src/python/dif/interchange_document.py:24-29):

    try:
        from csv.csv_writer import write_csv as _ff_write_csv
    except (ImportError, AttributeError):
        try:
            import sys as _sys
            _sys.path.insert(0, str(Path(__file__).resolve()...))

DETECTED FORMS
--------------
  <sys_alias>.path.insert/append/extend/remove/pop/clear(...)
  <path_alias>.insert/append/extend/remove/pop/clear(...)
  <sys_alias>.path = ...            (rebind)
  <sys_alias>.path += ...           (augmented assign)
  <path_alias> += ...
  <sys_alias>.path[...] = ...       (index/slice assign)

KNOWN LIMITS (documented, not hidden)
-------------------------------------
  * Alias collection is module-wide, not scope-aware. A function-local name that
    shadows a sys alias is still treated as one. This over-approximates -> it can
    over-report, never under-report. That bias is deliberate (fail-closed).
  * Fully dynamic mutation (`getattr(sys, "path").insert`, `importlib`,
    `exec("sys.path...")`, `site.addsitedir`) is NOT detected. These are not
    idioms present in this repo; if they appear, this module must be extended.
  * A file that fails to parse is reported as an explicit PARSE_ERROR finding,
    never silently skipped (a syntax error must not read as "clean").
"""
from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path

# List methods that mutate sys.path in place.
_MUTATING_METHODS = frozenset({"insert", "append", "extend", "remove", "pop", "clear"})


@dataclass(frozen=True)
class Finding:
    """One import-hygiene violation."""

    path: str
    line: int
    col: int
    kind: str
    snippet: str

    def format(self) -> str:
        return f"{self.path}:{self.line}:{self.col}: {self.kind}: {self.snippet}"


@dataclass
class _Aliases:
    """Names bound to the `sys` module and to the `sys.path` list."""

    sys_names: set[str] = field(default_factory=lambda: {"sys"})
    path_names: set[str] = field(default_factory=set)


def _collect_aliases(tree: ast.AST) -> _Aliases:
    """Resolve `sys` / `sys.path` aliases, including simple assignment chains.

    Runs to a fixpoint so that chained rebindings (`s = sys; p = s.path`) resolve.
    """
    al = _Aliases()

    for node in ast.walk(tree):
        # import sys / import sys as _sys
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name == "sys":
                    al.sys_names.add(a.asname or "sys")
        # from sys import path / from sys import path as _p
        elif isinstance(node, ast.ImportFrom):
            if node.module == "sys" and not node.level:
                for a in node.names:
                    if a.name == "path":
                        al.path_names.add(a.asname or "path")

    # Fixpoint over assignment rebindings: s = sys ; p = sys.path ; p2 = p
    for _ in range(5):
        grew = False
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
            if not targets:
                continue
            v = node.value
            # p = sys.path  /  p = _sys.path
            if (
                isinstance(v, ast.Attribute)
                and v.attr == "path"
                and isinstance(v.value, ast.Name)
                and v.value.id in al.sys_names
            ):
                for t in targets:
                    if t not in al.path_names:
                        al.path_names.add(t)
                        grew = True
            # s = sys  /  p2 = p
            elif isinstance(v, ast.Name):
                if v.id in al.sys_names:
                    for t in targets:
                        if t not in al.sys_names:
                            al.sys_names.add(t)
                            grew = True
                elif v.id in al.path_names:
                    for t in targets:
                        if t not in al.path_names:
                            al.path_names.add(t)
                            grew = True
        if not grew:
            break
    return al


def _is_syspath_attr(node: ast.AST, al: _Aliases) -> bool:
    """True for `<sys_alias>.path`."""
    return (
        isinstance(node, ast.Attribute)
        and node.attr == "path"
        and isinstance(node.value, ast.Name)
        and node.value.id in al.sys_names
    )


def _is_path_name(node: ast.AST, al: _Aliases) -> bool:
    """True for a bare name bound to sys.path (`_p` after `from sys import path as _p`)."""
    return isinstance(node, ast.Name) and node.id in al.path_names


def _snippet(source_lines: list[str], node: ast.AST) -> str:
    line = getattr(node, "lineno", 0)
    if 1 <= line <= len(source_lines):
        return source_lines[line - 1].strip()[:120]
    return "<unavailable>"


def check_source(source: str, path: str = "<memory>") -> list[Finding]:
    """Return every sys.path-mutation finding in `source`.

    A parse failure yields a single PARSE_ERROR finding rather than an empty
    (falsely clean) list.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [Finding(path, exc.lineno or 0, exc.offset or 0, "PARSE_ERROR",
                        f"could not parse: {exc.msg}")]

    al = _collect_aliases(tree)
    lines = source.splitlines()
    out: list[Finding] = []

    for node in ast.walk(tree):
        # <sys>.path.insert(...)  |  <path_alias>.insert(...)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in _MUTATING_METHODS:
                recv = node.func.value
                if _is_syspath_attr(recv, al) or _is_path_name(recv, al):
                    out.append(Finding(path, node.lineno, node.col_offset,
                                       "SYSPATH_MUTATION",
                                       _snippet(lines, node)))
        # <sys>.path = ...  |  <sys>.path[...] = ...
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if _is_syspath_attr(t, al):
                    out.append(Finding(path, node.lineno, node.col_offset,
                                       "SYSPATH_REBIND", _snippet(lines, node)))
                elif isinstance(t, ast.Subscript) and (
                    _is_syspath_attr(t.value, al) or _is_path_name(t.value, al)
                ):
                    out.append(Finding(path, node.lineno, node.col_offset,
                                       "SYSPATH_SLICE_ASSIGN", _snippet(lines, node)))
        # <sys>.path += [...]  |  <path_alias> += [...]
        elif isinstance(node, ast.AugAssign):
            if _is_syspath_attr(node.target, al) or _is_path_name(node.target, al):
                out.append(Finding(path, node.lineno, node.col_offset,
                                   "SYSPATH_AUGASSIGN", _snippet(lines, node)))

    out.sort(key=lambda f: (f.line, f.col))
    return out


def check_file(path: Path | str) -> list[Finding]:
    """Check one .py file. Unreadable files yield a READ_ERROR finding."""
    p = Path(path)
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return [Finding(str(p), 0, 0, "READ_ERROR", str(exc))]
    return check_source(text, str(p).replace("\\", "/"))


def check_paths(paths: list[Path | str]) -> list[Finding]:
    """Check an explicit list of files (directories are walked for *.py)."""
    out: list[Finding] = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            for f in sorted(p.rglob("*.py")):
                if "__pycache__" in f.parts:
                    continue
                out.extend(check_file(f))
        elif p.suffix == ".py":
            out.extend(check_file(p))
    return out


def _main(argv=None) -> int:
    """CLI: scan paths for sys.path mutation.

        python -m tools.governance.skill_gates.import_hygiene src/python/sylk

    Exit 0 = clean, 1 = violations found. Deliberately has no `--fix`: the
    correct repair depends on why the path hack was there (see plan finding
    PA-F1 — csv's are load-bearing, most others are cargo-cult).
    """
    import argparse
    import json

    ap = argparse.ArgumentParser(
        description="Scan for sys.path mutation (AST, alias-resolving)")
    ap.add_argument("paths", nargs="+", help="files or directories to scan")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args(argv)

    findings = check_paths(args.paths)
    if args.json:
        print(json.dumps({
            "verdict": "CLEAN" if not findings else "VIOLATIONS",
            "count": len(findings),
            "findings": [
                {"path": f.path, "line": f.line, "col": f.col,
                 "kind": f.kind, "snippet": f.snippet} for f in findings],
        }, indent=2))
    else:
        for f in findings:
            print(f.format())
        print(f"\n{len(findings)} finding(s) in {len(set(f.path for f in findings))} file(s)"
              if findings else "clean: no sys.path mutation found")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(_main())
