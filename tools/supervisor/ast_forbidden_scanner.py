"""G3 AST Forbidden-Call Scanner.

Deterministic safety gate that rejects LLM-generated Python source containing
dangerous calls before they are accepted into product source.

Sprint: FF-LIBFORGE-GOVERNANCE-UNBLOCK-IMPLEMENTATION-001 (v1)
       FF-LIBFORGE-GUARDED-AUTONOMOUS-EXPANSION-001 (v2 alias hardening)
Taskcard: LFI-5-C (v1), LFI-6-A (v2)
Gate: G3 (post-LLM gates checklist)
Idempotency-key: lfi-5-c-ast-forbidden-scanner-v1
v2-idempotency-key: lfi-6-a-ast-scanner-alias-hardening-v2
"""
from __future__ import annotations

import ast
import json
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import List, Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Forbidden bare names (built-in calls).
FORBIDDEN_BUILTINS: frozenset[str] = frozenset({"eval", "exec"})

# Forbidden attribute calls: module.function or module.Class
FORBIDDEN_ATTR_CALLS: frozenset[tuple[str, str]] = frozenset({
    ("os", "system"),
    ("subprocess", "run"),
    ("subprocess", "Popen"),
    ("subprocess", "call"),
    ("subprocess", "check_call"),
    ("subprocess", "check_output"),
})


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"


@dataclass
class Finding:
    file: str
    line: int
    col: int
    symbol: str
    severity: str
    description: str

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


@dataclass
class ScanResult:
    file: str
    findings: List[Finding] = field(default_factory=list)
    parse_error: Optional[str] = None
    scanned: bool = True

    @property
    def safe(self) -> bool:
        return len(self.findings) == 0 and self.parse_error is None

    def to_dict(self) -> dict:
        return {
            "file": self.file,
            "safe": self.safe,
            "findings": [f.to_dict() for f in self.findings],
            "parse_error": self.parse_error,
            "scanned": self.scanned,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class ScanReport:
    files_scanned: int = 0
    files_with_findings: int = 0
    total_findings: int = 0
    results: List[ScanResult] = field(default_factory=list)

    @property
    def overall_safe(self) -> bool:
        return self.files_with_findings == 0

    @property
    def verdict(self) -> str:
        return "PASS" if self.overall_safe else "FAIL"

    def to_dict(self) -> dict:
        return {
            "verdict": self.verdict,
            "overall_safe": self.overall_safe,
            "files_scanned": self.files_scanned,
            "files_with_findings": self.files_with_findings,
            "total_findings": self.total_findings,
            "results": [r.to_dict() for r in self.results],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


# ---------------------------------------------------------------------------
# Core scanner (v2: alias-aware)
# ---------------------------------------------------------------------------


def _collect_aliases(
    tree: ast.AST,
) -> tuple[dict[str, str], dict[str, tuple[str, str]]]:
    """Pre-pass over the AST to collect import aliases.

    Returns:
        module_aliases: Maps local alias → canonical module name.
            e.g. {"sp": "subprocess", "operating": "os"}
        from_imports: Maps local name → (canonical_module, canonical_attr).
            e.g. {"run": ("subprocess", "run"), "execute": ("subprocess", "run")}
    """
    module_aliases: dict[str, str] = {}
    from_imports: dict[str, tuple[str, str]] = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.asname is not None:
                    # import subprocess as sp  →  sp → subprocess
                    module_aliases[alias.asname] = alias.name
        elif isinstance(node, ast.ImportFrom):
            if node.module is None:
                continue
            for alias in node.names:
                local_name = alias.asname if alias.asname else alias.name
                candidate = (node.module, alias.name)
                if candidate in FORBIDDEN_ATTR_CALLS:
                    # from subprocess import run [as execute]
                    from_imports[local_name] = candidate

    return module_aliases, from_imports


class _ForbiddenCallVisitor(ast.NodeVisitor):
    """AST visitor that detects forbidden function/method calls.

    v2: uses pre-collected import alias maps so that aliased calls like
    ``import subprocess as sp; sp.run(...)`` and
    ``from subprocess import run; run(...)`` are correctly detected.
    The finding.symbol always uses the canonical module name (e.g. subprocess.run).
    """

    def __init__(
        self,
        filename: str,
        module_aliases: dict[str, str],
        from_imports: dict[str, tuple[str, str]],
    ) -> None:
        self._filename = filename
        self.findings: List[Finding] = []
        # alias → canonical module: {"sp": "subprocess"}
        self._module_aliases = module_aliases
        # local_name → (canonical_module, canonical_attr): {"run": ("subprocess","run")}
        self._from_imports = from_imports

    def visit_Call(self, node: ast.Call) -> None:
        self._check_call(node)
        self.generic_visit(node)

    def _check_call(self, node: ast.Call) -> None:
        func = node.func

        # Case 1: bare name — eval(...), exec(...), or from-imported forbidden call
        if isinstance(func, ast.Name):
            name = func.id
            if name in FORBIDDEN_BUILTINS:
                self.findings.append(Finding(
                    file=self._filename,
                    line=node.lineno,
                    col=node.col_offset,
                    symbol=name,
                    severity=Severity.CRITICAL.value,
                    description=f"Forbidden built-in call: {name}()",
                ))
            elif name in self._from_imports:
                canonical_module, canonical_attr = self._from_imports[name]
                symbol = f"{canonical_module}.{canonical_attr}"
                self.findings.append(Finding(
                    file=self._filename,
                    line=node.lineno,
                    col=node.col_offset,
                    symbol=symbol,
                    severity=Severity.CRITICAL.value,
                    description=f"Forbidden call via from-import: {name}() -> {symbol}()",
                ))

        # Case 2: attribute call — os.system(...), sp.run(...) (direct or aliased)
        elif isinstance(func, ast.Attribute):
            value = func.value
            attr = func.attr
            if isinstance(value, ast.Name):
                local_name = value.id
                # Resolve canonical module (handles both direct and aliased)
                canonical_module = self._module_aliases.get(local_name, local_name)
                if (canonical_module, attr) in FORBIDDEN_ATTR_CALLS:
                    symbol = f"{canonical_module}.{attr}"
                    self.findings.append(Finding(
                        file=self._filename,
                        line=node.lineno,
                        col=node.col_offset,
                        symbol=symbol,
                        severity=Severity.CRITICAL.value,
                        description=f"Forbidden call: {local_name}.{attr}() -> {symbol}()",
                    ))


def scan_source(source_code: str, filename: str = "<string>") -> ScanResult:
    """Scan a Python source string for forbidden calls.

    Args:
        source_code: Python source code as a string.
        filename: Filename label for findings (used in output only).

    Returns:
        ScanResult with findings or parse_error populated.
    """
    try:
        tree = ast.parse(source_code, filename=filename)
    except SyntaxError as exc:
        return ScanResult(
            file=filename,
            parse_error=f"SyntaxError at line {exc.lineno}: {exc.msg}",
        )

    module_aliases, from_imports = _collect_aliases(tree)
    visitor = _ForbiddenCallVisitor(filename, module_aliases, from_imports)
    visitor.visit(tree)
    return ScanResult(file=filename, findings=visitor.findings)


def scan_file(path: str | Path) -> ScanResult:
    """Scan a Python source file for forbidden calls.

    Args:
        path: Absolute or relative path to a .py file.

    Returns:
        ScanResult with findings or parse_error populated.
    """
    p = Path(path)
    filename = str(p)
    try:
        source = p.read_text(encoding="utf-8")
    except OSError as exc:
        return ScanResult(file=filename, parse_error=f"IOError: {exc}", scanned=False)
    return scan_source(source, filename=filename)


def scan_directory(
    directory: str | Path,
    recursive: bool = True,
    file_pattern: str = "*.py",
) -> ScanReport:
    """Scan all Python files under a directory for forbidden calls.

    Args:
        directory: Directory to scan.
        recursive: Whether to recurse into subdirectories.
        file_pattern: Glob pattern for files to scan (default: *.py).

    Returns:
        ScanReport aggregating all file results.
    """
    d = Path(directory)
    glob_fn = d.rglob if recursive else d.glob
    py_files = sorted(glob_fn(file_pattern))

    report = ScanReport(files_scanned=len(py_files))
    for py_file in py_files:
        result = scan_file(py_file)
        report.results.append(result)
        if not result.safe:
            report.files_with_findings += 1
            report.total_findings += len(result.findings)
    return report


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    """CLI: ast_forbidden_scanner <path> [--json]"""
    import sys
    args = argv if argv is not None else sys.argv[1:]

    if not args:
        print("Usage: ast_forbidden_scanner <file_or_directory> [--json]", file=sys.stderr)
        return 2

    target = args[0]
    output_json = "--json" in args

    p = Path(target)
    if p.is_file():
        result = scan_file(p)
        if output_json:
            print(result.to_json())
        else:
            status = "SAFE" if result.safe else "UNSAFE"
            print(f"{status}: {target}")
            for f in result.findings:
                print(f"  Line {f.line}: {f.symbol} — {f.description}")
        return 0 if result.safe else 1

    elif p.is_dir():
        report = scan_directory(p)
        if output_json:
            print(report.to_json())
        else:
            print(f"Verdict: {report.verdict}")
            print(f"Files scanned: {report.files_scanned}")
            print(f"Files with findings: {report.files_with_findings}")
            print(f"Total findings: {report.total_findings}")
            for r in report.results:
                if not r.safe:
                    for f in r.findings:
                        print(f"  {f.file}:{f.line}: {f.symbol}")
        return 0 if report.overall_safe else 1

    else:
        print(f"Error: {target} does not exist", file=sys.stderr)
        return 2


if __name__ == "__main__":
    import sys
    sys.exit(main())
