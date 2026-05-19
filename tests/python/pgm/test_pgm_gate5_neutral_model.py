"""Gate 5 neutral model tests for PGM parser."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "python"))
from pgm.pgm_parser import SUPPORTED_FEATURES, UNSUPPORTED_FEATURES, get_capabilities


class TestPgmGate5NeutralModel:
    def test_capabilities_format(self):
        caps = get_capabilities()
        assert caps["format"] == "pgm"
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
        assert "p2_ascii_parse" in SUPPORTED_FEATURES
        assert "grayscale_pixel_decode" in SUPPORTED_FEATURES
        assert "probe" in SUPPORTED_FEATURES

    def test_key_unsupported_features(self):
        assert "p5_binary_parse" in UNSUPPORTED_FEATURES
        assert "encoding_to_pgm" in UNSUPPORTED_FEATURES

    def test_features_are_frozensets(self):
        assert isinstance(SUPPORTED_FEATURES, frozenset)
        assert isinstance(UNSUPPORTED_FEATURES, frozenset)
