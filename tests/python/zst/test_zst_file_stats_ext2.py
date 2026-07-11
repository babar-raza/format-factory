"""Tests for zst_file_stats extension functions (ext2 batch)."""
from __future__ import annotations

from pathlib import Path

import pytest

from zst.zst_file_stats import (
    zst_frame_count,
    zst_is_single_frame,
    zst_magic_valid,
    zst_is_valid_file,
    zst_bytes_saved,
    zst_is_empty_content,
)

SAMPLES = Path("samples/by-format/zst/valid")
BLOCK = SAMPLES / "block-128k.zst"
DICT = SAMPLES / "dict-compressed.zst"
EMPTY = SAMPLES / "empty-block.zst"


# --- zst_frame_count ---

def test_frame_count_block_returns_int():
    assert isinstance(zst_frame_count(BLOCK), int)


def test_frame_count_block_positive():
    assert zst_frame_count(BLOCK) >= 1


def test_frame_count_dict():
    assert zst_frame_count(DICT) >= 1


# --- zst_is_single_frame ---

def test_is_single_frame_block():
    result = zst_is_single_frame(BLOCK)
    assert isinstance(result, bool)


def test_is_single_frame_true_when_count_is_one():
    result = zst_is_single_frame(BLOCK)
    count = zst_frame_count(BLOCK)
    assert result == (count == 1)


# --- zst_magic_valid ---

def test_magic_valid_block_true():
    assert zst_magic_valid(BLOCK) is True


def test_magic_valid_dict_true():
    assert zst_magic_valid(DICT) is True


def test_magic_valid_returns_bool():
    assert isinstance(zst_magic_valid(BLOCK), bool)


# --- zst_is_valid_file ---

def test_is_valid_file_block():
    assert zst_is_valid_file(BLOCK) is True


def test_is_valid_file_dict():
    assert zst_is_valid_file(DICT) is True


def test_is_valid_file_returns_bool():
    assert isinstance(zst_is_valid_file(BLOCK), bool)


# --- zst_bytes_saved ---

def test_bytes_saved_returns_int():
    assert isinstance(zst_bytes_saved(BLOCK), int)


def test_bytes_saved_dict():
    assert isinstance(zst_bytes_saved(DICT), int)


# --- zst_is_empty_content ---

def test_is_empty_content_returns_bool():
    assert isinstance(zst_is_empty_content(BLOCK), bool)


def test_is_empty_content_block_false():
    assert zst_is_empty_content(BLOCK) is False


def test_is_empty_content_empty_true():
    assert zst_is_empty_content(EMPTY) is True
