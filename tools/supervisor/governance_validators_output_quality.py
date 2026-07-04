"""governance_validators_output_quality.py — V134-V136: Output escaping quality gates.

Added 2026-07-04 as part of playful-swimming-stearns assurance sprint (MA-SYSTEM-WIDE-2026-07-04).

V134 (GAP-CSV-008): validate_no_manual_json_escaping_in_dotnet
    .NET source files must not use manual string Replace chains to escape JSON.
    All JSON output must go through System.Text.Json.JsonSerializer or JsonDocument.
    Root cause: CsvDocumentAnalytics.cs _JsonEsc bug (GAP-CSV-008). Prevents recurrence.
    blocks_sprint: False (WARN — initial sprint to confirm no false positives).

V135 (GAP-CSV-009): validate_html_escaping_in_dotnet
    .NET source files that produce <td>/<th> HTML must use WebUtility.HtmlEncode or equivalent.
    Detects: C# string interpolation with <td>{...} without an escaping call on the value.
    Root cause: CsvDocumentAnalytics.cs ToHtml() bug (GAP-CSV-009). Prevents recurrence.
    blocks_sprint: False (WARN — initial sprint to confirm no false positives).

V136 (future-prevention): validate_html_escaping_in_python
    Python source files that produce <td>/<th> HTML must use html.escape() or str.maketrans().
    Confirms existing Python baseline is clean; blocks future regressions.
    blocks_sprint: False (WARN — confirms baseline; escalate if violations found).
"""

from __future__ import annotations

import re
from pathlib import Path


# ---------------------------------------------------------------------------
# Result helper — matches standard runner schema
# ---------------------------------------------------------------------------

def _result(vid: str, name: str, passed: bool, items: list, blocks: bool = False) -> dict:
    """Standard validator result shape compatible with governance_validator_runner.py."""
    result_label = "PASS" if passed else ("FAIL" if blocks else "WARN")
    return {
        "validator": name,
        "result": result_label,
        "blocks_sprint": (not passed) and blocks,
        "items": items,
        "summary": f"{vid}: {'OK' if passed else str(len(items)) + ' issue(s)'}",
    }


# ---------------------------------------------------------------------------
# V134: No manual JSON escaping in .NET source files
# ---------------------------------------------------------------------------

# Matches a .Replace("\\", ...) chain followed by a .Replace("\"", ...) chain
# — the exact pattern used by the defective _JsonEsc method.
#
# In a .cs file, the Replace-chain for manual JSON escaping looks like:
#   .Replace("\\", "\\\\").Replace("\"", "\\\"")
# As plain text in the file: .Replace("\\", "\\\\").Replace("\"", "\\\"")
# Where "\\" in the file is two literal backslash characters.
#
# Regex breakdown:
#   r'"\\\\"'  — matches "\\": ", then two literal backslashes, then "
#   r'"\\""'   — matches "\"": ", then one literal backslash, then ", then "
_MANUAL_JSON_ESC_PATTERN = re.compile(
    r'\.Replace\s*\(\s*"\\\\"'         # .Replace("\\", ...) — escaping backslash
    r'.*?'
    r'\.Replace\s*\(\s*"\\""',         # .Replace("\"", ...) — escaping double-quote
    re.DOTALL,
)

_SYSTEM_TEXT_JSON_IMPORTS = (
    "System.Text.Json",
    "using System.Text.Json",
    "JsonSerializer",
    "JsonDocument",
)


def validate_no_manual_json_escaping_in_dotnet(
    declaration: dict, repo_root: Path | None = None
) -> dict:
    """
    V134: .NET source files must not use manual string Replace chains to escape JSON output.
    All JSON serialization must go through System.Text.Json (JsonSerializer / JsonDocument).

    Detects the pattern: .Replace("\\\\", ...).Replace("\\\"", ...) without a
    System.Text.Json import. This is the exact defect pattern from CsvDocumentAnalytics.cs
    _JsonEsc (GAP-CSV-008).

    blocks_sprint: False (WARN-only during initial deployment).
    """
    _root = repo_root or Path(".")
    changed_files = declaration.get("changed_files", [])
    failures = []

    for rel_path in changed_files:
        if not str(rel_path).endswith(".cs"):
            continue
        norm = str(rel_path).replace("\\", "/")
        if "src/net/" not in norm:
            continue
        try:
            cf_path = _root / rel_path if not Path(str(rel_path)).is_absolute() else Path(str(rel_path))
            content = cf_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        if _MANUAL_JSON_ESC_PATTERN.search(content):
            has_stdlib = any(marker in content for marker in _SYSTEM_TEXT_JSON_IMPORTS)
            if not has_stdlib:
                failures.append(
                    f"{rel_path}: manual JSON escaping Replace chain without System.Text.Json import"
                )

    return _result("V134", "validate_no_manual_json_escaping_in_dotnet",
                   passed=len(failures) == 0, items=failures, blocks=False)


# ---------------------------------------------------------------------------
# V135: HTML cell content must be escaped in .NET source files
# ---------------------------------------------------------------------------

# Matches interpolated <td> or <th> where the variable is NOT wrapped in an escaping call.
# Escaping calls recognized: _HtmlEsc(...), HtmlEncode(...), EscapeHtml(...)
_RAW_TD_INTERPOLATION_DOTNET = re.compile(
    r'<t[dh]>\{(?!_HtmlEsc|HtmlEncode|EscapeHtml|WebUtility)'
)


def validate_html_escaping_in_dotnet(
    declaration: dict, repo_root: Path | None = None
) -> dict:
    """
    V135: .NET source files that produce <td>/<th> HTML must escape cell values.
    Acceptable escape methods: _HtmlEsc(), WebUtility.HtmlEncode(), HtmlWriter.EscapeHtml().

    Detects: C# string interpolation f"<td>{variable}</td>" where variable is not wrapped
    in an escaping call. This is the exact defect pattern from CsvDocumentAnalytics.cs
    ToHtml() (GAP-CSV-009).

    blocks_sprint: False (WARN-only during initial deployment).
    """
    _root = repo_root or Path(".")
    changed_files = declaration.get("changed_files", [])
    failures = []

    for rel_path in changed_files:
        if not str(rel_path).endswith(".cs"):
            continue
        norm = str(rel_path).replace("\\", "/")
        if "src/net/" not in norm:
            continue
        try:
            cf_path = _root / rel_path if not Path(str(rel_path)).is_absolute() else Path(str(rel_path))
            content = cf_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        if _RAW_TD_INTERPOLATION_DOTNET.search(content):
            failures.append(
                f"{rel_path}: HTML <td>/<th> interpolation without escaping call "
                f"(_HtmlEsc / HtmlEncode / EscapeHtml)"
            )

    return _result("V135", "validate_html_escaping_in_dotnet",
                   passed=len(failures) == 0, items=failures, blocks=False)


# ---------------------------------------------------------------------------
# V136: HTML cell content must be escaped in Python source files
# ---------------------------------------------------------------------------

# Matches Python f-string with <td> or <th> where the variable is NOT wrapped in
# html.escape() or .translate() call.
_RAW_TD_INTERPOLATION_PYTHON = re.compile(
    r'f["\']<t[dh]>\{(?!html\.escape|\.translate)'
)


def validate_html_escaping_in_python(
    declaration: dict, repo_root: Path | None = None
) -> dict:
    """
    V136: Python source files that produce <td>/<th> HTML must escape cell values.
    Acceptable escape methods: html.escape(), str.translate(str.maketrans(...)).

    Detects: Python f-string f"<td>{variable}</td>" where variable is not wrapped
    in html.escape() or str.translate(). Confirms existing Python baseline is safe;
    blocks future regressions.

    blocks_sprint: False (WARN-only — confirms baseline; no known current violations).
    """
    _root = repo_root or Path(".")
    changed_files = declaration.get("changed_files", [])
    failures = []

    for rel_path in changed_files:
        if not str(rel_path).endswith(".py"):
            continue
        norm = str(rel_path).replace("\\", "/")
        if "src/python/" not in norm:
            continue
        try:
            cf_path = _root / rel_path if not Path(str(rel_path)).is_absolute() else Path(str(rel_path))
            content = cf_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        if _RAW_TD_INTERPOLATION_PYTHON.search(content):
            failures.append(
                f"{rel_path}: Python HTML <td>/<th> f-string interpolation without "
                f"html.escape() or .translate() escaping"
            )

    return _result("V136", "validate_html_escaping_in_python",
                   passed=len(failures) == 0, items=failures, blocks=False)
