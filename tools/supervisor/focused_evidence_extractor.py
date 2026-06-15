"""SUP-RECT-006: Focused evidence extractor — executable implementation.

Extracts focused evidence snippets from source files to prevent LLM grader
truncation false positives. When a function is defined beyond line 200,
the LLM grader may not see it. This module extracts the function signature
and first N lines into a focused snippet that is placed BEFORE the full
source in evidence paths.

Also provides a deterministic fallback: if the LLM says a function is missing
but grep/AST evidence proves it exists, the verdict is overridden.

Usage:
    python tools/supervisor/focused_evidence_extractor.py \
        --source src/python/fodp/fodp_codec.py \
        --function fodp_slide_notes \
        --output .local/evidences/<run_id>/focused-evidence-fodp_slide_notes.md
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path


def extract_function_snippet(source_path: Path, function_name: str,
                             max_lines: int = 40) -> dict | None:
    """Extract a focused snippet for a function from a source file.

    Returns dict with line_number, signature, snippet, and test_hints,
    or None if the function is not found.
    """
    if not source_path.is_file():
        return None

    source_text = source_path.read_text(encoding="utf-8")
    lines = source_text.splitlines()

    # Try AST-based extraction first
    result = _extract_via_ast(source_text, function_name, lines, max_lines)
    if result:
        result["source_path"] = str(source_path)
        result["extraction_method"] = "AST"
        return result

    # Fallback to regex-based extraction
    result = _extract_via_regex(lines, function_name, max_lines)
    if result:
        result["source_path"] = str(source_path)
        result["extraction_method"] = "REGEX"
        return result

    return None


def _extract_via_ast(source_text: str, function_name: str,
                     lines: list[str], max_lines: int) -> dict | None:
    """Extract function using Python AST."""
    try:
        tree = ast.parse(source_text)
    except SyntaxError:
        return None

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == function_name:
                start_line = node.lineno  # 1-based
                end_line = node.end_lineno or (start_line + max_lines)
                snippet_end = min(start_line + max_lines - 1, end_line)
                snippet_lines = lines[start_line - 1:snippet_end]

                # Get signature
                sig_line = lines[start_line - 1].strip()

                # Get docstring if present
                docstring = ast.get_docstring(node) or ""

                return {
                    "function_name": function_name,
                    "line_number": start_line,
                    "end_line": end_line,
                    "total_lines": end_line - start_line + 1,
                    "signature": sig_line,
                    "docstring": docstring[:200],
                    "snippet": "\n".join(snippet_lines),
                    "snippet_lines": len(snippet_lines),
                    "beyond_line_200": start_line > 200,
                }
    return None


def _extract_via_regex(lines: list[str], function_name: str,
                       max_lines: int) -> dict | None:
    """Extract function using regex pattern matching."""
    pattern = re.compile(rf"^\s*def\s+{re.escape(function_name)}\s*\(")
    for i, line in enumerate(lines):
        if pattern.match(line):
            start_line = i + 1  # 1-based
            snippet_end = min(i + max_lines, len(lines))
            snippet_lines = lines[i:snippet_end]
            return {
                "function_name": function_name,
                "line_number": start_line,
                "end_line": start_line + max_lines - 1,
                "total_lines": max_lines,
                "signature": line.strip(),
                "docstring": "",
                "snippet": "\n".join(snippet_lines),
                "snippet_lines": len(snippet_lines),
                "beyond_line_200": start_line > 200,
            }
    return None


def generate_focused_evidence_file(extraction: dict, output_path: Path,
                                   test_file: Path | None = None) -> Path:
    """Generate a focused evidence markdown file from extraction result."""
    lines = [
        f"# Focused Evidence: {extraction['function_name']}",
        "",
        f"**Source:** `{extraction['source_path']}`",
        f"**Line:** {extraction['line_number']}",
        f"**Extraction method:** {extraction['extraction_method']}",
        f"**Beyond line 200:** {extraction['beyond_line_200']}",
        "",
        "## Signature",
        "```python",
        extraction["signature"],
        "```",
        "",
    ]

    if extraction.get("docstring"):
        lines.extend([
            "## Docstring",
            f"> {extraction['docstring']}",
            "",
        ])

    lines.extend([
        "## Implementation Snippet",
        "```python",
        extraction["snippet"],
        "```",
        "",
    ])

    if test_file and test_file.is_file():
        test_content = test_file.read_text(encoding="utf-8")
        # Extract just the test function names
        test_fns = re.findall(r"def (test_\w+)", test_content)
        lines.extend([
            "## Test Coverage",
            f"**Test file:** `{test_file}`",
            f"**Test count:** {len(test_fns)}",
            "",
        ])
        for fn in test_fns[:10]:
            lines.append(f"- `{fn}`")
        lines.append("")

    lines.extend([
        "## Deterministic Verification",
        f"- Function `{extraction['function_name']}` EXISTS at line {extraction['line_number']}",
        f"- Total function length: {extraction['total_lines']} lines",
        f"- Extraction method: {extraction['extraction_method']} (machine-verified)",
        "",
    ])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def deterministic_function_exists(source_path: Path,
                                  function_name: str) -> dict:
    """Deterministic check: does function_name exist in source_path?

    This is the fallback when LLM grader claims a function is missing.
    Uses AST parsing first, then regex, then raw grep.
    """
    if not source_path.is_file():
        return {
            "exists": False,
            "method": "file_not_found",
            "source_path": str(source_path),
            "function_name": function_name,
        }

    source_text = source_path.read_text(encoding="utf-8")

    # Method 1: AST
    try:
        tree = ast.parse(source_text)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == function_name:
                    return {
                        "exists": True,
                        "method": "AST",
                        "line_number": node.lineno,
                        "source_path": str(source_path),
                        "function_name": function_name,
                    }
    except SyntaxError:
        pass

    # Method 2: Regex
    pattern = re.compile(rf"^\s*def\s+{re.escape(function_name)}\s*\(", re.MULTILINE)
    match = pattern.search(source_text)
    if match:
        line_num = source_text[:match.start()].count("\n") + 1
        return {
            "exists": True,
            "method": "REGEX",
            "line_number": line_num,
            "source_path": str(source_path),
            "function_name": function_name,
        }

    return {
        "exists": False,
        "method": "not_found",
        "source_path": str(source_path),
        "function_name": function_name,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract focused evidence snippet")
    parser.add_argument("--source", required=True, help="Source file path")
    parser.add_argument("--function", required=True, help="Function name")
    parser.add_argument("--output", required=True, help="Output file path")
    parser.add_argument("--test-file", help="Optional test file for coverage info")
    parser.add_argument("--max-lines", type=int, default=40)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    source = Path(args.source)
    extraction = extract_function_snippet(source, args.function, args.max_lines)

    if not extraction:
        print(f"Function {args.function} not found in {source}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(extraction, indent=2))
    else:
        test_file = Path(args.test_file) if args.test_file else None
        output = Path(args.output)
        generate_focused_evidence_file(extraction, output, test_file)
        print(f"Generated: {output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
