"""test_system_healing_validators.py

TC-PQLM-014: System Healing Proof — validator-level controlled replay tests.

These tests demonstrate that the healed validators (V100-V109) reject the
6 bad-pattern fixture types defined in tests/product-quality/fixtures/.

Each test creates a minimal Python or C# source file, runs the relevant
validator against it, and asserts FAIL for bad patterns and PASS for healed patterns.
"""

import ast
import textwrap
import tempfile
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "tools" / "supervisor"))

from governance_validators_ext3 import (
    validate_suspicious_filenames,
    validate_undocumented_public_python_apis,
    validate_constant_return_public_methods,
    validate_detached_persistent_state,
    validate_history_identifiers_in_source,
    validate_files_outside_approved_layout,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _decl_with_changed_file(path: str) -> dict:
    """Minimal declaration dict referencing a single changed file."""
    return {
        "sprint": "R-TEST",
        "work_items": [
            {
                "item_id": "WI-TEST-001",
                "classification": "PRODUCT_SOURCE",
                "changed_files": [path],
            }
        ],
    }


# ---------------------------------------------------------------------------
# FIXTURE-001 / FIXTURE-003: Suspicious filename rejection (V100)
# ---------------------------------------------------------------------------

class TestSuspiciousFilenames:
    """V100 validate_suspicious_filenames — blocking for new ExtendedApis/Helpers/Misc files."""

    def test_extended_apis_filename_fails(self, tmp_path):
        """FodsDocumentExtendedApis.cs must FAIL V100."""
        bad_file = tmp_path / "src" / "net" / "fods" / "FodsDocumentExtendedApis.cs"
        bad_file.parent.mkdir(parents=True)
        bad_file.write_text("public class FodsDocumentExtendedApis {}")
        decl = _decl_with_changed_file(str(bad_file))
        result = validate_suspicious_filenames(decl, tmp_path)
        assert result["status"] == "FAIL", f"Expected FAIL for ExtendedApis filename, got: {result}"
        assert result["blocks_sprint"] is True

    def test_misc_python_filename_fails(self, tmp_path):
        """fods_misc.py must FAIL V100."""
        bad_file = tmp_path / "src" / "python" / "fods" / "fods_misc.py"
        bad_file.parent.mkdir(parents=True)
        bad_file.write_text("def helper(): pass")
        decl = _decl_with_changed_file(str(bad_file))
        result = validate_suspicious_filenames(decl, tmp_path)
        assert result["status"] == "FAIL", f"Expected FAIL for *Misc* filename, got: {result}"

    def test_helpers_python_filename_fails(self, tmp_path):
        """fods_helpers.py must FAIL V100 — FIXTURE-003."""
        bad_file = tmp_path / "src" / "python" / "fods" / "fods_helpers.py"
        bad_file.parent.mkdir(parents=True)
        bad_file.write_text("def help_func(): pass")
        decl = _decl_with_changed_file(str(bad_file))
        result = validate_suspicious_filenames(decl, tmp_path)
        assert result["status"] == "FAIL"

    def test_approved_filename_passes(self, tmp_path):
        """FodsParser.cs must PASS V100."""
        ok_file = tmp_path / "src" / "net" / "fods" / "FodsParser.cs"
        ok_file.parent.mkdir(parents=True)
        ok_file.write_text("public class FodsParser {}")
        decl = _decl_with_changed_file(str(ok_file))
        result = validate_suspicious_filenames(decl, tmp_path)
        assert result["status"] == "PASS", f"Expected PASS for FodsParser.cs, got: {result}"

    def test_sprint_identifier_filename_fails(self, tmp_path):
        """Sprint5Additions.cs must FAIL V100."""
        bad_file = tmp_path / "src" / "net" / "fods" / "Sprint5Additions.cs"
        bad_file.parent.mkdir(parents=True)
        bad_file.write_text("public class Sprint5Additions {}")
        decl = _decl_with_changed_file(str(bad_file))
        result = validate_suspicious_filenames(decl, tmp_path)
        assert result["status"] == "FAIL"


# ---------------------------------------------------------------------------
# FIXTURE-006: Undocumented public API rejection (V102)
# ---------------------------------------------------------------------------

class TestUndocumentedPublicApi:
    """V102 validate_undocumented_public_python_apis — blocking for new files."""

    def test_undocumented_public_def_fails(self, tmp_path):
        """Public def without docstring in new file must FAIL V102 — FIXTURE-006."""
        bad_file = tmp_path / "src" / "python" / "fods" / "parser.py"
        bad_file.parent.mkdir(parents=True)
        bad_file.write_text(textwrap.dedent("""\
            def get_named_ranges(doc):
                return doc.named_ranges
        """))
        decl = _decl_with_changed_file(str(bad_file))
        result = validate_undocumented_public_python_apis(decl, tmp_path)
        assert result["status"] == "FAIL", f"Expected FAIL for undocumented public def, got: {result}"
        assert result["blocks_sprint"] is True

    def test_documented_public_def_passes(self, tmp_path):
        """Public def with docstring must PASS V102."""
        ok_file = tmp_path / "src" / "python" / "fods" / "parser.py"
        ok_file.parent.mkdir(parents=True)
        ok_file.write_text(textwrap.dedent("""\
            def get_named_ranges(doc):
                \"\"\"Return all named ranges per ODF §9.4.5.

                Args:
                    doc: A parsed FodsDocument instance.

                Returns:
                    List of FodsNamedRange objects.
                \"\"\"
                return doc.named_ranges
        """))
        decl = _decl_with_changed_file(str(ok_file))
        result = validate_undocumented_public_python_apis(decl, tmp_path)
        assert result["status"] == "PASS", f"Expected PASS for documented def, got: {result}"

    def test_private_def_ignored(self, tmp_path):
        """Private def (underscore prefix) does not need docstring."""
        ok_file = tmp_path / "src" / "python" / "fods" / "parser.py"
        ok_file.parent.mkdir(parents=True)
        ok_file.write_text("def _internal_helper(x): return x\n")
        decl = _decl_with_changed_file(str(ok_file))
        result = validate_undocumented_public_python_apis(decl, tmp_path)
        assert result["status"] == "PASS"


# ---------------------------------------------------------------------------
# FIXTURE-004: Detached dict state rejection (V108)
# ---------------------------------------------------------------------------

class TestDetachedPersistentState:
    """V108 validate_detached_persistent_state — blocking for new .cs files."""

    def test_dictionary_field_fails(self, tmp_path):
        """Dictionary<string,X?> _field = new() must FAIL V108 — FIXTURE-004."""
        bad_file = tmp_path / "src" / "net" / "fods" / "FodsDocument.cs"
        bad_file.parent.mkdir(parents=True)
        bad_file.write_text(textwrap.dedent("""\
            public class FodsDocument
            {
                private Dictionary<string, double?> _columnWidthCache = new();

                public double? GetColumnWidth(string colRef)
                    => _columnWidthCache.GetValueOrDefault(colRef);
            }
        """))
        decl = _decl_with_changed_file(str(bad_file))
        result = validate_detached_persistent_state(decl, tmp_path)
        assert result["status"] in ("FAIL", "WARN"), f"Expected FAIL/WARN for dict field, got: {result}"

    def test_xml_backed_property_passes(self, tmp_path):
        """XElement-backed property must PASS V108."""
        ok_file = tmp_path / "src" / "net" / "fods" / "FodsDocument.cs"
        ok_file.parent.mkdir(parents=True)
        ok_file.write_text(textwrap.dedent("""\
            public class FodsDocument
            {
                private readonly XDocument _doc;

                public string? Title =>
                    _doc.Root?.Element(FodsNamespaces.Office + \"meta\")?
                         .Element(FodsNamespaces.Dc + \"title\")?.Value;
            }
        """))
        decl = _decl_with_changed_file(str(ok_file))
        result = validate_detached_persistent_state(decl, tmp_path)
        assert result["status"] == "PASS"


# ---------------------------------------------------------------------------
# FIXTURE-005: History identifier rejection (V101)
# ---------------------------------------------------------------------------

class TestHistoryIdentifiers:
    """V101 validate_history_identifiers_in_source — warns on sprint/phase markers."""

    def test_phase_marker_warns(self, tmp_path):
        """Phase 3b marker in .cs file must at least WARN V101 — FIXTURE-005."""
        bad_file = tmp_path / "src" / "net" / "fods" / "FodsDocumentAccessor.cs"
        bad_file.parent.mkdir(parents=True)
        bad_file.write_text(textwrap.dedent("""\
            // Phase 3b complete - R295 sprint adds GetSheetTabColor
            public class FodsDocumentAccessor {}
        """))
        decl = _decl_with_changed_file(str(bad_file))
        result = validate_history_identifiers_in_source(decl, tmp_path)
        assert result["status"] in ("WARN", "FAIL"), f"Expected WARN/FAIL for Phase marker, got: {result}"

    def test_clean_source_passes(self, tmp_path):
        """Source without history markers must PASS V101."""
        ok_file = tmp_path / "src" / "net" / "fods" / "FodsDocument.cs"
        ok_file.parent.mkdir(parents=True)
        ok_file.write_text(textwrap.dedent("""\
            /// <summary>Root FODS document. office:document per ODF §3.1.</summary>
            public class FodsDocument {}
        """))
        decl = _decl_with_changed_file(str(ok_file))
        result = validate_history_identifiers_in_source(decl, tmp_path)
        assert result["status"] == "PASS"


# ---------------------------------------------------------------------------
# Layout fixture (V109) — healed file layout enforcement
# ---------------------------------------------------------------------------

class TestFilesOutsideApprovedLayout:
    """V109 validate_files_outside_approved_layout — blocking for new violations."""

    def test_approved_fods_net_file_passes(self, tmp_path):
        """FodsParser.cs in approved layout must PASS V109."""
        ok_file = tmp_path / "src" / "net" / "fods" / "FodsParser.cs"
        ok_file.parent.mkdir(parents=True)
        ok_file.write_text("public class FodsParser {}")

        # Copy contract to tmp_path for the validator to find it
        contract_src = Path(__file__).parents[2] / "docs" / "code-quality" / "product-file-layout-contract.yaml"
        contract_dst = tmp_path / "docs" / "code-quality" / "product-file-layout-contract.yaml"
        contract_dst.parent.mkdir(parents=True)
        contract_dst.write_text(contract_src.read_text())

        decl = _decl_with_changed_file("src/net/fods/FodsParser.cs")
        result = validate_files_outside_approved_layout(decl, tmp_path)
        assert result["status"] == "PASS", f"FodsParser.cs should be in approved layout: {result}"

    def test_extended_apis_not_in_approved_layout_fails(self, tmp_path):
        """FodsDocumentExtendedApis.cs (not in approved layout) must FAIL V109."""
        bad_file = tmp_path / "src" / "net" / "fods" / "FodsDocumentExtendedApis.cs"
        bad_file.parent.mkdir(parents=True)
        bad_file.write_text("public class FodsDocumentExtendedApis {}")

        contract_src = Path(__file__).parents[2] / "docs" / "code-quality" / "product-file-layout-contract.yaml"
        contract_dst = tmp_path / "docs" / "code-quality" / "product-file-layout-contract.yaml"
        contract_dst.parent.mkdir(parents=True)
        contract_dst.write_text(contract_src.read_text())

        decl = _decl_with_changed_file("src/net/fods/FodsDocumentExtendedApis.cs")
        result = validate_files_outside_approved_layout(decl, tmp_path)
        assert result["status"] in ("FAIL", "WARN"), f"ExtendedApis.cs should fail layout check: {result}"
