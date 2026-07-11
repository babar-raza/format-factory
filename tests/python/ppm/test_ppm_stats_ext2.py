"""Tests for ppm_stats extension functions (ext2 batch)."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm.ppm_parser import parse_ppm
from src.python.ppm.ppm_stats import (
    ppm_magic_from_doc,
    ppm_maxval_from_doc,
    ppm_width_from_doc,
    ppm_height_from_doc,
    ppm_is_binary_ppm,
    ppm_is_high_depth_doc,
)

SAMPLES = Path("samples/by-format/ppm/valid")
PPM_1X1 = SAMPLES / "1x1-red.ppm"
PPM_2X2 = SAMPLES / "2x2-rgbw.ppm"
PPM_3X1 = SAMPLES / "3x1-gradient.ppm"


def _doc(path):
    return parse_ppm(str(path))


# --- ppm_magic_from_doc ---

def test_magic_from_doc_returns_str():
    assert isinstance(ppm_magic_from_doc(_doc(PPM_1X1)), str)


def test_magic_from_doc_1x1_p3():
    assert ppm_magic_from_doc(_doc(PPM_1X1)) == "P3"


def test_magic_from_doc_2x2():
    assert ppm_magic_from_doc(_doc(PPM_2X2)) == "P3"


# --- ppm_maxval_from_doc ---

def test_maxval_from_doc_returns_int():
    assert isinstance(ppm_maxval_from_doc(_doc(PPM_1X1)), int)


def test_maxval_from_doc_standard_255():
    assert ppm_maxval_from_doc(_doc(PPM_1X1)) == 255


def test_maxval_from_doc_positive():
    assert ppm_maxval_from_doc(_doc(PPM_2X2)) > 0


# --- ppm_width_from_doc ---

def test_width_from_doc_returns_int():
    assert isinstance(ppm_width_from_doc(_doc(PPM_1X1)), int)


def test_width_from_doc_1x1():
    assert ppm_width_from_doc(_doc(PPM_1X1)) == 1


def test_width_from_doc_2x2():
    assert ppm_width_from_doc(_doc(PPM_2X2)) == 2


# --- ppm_height_from_doc ---

def test_height_from_doc_returns_int():
    assert isinstance(ppm_height_from_doc(_doc(PPM_1X1)), int)


def test_height_from_doc_1x1():
    assert ppm_height_from_doc(_doc(PPM_1X1)) == 1


def test_height_from_doc_3x1():
    assert ppm_height_from_doc(_doc(PPM_3X1)) == 1


# --- ppm_is_binary_ppm ---

def test_is_binary_ppm_returns_bool():
    assert isinstance(ppm_is_binary_ppm(_doc(PPM_1X1)), bool)


def test_is_binary_ppm_p3_false():
    assert ppm_is_binary_ppm(_doc(PPM_1X1)) is False


def test_is_binary_ppm_2x2_false():
    assert ppm_is_binary_ppm(_doc(PPM_2X2)) is False


# --- ppm_is_high_depth_doc ---

def test_is_high_depth_doc_returns_bool():
    assert isinstance(ppm_is_high_depth_doc(_doc(PPM_1X1)), bool)


def test_is_high_depth_doc_255_false():
    assert ppm_is_high_depth_doc(_doc(PPM_1X1)) is False


def test_is_high_depth_doc_2x2_false():
    assert ppm_is_high_depth_doc(_doc(PPM_2X2)) is False
