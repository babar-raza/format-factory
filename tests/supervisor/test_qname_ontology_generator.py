"""Tests for the QName ontology generator."""

import json
import sys
import textwrap
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from qname_ontology_generator import (
    scan_source_for_qnames,
    scan_source_for_functions,
    generate_qname_to_code_map,
    generate_namespace_tree,
    generate_ontology,
)


@pytest.fixture
def odf_source(tmp_path):
    """Create a mock ODF codec source file."""
    src = tmp_path / "fodp_codec.py"
    src.write_text(textwrap.dedent("""\
        import xml.etree.ElementTree as ET

        NS = {
            "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
            "draw": "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
            "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
        }

        def load(source):
            tree = ET.parse(source)
            root = tree.find("office:document", NS)
            return root

        def get_page_count(source):
            model = load(source)
            pages = model.findall(".//draw:page", NS)
            return len(pages)

        def extract_text(source):
            model = load(source)
            texts = model.findall(".//text:p", NS)
            return " ".join(t.text or "" for t in texts)

        def fodp_slide_count(source):
            return get_page_count(source)
    """))
    return src


@pytest.fixture
def clark_source(tmp_path):
    """Create a source file using Clark notation and NS dict (like real FODP)."""
    src = tmp_path / "clark_codec.py"
    src.write_text(textwrap.dedent("""\
        import xml.etree.ElementTree as ET

        NS = {
            "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
            "draw": "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
            "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
            "style": "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
        }

        def load(source):
            root = ET.parse(source).getroot()
            expected_tag = f"{{{NS['office']}}}document"
            mime = root.get(f"{{{NS['office']}}}mimetype", "")
            styles = root.findall(f".//{{{NS['style']}}}style")
            return root

        def get_pages(root):
            for page in root.iter(f"{{{NS['draw']}}}page"):
                name = page.get(f"{{{NS['draw']}}}name", "")
                for frame in page.iter(f"{{{NS['draw']}}}frame"):
                    for tp in frame.iter(f"{{{NS['text']}}}p"):
                        pass
            return []
    """))
    return src


class TestScanSourceForQnames:
    def test_finds_odf_qnames(self, odf_source):
        qnames = scan_source_for_qnames(odf_source)
        qname_strs = [q["qname"] for q in qnames]
        assert "office:document" in qname_strs
        assert "draw:page" in qname_strs
        assert "text:p" in qname_strs

    def test_clark_notation_ns_dict(self, clark_source):
        """Scanner handles NS dict lookups + Clark notation from f-strings."""
        qnames = scan_source_for_qnames(clark_source)
        qname_strs = [q["qname"] for q in qnames]
        assert len(qnames) >= 5, f"Expected >= 5 QNames, found {qname_strs}"
        assert "office:document" in qname_strs
        assert "draw:page" in qname_strs
        assert "draw:name" in qname_strs
        assert "text:p" in qname_strs
        assert "style:style" in qname_strs

    def test_includes_line_numbers(self, odf_source):
        qnames = scan_source_for_qnames(odf_source)
        for q in qnames:
            assert "line_number" in q
            assert q["line_number"] > 0

    def test_includes_namespace(self, odf_source):
        qnames = scan_source_for_qnames(odf_source)
        office_qnames = [q for q in qnames if q["prefix"] == "office"]
        assert len(office_qnames) > 0
        assert "oasis" in office_qnames[0]["namespace"]

    def test_empty_file(self, tmp_path):
        src = tmp_path / "empty.py"
        src.write_text("")
        assert scan_source_for_qnames(src) == []

    def test_missing_file(self, tmp_path):
        assert scan_source_for_qnames(tmp_path / "nope.py") == []


class TestScanSourceForFunctions:
    def test_finds_public_functions(self, odf_source):
        funcs = scan_source_for_functions(odf_source)
        names = [f["name"] for f in funcs]
        assert "load" in names
        assert "get_page_count" in names
        assert "extract_text" in names

    def test_excludes_private(self, tmp_path):
        src = tmp_path / "test.py"
        src.write_text("def _private(): pass\ndef public(): pass\n")
        funcs = scan_source_for_functions(src)
        names = [f["name"] for f in funcs]
        assert "public" in names
        assert "_private" not in names


class TestGenerateQnameToCodeMap:
    def test_produces_mappings(self, odf_source):
        result = generate_qname_to_code_map("FODP", odf_source)
        assert len(result["mappings"]) > 0

    def test_coverage_summary(self, odf_source):
        result = generate_qname_to_code_map("FODP", odf_source)
        summary = result["coverage_summary"]
        assert "total_expected" in summary
        assert "mapped" in summary
        assert "coverage_percent" in summary

    def test_lists_functions(self, odf_source):
        result = generate_qname_to_code_map("FODP", odf_source)
        assert "load" in result["functions"]

    def test_unknown_format(self, odf_source):
        result = generate_qname_to_code_map("UNKNOWN", odf_source)
        assert result["format_id"] == "UNKNOWN"


class TestGenerateNamespaceTree:
    def test_fodp_tree(self):
        tree = generate_namespace_tree("FODP")
        assert tree["format_id"] == "FODP"
        assert tree["containment_tree"]["element"] == "office:document"

    def test_fods_tree(self):
        tree = generate_namespace_tree("FODS")
        assert tree["containment_tree"]["element"] == "office:document"

    def test_unknown_format(self):
        tree = generate_namespace_tree("UNKNOWN")
        assert "note" in tree["containment_tree"]


class TestGenerateOntology:
    def test_writes_output_files(self, odf_source, tmp_path):
        result = generate_ontology("FODP", odf_source, tmp_path / "out")
        assert Path(result["qname_map_path"]).is_file()
        assert Path(result["namespace_tree_path"]).is_file()
        assert Path(result["unmapped_ledger_path"]).is_file()

    def test_coverage_in_result(self, odf_source, tmp_path):
        result = generate_ontology("FODP", odf_source, tmp_path / "out")
        assert "coverage" in result
        assert result["coverage"]["mapped"] > 0

    def test_output_is_valid_json(self, odf_source, tmp_path):
        result = generate_ontology("FODP", odf_source, tmp_path / "out")
        data = json.loads(Path(result["qname_map_path"]).read_text())
        assert data["format_id"] == "FODP"


class TestRealRepoOntology:
    """Test against actual repo source files."""

    def test_fodp_ontology(self, tmp_path):
        src = _REPO / "src" / "python" / "fodp" / "fodp_codec.py"
        if not src.is_file():
            pytest.skip("fodp_codec.py not available")
        result = generate_ontology("FODP", src, tmp_path / "out")
        assert Path(result["qname_map_path"]).is_file()
        assert Path(result["namespace_tree_path"]).is_file()
        # Scanner now handles NS dict lookups and Clark notation
        assert result["coverage"]["mapped"] > 0, (
            f"Expected mapped QNames > 0, got {result['coverage']}"
        )

    def test_fodp_finds_functions(self):
        src = _REPO / "src" / "python" / "fodp" / "fodp_codec.py"
        if not src.is_file():
            pytest.skip("fodp_codec.py not available")
        funcs = scan_source_for_functions(src)
        names = [f["name"] for f in funcs]
        assert "load" in names
        assert "fodp_slide_count" in names
