"""Tests for generate_canonical_stubs.py (Step 0.6).

Verifies:
- Idempotency: run twice → identical file contents
- __init__.py created in all spec/ subdirectories
- No overwrite of files with status > seeded
- Generated file has spec_qname attribute
- python_file: null entries are skipped (no Python file created)
- dotnet_file generates .NET static class with QName constant
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).parent.parent.parent
_TOOLS_SPEC = _REPO / "tools" / "spec"
if str(_TOOLS_SPEC) not in sys.path:
    sys.path.insert(0, str(_TOOLS_SPEC))

from generate_canonical_stubs import generate_stubs  # noqa: E402


def _make_registry(tmp_path: Path, entries: list[dict]) -> Path:
    """Write a minimal YAML registry file and return repo root."""
    registry_dir = tmp_path / "shared" / "qname-registry"
    registry_dir.mkdir(parents=True)
    lines = []
    for e in entries:
        first = True
        for k, v in e.items():
            prefix = "- " if first else "  "
            first = False
            if v is None:
                lines.append(f"{prefix}{k}: null")
            else:
                lines.append(f'{prefix}{k}: "{v}"')
    (registry_dir / "fodt.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return tmp_path


class TestIdempotency:
    def test_run_twice_produces_identical_output(self, tmp_path):
        """Running generate_stubs twice must produce identical file contents."""
        entry = {
            "qname": "text:p",
            "namespace_uri": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
            "local_name": "p",
            "canonical_class": "Text.Paragraph",
            "spec_fact_ref": "FACT-FODT-003",
            "status": "seeded",
            "source_layer": "Spec",
            "python_file": "src/python/fodt/spec/text/paragraph.py",
            "dotnet_file": None,
        }
        _make_registry(tmp_path, [entry])

        generate_stubs("fodt", tmp_path, dry_run=False, verbose=False)
        py_path = tmp_path / "src/python/fodt/spec/text/paragraph.py"
        first_content = py_path.read_text(encoding="utf-8")

        generate_stubs("fodt", tmp_path, dry_run=False, verbose=False)
        second_content = py_path.read_text(encoding="utf-8")

        assert first_content == second_content, "File contents differ between runs (not idempotent)"

    def test_dotnet_idempotent(self, tmp_path):
        """Running generate_stubs twice for .NET must produce identical file contents."""
        entry = {
            "qname": "office:body",
            "namespace_uri": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
            "local_name": "body",
            "canonical_class": "Office.Body",
            "spec_fact_ref": "FACT-FODT-002",
            "status": "seeded",
            "source_layer": "Spec",
            "python_file": None,
            "dotnet_file": "src/net/fodt/Spec/Office/Body.cs",
        }
        _make_registry(tmp_path, [entry])

        generate_stubs("fodt", tmp_path, dry_run=False, verbose=False)
        cs_path = tmp_path / "src/net/fodt/Spec/Office/Body.cs"
        first_content = cs_path.read_text(encoding="utf-8")

        generate_stubs("fodt", tmp_path, dry_run=False, verbose=False)
        second_content = cs_path.read_text(encoding="utf-8")

        assert first_content == second_content


class TestInitFilesCreated:
    def test_init_files_created_in_spec_subdirs(self, tmp_path):
        """__init__.py must be created in spec/ and all subdirectories."""
        entry = {
            "qname": "text:p",
            "namespace_uri": "urn:x",
            "local_name": "p",
            "canonical_class": "Text.Paragraph",
            "spec_fact_ref": "FACT-FODT-003",
            "status": "seeded",
            "source_layer": "Spec",
            "python_file": "src/python/fodt/spec/text/paragraph.py",
            "dotnet_file": None,
        }
        _make_registry(tmp_path, [entry])
        generate_stubs("fodt", tmp_path, dry_run=False, verbose=False)

        # All __init__.py files must exist
        assert (tmp_path / "src/python/fodt/spec/__init__.py").exists(), "spec/__init__.py missing"
        assert (tmp_path / "src/python/fodt/spec/text/__init__.py").exists(), "spec/text/__init__.py missing"

    def test_deep_namespace_init_files(self, tmp_path):
        """__init__.py must be created even for table/ subdirectory."""
        entry = {
            "qname": "table:table-cell",
            "namespace_uri": "urn:x",
            "local_name": "table-cell",
            "canonical_class": "Table.TableCell",
            "spec_fact_ref": "FACT-FODT-007",
            "status": "seeded",
            "source_layer": "Spec",
            "python_file": "src/python/fodt/spec/table/table_cell.py",
            "dotnet_file": None,
        }
        _make_registry(tmp_path, [entry])
        generate_stubs("fodt", tmp_path, dry_run=False, verbose=False)

        assert (tmp_path / "src/python/fodt/spec/__init__.py").exists()
        assert (tmp_path / "src/python/fodt/spec/table/__init__.py").exists()


class TestNoOverwrite:
    def test_no_overwrite_architecture_only_status(self, tmp_path):
        """Files with status=architecture_only must NOT be overwritten."""
        entry = {
            "qname": "text:p",
            "namespace_uri": "urn:x",
            "local_name": "p",
            "canonical_class": "Text.Paragraph",
            "spec_fact_ref": "FACT-FODT-003",
            "status": "architecture_only",
            "source_layer": "Spec",
            "python_file": "src/python/fodt/spec/text/paragraph.py",
            "dotnet_file": None,
        }
        _make_registry(tmp_path, [entry])

        # Pre-create the file with custom content
        py_path = tmp_path / "src/python/fodt/spec/text/paragraph.py"
        py_path.parent.mkdir(parents=True, exist_ok=True)
        original = "# CUSTOM — do not overwrite\nclass Paragraph:\n    spec_qname = \"text:p\"\n"
        py_path.write_text(original, encoding="utf-8")

        generate_stubs("fodt", tmp_path, dry_run=False, verbose=False)
        assert py_path.read_text(encoding="utf-8") == original, "File was overwritten despite status=architecture_only"

    def test_no_overwrite_implemented_status(self, tmp_path):
        """Files with status=implemented must NOT be overwritten."""
        entry = {
            "qname": "text:p",
            "namespace_uri": "urn:x",
            "local_name": "p",
            "canonical_class": "Text.Paragraph",
            "spec_fact_ref": "FACT-FODT-003",
            "status": "implemented",
            "source_layer": "Spec",
            "python_file": "src/python/fodt/spec/text/paragraph.py",
            "dotnet_file": None,
        }
        _make_registry(tmp_path, [entry])

        py_path = tmp_path / "src/python/fodt/spec/text/paragraph.py"
        py_path.parent.mkdir(parents=True, exist_ok=True)
        original = "# FULLY IMPLEMENTED — do not regenerate\n"
        py_path.write_text(original, encoding="utf-8")

        generate_stubs("fodt", tmp_path, dry_run=False, verbose=False)
        assert py_path.read_text(encoding="utf-8") == original


class TestGeneratedContent:
    def test_python_stub_has_spec_qname(self, tmp_path):
        """Generated Python stub must have spec_qname attribute."""
        entry = {
            "qname": "text:span",
            "namespace_uri": "urn:x",
            "local_name": "span",
            "canonical_class": "Text.Span",
            "spec_fact_ref": "FACT-FODT-006",
            "status": "seeded",
            "source_layer": "Spec",
            "python_file": "src/python/fodt/spec/text/span.py",
            "dotnet_file": None,
        }
        _make_registry(tmp_path, [entry])
        generate_stubs("fodt", tmp_path, dry_run=False, verbose=False)

        content = (tmp_path / "src/python/fodt/spec/text/span.py").read_text(encoding="utf-8")
        assert 'spec_qname = "text:span"' in content
        assert "architecture_only" in content

    def test_dotnet_stub_has_qname_constant(self, tmp_path):
        """Generated .NET stub must have QName constant matching registry qname."""
        entry = {
            "qname": "office:body",
            "namespace_uri": "urn:x",
            "local_name": "body",
            "canonical_class": "Office.Body",
            "spec_fact_ref": "FACT-FODT-002",
            "status": "seeded",
            "source_layer": "Spec",
            "python_file": None,
            "dotnet_file": "src/net/fodt/Spec/Office/Body.cs",
        }
        _make_registry(tmp_path, [entry])
        generate_stubs("fodt", tmp_path, dry_run=False, verbose=False)

        content = (tmp_path / "src/net/fodt/Spec/Office/Body.cs").read_text(encoding="utf-8")
        assert 'QName = "office:body"' in content
        assert "architecture_only" in content

    def test_null_python_file_not_created(self, tmp_path):
        """Entries with python_file: null must not create any Python file."""
        entry = {
            "qname": "office:body",
            "namespace_uri": "urn:x",
            "local_name": "body",
            "canonical_class": "Office.Body",
            "spec_fact_ref": "FACT-FODT-002",
            "status": "seeded",
            "source_layer": "Spec",
            "python_file": None,
            "dotnet_file": None,
        }
        _make_registry(tmp_path, [entry])
        generate_stubs("fodt", tmp_path, dry_run=False, verbose=False)

        py_spec_dir = tmp_path / "src" / "python" / "fodt" / "spec"
        # No Python files should be created (only possibly .NET)
        python_files = list(py_spec_dir.rglob("*.py")) if py_spec_dir.exists() else []
        assert len(python_files) == 0, f"Python files created despite python_file: null: {python_files}"


class TestDryRun:
    def test_dry_run_creates_no_files(self, tmp_path):
        """--dry-run must not create any files."""
        entry = {
            "qname": "text:p",
            "namespace_uri": "urn:x",
            "local_name": "p",
            "canonical_class": "Text.Paragraph",
            "spec_fact_ref": "FACT-FODT-003",
            "status": "seeded",
            "source_layer": "Spec",
            "python_file": "src/python/fodt/spec/text/paragraph.py",
            "dotnet_file": "src/net/fodt/Spec/Text/Paragraph.cs",
        }
        _make_registry(tmp_path, [entry])
        generate_stubs("fodt", tmp_path, dry_run=True, verbose=False)

        assert not (tmp_path / "src/python/fodt/spec/text/paragraph.py").exists()
        assert not (tmp_path / "src/net/fodt/Spec/Text/Paragraph.cs").exists()


class TestMissingRegistry:
    def test_missing_registry_returns_error(self, tmp_path):
        """Missing registry file must return error summary."""
        summary = generate_stubs("fodt", tmp_path, dry_run=False, verbose=False)
        assert "error" in summary
