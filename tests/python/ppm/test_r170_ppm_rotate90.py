"""Tests for PPM rotate_90 API.

Sprint: PRODUCT-API-BROADENING-20260612
Skill: /add-python-api
Format: PPM
API: rotate_90
"""

from __future__ import annotations

import os
import tempfile

import pytest

from src.python.ppm.ppm_parser import (
    rotate_90,
    parse_ppm_strict,
    write_ppm,
    PpmError,
)


def _make_ppm(pixels, width, height, maxval=255):
    """Create a temporary PPM file and return path."""
    fd, path = tempfile.mkstemp(suffix=".ppm")
    os.close(fd)
    write_ppm(pixels, width, height, maxval, path)
    return path


def test_rotate_dimensions_swap():
    """A 3x2 image becomes 2x3 after rotation."""
    pixels = [(1, 0, 0), (2, 0, 0), (3, 0, 0),
              (4, 0, 0), (5, 0, 0), (6, 0, 0)]
    src = _make_ppm(pixels, 3, 2)
    fd, dst = tempfile.mkstemp(suffix=".ppm")
    os.close(fd)
    try:
        result = rotate_90(src, dst)
        assert result["ok"] is True
        assert result["width"] == 2
        assert result["height"] == 3
        img = parse_ppm_strict(dst)
        assert img.width == 2
        assert img.height == 3
    finally:
        os.unlink(src)
        os.unlink(dst)


def test_rotate_pixel_values_correct():
    """Verify specific pixel positions after 90-degree clockwise rotation."""
    # 2x2 image:
    # (R,0,0) (G,0,0)
    # (B,0,0) (W,0,0)
    # After 90 CW:
    # (B,0,0) (R,0,0)
    # (W,0,0) (G,0,0)
    R, G, B, W = (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255)
    src = _make_ppm([R, G, B, W], 2, 2)
    fd, dst = tempfile.mkstemp(suffix=".ppm")
    os.close(fd)
    try:
        rotate_90(src, dst)
        img = parse_ppm_strict(dst)
        assert img.pixels[0] == B
        assert img.pixels[1] == R
        assert img.pixels[2] == W
        assert img.pixels[3] == G
    finally:
        os.unlink(src)
        os.unlink(dst)


def test_rotate_four_times_roundtrip():
    """Rotating 4 times returns to the original image."""
    pixels = [(10, 20, 30), (40, 50, 60), (70, 80, 90),
              (100, 110, 120), (130, 140, 150), (160, 170, 180)]
    src = _make_ppm(pixels, 3, 2)
    paths = [src]
    try:
        current = src
        for _ in range(4):
            fd, nxt = tempfile.mkstemp(suffix=".ppm")
            os.close(fd)
            rotate_90(current, nxt)
            paths.append(nxt)
            current = nxt
        final = parse_ppm_strict(current)
        assert final.width == 3
        assert final.height == 2
        assert final.pixels == pixels
    finally:
        for p in paths:
            os.unlink(p)


def test_rotate_single_pixel():
    """A 1x1 image stays the same after rotation."""
    src = _make_ppm([(42, 42, 42)], 1, 1)
    fd, dst = tempfile.mkstemp(suffix=".ppm")
    os.close(fd)
    try:
        result = rotate_90(src, dst)
        assert result["width"] == 1
        assert result["height"] == 1
        img = parse_ppm_strict(dst)
        assert img.pixels[0] == (42, 42, 42)
    finally:
        os.unlink(src)
        os.unlink(dst)


def test_rotate_row_becomes_column():
    """A 3x1 row becomes a 1x3 column."""
    pixels = [(1, 0, 0), (2, 0, 0), (3, 0, 0)]
    src = _make_ppm(pixels, 3, 1)
    fd, dst = tempfile.mkstemp(suffix=".ppm")
    os.close(fd)
    try:
        result = rotate_90(src, dst)
        assert result["width"] == 1
        assert result["height"] == 3
        img = parse_ppm_strict(dst)
        assert len(img.pixels) == 3
    finally:
        os.unlink(src)
        os.unlink(dst)


def test_rotate_all_black():
    """All-black image stays all-black."""
    pixels = [(0, 0, 0)] * 6
    src = _make_ppm(pixels, 3, 2)
    fd, dst = tempfile.mkstemp(suffix=".ppm")
    os.close(fd)
    try:
        rotate_90(src, dst)
        img = parse_ppm_strict(dst)
        assert all(p == (0, 0, 0) for p in img.pixels)
    finally:
        os.unlink(src)
        os.unlink(dst)


def test_rotate_invalid_file():
    """Non-PPM file raises PpmError."""
    fd, path = tempfile.mkstemp(suffix=".ppm")
    os.write(fd, b"not a ppm file")
    os.close(fd)
    fd2, dst = tempfile.mkstemp(suffix=".ppm")
    os.close(fd2)
    try:
        with pytest.raises(PpmError):
            rotate_90(path, dst)
    finally:
        os.unlink(path)
        if os.path.exists(dst):
            os.unlink(dst)


def test_rotate_nonexistent_file():
    """Nonexistent file raises PpmError."""
    fd, dst = tempfile.mkstemp(suffix=".ppm")
    os.close(fd)
    try:
        with pytest.raises(PpmError):
            rotate_90("/tmp/nonexistent_ppm_file_xyz.ppm", dst)
    finally:
        if os.path.exists(dst):
            os.unlink(dst)
