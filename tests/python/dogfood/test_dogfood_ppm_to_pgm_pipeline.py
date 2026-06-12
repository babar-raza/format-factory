"""
test_dogfood_ppm_to_pgm_pipeline.py -- PPM->PGM cross-format dogfood.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-3
Uses PPM parser + to_grayscale to create PGM, then parses the PGM output.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

_PPM_SAMPLES = _REPO / "samples" / "by-format" / "ppm" / "valid"

from ppm.ppm_parser import to_grayscale
from pgm.pgm_parser import parse_pgm


def test_ppm_to_pgm_pipeline(tmp_path):
    """Convert PPM to PGM grayscale, then parse the PGM output."""
    src = str(_PPM_SAMPLES / "2x2-rgbw.ppm")
    pgm_out = tmp_path / "gray.pgm"
    to_grayscale(src, str(pgm_out))
    assert pgm_out.exists()
    result = parse_pgm(str(pgm_out))
    assert result["ok"] is True
    assert result["width"] == 2
    assert result["height"] == 2


def test_ppm_to_pgm_gradient(tmp_path):
    """Convert gradient PPM to PGM."""
    src = str(_PPM_SAMPLES / "3x1-gradient.ppm")
    pgm_out = tmp_path / "gray_grad.pgm"
    to_grayscale(src, str(pgm_out))
    result = parse_pgm(str(pgm_out))
    assert result["ok"] is True
    assert result["width"] == 3
