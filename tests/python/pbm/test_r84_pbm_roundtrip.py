"""R84 Train M: Tests for write_pbm and roundtrip verification."""

import sys
import os
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "python"))
from pbm.pbm_parser import write_pbm, parse_pbm_strict, PbmSizeError


class TestWritePbm:
    def test_write_1x1_black(self):
        with tempfile.NamedTemporaryFile(suffix=".pbm", delete=False) as f:
            path = f.name
        try:
            write_pbm([1], 1, 1, path)
            img = parse_pbm_strict(path)
            assert img.width == 1
            assert img.height == 1
            assert img.pixels == [1]
            assert img.magic == "P1"
        finally:
            os.unlink(path)

    def test_write_1x1_white(self):
        with tempfile.NamedTemporaryFile(suffix=".pbm", delete=False) as f:
            path = f.name
        try:
            write_pbm([0], 1, 1, path)
            img = parse_pbm_strict(path)
            assert img.pixels == [0]
        finally:
            os.unlink(path)

    def test_write_2x2_checker(self):
        pixels = [1, 0, 0, 1]
        with tempfile.NamedTemporaryFile(suffix=".pbm", delete=False) as f:
            path = f.name
        try:
            write_pbm(pixels, 2, 2, path)
            img = parse_pbm_strict(path)
            assert img.width == 2
            assert img.height == 2
            assert img.pixels == pixels
        finally:
            os.unlink(path)

    def test_write_with_comment(self):
        with tempfile.NamedTemporaryFile(suffix=".pbm", delete=False) as f:
            path = f.name
        try:
            write_pbm([1], 1, 1, path, comment="test comment")
            content = open(path).read()
            assert "# test comment" in content
        finally:
            os.unlink(path)

    def test_roundtrip_3x2_pattern(self):
        pixels = [1, 0, 1, 0, 1, 0]
        with tempfile.NamedTemporaryFile(suffix=".pbm", delete=False) as f:
            path = f.name
        try:
            write_pbm(pixels, 3, 2, path)
            img = parse_pbm_strict(path)
            assert img.pixels == pixels
            assert img.width == 3
            assert img.height == 2
        finally:
            os.unlink(path)

    def test_wrong_pixel_count_raises_value_error(self):
        with tempfile.NamedTemporaryFile(suffix=".pbm", delete=False) as f:
            path = f.name
        try:
            with pytest.raises(ValueError):
                write_pbm([1, 0], 3, 3, path)  # 2 pixels for 3x3=9
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_oversized_dimension_raises_pbm_size_error(self):
        with tempfile.NamedTemporaryFile(suffix=".pbm", delete=False) as f:
            path = f.name
        try:
            with pytest.raises(PbmSizeError):
                write_pbm([1], 70000, 1, path)
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_output_file_is_ascii_p1(self):
        with tempfile.NamedTemporaryFile(suffix=".pbm", delete=False) as f:
            path = f.name
        try:
            write_pbm([1, 0, 0, 1], 2, 2, path)
            with open(path) as f:
                first_line = f.readline().strip()
            assert first_line == "P1"
        finally:
            os.unlink(path)
