"""Tests for PBM rotate_90 API.

Sprint: PRODUCT-DEEPENING-HEALING-20260612
Skill: /add-python-api
Format: PBM
API: rotate_90
"""

from __future__ import annotations

import os
import tempfile
import pytest

from src.python.pbm.pbm_parser import (
    rotate_90,
    parse_pbm_strict,
    write_pbm,
    PbmError,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_pbm(pixels: list[int], width: int, height: int) -> str:
    """Write a temporary P1 PBM file and return its path."""
    fd, path = tempfile.mkstemp(suffix=".pbm")
    os.close(fd)
    write_pbm(pixels, width, height, path)
    return path


# ---------------------------------------------------------------------------
# Normal behavior
# ---------------------------------------------------------------------------


def test_rotate_90_dimensions():
    """After 90-degree CW rotation, width and height swap."""
    # 3x2 image → should become 2x3
    pixels = [
        1, 0, 1,
        0, 1, 0,
    ]
    src = _make_pbm(pixels, 3, 2)
    fd, dst = tempfile.mkstemp(suffix=".pbm")
    os.close(fd)
    try:
        result = rotate_90(src, dst)
        assert result["ok"] is True
        assert result["width"] == 2  # original height
        assert result["height"] == 3  # original width
        assert result["pixel_count"] == 6
    finally:
        os.unlink(src)
        os.unlink(dst)


def test_rotate_90_pixel_values():
    """Verify pixel mapping after 90-degree CW rotation."""
    # 3x2 source:
    #   row0: 1 0 0
    #   row1: 0 0 1
    # After 90 CW rotation (new_w=2, new_h=3):
    #   new pixel at (dst_row=col, dst_col=height-1-row)
    #   (0,0)->src[0,0]=1 maps to dst[0,1]; (0,1)->src[0,1]=0 maps to dst[1,1]
    #   (0,2)->src[0,2]=0 maps to dst[2,1]; (1,0)->src[1,0]=0 maps to dst[0,0]
    #   (1,1)->src[1,1]=0 maps to dst[1,0]; (1,2)->src[1,2]=1 maps to dst[2,0]
    # Result (2-wide, 3-tall):
    #   row0: 0 1
    #   row1: 0 0
    #   row2: 1 0
    pixels = [1, 0, 0, 0, 0, 1]
    src = _make_pbm(pixels, 3, 2)
    fd, dst = tempfile.mkstemp(suffix=".pbm")
    os.close(fd)
    try:
        rotate_90(src, dst)
        img = parse_pbm_strict(dst)
        assert img.width == 2
        assert img.height == 3
        assert img.pixels == [0, 1, 0, 0, 1, 0]
    finally:
        os.unlink(src)
        os.unlink(dst)


def test_rotate_90_roundtrip():
    """Four rotations should return to the original image."""
    pixels = [1, 0, 0, 1]
    src = _make_pbm(pixels, 2, 2)
    paths = [src]
    try:
        current = src
        for _ in range(4):
            fd, nxt = tempfile.mkstemp(suffix=".pbm")
            os.close(fd)
            paths.append(nxt)
            rotate_90(current, nxt)
            current = nxt
        final = parse_pbm_strict(current)
        assert final.pixels == pixels
        assert final.width == 2
        assert final.height == 2
    finally:
        for p in paths:
            os.unlink(p)


def test_rotate_90_single_pixel():
    """1x1 image stays the same after rotation."""
    src = _make_pbm([1], 1, 1)
    fd, dst = tempfile.mkstemp(suffix=".pbm")
    os.close(fd)
    try:
        result = rotate_90(src, dst)
        assert result["ok"] is True
        assert result["width"] == 1
        assert result["height"] == 1
        img = parse_pbm_strict(dst)
        assert img.pixels == [1]
    finally:
        os.unlink(src)
        os.unlink(dst)


def test_rotate_90_row_image():
    """1xN row image becomes Nx1 column image."""
    pixels = [1, 0, 1, 1]
    src = _make_pbm(pixels, 4, 1)
    fd, dst = tempfile.mkstemp(suffix=".pbm")
    os.close(fd)
    try:
        result = rotate_90(src, dst)
        assert result["width"] == 1  # original height=1
        assert result["height"] == 4  # original width=4
        img = parse_pbm_strict(dst)
        assert len(img.pixels) == 4
    finally:
        os.unlink(src)
        os.unlink(dst)


# ---------------------------------------------------------------------------
# Boundary case
# ---------------------------------------------------------------------------


def test_rotate_90_all_black():
    """All-black image stays all-black after rotation."""
    pixels = [1, 1, 1, 1, 1, 1]
    src = _make_pbm(pixels, 3, 2)
    fd, dst = tempfile.mkstemp(suffix=".pbm")
    os.close(fd)
    try:
        rotate_90(src, dst)
        img = parse_pbm_strict(dst)
        assert all(p == 1 for p in img.pixels)
        assert img.width == 2
        assert img.height == 3
    finally:
        os.unlink(src)
        os.unlink(dst)


# ---------------------------------------------------------------------------
# Invalid input
# ---------------------------------------------------------------------------


def test_rotate_90_invalid_file():
    """Non-PBM file raises PbmError."""
    fd, path = tempfile.mkstemp(suffix=".pbm")
    os.write(fd, b"not a pbm file")
    os.close(fd)
    fd2, dst = tempfile.mkstemp(suffix=".pbm")
    os.close(fd2)
    try:
        with pytest.raises(PbmError):
            rotate_90(path, dst)
    finally:
        os.unlink(path)
        os.unlink(dst)


def test_rotate_90_nonexistent_file():
    """Nonexistent file raises PbmError."""
    fd, dst = tempfile.mkstemp(suffix=".pbm")
    os.close(fd)
    try:
        with pytest.raises(PbmError):
            rotate_90("/tmp/nonexistent_r169.pbm", dst)
    finally:
        os.unlink(dst)
