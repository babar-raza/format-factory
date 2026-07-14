"""
product_feature_factory.py — Product Feature Code-Generation Patterns
Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-3-001

Provides 6 repeatable patterns for adding Python FOSS functions to Format Factory codecs:
  Pattern A: Getter         — get_X(model, ...) -> T
  Pattern B: ExportCsv      — export_to_csv(source, dest=None) -> str
  Pattern C: Roundtrip      — test_roundtrip_<format>() — test skeleton only
  Pattern D: Append         — append_row/append_record(source, row) -> bytes
  Pattern E: Probe          — probe_<format>(source) -> dict
  Pattern F: PackageProof   — package import proof command

Each apply_* method:
  1. Reads the target source file
  2. Identifies the insertion point (before first def or end of file)
  3. Generates the function body
  4. Writes the modified source
  5. Generates and returns a test skeleton string

Does NOT execute pytest — caller must run tests separately.
Does NOT modify test files — returns test skeleton as string for caller review.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Optional

# Ensure repo root is on sys.path so `tools.supervisor.*` absolute imports work
# when this file is run as a script (python tools/supervisor/product_feature_factory.py)
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.supervisor.test_drivers import (
    render_getter_test,
    render_export_csv_test,
    render_roundtrip_test,
    render_append_test,
    render_probe_test,
    is_maintained_test,
)
from tools.supervisor.drivers_promotion import (
    create_promotion_task,
    write_promotion_task,
)

_PROMOTION_TASKS_DEFAULT_DIR = _REPO_ROOT / ".local" / "supervisor" / "promotion-tasks"


class FeatureFactoryError(Exception):
    """Raised when a pattern cannot be applied."""


class FeatureFactory:
    """Generate and insert Python FOSS product functions using repeatable patterns.

    Usage:
        factory = FeatureFactory()
        test_skeleton = factory.apply_getter(
            source_path="src/python/abw/abw_codec.py",
            function_name="get_page_count",
            return_type="int",
            docstring="Return total paragraph count.",
            body_lines=["    paragraphs = model.get('paragraphs', [])", "    return len(paragraphs)"],
        )
    """

    def __init__(self, repo_root: Optional[Path] = None) -> None:
        self.repo_root = Path(repo_root) if repo_root else _REPO_ROOT

    # ------------------------------------------------------------------
    # Pattern A: Getter
    # ------------------------------------------------------------------

    def apply_getter(
        self,
        source_path: str,
        function_name: str,
        return_type: str,
        docstring: str,
        body_lines: list[str],
        params: str = "model: dict",
        *,
        insert_before: Optional[str] = None,
    ) -> str:
        """Pattern A: Add a getter function that reads from a model dict.

        Args:
            source_path:    Relative path to source file.
            function_name:  Name for the new function.
            return_type:    Return type annotation string (e.g. 'int', 'list[str]').
            docstring:      One-line docstring.
            body_lines:     List of body lines (already indented with 4 spaces).
            params:         Parameter list string (default: 'model: dict').
            insert_before:  Optional anchor function name to insert before.

        Returns:
            Test skeleton string (not written to disk).
        """
        sig = f"def {function_name}({params}) -> {return_type}:"
        lines = [
            f"\n\n{sig}",
            f'    """{docstring}"""',
        ] + body_lines

        code_block = "\n".join(lines) + "\n"
        self._insert_into_source(source_path, code_block, insert_before=insert_before)

        return self._getter_test_skeleton(source_path, function_name, params, return_type)

    # ------------------------------------------------------------------
    # Pattern B: Export to CSV
    # ------------------------------------------------------------------

    def apply_export_csv(
        self,
        source_path: str,
        function_name: str,
        format_name: str,
        load_function: str,
        rows_expression: str,
        headers_expression: str,
        *,
        insert_before: Optional[str] = None,
    ) -> str:
        """Pattern B: Add an export_to_csv function.

        Args:
            source_path:        Relative path to source file.
            function_name:      Name for the new function (e.g. 'export_to_csv').
            format_name:        Human-readable format name (for docstring).
            load_function:      Name of the load function in the same module.
            rows_expression:    Python expression for rows given model (e.g. "model['rows']").
            headers_expression: Python expression for headers given model.
            insert_before:      Optional anchor function name.

        Returns:
            Test skeleton string.
        """
        code_block = f"""

def {function_name}(source, dest=None) -> str:
    \"\"\"{format_name}: Export content to CSV string or file.\"\"\"
    import io as _io
    model = {load_function}(source)
    rows = {rows_expression}
    headers = {headers_expression}
    out = _io.StringIO()
    if headers:
        out.write("\\t".join(str(h) for h in headers) + "\\n")
    for row in rows:
        out.write("\\t".join(str(c) for c in row) + "\\n")
    result = out.getvalue()
    if dest is not None:
        import pathlib as _pl
        _pl.Path(dest).write_text(result, encoding="utf-8")
    return result
"""
        self._insert_into_source(source_path, code_block, insert_before=insert_before)
        return self._export_csv_test_skeleton(source_path, function_name, format_name)

    # ------------------------------------------------------------------
    # Pattern C: Roundtrip test skeleton
    # ------------------------------------------------------------------

    def generate_roundtrip_test(
        self,
        format_name: str,
        source_path: str,
        load_function: str,
        write_function: str,
        compare_field: str,
        test_run_number: int = 135,
    ) -> str:
        """Pattern C: Generate a roundtrip test skeleton (does NOT write to source).

        Returns:
            Test file content as string.
        """
        return render_roundtrip_test(
            format_name, source_path, load_function, write_function, compare_field
        )

    # ------------------------------------------------------------------
    # Pattern D: Append / Mutation
    # ------------------------------------------------------------------

    def apply_append(
        self,
        source_path: str,
        function_name: str,
        format_name: str,
        load_function: str,
        collection_key: str,
        *,
        item_type: str = "list",
        insert_before: Optional[str] = None,
    ) -> str:
        """Pattern D: Add an append_X function that mutates a collection in the model.

        Args:
            source_path:    Relative source path.
            function_name:  New function name (e.g. 'append_row').
            format_name:    Human-readable format name.
            load_function:  Load function in same module.
            collection_key: Key in model dict to append to (e.g. 'rows').
            item_type:      Type annotation for the item parameter.
            insert_before:  Optional anchor.

        Returns:
            Test skeleton string.
        """
        code_block = f"""

def {function_name}(source, item: {item_type}) -> dict:
    \"\"\"{format_name}: Append item to {collection_key} and return updated model.\"\"\"
    model = {load_function}(source)
    import copy as _copy
    model = _copy.deepcopy(model)
    model["{collection_key}"] = model.get("{collection_key}", []) + [item]
    return model
"""
        self._insert_into_source(source_path, code_block, insert_before=insert_before)
        return self._append_test_skeleton(source_path, function_name, format_name, collection_key)

    # ------------------------------------------------------------------
    # Pattern E: Probe / Metadata
    # ------------------------------------------------------------------

    def apply_probe(
        self,
        source_path: str,
        function_name: str,
        format_name: str,
        metadata_fields: list[tuple[str, str]],
        *,
        insert_before: Optional[str] = None,
    ) -> str:
        """Pattern E: Add a probe function returning format metadata.

        Args:
            source_path:      Relative source path.
            function_name:    New function name (e.g. 'probe_tsv').
            format_name:      Human-readable format name.
            metadata_fields:  List of (field_name, expression) pairs.
            insert_before:    Optional anchor.

        Returns:
            Test skeleton string.
        """
        field_lines = []
        for name, expr in metadata_fields:
            field_lines.append(f'        "{name}": {expr},')

        fields_str = "\n".join(field_lines)
        code_block = f"""

def {function_name}(source) -> dict:
    \"\"\"{format_name}: Return format metadata without full parse.\"\"\"
    try:
        raw = _read_source(source) if callable(globals().get("_read_source")) else b""
        return {{
            "format": "{format_name.lower()}",
{fields_str}
            "valid": True,
        }}
    except Exception as exc:
        return {{"format": "{format_name.lower()}", "valid": False, "error": str(exc)}}
"""
        self._insert_into_source(source_path, code_block, insert_before=insert_before)
        return self._probe_test_skeleton(source_path, function_name, format_name)

    # ------------------------------------------------------------------
    # Pattern F: Package Import Proof command
    # ------------------------------------------------------------------

    def generate_and_write_scaffold(
        self,
        format_id: str,
        pattern_id: str,
        function_name: str,
        module: str,
        *,
        format_cap: str = "",
        format_lower: str = "",
        scaffold_dir: Optional[Path] = None,
        promotion_tasks_dir: Optional[Path] = None,
        source_path: Optional[str] = None,
        params: str = "model: dict",
        return_type: str = "Any",
        collection_key: str = "records",
        metadata_fields: Optional[list] = None,
    ) -> dict:
        """Render a test scaffold, write it to disk, create and write a promotion task.

        Args:
            format_id:           Format identifier (e.g. 'ndjson', 'abw').
            pattern_id:          One of: getter, export_csv, roundtrip, append, probe.
            function_name:       Name of the function being tested.
            module:              Module path for imports (e.g. 'ndjson').
            format_cap:          Capitalized format name (e.g. 'Ndjson'). Defaults to format_id.title().
            format_lower:        Lowercase format name. Defaults to format_id.lower().
            scaffold_dir:        Directory for scaffold file. Defaults to
                                 tests/python/{format_id}/_scaffolds/.
            promotion_tasks_dir: Directory for promotion task YAML. Defaults to
                                 .local/supervisor/promotion-tasks/.
            source_path:         Source file path (e.g. src/python/ndjson/ndjson_codec.py).
                                 Defaults to src/python/{format_id}/{format_id}_codec.py.
            params:              Parameter list for getter pattern.
            return_type:         Return type annotation for getter pattern.
            collection_key:      Collection key for append pattern.
            metadata_fields:     Metadata fields for probe pattern.

        Returns:
            dict with keys: scaffold_path, promotion_task_path, task_id, status,
            incomplete_markers.

        Raises:
            ValueError: If pattern_id is not one of the allowed values.
            FeatureFactoryError: If rendering or file write fails.
        """
        allowed_patterns = ("getter", "export_csv", "roundtrip", "append", "probe")
        if pattern_id not in allowed_patterns:
            raise ValueError(
                f"pattern_id {pattern_id!r} not in {allowed_patterns}"
            )

        fmt_cap = format_cap or format_id.title()
        fmt_low = format_lower or format_id.lower()
        src_path = source_path or f"src/python/{format_id}/{format_id}_codec.py"

        if pattern_id == "getter":
            rendered = render_getter_test(src_path, function_name, params, return_type)
        elif pattern_id == "export_csv":
            rendered = render_export_csv_test(src_path, function_name, fmt_cap)
        elif pattern_id == "roundtrip":
            rendered = render_roundtrip_test(src_path, fmt_cap)
        elif pattern_id == "append":
            rendered = render_append_test(src_path, function_name, fmt_cap, collection_key)
        elif pattern_id == "probe":
            fields = metadata_fields or [
                ("format", f'"{fmt_low}"'),
                ("valid", "True"),
            ]
            rendered = render_probe_test(src_path, function_name, fmt_cap)
        else:
            raise ValueError(f"Unhandled pattern_id: {pattern_id!r}")

        s_dir = Path(scaffold_dir) if scaffold_dir else (
            self.repo_root / "tests" / "python" / format_id / "_scaffolds"
        )
        p_dir = Path(promotion_tasks_dir) if promotion_tasks_dir else _PROMOTION_TASKS_DEFAULT_DIR
        s_dir.mkdir(parents=True, exist_ok=True)
        p_dir.mkdir(parents=True, exist_ok=True)

        scaffold_path = s_dir / f"test_{function_name}_scaffold.py"
        scaffold_path.write_text(rendered, encoding="utf-8")

        task = create_promotion_task(
            rendered_code=rendered,
            format_id=format_id,
            pattern_id=pattern_id,
            template_id=f"{pattern_id}_template",
            renderer_id=f"render_{pattern_id}_test",
            generated_path=str(scaffold_path),
            target_path=str(self.repo_root / "tests" / "python" / format_id / f"test_{function_name}.py"),
        )
        task_path = write_promotion_task(task, p_dir)

        return {
            "scaffold_path": str(scaffold_path),
            "promotion_task_path": str(task_path),
            "task_id": task.task_id,
            "status": task.status,
            "incomplete_markers": task.incomplete_markers,
        }

    def generate_package_proof_command(self, package_name: str, version_attr: str = "__version__") -> str:
        """Pattern F: Return a shell command that proves a package can be imported.

        Args:
            package_name:   Python package name (e.g. 'zstandard').
            version_attr:   Attribute to read for version proof.

        Returns:
            Shell command string.
        """
        return (
            f'python -c "import {package_name}; '
            f'print(getattr({package_name}, \\"{version_attr}\\", \\"ok\\"))"'
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _read_source(self, source_path: str) -> str:
        abs_path = self.repo_root / source_path
        if not abs_path.exists():
            raise FeatureFactoryError(f"Source file not found: {source_path}")
        return abs_path.read_text(encoding="utf-8")

    def _write_source(self, source_path: str, content: str) -> None:
        abs_path = self.repo_root / source_path
        abs_path.write_text(content, encoding="utf-8")

    def _find_insertion_point(self, content: str, insert_before: Optional[str]) -> int:
        """Find the character index for inserting a new function.

        If insert_before is given, insert just before that def.
        Otherwise insert at the end of the file.
        """
        if insert_before:
            pattern = re.compile(rf"^def {re.escape(insert_before)}\b", re.MULTILINE)
            match = pattern.search(content)
            if match:
                return match.start()

        return len(content)

    def _insert_into_source(
        self, source_path: str, code_block: str, insert_before: Optional[str] = None
    ) -> None:
        """Read source, insert code_block at insertion point, write back."""
        content = self._read_source(source_path)
        idx = self._find_insertion_point(content, insert_before)
        new_content = content[:idx] + code_block + content[idx:]
        self._write_source(source_path, new_content)

    # ------------------------------------------------------------------
    # Test skeleton generators
    # ------------------------------------------------------------------

    def _getter_test_skeleton(
        self, source_path: str, function_name: str, params: str, return_type: str
    ) -> str:
        return render_getter_test(source_path, function_name, params, return_type)

    def _export_csv_test_skeleton(
        self, source_path: str, function_name: str, format_name: str
    ) -> str:
        return render_export_csv_test(source_path, function_name, format_name)

    def _append_test_skeleton(
        self, source_path: str, function_name: str, format_name: str, collection_key: str
    ) -> str:
        return render_append_test(source_path, function_name, format_name, collection_key)

    def _probe_test_skeleton(
        self, source_path: str, function_name: str, format_name: str
    ) -> str:
        return render_probe_test(source_path, function_name, format_name)

    def _source_to_import(self, source_path: str) -> str:
        """Convert 'src/python/abw/abw_codec.py' -> 'abw.abw_codec'."""
        parts = Path(source_path).parts
        # Find index after 'python'
        try:
            idx = list(parts).index("python")
            module_parts = list(parts[idx + 1:])
        except ValueError:
            module_parts = list(Path(source_path).parts)
        # Remove .py from last part
        if module_parts:
            module_parts[-1] = module_parts[-1].removesuffix(".py")
        return ".".join(module_parts)


# ---------------------------------------------------------------------------
# CLI entry point (TC-EXPAND-001c)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    _PATTERNS = ("getter", "export_csv", "roundtrip_test", "append", "probe", "package_proof")

    parser = argparse.ArgumentParser(
        description="product_feature_factory — generate Python FOSS product functions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="\n".join([
            "Patterns:",
            "  getter         — get_X(model, ...) -> T",
            "  export_csv     — export_to_csv(source, dest=None) -> str",
            "  roundtrip_test — test_roundtrip_<format>() skeleton",
            "  append         — append_row/record(source, row) -> bytes",
            "  probe          — probe_<format>(source) -> dict",
            "  package_proof  — package import proof command",
            "",
            "Use --generate-scaffold to write scaffold+promotion-task to disk:",
            "  python tools/supervisor/product_feature_factory.py \\",
            "    --generate-scaffold --format-id ndjson --pattern-id probe \\",
            "    --function-name probe_ndjson --module ndjson",
        ]),
    )
    parser.add_argument("--pattern", default=None, choices=_PATTERNS,
                        help="Which code-generation pattern to apply (source edit mode)")
    parser.add_argument("--generate-scaffold", action="store_true",
                        help="Write scaffold and promotion task to disk (no source edit)")
    parser.add_argument("--pattern-id", default=None,
                        choices=("getter", "export_csv", "roundtrip", "append", "probe"),
                        help="Pattern for --generate-scaffold mode")
    parser.add_argument("--source-path", default=None,
                        help="Target source file (e.g. src/python/abw/abw_codec.py)")
    parser.add_argument("--function-name", default=None,
                        help="Name of the function to generate")
    parser.add_argument("--module", default=None,
                        help="Module name for --generate-scaffold (e.g. ndjson)")
    parser.add_argument("--format-id", default=None,
                        help="Format identifier (e.g. 'abw', 'ndjson'); inferred from source-path if omitted")
    args = parser.parse_args()

    factory = FeatureFactory()

    if args.generate_scaffold:
        if not args.pattern_id or not args.function_name:
            parser.error("--generate-scaffold requires --pattern-id and --function-name")
        fmt = args.format_id or (
            Path(args.source_path).parts[-2] if args.source_path and len(Path(args.source_path).parts) >= 2 else "unknown"
        )
        result = factory.generate_and_write_scaffold(
            format_id=fmt,
            pattern_id=args.pattern_id,
            function_name=args.function_name,
            module=args.module or fmt,
        )
        print(f"SCAFFOLD_WRITTEN: {result['scaffold_path']}")
        print(f"PROMOTION_TASK: {result['promotion_task_path']}")
        print(f"TASK_ID: {result['task_id']}")
        print(f"STATUS: {result['status']}")
        raise SystemExit(0)

    if not args.pattern:
        parser.error("--pattern is required unless --generate-scaffold is used")
    if not args.source_path or not args.function_name:
        parser.error("--source-path and --function-name are required for --pattern mode")

    fmt = args.format_id or Path(args.source_path).parts[-2] if len(Path(args.source_path).parts) >= 2 else "unknown"

    try:
        if args.pattern == "getter":
            skeleton = factory.apply_getter(
                source_path=args.source_path,
                function_name=args.function_name,
                return_type="Any",
                docstring=f"Return {args.function_name.replace('_', ' ')} value.",
                body_lines=[f'    return model.get("{args.function_name}", None)'],
            )
        elif args.pattern == "export_csv":
            skeleton = factory.apply_export_csv(
                source_path=args.source_path,
                function_name=args.function_name,
                format_name=fmt,
            )
        elif args.pattern == "roundtrip_test":
            skeleton = factory.apply_roundtrip_test(
                source_path=args.source_path,
                format_name=fmt,
            )
        elif args.pattern == "append":
            skeleton = factory.apply_append(
                source_path=args.source_path,
                function_name=args.function_name,
                format_name=fmt,
                collection_key="records",
            )
        elif args.pattern == "probe":
            skeleton = factory.apply_probe(
                source_path=args.source_path,
                function_name=args.function_name,
                format_name=fmt,
                metadata_fields=[("file_size", "Path(source).stat().st_size"), ("format", f'"{fmt}"')],
            )
        elif args.pattern == "package_proof":
            skeleton = factory.apply_package_proof(
                source_path=args.source_path,
                format_name=fmt,
            )
        else:
            raise SystemExit(f"Unknown pattern: {args.pattern}")

        print(f"PATTERN_APPLIED: {args.pattern} -> {args.source_path}")
        print("--- test skeleton ---")
        print(skeleton)
    except FeatureFactoryError as exc:
        print(f"ERROR: {exc}", file=__import__("sys").stderr)
        raise SystemExit(1)
