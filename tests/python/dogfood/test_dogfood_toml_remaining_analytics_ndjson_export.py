"""
tests/python/dogfood/test_dogfood_toml_remaining_analytics_ndjson_export.py

Sprint: PRODUCT-DEEPENING-SPRINT-58
Dogfood export: TOML remaining uncovered analytics -> NDJSON -> verify.
Uses: toml_avg_key_length, toml_depth, toml_numeric_density.
Note: TOML has no sample files — uses inline TOML bytes (same approach as Sprint 1).
"""
from __future__ import annotations

import json
import sys
import importlib.util
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

_spec = importlib.util.spec_from_file_location("toml_codec", str(_REPO / "src" / "python" / "toml" / "toml_codec.py"))
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

toml_avg_key_length = _mod.toml_avg_key_length
toml_depth = _mod.toml_depth
toml_numeric_density = _mod.toml_numeric_density

from ndjson.ndjson_codec import write_ndjson, load_ndjson


# Inline TOML samples (no sample files exist for TOML)
_SAMPLES = [
    (
        "flat-config",
        b'title = "app"\nversion = 1\nenabled = true\npath = "/usr"\n',
    ),
    (
        "nested-config",
        b'title = "app"\nversion = 1\n\n[database]\nhost = "localhost"\nport = 5432\n\n[features]\nlist_1 = [1, 2, 3]\nenabled = true\n',
    ),
    (
        "deep-nested",
        b'[a]\n[a.b]\n[a.b.c]\nvalue = 42\n',
    ),
    (
        "string-heavy",
        b'name = "foo"\ndesc = "bar"\ntag = "baz"\nkind = "qux"\n',
    ),
    (
        "mixed-types",
        b'count = 5\nratio = 0.75\nflag = true\nlabel = "test"\n',
    ),
]


class TestTomlRemainingAnalyticsNdjsonExport:
    """TOML remaining analytics -> NDJSON export -> roundtrip verification."""

    def test_avg_key_length_basics(self):
        # flat-config: keys = title(5), version(7), enabled(7), path(4) -> avg = 5.75
        flat = b'title = "app"\nversion = 1\nenabled = true\npath = "/usr"\n'
        # nested-config: top keys + sub keys
        nested = b'title = "app"\nversion = 1\n\n[database]\nhost = "localhost"\nport = 5432\n\n[features]\nlist_1 = [1, 2, 3]\nenabled = true\n'
        avg_flat = toml_avg_key_length(flat)
        avg_nested = toml_avg_key_length(nested)
        assert isinstance(avg_flat, float), "avg_key_length must be float"
        assert avg_flat > 0.0, "avg_key_length must be > 0 for non-empty TOML"
        assert isinstance(avg_nested, float)
        assert avg_nested > 0.0

    def test_depth_basics(self):
        flat = b'key = "value"\n'
        nested = b'[a]\n[a.b]\n[a.b.c]\nvalue = 42\n'
        assert toml_depth(flat) == 1
        assert toml_depth(nested) == 4  # a -> b -> c -> value = depth 4

    def test_numeric_density_basics(self):
        all_strings = b'a = "x"\nb = "y"\nc = "z"\nd = "w"\n'
        all_numeric = b'a = 1\nb = 2\nc = 3\nd = 4\n'
        mixed = b'a = 1\nb = "text"\nc = 3\nd = "other"\n'
        assert toml_numeric_density(all_strings) == 0.0
        assert toml_numeric_density(all_numeric) == 1.0
        assert 0.0 < toml_numeric_density(mixed) < 1.0

    def test_toml_remaining_to_ndjson(self, tmp_path):
        records = []
        for name, source in _SAMPLES:
            avg_key = toml_avg_key_length(source)
            depth = toml_depth(source)
            num_density = toml_numeric_density(source)
            assert isinstance(avg_key, (int, float)), f"avg_key_length must be numeric for {name}"
            assert isinstance(depth, int), f"depth must be int for {name}"
            assert 0.0 <= num_density <= 1.0, f"numeric_density must be in [0,1] for {name}"
            records.append({
                "name": name,
                "avg_key_length": float(avg_key),
                "depth": depth,
                "numeric_density": num_density,
                "source_format": "toml",
            })
        dest = tmp_path / "toml-remaining.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists() and dest.stat().st_size > 0
        assert len(records) == 5

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for name, source in _SAMPLES:
            records.append({
                "name": name,
                "depth": toml_depth(source),
                "numeric_density": toml_numeric_density(source),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["name"] == back["name"]
            assert orig["depth"] == back["depth"]

    def test_json_lines_valid(self, tmp_path):
        source = b'a = 1\nb = "text"\n'
        records = [{
            "name": "simple",
            "avg_key_length": toml_avg_key_length(source),
            "depth": toml_depth(source),
            "numeric_density": toml_numeric_density(source),
            "format": "toml",
        }]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)
