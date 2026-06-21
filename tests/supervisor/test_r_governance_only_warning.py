"""Tests for V39: governance_only_no_source_delta validator."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from tools.supervisor.governance_validators import (
    validate_governance_only_no_source_delta,
)


def _decl(items, changed_files=None):
    d = {"planned_work_items": items}
    if changed_files is not None:
        d["changed_files"] = changed_files
    return d


def _item(item_id, item_type):
    return {"item_id": item_id, "item_type": item_type}


class TestGovernanceOnlyNoSourceDelta:
    def test_governance_only_no_source_emits_warning(self):
        """All GOVERNANCE_DOC items + no src/ files → WARNING."""
        decl = _decl(
            [
                _item("GOV-001", "GOVERNANCE_DOC"),
                _item("GOV-002", "GOVERNANCE_REPORT"),
            ],
            changed_files=["reports/supervisor/latest-review.md", "registry/foo.yaml"],
        )
        result = validate_governance_only_no_source_delta(decl)
        assert result["result"] == "WARN"
        assert not result["blocks_sprint"]
        assert "governance-type with no source delta" in result["summary"]

    def test_governance_with_source_no_warning(self):
        """GOVERNANCE_DOC items + src/ file in changed_files → PASS."""
        decl = _decl(
            [
                _item("GOV-001", "GOVERNANCE_DOC"),
                _item("GOV-002", "GOVERNANCE_TASKCARD"),
            ],
            changed_files=["src/python/fods/writer.py", "reports/foo.md"],
        )
        result = validate_governance_only_no_source_delta(decl)
        assert result["result"] == "PASS"

    def test_product_source_no_warning(self):
        """PRODUCT_SOURCE item present → PASS (mixed types)."""
        decl = _decl(
            [_item("PROD-001", "PRODUCT_SOURCE")],
            changed_files=[],
        )
        result = validate_governance_only_no_source_delta(decl)
        assert result["result"] == "PASS"

    def test_mixed_items_no_warning(self):
        """1 PRODUCT_SOURCE + 1 GOVERNANCE_DOC → PASS."""
        decl = _decl(
            [
                _item("PROD-001", "PRODUCT_SOURCE"),
                _item("GOV-001", "GOVERNANCE_DOC"),
            ],
            changed_files=[],
        )
        result = validate_governance_only_no_source_delta(decl)
        assert result["result"] == "PASS"

    def test_empty_items_no_warning(self):
        """No items at all → PASS (nothing to check)."""
        decl = _decl([], changed_files=[])
        result = validate_governance_only_no_source_delta(decl)
        assert result["result"] == "PASS"
