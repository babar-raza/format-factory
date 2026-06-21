"""Tests for FODT spec/ stub files (Phase 4 — TC-SRC-REVIEW-006).

Verifies:
- All 8 Python stub files exist with correct spec_qname values
- All required __init__.py files exist in spec/ subdirectories
- Stubs are importable and spec_qname is accessible as a class attribute
- architecture_only comment is present in all stubs
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).parent.parent.parent.parent
_SPEC_ROOT = _REPO / "src" / "python" / "fodt" / "spec"

# Expected Python spec stubs: (relative_path, expected_spec_qname)
EXPECTED_STUBS = [
    ("text/paragraph.py", "text:p"),
    ("text/heading.py", "text:h"),
    ("text/span.py", "text:span"),
    ("text/list_.py", "text:list"),
    ("text/list_item.py", "text:list-item"),
    ("table/table.py", "table:table"),
    ("table/table_row.py", "table:table-row"),
    ("table/table_cell.py", "table:table-cell"),
]

# Required __init__.py files
REQUIRED_INIT_FILES = [
    "__init__.py",
    "text/__init__.py",
    "table/__init__.py",
]


class TestStubFilesExist:
    @pytest.mark.parametrize("rel_path,_qname", EXPECTED_STUBS)
    def test_stub_file_exists(self, rel_path, _qname):
        """All 8 Python spec stub files must exist."""
        stub_path = _SPEC_ROOT / rel_path
        assert stub_path.exists(), f"Spec stub missing: {stub_path}"

    @pytest.mark.parametrize("init_rel", REQUIRED_INIT_FILES)
    def test_init_file_exists(self, init_rel):
        """All required __init__.py files must exist in spec/ subdirectories."""
        init_path = _SPEC_ROOT / init_rel
        assert init_path.exists(), f"__init__.py missing: {init_path}"


class TestStubContent:
    @pytest.mark.parametrize("rel_path,expected_qname", EXPECTED_STUBS)
    def test_stub_has_correct_spec_qname(self, rel_path, expected_qname):
        """Each spec stub must have spec_qname = '<correct qname>'."""
        stub_path = _SPEC_ROOT / rel_path
        content = stub_path.read_text(encoding="utf-8")
        assert f'spec_qname = "{expected_qname}"' in content, (
            f"{rel_path}: expected spec_qname = \"{expected_qname}\", not found in file"
        )

    @pytest.mark.parametrize("rel_path,_qname", EXPECTED_STUBS)
    def test_stub_has_architecture_only_marker(self, rel_path, _qname):
        """Each spec stub must have the architecture_only marker comment."""
        stub_path = _SPEC_ROOT / rel_path
        content = stub_path.read_text(encoding="utf-8")
        assert "architecture_only" in content, (
            f"{rel_path}: 'architecture_only' marker missing"
        )

    @pytest.mark.parametrize("rel_path,_qname", EXPECTED_STUBS)
    def test_stub_has_spec_fact_ref(self, rel_path, _qname):
        """Each spec stub must have a spec_fact_ref attribute."""
        stub_path = _SPEC_ROOT / rel_path
        content = stub_path.read_text(encoding="utf-8")
        assert "spec_fact_ref" in content, f"{rel_path}: spec_fact_ref attribute missing"


class TestStubImportability:
    def test_paragraph_importable_with_spec_qname(self):
        """fodt.spec.text.paragraph.Paragraph must be importable with correct spec_qname."""
        if str(_REPO / "src" / "python") not in sys.path:
            sys.path.insert(0, str(_REPO / "src" / "python"))
        from fodt.spec.text.paragraph import Paragraph
        assert Paragraph.spec_qname == "text:p"

    def test_span_importable(self):
        """fodt.spec.text.span.Span must be importable with correct spec_qname."""
        if str(_REPO / "src" / "python") not in sys.path:
            sys.path.insert(0, str(_REPO / "src" / "python"))
        from fodt.spec.text.span import Span
        assert Span.spec_qname == "text:span"

    def test_table_cell_importable(self):
        """fodt.spec.table.table_cell.TableCell must be importable with correct spec_qname."""
        if str(_REPO / "src" / "python") not in sys.path:
            sys.path.insert(0, str(_REPO / "src" / "python"))
        from fodt.spec.table.table_cell import TableCell
        assert TableCell.spec_qname == "table:table-cell"


class TestNoOfficePythonStub:
    def test_no_office_body_python_stub(self):
        """office:body must NOT have a Python spec file — Python uses FodtDocument instead."""
        # The office/ directory should either not exist or not contain body.py
        office_dir = _SPEC_ROOT / "office"
        if office_dir.exists():
            body_py = office_dir / "body.py"
            assert not body_py.exists(), (
                "office/body.py should not exist — Python has no FodtBody; "
                "body concept is represented by FodtDocument (public facade)"
            )
