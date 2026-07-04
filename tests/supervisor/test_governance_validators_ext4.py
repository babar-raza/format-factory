"""Tests for V111-V129 Architecture QName Validators (TC-ARC-012, TC-VAL-002).

38 tests: 2 per validator (pass + fail case) for V111-V127 + V128 + V129.
Baseline: 186 tests in test_governance_validators.py.
Target: 186 + 38 = 224 total across both files.
"""

from tools.supervisor.governance_validators_ext4 import (
    validate_compat_facade_behavioral,
    validate_dotnet_parser_required,
    ArchitectureGateNotPassed,
    validate_broken_traceability_chain,
    validate_certification_without_architecture_proof,
    validate_detached_persistent_dict_on_model,
    validate_dumping_ground_or_catchall_file,
    validate_file_outside_approved_qname_layout,
    validate_getter_without_parser_obligation,
    validate_missing_public_documentation,
    validate_model_type_without_spec_authority,
    validate_nested_concept_on_root_document,
    validate_new_product_bypassing_architecture_gate,
    validate_product_architecture_ready,
    validate_promoted_code_changed_without_reopening,
    validate_public_symbol_without_qname_authority,
    validate_semantic_stub_constant_return,
    validate_setter_without_writer_obligation,
    validate_sprint_history_identifier_in_source,
    validate_type_outside_approved_qname_hierarchy,
    validate_ungoverned_code_marker,
)


class TestV111PublicSymbolWithoutQnameAuthority:
    def test_pass_spec_class_has_spec_qname(self):
        src = 'class TableCell:\n    spec_qname = "table:table-cell"\n'
        r = validate_public_symbol_without_qname_authority(
            src, "src/python/fods/spec/table/table_cell.py"
        )
        assert r["passed"] is True

    def test_fail_spec_class_missing_spec_qname(self):
        src = "class Orphan:\n    pass\n"
        r = validate_public_symbol_without_qname_authority(
            src, "src/python/fods/spec/table/orphan.py"
        )
        assert r["passed"] is False
        assert any("spec_qname" in v for v in r["violations"])


class TestV112ModelTypeWithoutSpecAuthority:
    def test_pass_model_class_has_spec_qname(self):
        src = 'class TableCell:\n    spec_qname = "table:table-cell"\n'
        r = validate_model_type_without_spec_authority(
            src, "src/python/fods/spec/table/table_cell.py"
        )
        assert r["passed"] is True

    def test_fail_model_class_missing_spec_qname(self):
        src = "class RandomModel:\n    pass\n"
        r = validate_model_type_without_spec_authority(
            src, "src/net/fods/Model/Table/RandomModel.cs"
        )
        assert r["passed"] is False
        assert r["violations"]


class TestV113NestedConceptOnRootDocument:
    def test_pass_non_root_file(self):
        src = "public void GetCellValue() {}"
        r = validate_nested_concept_on_root_document(src, "src/net/fods/FodsCell.cs")
        assert r["passed"] is True

    def test_fail_root_has_nested_method(self):
        src = (
            "public class FodsDocument {\n"
            "    public string GetCellValue(int r, int c) { return null; }\n"
            "}"
        )
        r = validate_nested_concept_on_root_document(src, "src/net/fods/FodsDocument.cs")
        assert r["passed"] is False
        assert any("GetCellValue" in v for v in r["violations"])


class TestV114GetterWithoutParserObligation:
    def test_pass_getter_has_parser_path(self):
        sym = {
            "member_type": "property_getter",
            "parser_path": "Parsing/FodsParser.cs",
            "member_name": "Value",
        }
        r = validate_getter_without_parser_obligation(sym)
        assert r["passed"] is True

    def test_fail_getter_missing_parser_path(self):
        sym = {
            "member_type": "property_getter",
            "parser_path": "",
            "member_name": "Value",
            "disposition": "retained",
        }
        r = validate_getter_without_parser_obligation(sym)
        assert r["passed"] is False
        assert r["violations"]


class TestV115SetterWithoutWriterObligation:
    def test_pass_setter_has_writer_path(self):
        sym = {
            "member_type": "method_setter",
            "writer_path": "Writing/FodsWriter.cs",
            "member_name": "SetValue",
        }
        r = validate_setter_without_writer_obligation(sym)
        assert r["passed"] is True

    def test_fail_setter_missing_writer_path(self):
        sym = {
            "member_type": "method_setter",
            "writer_path": "",
            "member_name": "SetValue",
            "disposition": "retained",
        }
        r = validate_setter_without_writer_obligation(sym)
        assert r["passed"] is False
        assert r["violations"]


class TestV116DetachedPersistentDictOnModel:
    def test_pass_model_no_dict(self):
        src = "public class TableCell { public string Value { get; set; } }"
        r = validate_detached_persistent_dict_on_model(
            src, "src/net/fods/Model/Table/TableCell.cs"
        )
        assert r["passed"] is True

    def test_fail_model_has_dict(self):
        src = "private Dictionary<string, object?> _state = new();"
        r = validate_detached_persistent_dict_on_model(
            src, "src/net/fods/Model/Table/TableCell.cs"
        )
        assert r["passed"] is False
        assert r["violations"]


class TestV117DumpingGroundOrCatchallFile:
    def test_pass_normal_filename(self):
        r = validate_dumping_ground_or_catchall_file(
            "src/net/fods/Model/Table/TableCell.cs"
        )
        assert r["passed"] is True

    def test_fail_catchall_filename(self):
        r = validate_dumping_ground_or_catchall_file("src/net/fods/MissingMethods.cs")
        assert r["passed"] is False
        assert r["violations"]


class TestV118SprintHistoryIdentifierInSource:
    def test_pass_no_sprint_id(self):
        src = "public class FodsDocument { }"
        r = validate_sprint_history_identifier_in_source(src, "src/net/fods/FodsDocument.cs")
        assert r["passed"] is True

    def test_fail_sprint_id_present(self):
        src = "# sprint123 work\npublic class FodsDocument { }"
        r = validate_sprint_history_identifier_in_source(src, "src/net/fods/FodsDocument.cs")
        assert r["passed"] is False
        assert r["violations"]


class TestV119PromotedCodeChangedWithoutReopening:
    def test_pass_not_promoted_file(self):
        registry = {
            "promotion_records": [
                {"promotion_level": "DRAFT", "promoted_files": ["src/net/fods/FodsDocument.cs"]}
            ]
        }
        r = validate_promoted_code_changed_without_reopening(
            ["src/net/fods/FodsDocument.cs"], registry
        )
        assert r["passed"] is True

    def test_fail_promoted_file_modified(self):
        registry = {
            "promotion_records": [
                {
                    "promotion_level": "PROMOTED_STABLE",
                    "promoted_files": ["src/net/fods/FodsDocument.cs"],
                }
            ]
        }
        r = validate_promoted_code_changed_without_reopening(
            ["src/net/fods/FodsDocument.cs"], registry
        )
        assert r["passed"] is False
        assert r["violations"]


class TestV120CertificationWithoutArchitectureProof:
    def test_pass_certified_and_compliant(self):
        r = validate_certification_without_architecture_proof("CERTIFIED", "COMPLIANT", "fods")
        assert r["passed"] is True

    def test_fail_certified_not_compliant(self):
        r = validate_certification_without_architecture_proof(
            "CERTIFIED", "QNAME_MODEL_DECOMPOSITION", "fods"
        )
        assert r["passed"] is False
        assert r["violations"]


class TestV121MissingPublicDocumentation:
    def test_pass_has_docstring(self):
        src = 'def get_value():\n    """Return cell value."""\n    return 0\n'
        r = validate_missing_public_documentation(src, "src/python/fods/models.py")
        assert r["passed"] is True

    def test_fail_missing_docstring(self):
        src = "def get_value():\n    return 0\n"
        r = validate_missing_public_documentation(src, "src/python/fods/models.py")
        assert r["passed"] is False
        assert r["violations"]


class TestV122BrokenTraceabilityChain:
    def test_pass_has_spec_facts(self):
        sym = {
            "member_name": "Value",
            "spec_fact_ids": ["FACT-FODS-006"],
            "disposition": "retained",
        }
        r = validate_broken_traceability_chain(sym)
        assert r["passed"] is True

    def test_fail_missing_spec_facts(self):
        sym = {"member_name": "Value", "spec_fact_ids": [], "disposition": "retained"}
        r = validate_broken_traceability_chain(sym)
        assert r["passed"] is False
        assert r["violations"]


class TestV123UngovernedCodeMarker:
    def test_pass_governed_todo(self):
        src = "# TODO GAP-FODS-NET-001: implement delegation\n"
        r = validate_ungoverned_code_marker(src, "src/net/fods/FodsDocument.cs")
        assert r["passed"] is True

    def test_fail_ungoverned_todo(self):
        src = "# TODO: implement this later\n"
        r = validate_ungoverned_code_marker(src, "src/net/fods/FodsDocument.cs")
        assert r["passed"] is False
        assert r["violations"]


class TestV124SemanticStubConstantReturn:
    def test_pass_real_implementation(self):
        src = 'def get_value(self):\n    """Get cell value."""\n    return self._cell.value\n'
        r = validate_semantic_stub_constant_return(src, "src/python/fods/models.py")
        assert r["passed"] is True

    def test_fail_constant_return_stub(self):
        src = "def get_count(self):\n    return 0\n"
        r = validate_semantic_stub_constant_return(src, "src/python/fods/models.py")
        assert r["passed"] is False
        assert r["violations"]


class TestV125NewProductBypassingArchitectureGate:
    def test_pass_format_in_plan(self):
        entries = [{"format": "fods"}, {"format": "csv"}]
        r = validate_new_product_bypassing_architecture_gate("fods", entries)
        assert r["passed"] is True

    def test_fail_format_not_in_plan(self):
        entries = [{"format": "fods"}, {"format": "csv"}]
        r = validate_new_product_bypassing_architecture_gate("xyz_nonexistent", entries)
        assert r["passed"] is False
        assert r["violations"]


class TestV126FileOutsideApprovedQnameLayout:
    def test_pass_file_in_approved_layout(self):
        entries = [
            {"format": "fods", "root": "src/net/fods/", "target_subdirs": ["Model/Table/"]}
        ]
        r = validate_file_outside_approved_qname_layout(
            "src/net/fods/Model/Table/TableCell.cs", entries
        )
        assert r["passed"] is True

    def test_fail_format_not_in_plan(self):
        entries = [{"format": "csv", "root": "src/net/csv/", "target_subdirs": ["Model/"]}]
        r = validate_file_outside_approved_qname_layout("src/net/xyz/SomeFile.cs", entries)
        assert r["passed"] is False
        assert r["violations"]


class TestV127TypeOutsideApprovedQnameHierarchy:
    def test_pass_type_derivable_from_qname(self):
        nodes = [{"qname": "table:table-cell", "canonical_class": "Table.TableCell"}]
        r = validate_type_outside_approved_qname_hierarchy("FodsCell", nodes)
        assert r["passed"] is True

    def test_fail_type_not_derivable(self):
        nodes = [{"qname": "table:table-cell", "canonical_class": "Table.TableCell"}]
        r = validate_type_outside_approved_qname_hierarchy("LegacyMiscHelper", nodes)
        assert r["passed"] is False
        assert r["violations"]


class TestProductArchitectureReadyGate:
    """TC-ARC-015: PRODUCT_ARCHITECTURE_READY gate tests."""

    _PLAN_ENTRIES = [{"format": "fods"}, {"format": "csv"}, {"format": "zst"}]

    def test_pass_format_in_plan(self):
        r = validate_product_architecture_ready("fods", self._PLAN_ENTRIES)
        assert r["passed"] is True

    def test_fail_format_not_in_plan(self):
        import pytest
        with pytest.raises(ArchitectureGateNotPassed):
            validate_product_architecture_ready("xyz_nonexistent", self._PLAN_ENTRIES)


class TestV128:
    """V128: dotnet_parser_required — FULL_REBUILD_STUB detection."""

    def test_pass_has_parser_and_writer(self):
        files = ["HtmlDocument.cs", "HtmlParser.cs", "HtmlWriter.cs", "HtmlDocument.csproj"]
        r = validate_dotnet_parser_required("html", files)
        assert r["passed"] is True
        assert r["validator_id"] == "V128"

    def test_fail_stub_only_single_file(self):
        files = ["HtmlDocument.cs", "HtmlDocument.csproj"]
        r = validate_dotnet_parser_required("html", files)
        assert r["passed"] is False
        assert r["violations"]
        assert "stub-only" in r["violations"][0].lower() or "1" in r["violations"][0]

    def test_fail_no_parser_file(self):
        files = ["MarkdownDocument.cs", "MarkdownHelper.cs", "MarkdownDocument.csproj"]
        r = validate_dotnet_parser_required("markdown", files)
        assert r["passed"] is False
        assert r["violations"]


class TestV129:
    """V129: compat_facade_behavioral — Compat/ marker detection."""

    def test_pass_behavioral_compat(self):
        src = '''
class FodsDocument:
    """Public facade over spec/office/document.Document."""

    def load(self, path: str) -> None:
        self._doc = parse_fods(path)

    def save(self, path: str) -> None:
        write_fods(self._doc, path)
'''
        r = validate_compat_facade_behavioral(src, "src/python/fods/Compat/fods_document.py")
        assert r["passed"] is True
        assert r["validator_id"] == "V129"

    def test_fail_architecture_marker_only(self):
        src = '''
class FodsDocument(_SpecDocument):
    """This class is not behavioral — architecture marker only.
    Real behavior is in models.py until Wave 1 wiring completes.
    """
    pass
'''
        r = validate_compat_facade_behavioral(src, "src/python/fods/Compat/fods_document.py")
        assert r["passed"] is False
        assert r["violations"]
        assert "not behavioral" in r["violations"][0].lower() or "marker" in r["violations"][0].lower()

    def test_pass_non_compat_file_skipped(self):
        # V129 only applies to Compat/ paths
        src = "class FooBar:\n    pass\n"
        r = validate_compat_facade_behavioral(src, "src/python/fods/models.py")
        assert r["passed"] is True
