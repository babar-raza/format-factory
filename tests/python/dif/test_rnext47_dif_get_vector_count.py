"""
test_rnext47_dif_get_vector_count.py

New product function: dif_parser.get_vector_count
Sprint: FORMAT-FACTORY-PROBE-COVERAGE-PRODUCT-RNEXT47-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.dif.dif_parser import get_vector_count

_DIF_3COL = """\
TABLE
0,1
"Three Columns"
VECTORS
0,3
""
TUPLES
0,2
""
DATA
0,0
""
-1,0
BOT
1,0
10
1,0
20
1,0
30
-1,0
EOD
"""

_DIF_1COL = """\
TABLE
0,1
"One Column"
VECTORS
0,1
""
TUPLES
0,1
""
DATA
0,0
""
-1,0
BOT
1,0
99
-1,0
EOD
"""


class TestGetVectorCount:
    def test_three_columns(self, tmp_path):
        f = tmp_path / "three.dif"
        f.write_text(_DIF_3COL, encoding="utf-8")
        assert get_vector_count(f) == 3

    def test_one_column(self, tmp_path):
        f = tmp_path / "one.dif"
        f.write_text(_DIF_1COL, encoding="utf-8")
        assert get_vector_count(f) == 1

    def test_returns_int(self, tmp_path):
        f = tmp_path / "data.dif"
        f.write_text(_DIF_3COL, encoding="utf-8")
        result = get_vector_count(f)
        assert isinstance(result, int)

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(Exception):
            get_vector_count(tmp_path / "ghost.dif")

    def test_consistent_with_probe_dif(self, tmp_path):
        from src.python.dif.dif_parser import probe_dif
        f = tmp_path / "data.dif"
        f.write_text(_DIF_3COL, encoding="utf-8")
        vec_count = get_vector_count(f)
        probe = probe_dif(f)
        assert vec_count == probe.get("vectors")
