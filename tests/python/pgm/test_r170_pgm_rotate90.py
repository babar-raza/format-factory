"""Tests for PGM rotate_90 API.

Sprint: PRODUCT-API-BROADENING-20260612
Skill: /add-python-api
Format: PGM
API: rotate_90
"""

from __future__ import annotations

import os
import tempfile

import pytest

from src.python.pgm.pgm_parser import (
    rotate_90,
    parse_pgm_strict,
    write_pgm,
    PgmError,
)


def _make_pgm(pixels, width, height, maxval=255):
    """Create a temporary PGM file and return path."""
    fd, path = tempfile.mkstemp(suffix=".pgm")
    os.close(fd)
    write_pgm(pixels, width, height, maxval, path)
    return path


def test_rotate_dimensions_swap():
    """A 3x2 image becomes 2x3 after rotation."""
    pixels = [10, 20, 30, 40, 50, 60]
    src = _make_pgm(pixels, 3, 2)
    fd, dst = tempfile.mkstemp(suffix=".pgm")
    os.close(fd)
    try:
        result = rotate_90(src, dst)
        assert result["ok"] is True
        assert result["width"] == 2
        assert result["height"] == 3
        img = parse_pgm_strict(dst)
        assert img.width == 2
        assert img.height == 3
    finally:
        os.unlink(src)
        os.unlink(dst)


def test_rotate_pixel_values_correct():
    """Verify specific pixel positions after 90-degree clockwise rotation."""
    # 2x2: [A B / C D] -> [C A / D B]
    pixels = [10, 20, 30, 40]
    src = _make_pgm(pixels, 2, 2)
    fd, dst = tempfile.mkstemp(suffix=".pgm")
    os.close(fd)
    try:
        rotate_90(src, dst)
        img = parse_pgm_strict(dst)
        assert img.pixels[0] == 30  # C
        assert img.pixels[1] == 10  # A
        assert img.pixels[2] == 40  # D
        assert img.pixels[3] == 20  # B
    finally:
        os.unlink(src)
        os.unlink(dst)


def test_rotate_four_times_roundtrip():
    """Rotating 4 times returns to the original image."""
    pixels = [10, 20, 30, 40, 50, 60]
    src = _make_pgm(pixels, 3, 2)
    paths = [src]
    try:
        current = src
        for _ in range(4):
            fd, nxt = tempfile.mkstemp(suffix=".pgm")
            os.close(fd)
            rotate_90(current, nxt)
            paths.append(nxt)
            current = nxt
        final = parse_pgm_strict(current)
        assert final.width == 3
        assert final.height == 2
        assert final.pixels == pixels
    finally:
        for p in paths:
            os.unlink(p)


def test_rotate_single_pixel():
    """A 1x1 image stays the same after rotation."""
    src = _make_pgm([42], 1, 1)
    fd, dst = tempfile.mkstemp(suffix=".pgm")
    os.close(fd)
    try:
        result = rotate_90(src, dst)
        assert result["width"] == 1
        assert result["height"] == 1
        img = parse_pgm_strict(dst)
        assert img.pixels[0] == 42
    finally:
        os.unlink(src)
        os.unlink(dst)


def test_rotate_row_becomes_column():
    """A 3x1 row becomes a 1x3 column."""
    pixels = [10, 20, 30]
    src = _make_pgm(pixels, 3, 1)
    fd, dst = tempfile.mkstemp(suffix=".pgm")
    os.close(fd)
    try:
        result = rotate_90(src, dst)
        assert result["width"] == 1
        assert result["height"] == 3
        img = parse_pgm_strict(dst)
        assert len(img.pixels) == 3
    finally:
        os.unlink(src)
        os.unlink(dst)


def test_rotate_all_black():
    """All-zero image stays all-zero."""
    pixels = [0] * 6
    src = _make_pgm(pixels, 3, 2)
    fd, dst = tempfile.mkstemp(suffix=".pgm")
    os.close(fd)
    try:
        rotate_90(src, dst)
        img = parse_pgm_strict(dst)
        assert all(p == 0 for p in img.pixels)
    finally:
        os.unlink(src)
        os.unlink(dst)


def test_rotate_invalid_file():
    """Non-PGM file raises PgmError."""
    fd, path = tempfile.mkstemp(suffix=".pgm")
    os.write(fd, b"not a pgm file")
    os.close(fd)
    fd2, dst = tempfile.mkstemp(suffix=".pgm")
    os.close(fd2)
    try:
        with pytest.raises(PgmError):
            rotate_90(path, dst)
    finally:
        os.unlink(path)
        if os.path.exists(dst):
            os.unlink(dst)


def test_rotate_nonexistent_file():
    """Nonexistent file raises PgmError."""
    fd, dst = tempfile.mkstemp(suffix=".pgm")
    os.close(fd)
    try:
        with pytest.raises(PgmError):
            rotate_90("/tmp/nonexistent_pgm_file_xyz.pgm", dst)
    finally:
        if os.path.exists(dst):
            os.unlink(dst)
