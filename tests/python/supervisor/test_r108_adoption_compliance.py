"""R108 Wave 4: Adoption compliance validator tests.

Verify that validate_adoption_compliance checks skill_id, transcript,
and ledger requirements for evidence declarations.
"""

from __future__ import annotations

import sys
from pathlib import Path

TOOLS_DIR = str(Path(__file__).resolve().parent.parent.parent.parent / "tools" / "supervisor")
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

from validate_adoption_compliance import validate_adoption  # noqa: E402


def _make_declaration(items):
    return {"planned_work_items": items}


class TestAdoptionCompliance:
    """Core adoption compliance checks."""

    def test_compliant_declaration(self):
        decl = _make_declaration([
            {
                "item_id": "W1-PRODUCT",
                "title": "Product feature",
                "skill_id": "add-python-api",
                "evidence_paths": ["reports/r108/transcript-001.json"],
                "status": "completed",
            }
        ])
        result = validate_adoption(decl)
        assert result["compliant"]
        assert result["items_with_skill_id"] == 1
        assert result["items_with_transcript"] == 1

    def test_missing_skill_id_still_compliant(self):
        """skill_id is recommended but not blocking."""
        decl = _make_declaration([
            {
                "item_id": "W1-WORK",
                "title": "Some work",
                "evidence_paths": ["reports/r108/report.md"],
                "status": "completed",
            }
        ])
        result = validate_adoption(decl)
        assert result["compliant"]
        assert result["items_with_skill_id"] == 0

    def test_missing_transcript_still_compliant(self):
        """Transcript is tracked but not blocking for non-src items."""
        decl = _make_declaration([
            {
                "item_id": "W1-DOCS",
                "title": "Documentation",
                "evidence_paths": ["reports/r108/docs.md"],
                "status": "completed",
            }
        ])
        result = validate_adoption(decl)
        assert result["compliant"]
        assert result["items_with_transcript"] == 0

    def test_missing_ledger_for_src_editing(self):
        """src-editing track without ledger_entry_id should fail."""
        decl = _make_declaration([
            {
                "item_id": "W1-CODE",
                "title": "Python code change",
                "product_track": "foss_python",
                "evidence_paths": ["reports/r108/code.md"],
                "status": "completed",
            }
        ])
        result = validate_adoption(decl)
        assert not result["compliant"]
        non_exempt = [i for i in result["items"] if not i["exempt"]]
        assert not non_exempt[0]["compliant"]

    def test_exempt_preflight(self):
        """Preflight items are exempt from adoption checks."""
        decl = _make_declaration([
            {
                "item_id": "W0-PREFLIGHT",
                "title": "Preflight reads",
                "evidence_paths": [],
                "status": "completed",
            }
        ])
        result = validate_adoption(decl)
        assert result["compliant"]
        assert result["exempt_items"] == 1
        assert result["non_exempt_items"] == 0

    def test_exempt_final_iv(self):
        """Final IV items are exempt."""
        decl = _make_declaration([
            {
                "item_id": "W9-FINAL-IV",
                "title": "Final adversarial independent verification",
                "evidence_paths": [],
                "status": "completed",
            }
        ])
        result = validate_adoption(decl)
        assert result["compliant"]
        assert result["exempt_items"] == 1

    def test_src_editing_with_ledger_compliant(self):
        """src-editing track with ledger_entry_id passes."""
        decl = _make_declaration([
            {
                "item_id": "W1-DOTNET",
                "title": ".NET feature",
                "product_track": "commercial_dotnet",
                "ledger_entry_id": "LED-001",
                "evidence_paths": ["reports/r108/code.md"],
                "status": "completed",
            }
        ])
        result = validate_adoption(decl)
        assert result["compliant"]
