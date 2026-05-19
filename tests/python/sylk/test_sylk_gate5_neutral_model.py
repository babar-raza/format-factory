"""Gate 5 neutral model tests for SYLK parser."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "python"))
from sylk.sylk_parser import SUPPORTED_FEATURES, UNSUPPORTED_FEATURES, get_capabilities


class TestSylkGate5NeutralModel:
    def test_capabilities_format(self):
        caps = get_capabilities()
        assert caps["format"] == "sylk"
        assert caps["gate"] == 5
        assert caps["commercial_product_ready"] is False

    def test_supported_nonempty(self):
        assert len(SUPPORTED_FEATURES) > 0

    def test_unsupported_nonempty(self):
        assert len(UNSUPPORTED_FEATURES) > 0

    def test_no_overlap(self):
        assert SUPPORTED_FEATURES.isdisjoint(UNSUPPORTED_FEATURES)

    def test_supported_sorted_in_caps(self):
        caps = get_capabilities()
        assert caps["supported"] == sorted(caps["supported"])

    def test_unsupported_sorted_in_caps(self):
        caps = get_capabilities()
        assert caps["unsupported"] == sorted(caps["unsupported"])

    def test_key_supported_features(self):
        assert "id_record_parse" in SUPPORTED_FEATURES
        assert "c_record_parse" in SUPPORTED_FEATURES
        assert "numeric_cell_values" in SUPPORTED_FEATURES
        assert "string_cell_values" in SUPPORTED_FEATURES

    def test_key_unsupported_features(self):
        assert "formula_cells" in UNSUPPORTED_FEATURES
        assert "encoding_to_sylk" in UNSUPPORTED_FEATURES

    def test_features_are_frozensets(self):
        assert isinstance(SUPPORTED_FEATURES, frozenset)
        assert isinstance(UNSUPPORTED_FEATURES, frozenset)
