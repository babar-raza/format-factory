"""
tests/python/dogfood/test_dogfood_ods_cell_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-13
Dogfood export: ODS parse -> extract cell metadata -> write as NDJSON -> verify.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods import count_sheets, get_cell_count, count_nonempty_cells
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"


class TestOdsCellNdjsonExport:
    """ODS -> cell metadata extraction -> NDJSON export -> roundtrip verification."""

    def test_count_sheets(self):
        sample = str(_ODS_DIR / "minimal-spreadsheet.ods")
        assert count_sheets(sample) >= 1

    def test_cell_count(self):
        sample = str(_ODS_DIR / "minimal-spreadsheet.ods")
        assert get_cell_count(sample) >= 1

    def test_cell_metadata_to_ndjson(self, tmp_path):
        records = []
        for f in sorted(_ODS_DIR.glob("*.ods")):
            records.append({
                "file": f.name,
                "sheets": count_sheets(str(f)),
                "cells": get_cell_count(str(f)),
                "nonempty": count_nonempty_cells(str(f)),
                "source_format": "ods",
            })
        dest = tmp_path / "ods-cells.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in sorted(_ODS_DIR.glob("*.ods")):
            records.append({
                "file": f.name,
                "sheets": count_sheets(str(f)),
                "cells": get_cell_count(str(f)),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["sheets"] == back["sheets"]
            assert orig["cells"] == back["cells"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_ODS_DIR / "single-cell.ods")
        records = [{"file": "single-cell.ods", "cells": get_cell_count(sample), "format": "ods"}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_nonempty_cell_ratio(self, tmp_path):
        records = []
        for f in sorted(_ODS_DIR.glob("*.ods")):
            total = get_cell_count(str(f))
            nonempty = count_nonempty_cells(str(f))
            records.append({
                "file": f.name,
                "total_cells": total,
                "nonempty_cells": nonempty,
                "fill_ratio": nonempty / total if total > 0 else 0.0,
            })
        dest = tmp_path / "ratio.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(0 <= r["fill_ratio"] <= 1.0 for r in loaded)
