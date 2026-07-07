"""
tests/packaging/test_r79_package_source_sync.py

R79 Train C — Package source sync verification tests.

Validates that R79 repairs are in place:
- PACKAGE_VERSION matches wheel metadata version (D78-04)
- FODT paragraph APIs use root-level doc["blocks"] (GAP-FODT-STRUCT-001)
- FODS R77 sheet management APIs are present in source (D78-01)
- FODT R77 paragraph management APIs are present in source (D78-02)
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


class TestPackageVersionSync:
    """D78-04: PACKAGE_VERSION in constants.py must match 0.1.0."""

    def test_fods_package_version_is_dev0(self):
        from src.python.fods.constants import PACKAGE_VERSION
        assert PACKAGE_VERSION == "0.1.0", (
            f"fods PACKAGE_VERSION is {PACKAGE_VERSION!r}, expected '0.1.0'"
        )

    def test_fodt_package_version_is_dev0(self):
        from src.python.fodt.constants import PACKAGE_VERSION
        assert PACKAGE_VERSION == "0.1.0", (
            f"fodt PACKAGE_VERSION is {PACKAGE_VERSION!r}, expected '0.1.0'"
        )

    def test_fods_dunder_version_is_dev0(self):
        from src.python.fods import __version__
        assert __version__ == "0.1.0", (
            f"fods.__version__ is {__version__!r}, expected '0.1.0'"
        )

    def test_fodt_dunder_version_is_dev0(self):
        from src.python.fodt import __version__
        assert __version__ == "0.1.0", (
            f"fodt.__version__ is {__version__!r}, expected '0.1.0'"
        )


class TestFodsR77ApiPresence:
    """D78-01: R77 sheet management APIs must be present in fods source."""

    def test_workbook_add_sheet_exported(self):
        from src.python.fods import workbook_add_sheet
        assert callable(workbook_add_sheet)

    def test_workbook_rename_sheet_exported(self):
        from src.python.fods import workbook_rename_sheet
        assert callable(workbook_rename_sheet)

    def test_workbook_remove_sheet_exported(self):
        from src.python.fods import workbook_remove_sheet
        assert callable(workbook_remove_sheet)

    def test_workbook_set_cell_value_exported(self):
        from src.python.fods import workbook_set_cell_value
        assert callable(workbook_set_cell_value)

    def test_fods_api_count_at_least_28(self):
        import src.python.fods as fods_mod
        public_api = [a for a in dir(fods_mod) if not a.startswith("_")]
        assert len(public_api) >= 28, (
            f"fods public API count {len(public_api)} < 28 — stale wheel or missing APIs"
        )


class TestFodtR77ApiPresence:
    """D78-02: R77 paragraph management APIs must be present in fodt source."""

    def test_document_append_paragraph_exported(self):
        from src.python.fodt import document_append_paragraph
        assert callable(document_append_paragraph)

    def test_document_remove_paragraph_exported(self):
        from src.python.fodt import document_remove_paragraph
        assert callable(document_remove_paragraph)

    def test_document_paragraph_count_exported(self):
        from src.python.fodt import document_paragraph_count
        assert callable(document_paragraph_count)

    def test_fodt_api_count_at_least_28(self):
        import src.python.fodt as fodt_mod
        public_api = [a for a in dir(fodt_mod) if not a.startswith("_")]
        assert len(public_api) >= 28, (
            f"fodt public API count {len(public_api)} < 28 — stale wheel or missing APIs"
        )


class TestFodtStructuralGapRepaired:
    """GAP-FODT-STRUCT-001: Paragraph APIs must use root-level doc['blocks']."""

    def test_append_paragraph_writes_to_root_blocks(self):
        from src.python.fodt import document_append_paragraph
        doc = {"blocks": []}
        ok, msg = document_append_paragraph(doc, "Test paragraph")
        assert ok, f"append failed: {msg}"
        assert "blocks" in doc, "doc must have root-level 'blocks' key"
        assert len(doc["blocks"]) == 1, "block must be in root doc['blocks']"
        assert doc["blocks"][0]["runs"][0]["text"] == "Test paragraph"

    def test_append_paragraph_does_not_write_to_body_blocks(self):
        from src.python.fodt import document_append_paragraph
        doc = {"blocks": []}
        document_append_paragraph(doc, "Test paragraph")
        # body.blocks must NOT be populated (parser never creates it)
        body = doc.get("body", {})
        assert "blocks" not in body, (
            "document_append_paragraph must NOT write to doc['body']['blocks'] — "
            "use root-level doc['blocks'] instead"
        )

    def test_paragraph_count_reads_from_root_blocks(self):
        from src.python.fodt import document_paragraph_count
        doc = {
            "blocks": [
                {"type": "paragraph", "runs": [{"text": "A"}]},
                {"type": "paragraph", "runs": [{"text": "B"}]},
            ]
        }
        count = document_paragraph_count(doc)
        assert count == 2, f"Expected 2 paragraphs in root blocks, got {count}"

    def test_paragraph_count_ignores_body_blocks(self):
        from src.python.fodt import document_paragraph_count
        # body.blocks is NOT the canonical location — count must return 0 for empty root blocks
        doc = {
            "body": {
                "blocks": [
                    {"type": "paragraph", "runs": [{"text": "Old location"}]},
                ]
            },
            "blocks": [],
        }
        count = document_paragraph_count(doc)
        assert count == 0, (
            f"document_paragraph_count must read root doc['blocks'] only, got {count}"
        )

    def test_remove_paragraph_modifies_root_blocks(self):
        from src.python.fodt import document_remove_paragraph
        doc = {
            "blocks": [
                {"type": "paragraph", "runs": [{"text": "Remove me"}]},
                {"type": "paragraph", "runs": [{"text": "Keep me"}]},
            ]
        }
        ok, msg = document_remove_paragraph(doc, 0)
        assert ok, f"remove failed: {msg}"
        assert len(doc["blocks"]) == 1
        assert doc["blocks"][0]["runs"][0]["text"] == "Keep me"

    def test_append_then_roundtrip_preserves_paragraph(self):
        """After R79 fix: appended paragraphs survive write_fodt/parse_fodt roundtrip."""
        import tempfile
        from pathlib import Path
        from src.python.fodt import (
            parse_fodt, write_fodt, document_append_paragraph, document_paragraph_count
        )
        sample = REPO_ROOT / "samples" / "by-format" / "fodt" / "minimal-document.fodt"
        doc = parse_fodt(sample)
        count_before = document_paragraph_count(doc)
        ok, _ = document_append_paragraph(doc, "R79_ROUNDTRIP_TEST_PARAGRAPH")
        assert ok
        with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False) as tf:
            out = Path(tf.name)
        write_fodt(doc, out)
        doc2 = parse_fodt(out)
        count_after = document_paragraph_count(doc2)
        out.unlink(missing_ok=True)
        assert count_after == count_before + 1, (
            f"Roundtrip paragraph count: before={count_before}, after={count_after} — "
            "appended paragraph must survive write/parse roundtrip"
        )
