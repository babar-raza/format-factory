"""
test_r58_fodt_public_api.py — R58 Train F: document_stats in FODT public API.

Verifies that document_stats() is accessible from the installed package API.

R58 Sprint: FORMAT-FACTORY-R58-TRUE-SELF-VERIFYING-RC-REBUILD-PHASE9-EXPANSION-MEGA-TRAIN-001
IV-R57-009
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))


class TestFodtPublicApi:
    """document_stats must be accessible from the fodt package public API."""

    def test_document_stats_importable_from_package(self):
        import fodt
        assert hasattr(fodt, "document_stats"), (
            "document_stats must be exported from fodt package __init__.py (IV-R57-009)"
        )

    def test_document_stats_in_all(self):
        import fodt
        assert "document_stats" in fodt.__all__

    def test_document_stats_callable(self):
        import fodt
        doc = {"format_id": "fodt", "blocks": []}
        result = fodt.document_stats(doc)
        assert isinstance(result, dict)

    def test_document_stats_returns_required_keys(self):
        import fodt
        doc = {"format_id": "fodt", "blocks": [
            {"type": "paragraph", "text": "Hello world", "runs": []},
            {"type": "heading", "heading_level": 1, "text": "Title", "runs": []},
        ]}
        stats = fodt.document_stats(doc)
        required_keys = ["block_count", "paragraph_count", "heading_count",
                         "list_count", "table_count", "total_text_length"]
        for k in required_keys:
            assert k in stats, f"document_stats missing key: {k}"

    def test_document_stats_counts_blocks(self):
        import fodt
        # Block format uses "type" field (not "kind"), matches neutral model schema
        doc = {"format_id": "fodt", "blocks": [
            {"type": "paragraph", "text": "Para 1", "runs": []},
            {"type": "paragraph", "text": "Para 2", "runs": []},
            {"type": "heading", "heading_level": 2, "text": "Heading", "runs": []},
        ]}
        stats = fodt.document_stats(doc)
        assert stats["block_count"] == 3
        assert stats["heading_count"] == 1
