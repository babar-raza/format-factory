"""Dogfood: PGM + PPM deepening analytics -> NDJSON export."""
from __future__ import annotations
import json, sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))


class TestPgmPpmDeepeningExport:
    def test_multiformat_analytics_export(self, tmp_path):
        from ndjson.ndjson_codec import write_ndjson, load_ndjson
        records = []

        pgm_files = sorted((_REPO / "samples" / "by-format" / "pgm" / "valid").glob("*.pgm"))
        if pgm_files:
            from pgm import pgm_perimeter, pgm_unique_value_count
            s = str(pgm_files[0])
            records.append({
                "format": "pgm",
                "perimeter": pgm_perimeter(s),
                "unique_values": pgm_unique_value_count(s),
            })

        ppm_files = sorted((_REPO / "samples" / "by-format" / "ppm" / "valid").glob("*.ppm"))
        if ppm_files:
            from ppm import ppm_unique_color_count, ppm_perimeter
            s = str(ppm_files[0])
            records.append({
                "format": "ppm",
                "unique_colors": ppm_unique_color_count(s),
                "perimeter": ppm_perimeter(s),
            })

        assert len(records) == 2
        out = tmp_path / "pgm-ppm-deepening.ndjson"
        write_ndjson(records, str(out))
        loaded = load_ndjson(str(out))
        assert len(loaded) == 2
        assert {r["format"] for r in loaded} == {"pgm", "ppm"}

    def test_all_records_valid_json(self, tmp_path):
        from ndjson.ndjson_codec import write_ndjson
        from pgm import pgm_perimeter
        from ppm import ppm_perimeter

        records = []
        pgm_files = sorted((_REPO / "samples" / "by-format" / "pgm" / "valid").glob("*.pgm"))
        if pgm_files:
            records.append({"metric": "pgm_perimeter", "value": pgm_perimeter(str(pgm_files[0]))})
        ppm_files = sorted((_REPO / "samples" / "by-format" / "ppm" / "valid").glob("*.ppm"))
        if ppm_files:
            records.append({"metric": "ppm_perimeter", "value": ppm_perimeter(str(ppm_files[0]))})

        out = tmp_path / "metrics.ndjson"
        write_ndjson(records, str(out))
        for line in out.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert "metric" in obj
            assert "value" in obj
