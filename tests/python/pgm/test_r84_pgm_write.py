"""R84 Train M: Tests for write_pgm function."""

import sys
import os
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "python"))
from pgm.pgm_parser import write_pgm, parse_pgm_strict, PgmSizeError


class TestWritePgm:
    def test_write_1x1_black(self):
        with tempfile.NamedTemporaryFile(suffix=".pgm", delete=False) as f:
            path = f.name
        try:
            write_pgm([0], 1, 1, 255, path)
            img = parse_pgm_strict(path)
            assert img.width == 1
            assert img.height == 1
            assert img.pixels == [0]
            assert img.magic == "P2"
        finally:
            os.unlink(path)

    def test_write_1x1_white(self):
        with tempfile.NamedTemporaryFile(suffix=".pgm", delete=False) as f:
            path = f.name
        try:
            write_pgm([255], 1, 1, 255, path)
            img = parse_pgm_strict(path)
            assert img.pixels == [255]
        finally:
            os.unlink(path)

    def test_roundtrip_2x2(self):
        pixels = [0, 64, 128, 255]
        with tempfile.NamedTemporaryFile(suffix=".pgm", delete=False) as f:
            path = f.name
        try:
            write_pgm(pixels, 2, 2, 255, path)
            img = parse_pgm_strict(path)
            assert img.pixels == pixels
            assert img.width == 2
            assert img.height == 2
            assert img.maxval == 255
        finally:
            os.unlink(path)

    def test_custom_maxval(self):
        pixels = [0, 15, 63, 127]
        with tempfile.NamedTemporaryFile(suffix=".pgm", delete=False) as f:
            path = f.name
        try:
            write_pgm(pixels, 2, 2, 127, path)
            img = parse_pgm_strict(path)
            assert img.maxval == 127
            assert img.pixels == pixels
        finally:
            os.unlink(path)

    def test_write_with_comment(self):
        with tempfile.NamedTemporaryFile(suffix=".pgm", delete=False) as f:
            path = f.name
        try:
            write_pgm([128], 1, 1, 255, path, comment="my comment")
            content = open(path).read()
            assert "# my comment" in content
        finally:
            os.unlink(path)

    def test_wrong_pixel_count_raises_value_error(self):
        with tempfile.NamedTemporaryFile(suffix=".pgm", delete=False) as f:
            path = f.name
        try:
            with pytest.raises(ValueError):
                write_pgm([0, 128], 3, 3, 255, path)
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_invalid_maxval_raises_value_error(self):
        with tempfile.NamedTemporaryFile(suffix=".pgm", delete=False) as f:
            path = f.name
        try:
            with pytest.raises(ValueError):
                write_pgm([0], 1, 1, 0, path)
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_oversized_dimension_raises_pgm_size_error(self):
        with tempfile.NamedTemporaryFile(suffix=".pgm", delete=False) as f:
            path = f.name
        try:
            with pytest.raises(PgmSizeError):
                write_pgm([128], 70000, 1, 255, path)
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_output_file_is_p2(self):
        with tempfile.NamedTemporaryFile(suffix=".pgm", delete=False) as f:
            path = f.name
        try:
            write_pgm([100, 200, 50, 150], 2, 2, 255, path)
            with open(path) as f:
                first_line = f.readline().strip()
            assert first_line == "P2"
        finally:
            os.unlink(path)
