"""Gate 5 neutral model tests for DIF parser."""

import sys
from pathlib import Path

_src = Path(__file__).resolve().parents[3] / "src" / "python"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from dif.dif_parser import (
    SUPPORTED_FEATURES,
    UNSUPPORTED_FEATURES,
    get_capabilities,
)


class TestDifGate5NeutralModel:
    """Neutral model tests: capability declarations are honest and complete."""

    def test_capabilities_format(self):
        caps = get_capabilities()
        assert caps["format"] == "dif"
        assert caps["gate"] == 5
        assert caps["commercial_product_ready"] is False

    def test_supported_features_nonempty(self):
        assert len(SUPPORTED_FEATURES) >= 5

    def test_unsupported_features_nonempty(self):
        assert len(UNSUPPORTED_FEATURES) >= 5

    def test_no_overlap(self):
        assert SUPPORTED_FEATURES.isdisjoint(UNSUPPORTED_FEATURES)

    def test_supported_features_are_strings(self):
        for f in SUPPORTED_FEATURES:
            assert isinstance(f, str)

    def test_unsupported_features_are_strings(self):
        for f in UNSUPPORTED_FEATURES:
            assert isinstance(f, str)

    def test_capabilities_sorted(self):
        caps = get_capabilities()
        assert caps["supported"] == sorted(caps["supported"])
        assert caps["unsupported"] == sorted(caps["unsupported"])

    def test_key_supported_features(self):
        assert "numeric_cells" in SUPPORTED_FEATURES
        assert "string_cells" in SUPPORTED_FEATURES
        assert "table_header_parse" in SUPPORTED_FEATURES

    def test_key_unsupported_features(self):
        assert "formula_cells" in UNSUPPORTED_FEATURES
        assert "date_cells" in UNSUPPORTED_FEATURES
