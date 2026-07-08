"""Tests for SUP-RECT-006 focused evidence extractor.

Verifies that functions beyond line 200 are correctly extracted into
focused evidence snippets, and the deterministic fallback works.
"""

import sys
import textwrap
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from focused_evidence_extractor import (
    extract_function_snippet,
    generate_focused_evidence_file,
    deterministic_function_exists,
)


@pytest.fixture
def short_source(tmp_path):
    """Source file with function at line 5."""
    src = tmp_path / "short.py"
    src.write_text(textwrap.dedent("""\
        import os

        X = 1

        def my_func(a: int, b: str) -> bool:
            \"\"\"Check something.\"\"\"
            return len(b) > a

        def other():
            pass
    """))
    return src


@pytest.fixture
def long_source(tmp_path):
    """Source file with function beyond line 200."""
    lines = ["# filler line"] * 250
    lines[0] = "import os"
    lines[210] = "def deep_function(source: str) -> list[str]:"
    lines[211] = '    """A function beyond line 200."""'
    lines[212] = "    return source.split()"
    lines[213] = ""
    lines[220] = "def another_deep(x: int) -> int:"
    lines[221] = '    """Another deep function."""'
    lines[222] = "    return x * 2"
    src = tmp_path / "long.py"
    src.write_text("\n".join(lines))
    return src


@pytest.fixture
def very_long_source(tmp_path):
    """Source file with function beyond line 300."""
    lines = ["# filler"] * 350
    lines[0] = "import sys"
    lines[310] = "def very_deep(path):"
    lines[311] = '    """Very deep function."""'
    lines[312] = "    return str(path)"
    src = tmp_path / "vlong.py"
    src.write_text("\n".join(lines))
    return src


class TestExtractFunctionSnippet:
    def test_short_file_extraction(self, short_source):
        result = extract_function_snippet(short_source, "my_func")
        assert result is not None
        assert result["function_name"] == "my_func"
        assert result["line_number"] == 5
        assert result["beyond_line_200"] is False
        assert "def my_func" in result["signature"]

    def test_function_not_found(self, short_source):
        result = extract_function_snippet(short_source, "nonexistent")
        assert result is None

    def test_beyond_line_200(self, long_source):
        result = extract_function_snippet(long_source, "deep_function")
        assert result is not None
        assert result["line_number"] == 211
        assert result["beyond_line_200"] is True

    def test_beyond_line_300(self, very_long_source):
        result = extract_function_snippet(very_long_source, "very_deep")
        assert result is not None
        assert result["line_number"] == 311
        assert result["beyond_line_200"] is True

    def test_extraction_method_is_ast(self, short_source):
        result = extract_function_snippet(short_source, "my_func")
        assert result["extraction_method"] == "AST"

    def test_snippet_contains_body(self, short_source):
        result = extract_function_snippet(short_source, "my_func")
        assert "return len(b) > a" in result["snippet"]

    def test_file_not_found(self, tmp_path):
        result = extract_function_snippet(tmp_path / "nope.py", "func")
        assert result is None

    def test_max_lines_limit(self, long_source):
        result = extract_function_snippet(long_source, "deep_function", max_lines=2)
        assert result is not None
        assert result["snippet_lines"] <= 3


class TestDeterministicFunctionExists:
    def test_exists_short(self, short_source):
        result = deterministic_function_exists(short_source, "my_func")
        assert result["exists"] is True
        assert result["method"] == "AST"
        assert result["line_number"] == 5

    def test_exists_deep(self, long_source):
        result = deterministic_function_exists(long_source, "deep_function")
        assert result["exists"] is True
        assert result["line_number"] == 211

    def test_not_exists(self, short_source):
        result = deterministic_function_exists(short_source, "nope")
        assert result["exists"] is False

    def test_file_missing(self, tmp_path):
        result = deterministic_function_exists(tmp_path / "x.py", "f")
        assert result["exists"] is False
        assert result["method"] == "file_not_found"

    def test_llm_false_negative_override(self, long_source):
        """If LLM says function missing but it exists at line 211, deterministic wins."""
        llm_says_missing = True
        det = deterministic_function_exists(long_source, "deep_function")
        # Deterministic override: function exists
        assert det["exists"] is True
        override = not llm_says_missing or det["exists"]
        assert override is True


class TestGenerateFocusedEvidenceFile:
    def test_generates_file(self, short_source, tmp_path):
        extraction = extract_function_snippet(short_source, "my_func")
        output = tmp_path / "evidence.md"
        result = generate_focused_evidence_file(extraction, output)
        assert result.is_file()
        content = result.read_text()
        assert "my_func" in content
        assert "Line:" in content
        assert "Signature" in content

    def test_with_test_file(self, short_source, tmp_path):
        extraction = extract_function_snippet(short_source, "my_func")
        test_file = tmp_path / "test_x.py"
        test_file.write_text("def test_one(): pass\ndef test_two(): pass\n")
        output = tmp_path / "evidence.md"
        result = generate_focused_evidence_file(extraction, output, test_file)
        content = result.read_text()
        assert "test_one" in content
        assert "Test count:** 2" in content


class TestRealRepoFunctions:
    """Test extraction on actual repo source files."""

    def test_fodp_slide_titles_extraction(self):
        # fodp_slide_titles lives in presentation_document.py (refactored from fodp_codec.py)
        src = _REPO / "src" / "python" / "fodp" / "presentation_document.py"
        if not src.is_file():
            pytest.skip("presentation_document.py not available")
        result = extract_function_snippet(src, "fodp_slide_titles")
        assert result is not None
        assert result["function_name"] == "fodp_slide_titles"
        # Function is early in the file (line ~38), not beyond 200
        assert result["beyond_line_200"] is False

    def test_qoi_is_opaque_extraction(self):
        # qoi_is_opaque lives in image_document.py (refactored from qoi_parser.py)
        src = _REPO / "src" / "python" / "qoi" / "image_document.py"
        if not src.is_file():
            pytest.skip("image_document.py not available")
        result = extract_function_snippet(src, "qoi_is_opaque")
        assert result is not None
        assert result["function_name"] == "qoi_is_opaque"
        # Function is early in the file (line ~49), not beyond 200
        assert result["beyond_line_200"] is False

    def test_deterministic_override_fodp(self):
        # fodp_slide_titles lives in presentation_document.py (refactored from fodp_codec.py)
        src = _REPO / "src" / "python" / "fodp" / "presentation_document.py"
        if not src.is_file():
            pytest.skip("presentation_document.py not available")
        result = deterministic_function_exists(src, "fodp_slide_titles")
        assert result["exists"] is True

    def test_deterministic_override_qoi(self):
        # qoi_is_opaque lives in image_document.py (refactored from qoi_parser.py)
        src = _REPO / "src" / "python" / "qoi" / "image_document.py"
        if not src.is_file():
            pytest.skip("image_document.py not available")
        result = deterministic_function_exists(src, "qoi_is_opaque")
        assert result["exists"] is True
