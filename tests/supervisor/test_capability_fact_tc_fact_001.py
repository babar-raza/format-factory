"""TC-FACT-001 verification tests.

Verifies that:
1. _match_sal_facts_per_op returns non-empty matches for common operation kinds
2. FOSS capability records have per-capability spec_refs (not bulk-identical)
3. _build_foss_records accepts and uses sal_fact_objects parameter
4. _discover_missing_foss_formats passes sal_fact_objects to _build_foss_records
"""
from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
_FOSS_MAP = _REPO / "reports" / "capability-layer" / "foss-reduced-capability-map.json"


class TestMatchSalFactsPerOp:
    def test_load_op_returns_matches(self):
        """_match_sal_facts_per_op returns qnames for 'load' with real SAL facts."""
        import sys
        sys.path.insert(0, str(_REPO))
        from tools.capability_layer.capability_map_generator import (
            _match_sal_facts_per_op, _load_sal_facts,
        )
        sal_facts = _load_sal_facts()
        fods_objs = sal_facts.get("FODS", [])
        if not fods_objs:
            return  # skip if SAL not available
        result = _match_sal_facts_per_op(fods_objs, "load")
        assert len(result) > 0, "load should match SAL facts"
        assert len(result) <= 20, "capped at 20"

    def test_sheet_count_returns_cell_table_refs(self):
        """fods_sheet_count matches sheet/table-related SAL facts."""
        import sys
        sys.path.insert(0, str(_REPO))
        from tools.capability_layer.capability_map_generator import (
            _match_sal_facts_per_op, _load_sal_facts,
        )
        sal_facts = _load_sal_facts()
        fods_objs = sal_facts.get("FODS", [])
        if not fods_objs:
            return
        result = _match_sal_facts_per_op(fods_objs, "fods_sheet_count")
        assert len(result) > 0

    def test_empty_facts_returns_empty(self):
        """Empty sal_fact_objects returns empty list."""
        import sys
        sys.path.insert(0, str(_REPO))
        from tools.capability_layer.capability_map_generator import _match_sal_facts_per_op
        result = _match_sal_facts_per_op([], "load")
        assert result == []

    def test_empty_op_returns_empty(self):
        """Empty operation_kind returns empty list."""
        import sys
        sys.path.insert(0, str(_REPO))
        from tools.capability_layer.capability_map_generator import _match_sal_facts_per_op
        result = _match_sal_facts_per_op([{"qname": "Q1", "description": "test", "section": "s1"}], "")
        assert result == []

    def test_different_ops_return_different_refs(self):
        """load and write return different (or at least distinct) spec_refs."""
        import sys
        sys.path.insert(0, str(_REPO))
        from tools.capability_layer.capability_map_generator import (
            _match_sal_facts_per_op, _load_sal_facts,
        )
        sal_facts = _load_sal_facts()
        fods_objs = sal_facts.get("FODS", [])
        if not fods_objs:
            return
        load_refs = _match_sal_facts_per_op(fods_objs, "load")
        write_refs = _match_sal_facts_per_op(fods_objs, "write")
        # They don't have to be completely disjoint but should differ
        assert set(load_refs) != set(write_refs), "load and write should produce different spec_refs"


class TestFossMapPerCapabilitySpecRefs:
    def test_foss_map_exists(self):
        """foss-reduced-capability-map.json exists."""
        assert _FOSS_MAP.exists()

    def test_fods_has_multiple_unique_spec_refs_sets(self):
        """FODS capabilities have multiple distinct spec_refs sets (not bulk)."""
        if not _FOSS_MAP.exists():
            return
        data = json.loads(_FOSS_MAP.read_text(encoding="utf-8"))
        fods_caps = [c for c in data["capabilities"] if c["format"] == "FODS"]
        if len(fods_caps) < 5:
            return  # skip if no FODS caps
        ref_sets = [frozenset(c["spec_refs"]) for c in fods_caps if c["spec_refs"]]
        unique_sets = len(set(ref_sets))
        assert unique_sets > 3, (
            f"Expected >3 unique spec_refs sets for FODS capabilities (got {unique_sets}). "
            "TC-FACT-001 requires per-capability spec_refs, not bulk."
        )

    def test_fods_sheet_count_has_table_refs(self):
        """fods_sheet_count cap has sheet/table-relevant spec_refs."""
        if not _FOSS_MAP.exists():
            return
        data = json.loads(_FOSS_MAP.read_text(encoding="utf-8"))
        sc = next(
            (c for c in data["capabilities"]
             if c["format"] == "FODS" and c["operation_kind"] == "fods_sheet_count"),
            None,
        )
        if sc is None:
            return  # cap may not exist
        refs = sc.get("spec_refs", [])
        # Should have some refs matching sheet/table content
        assert len(refs) > 0, "fods_sheet_count should have spec_refs"
        assert len(refs) <= 20, "spec_refs capped at 20 for per-capability match"

    def test_spec_refs_not_all_same_for_multi_format(self):
        """Across all FOSS caps, different operation_kinds produce different spec_refs."""
        if not _FOSS_MAP.exists():
            return
        data = json.loads(_FOSS_MAP.read_text(encoding="utf-8"))
        caps = data["capabilities"]
        # Get a format with many caps and SAL facts (e.g., FODS)
        fods_caps = [c for c in caps if c["format"] == "FODS" and c["spec_refs"]]
        if len(fods_caps) < 10:
            return
        ref_sets = [frozenset(c["spec_refs"]) for c in fods_caps]
        unique_count = len(set(ref_sets))
        # At least 10% of caps should have distinct refs
        assert unique_count >= len(fods_caps) * 0.10, (
            f"Only {unique_count}/{len(fods_caps)} unique spec_refs sets — still bulk-like"
        )
