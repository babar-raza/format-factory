"""Tests for XCF layer analytics extension functions."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf.xcf_layer_analytics import (
    xcf_num_layers,
    xcf_local_name,
    xcf_namespace_uri,
    xcf_layer_names_sorted,
    xcf_has_named_layers,
    xcf_all_layers_named,
)

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"
# All three files: 1 layer named 'Background', type RGB(=0) or Gray(=1)


# --- xcf_num_layers ---

def test_num_layers_red():
    assert xcf_num_layers(RED) == 1


def test_num_layers_gray():
    assert xcf_num_layers(GRAY) == 1


def test_num_layers_returns_int():
    assert isinstance(xcf_num_layers(RED), int)


# --- xcf_local_name ---

def test_local_name_red():
    assert xcf_local_name(RED) == "image"


def test_local_name_gray():
    assert xcf_local_name(GRAY) == "image"


def test_local_name_returns_str():
    assert isinstance(xcf_local_name(RED), str)


# --- xcf_namespace_uri ---

def test_namespace_uri_red():
    uri = xcf_namespace_uri(RED)
    assert "gimp" in uri.lower() or uri.startswith("http")


def test_namespace_uri_returns_str():
    assert isinstance(xcf_namespace_uri(RED), str)


def test_namespace_uri_nonempty():
    assert len(xcf_namespace_uri(RED)) > 0


# --- xcf_layer_names_sorted ---

def test_layer_names_sorted_red():
    assert xcf_layer_names_sorted(RED) == ["Background"]


def test_layer_names_sorted_gray():
    assert xcf_layer_names_sorted(GRAY) == ["Background"]


def test_layer_names_sorted_returns_list():
    assert isinstance(xcf_layer_names_sorted(RED), list)


def test_layer_names_sorted_is_sorted():
    names = xcf_layer_names_sorted(RED)
    assert names == sorted(names)


# --- xcf_has_named_layers ---

def test_has_named_layers_red():
    assert xcf_has_named_layers(RED) is True


def test_has_named_layers_gray():
    assert xcf_has_named_layers(GRAY) is True


def test_has_named_layers_returns_bool():
    assert isinstance(xcf_has_named_layers(RED), bool)


# --- xcf_all_layers_named ---

def test_all_layers_named_red():
    assert xcf_all_layers_named(RED) is True


def test_all_layers_named_blue():
    assert xcf_all_layers_named(BLUE) is True


def test_all_layers_named_returns_bool():
    assert isinstance(xcf_all_layers_named(RED), bool)
