"""Tests for validate_cross_language_parity.py (Step 0.5).

Verifies:
- Missing registry → PARTIAL exit 1
- Matching Python+.NET → PASS exit 0
- python_file: null entry → PARTIAL exit 1 (expected, not failure)
- QName mismatch in Python stub → FAIL exit 2
- QName mismatch in .NET stub → FAIL exit 2
- Missing Python file → FAIL exit 2
- Missing .NET file → FAIL exit 2
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).parent.parent.parent
_TOOLS_SPEC = _REPO / "tools" / "spec"
if str(_TOOLS_SPEC) not in sys.path:
    sys.path.insert(0, str(_TOOLS_SPEC))

from validate_cross_language_parity import run_parity_check  # noqa: E402


def _make_registry(tmp_path: Path, entries: list[dict]) -> Path:
    """Write a minimal registry YAML file and return its path."""
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


def _make_python_stub(tmp_path: Path, rel_path: str, spec_qname: str | None) -> None:
    file_path = tmp_path / rel_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if spec_qname is not None:
        file_path.write_text(
            f'# GENERATED — architecture_only\nclass Paragraph:\n    spec_qname = "{spec_qname}"\n',
            encoding="utf-8",
        )
    else:
        file_path.write_text("class Paragraph:\n    pass\n", encoding="utf-8")


def _make_dotnet_stub(tmp_path: Path, rel_path: str, qname: str | None) -> None:
    file_path = tmp_path / rel_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if qname is not None:
        file_path.write_text(
            f'// GENERATED — architecture_only\npublic static class Paragraph {{\n    public const string QName = "{qname}";\n}}\n',
            encoding="utf-8",
        )
    else:
        file_path.write_text(
            "public static class Paragraph {\n    // no constant defined\n}\n", encoding="utf-8"
        )


class TestMissingRegistry:
    def test_missing_registry_returns_partial(self, tmp_path):
        """Missing registry file → PARTIAL exit 1."""
        exit_code, results = run_parity_check("fodt", tmp_path)
        assert exit_code == 1
        assert len(results) == 1
        assert results[0]["status"] == "partial_by_design"
        assert "bootstrap" in results[0]["reason"].lower() or "absent" in results[0]["reason"].lower()


class TestNullPythonFile:
    def test_null_python_file_is_partial(self, tmp_path):
        """Entry with python_file: null → PARTIAL (expected), not FAIL."""
        entry = {
            "qname": "office:body",
            "python_file": None,
            "dotnet_file": "src/net/fodt/Spec/Office/Body.cs",
        }
        _make_registry(tmp_path, [entry])
        # Create matching .NET stub
        _make_dotnet_stub(tmp_path, "src/net/fodt/Spec/Office/Body.cs", "office:body")

        exit_code, results = run_parity_check("fodt", tmp_path)
        assert exit_code == 1  # PARTIAL_BY_DESIGN
        py_result = results[0]["python"]
        assert py_result["status"] == "partial_by_design"


class TestAllPass:
    def test_matching_python_and_dotnet_returns_pass(self, tmp_path):
        """Matching Python + .NET stubs → ALL_PASS exit 0."""
        entry = {
            "qname": "text:p",
            "python_file": "src/python/fodt/spec/text/paragraph.py",
            "dotnet_file": "src/net/fodt/Spec/Text/Paragraph.cs",
        }
        _make_registry(tmp_path, [entry])
        _make_python_stub(tmp_path, "src/python/fodt/spec/text/paragraph.py", "text:p")
        _make_dotnet_stub(tmp_path, "src/net/fodt/Spec/Text/Paragraph.cs", "text:p")

        exit_code, results = run_parity_check("fodt", tmp_path)
        assert exit_code == 0  # ALL_PASS
        assert results[0]["python"]["status"] == "pass"
        assert results[0]["dotnet"]["status"] == "pass"


class TestQNameMismatch:
    def test_python_qname_mismatch_is_fail(self, tmp_path):
        """Python stub has wrong spec_qname → FAIL exit 2."""
        entry = {
            "qname": "text:p",
            "python_file": "src/python/fodt/spec/text/paragraph.py",
            "dotnet_file": None,
        }
        _make_registry(tmp_path, [entry])
        # Wrong qname in file
        _make_python_stub(tmp_path, "src/python/fodt/spec/text/paragraph.py", "text:WRONG")

        exit_code, results = run_parity_check("fodt", tmp_path)
        assert exit_code == 2  # FAIL
        assert results[0]["python"]["status"] == "fail"
        assert "mismatch" in results[0]["python"]["reason"].lower()

    def test_dotnet_qname_mismatch_is_fail(self, tmp_path):
        """.NET stub has wrong QName → FAIL exit 2."""
        entry = {
            "qname": "text:p",
            "python_file": None,
            "dotnet_file": "src/net/fodt/Spec/Text/Paragraph.cs",
        }
        _make_registry(tmp_path, [entry])
        _make_dotnet_stub(tmp_path, "src/net/fodt/Spec/Text/Paragraph.cs", "text:WRONG")

        exit_code, results = run_parity_check("fodt", tmp_path)
        assert exit_code == 2  # FAIL
        assert results[0]["dotnet"]["status"] == "fail"
        assert "mismatch" in results[0]["dotnet"]["reason"].lower()


class TestMissingFiles:
    def test_missing_python_file_is_fail(self, tmp_path):
        """python_file path doesn't exist → FAIL exit 2."""
        entry = {
            "qname": "text:p",
            "python_file": "src/python/fodt/spec/text/paragraph.py",
            "dotnet_file": None,
        }
        _make_registry(tmp_path, [entry])
        # Do NOT create the file

        exit_code, results = run_parity_check("fodt", tmp_path)
        assert exit_code == 2
        assert results[0]["python"]["status"] == "fail"
        assert "does not exist" in results[0]["python"]["reason"]

    def test_missing_dotnet_file_is_fail(self, tmp_path):
        """dotnet_file path doesn't exist → FAIL exit 2."""
        entry = {
            "qname": "office:body",
            "python_file": None,
            "dotnet_file": "src/net/fodt/Spec/Office/Body.cs",
        }
        _make_registry(tmp_path, [entry])
        # Do NOT create the .NET file

        exit_code, results = run_parity_check("fodt", tmp_path)
        assert exit_code == 2
        assert results[0]["dotnet"]["status"] == "fail"
        assert "does not exist" in results[0]["dotnet"]["reason"]


class TestMissingSpecQname:
    def test_python_file_without_spec_qname_is_fail(self, tmp_path):
        """Python file exists but has no spec_qname → FAIL."""
        entry = {
            "qname": "text:p",
            "python_file": "src/python/fodt/spec/text/paragraph.py",
            "dotnet_file": None,
        }
        _make_registry(tmp_path, [entry])
        _make_python_stub(tmp_path, "src/python/fodt/spec/text/paragraph.py", None)

        exit_code, results = run_parity_check("fodt", tmp_path)
        assert exit_code == 2
        assert results[0]["python"]["status"] == "fail"
        assert "missing" in results[0]["python"]["reason"].lower()

    def test_dotnet_file_without_qname_constant_is_fail(self, tmp_path):
        """.NET file exists but has no QName constant → FAIL."""
        entry = {
            "qname": "office:body",
            "python_file": None,
            "dotnet_file": "src/net/fodt/Spec/Office/Body.cs",
        }
        _make_registry(tmp_path, [entry])
        _make_dotnet_stub(tmp_path, "src/net/fodt/Spec/Office/Body.cs", None)

        exit_code, results = run_parity_check("fodt", tmp_path)
        assert exit_code == 2
        assert results[0]["dotnet"]["status"] == "fail"
        assert "missing" in results[0]["dotnet"]["reason"].lower()


class TestMixedEntries:
    def test_pass_and_partial_yields_partial(self, tmp_path):
        """One PASS entry + one PARTIAL (null python_file) → overall PARTIAL exit 1."""
        entries = [
            {
                "qname": "text:p",
                "python_file": "src/python/fodt/spec/text/paragraph.py",
                "dotnet_file": None,
            },
            {
                "qname": "office:body",
                "python_file": None,
                "dotnet_file": None,
            },
        ]
        _make_registry(tmp_path, entries)
        _make_python_stub(tmp_path, "src/python/fodt/spec/text/paragraph.py", "text:p")

        exit_code, results = run_parity_check("fodt", tmp_path)
        assert exit_code == 1  # PARTIAL_BY_DESIGN (not FAIL, not ALL_PASS)

    def test_pass_and_fail_yields_fail(self, tmp_path):
        """One PASS entry + one FAIL → overall FAIL exit 2."""
        entries = [
            {
                "qname": "text:p",
                "python_file": "src/python/fodt/spec/text/paragraph.py",
                "dotnet_file": None,
            },
            {
                "qname": "text:h",
                "python_file": "src/python/fodt/spec/text/heading.py",
                "dotnet_file": None,
            },
        ]
        _make_registry(tmp_path, entries)
        _make_python_stub(tmp_path, "src/python/fodt/spec/text/paragraph.py", "text:p")
        # heading.py does NOT exist (FAIL)

        exit_code, results = run_parity_check("fodt", tmp_path)
        assert exit_code == 2  # FAIL takes priority
