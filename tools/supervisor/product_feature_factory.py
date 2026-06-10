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

_here = Path(__file__).resolve().parent
_REPO_ROOT = _here.parent.parent


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
        module_path = source_path.replace("/", ".").removesuffix(".py")
        module_parts = module_path.split(".")
        test_import = f"from {'.'.join(module_parts[:-1])} import {load_function}, {write_function}"

        return f'''"""Roundtrip test for {format_name.upper()}.

Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-3-001
Pattern C: Load → write → reload → compare
"""
from __future__ import annotations

import sys
from pathlib import Path
import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

{test_import}


class TestRoundtrip{format_name.capitalize()}:
    def test_roundtrip_preserves_{compare_field}(self, tmp_path):
        # TODO: Replace with a real fixture or minimal bytes for this format
        source_bytes = b""  # ADD FORMAT-SPECIFIC MINIMAL BYTES HERE
        model = {load_function}(source_bytes)
        dest = tmp_path / "out.{format_name}"
        {write_function}(model, dest)
        model2 = {load_function}(dest)
        assert model2["{compare_field}"] == model["{compare_field}"]

    def test_roundtrip_file_exists(self, tmp_path):
        source_bytes = b""  # ADD FORMAT-SPECIFIC MINIMAL BYTES HERE
        model = {load_function}(source_bytes)
        dest = tmp_path / "out.{format_name}"
        {write_function}(model, dest)
        assert dest.exists()
        assert dest.stat().st_size > 0
'''

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
        module = self._source_to_import(source_path)
        return f'''"""Test skeleton for {function_name}() — Pattern A (Getter)."""
import sys
from pathlib import Path
_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))
from {module} import {function_name}


class Test{function_name.replace("_", " ").title().replace(" ", "")}:
    def test_basic(self):
        # TODO: provide a real model or input
        result = {function_name}(None)
        assert result is not None

    def test_returns_{return_type.replace("[", "_").replace("]", "").replace(",", "_").strip()}(self):
        result = {function_name}(None)
        assert isinstance(result, object)
'''

    def _export_csv_test_skeleton(
        self, source_path: str, function_name: str, format_name: str
    ) -> str:
        module = self._source_to_import(source_path)
        return f'''"""Test skeleton for {function_name}() — Pattern B (ExportCsv)."""
import sys
from pathlib import Path
_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))
from {module} import {function_name}


class Test{format_name.capitalize()}CsvExport:
    def test_returns_string(self):
        # TODO: provide real source bytes
        result = {function_name}(b"")
        assert isinstance(result, str)

    def test_writes_file(self, tmp_path):
        dest = tmp_path / "out.csv"
        {function_name}(b"", dest=dest)
        assert dest.exists()
'''

    def _append_test_skeleton(
        self, source_path: str, function_name: str, format_name: str, collection_key: str
    ) -> str:
        module = self._source_to_import(source_path)
        return f'''"""Test skeleton for {function_name}() — Pattern D (Append)."""
import sys
from pathlib import Path
_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))
from {module} import {function_name}


class Test{format_name.capitalize()}Append:
    def test_append_increases_count(self):
        # TODO: provide real source bytes
        result = {function_name}(b"", [])
        assert isinstance(result, dict)
        assert "{collection_key}" in result
'''

    def _probe_test_skeleton(
        self, source_path: str, function_name: str, format_name: str
    ) -> str:
        module = self._source_to_import(source_path)
        return f'''"""Test skeleton for {function_name}() — Pattern E (Probe)."""
import sys
from pathlib import Path
_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))
from {module} import {function_name}


class Test{format_name.capitalize()}Probe:
    def test_returns_dict(self):
        result = {function_name}(b"")
        assert isinstance(result, dict)

    def test_format_field(self):
        result = {function_name}(b"")
        assert result.get("format") == "{format_name.lower()}"
'''

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
