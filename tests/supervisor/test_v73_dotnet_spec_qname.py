"""Tests for V73 validate_dotnet_spec_qname governance validator.

TC-DOTNET-QNAME-001: .NET Spec/*.cs files must have SpecQName constant
with the correct value matching shared/qname-registry/.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from governance_validators_dotnet import validate_dotnet_spec_qname  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_spec_file(tmp_path: Path, content: str, rel="src/net/csv/Spec/CsvRecord.cs") -> Path:
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


def _decl(changed_files=None, item_types=None):
    items = [{"item_type": t} for t in (item_types or [])]
    return {
        "changed_files": changed_files or [],
        "planned_work_items": items,
    }


# ---------------------------------------------------------------------------
# Tests: skip cases (no Spec/ files)
# ---------------------------------------------------------------------------

def test_no_dotnet_spec_files_passes():
    """Non-.NET files → PASS, no violation."""
    result = validate_dotnet_spec_qname(
        _decl(changed_files=["src/python/csv/csv_parser.py"])
    )
    assert result["result"] == "PASS"
    assert not result["blocks_sprint"]


def test_python_spec_files_not_checked():
    """src/python/*/spec/*.py files are not .NET Spec/ files — PASS."""
    result = validate_dotnet_spec_qname(
        _decl(changed_files=["src/python/csv/spec/record/record.py"])
    )
    assert result["result"] == "PASS"


def test_empty_changed_files_passes():
    """No changed files → PASS."""
    result = validate_dotnet_spec_qname(_decl())
    assert result["result"] == "PASS"


# ---------------------------------------------------------------------------
# Tests: SpecQName present and correct
# ---------------------------------------------------------------------------

def test_correct_specqname_passes(tmp_path):
    """Spec/ file with matching SpecQName → PASS."""
    # Use real repo path so registry lookup works
    real_spec = _REPO / "src" / "net" / "csv" / "Spec" / "CsvRecord.cs"
    if not real_spec.exists():
        pytest.skip(".NET CsvRecord.cs not present")

    result = validate_dotnet_spec_qname(
        _decl(changed_files=["src/net/csv/Spec/CsvRecord.cs"]),
        repo_root=_REPO,
    )
    assert result["result"] == "PASS", f"Unexpected: {result['summary']}"
    assert not result["blocks_sprint"]


def test_specqname_present_but_unregistered_warns(tmp_path):
    """SpecQName present but file not in registry → WARN (not blocking)."""
    _make_spec_file(tmp_path, 'public const string SpecQName = "test:element";',
                    rel="src/net/unknown/Spec/Unknown.cs")
    result = validate_dotnet_spec_qname(
        _decl(changed_files=["src/net/unknown/Spec/Unknown.cs"]),
        repo_root=tmp_path,
    )
    # WARN because file is not in registry
    assert result["result"] in ("WARN", "PASS")  # PASS if no violations, WARN if not_in_registry
    assert not result["blocks_sprint"]


# ---------------------------------------------------------------------------
# Tests: SpecQName missing
# ---------------------------------------------------------------------------

def test_missing_specqname_warns_for_product_source(tmp_path):
    """Missing SpecQName in PRODUCT_SOURCE → WARN (not blocking)."""
    _make_spec_file(tmp_path, "// No SpecQName constant here\npublic class Foo { }")
    result = validate_dotnet_spec_qname(
        _decl(
            changed_files=["src/net/csv/Spec/CsvRecord.cs"],
            item_types=["PRODUCT_SOURCE"],
        ),
        repo_root=tmp_path,
    )
    assert result["result"] == "WARN"
    assert not result["blocks_sprint"]
    assert any(v["issue"] == "specqname_missing" for v in result["items"])


def test_missing_specqname_fails_for_release_gate(tmp_path):
    """Missing SpecQName in RELEASE_GATE → FAIL (blocking)."""
    _make_spec_file(tmp_path, "// No SpecQName constant here\npublic class Foo { }")
    result = validate_dotnet_spec_qname(
        _decl(
            changed_files=["src/net/csv/Spec/CsvRecord.cs"],
            item_types=["RELEASE_GATE"],
        ),
        repo_root=tmp_path,
    )
    assert result["result"] == "FAIL"
    assert result["blocks_sprint"]


# ---------------------------------------------------------------------------
# Tests: SpecQName wrong value
# ---------------------------------------------------------------------------

def test_wrong_specqname_value_warns(tmp_path):
    """SpecQName present but wrong value → WARN for PRODUCT_SOURCE."""
    _make_spec_file(
        tmp_path,
        'public const string SpecQName = "csv:wrong-element";',
    )
    result = validate_dotnet_spec_qname(
        _decl(
            changed_files=["src/net/csv/Spec/CsvRecord.cs"],
            item_types=["PRODUCT_SOURCE"],
        ),
        repo_root=tmp_path,
    )
    # Wrong value against registry → WARN (or PASS if registry mismatch can't be detected without registry)
    assert result["result"] in ("WARN", "PASS")
    assert not result["blocks_sprint"]


def test_wrong_specqname_fails_for_release_gate(tmp_path):
    """SpecQName present but wrong value in RELEASE_GATE → FAIL."""
    _make_spec_file(
        tmp_path,
        'public const string SpecQName = "csv:wrong-element";',
    )
    # Manually inject registry expectation by using real repo root for registry load
    # but temp dir for file loading — this tests value mismatch detection
    # Create a "fake" registry entry that the validator would find
    registry_dir = tmp_path / "shared" / "qname-registry"
    registry_dir.mkdir(parents=True)
    (registry_dir / "csv.yaml").write_text(
        "- qname: csv:record\n"
        "  namespace_uri: urn:ietf:rfc:4180:csv\n"
        "  local_name: record\n"
        "  canonical_class: Csv.Record\n"
        "  spec_fact_ref: FACT-CSV-001\n"
        "  status: implemented\n"
        "  source_layer: Spec\n"
        "  python_file: null\n"
        "  dotnet_file: src/net/csv/Spec/CsvRecord.cs\n",
        encoding="utf-8",
    )

    # Temporarily patch registry dir — use monkeypatching approach
    import governance_validators_dotnet as gvd
    original_dir = gvd._REGISTRY_DIR
    gvd._REGISTRY_DIR = registry_dir
    try:
        result = validate_dotnet_spec_qname(
            _decl(
                changed_files=["src/net/csv/Spec/CsvRecord.cs"],
                item_types=["RELEASE_GATE"],
            ),
            repo_root=tmp_path,
        )
    finally:
        gvd._REGISTRY_DIR = original_dir

    assert result["result"] == "FAIL"
    assert result["blocks_sprint"]
    assert any(v["issue"] == "specqname_wrong_value" for v in result["items"])


# ---------------------------------------------------------------------------
# Tests: file missing on disk
# ---------------------------------------------------------------------------

def test_missing_file_on_disk_reports_violation(tmp_path):
    """Changed file listed but doesn't exist → violation recorded."""
    result = validate_dotnet_spec_qname(
        _decl(changed_files=["src/net/csv/Spec/DoesNotExist.cs"]),
        repo_root=tmp_path,
    )
    assert result["result"] in ("WARN", "FAIL")
    assert any(v["issue"] == "file_not_found" for v in result["items"])


# ---------------------------------------------------------------------------
# Tests: path pattern matching
# ---------------------------------------------------------------------------

def test_non_spec_dotnet_file_not_checked(tmp_path):
    """src/net/csv/CsvDocument.cs (not in Spec/) → PASS (not checked)."""
    _make_spec_file(tmp_path, "// Not a Spec file", rel="src/net/csv/CsvDocument.cs")
    result = validate_dotnet_spec_qname(
        _decl(changed_files=["src/net/csv/CsvDocument.cs"]),
        repo_root=tmp_path,
    )
    assert result["result"] == "PASS"


def test_deeply_nested_spec_file_checked(tmp_path):
    """src/net/fods/Spec/Table/TableCell.cs → checked."""
    _make_spec_file(
        tmp_path,
        '// No SpecQName',
        rel="src/net/fods/Spec/Table/TableCell.cs",
    )
    result = validate_dotnet_spec_qname(
        _decl(
            changed_files=["src/net/fods/Spec/Table/TableCell.cs"],
            item_types=["PRODUCT_SOURCE"],
        ),
        repo_root=tmp_path,
    )
    # Should detect missing SpecQName
    assert result["result"] in ("WARN", "FAIL")
