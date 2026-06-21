"""
Tests for Sprint r311: toml_string_count, toml_numeric_count.
No sample files — uses inline bytes.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.toml.toml_codec import toml_string_count, toml_numeric_count

_S1 = b'name = "Alice"\nage = 30\nactive = true\n'
_S2 = b'title = "Hello"\nsubject = "World"\nversion = 2\n'
_S3 = b'count = 5\nmax = 10\nflag = false\n'


# --- toml_string_count ---

def test_toml_string_count_s1_one():
    assert toml_string_count(_S1) == 1


def test_toml_string_count_s2_two():
    assert toml_string_count(_S2) == 2


def test_toml_string_count_s3_zero():
    assert toml_string_count(_S3) == 0


def test_toml_string_count_returns_int_s1():
    assert isinstance(toml_string_count(_S1), int)


def test_toml_string_count_returns_int_s2():
    assert isinstance(toml_string_count(_S2), int)


def test_toml_string_count_all_three_distinct():
    results = [toml_string_count(_S1), toml_string_count(_S2), toml_string_count(_S3)]
    assert results == [1, 2, 0]


# --- toml_numeric_count ---

def test_toml_numeric_count_s1_one():
    # age=30 is int; active=True is bool (excluded)
    assert toml_numeric_count(_S1) == 1


def test_toml_numeric_count_s2_one():
    # version=2 is int; title, subject are strings
    assert toml_numeric_count(_S2) == 1


def test_toml_numeric_count_s3_two():
    # count=5, max=10 are ints; flag=False is bool (excluded)
    assert toml_numeric_count(_S3) == 2


def test_toml_numeric_count_returns_int_s1():
    assert isinstance(toml_numeric_count(_S1), int)


def test_toml_numeric_count_returns_int_s3():
    assert isinstance(toml_numeric_count(_S3), int)


def test_toml_numeric_count_all_three():
    results = [toml_numeric_count(_S1), toml_numeric_count(_S2), toml_numeric_count(_S3)]
    assert results == [1, 1, 2]
