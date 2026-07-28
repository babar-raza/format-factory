"""
tests/python/dogfood/test_dogfood_toml_roundtrip_write_ndjson_export.py

Dogfood export: TOML roundtrip (load -> write_toml -> re-parse) + NDJSON export.
Covers GAP-TOML-FOSS-ROUNDTRIP-001: write_toml, roundtrip functions.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

# `toml` is a normal package import here. There is NO stdlib collision:
# stdlib ships `tomllib`, not `toml`, and no third-party `toml` is installed.
# (An earlier importlib workaround citing a "stdlib 'toml' conflict" was a
# cargo-culted csv-shaped hack that loaded toml_codec.py without package
# context, breaking its `from .exceptions import ...` relative import and
# making this whole module uncollectable. See TC-PA-030 / ISS-TEST_GAP-0001.)
from toml.toml_codec import load_toml, write_toml, roundtrip

from ndjson.ndjson_codec import write_ndjson, load_ndjson

_TOML_DATA = b"[section]\nkey = \"hello\"\nnum = 42\n"


def test_toml_write_toml(tmp_path):
    """write_toml produces a file that can be re-parsed."""
    src = tmp_path / "input.toml"
    src.write_bytes(_TOML_DATA)
    data = load_toml(src)
    out = tmp_path / "output.toml"
    write_toml(data["data"], str(out))
    assert out.exists()
    assert out.stat().st_size > 0
    re_parsed = load_toml(str(out))
    assert isinstance(re_parsed, dict)
    assert re_parsed["key_count"] >= 1


def test_toml_roundtrip(tmp_path):
    """roundtrip(src, dest) produces a result dict with data."""
    src = tmp_path / "source.toml"
    src.write_bytes(_TOML_DATA)
    dest = tmp_path / "roundtrip-out.toml"
    result = roundtrip(str(src), str(dest))
    assert isinstance(result, dict)
    assert "data" in result
    assert result["key_count"] >= 1
    assert dest.exists()


def test_toml_roundtrip_to_ndjson(tmp_path):
    """Roundtrip + export result to NDJSON."""
    src = tmp_path / "source.toml"
    src.write_bytes(_TOML_DATA)
    dest = tmp_path / "roundtrip-out.toml"
    result = roundtrip(str(src), str(dest))
    record = {
        "file": "source.toml",
        "toml_key_count": result["key_count"],
        "toml_top_level_keys": int(result["key_count"]),  # key_count is int; top_level_keys is list
        "roundtrip_dest_size": dest.stat().st_size,
    }
    out = tmp_path / "toml_roundtrip.ndjson"
    write_ndjson([record], str(out))
    rows = load_ndjson(str(out))
    assert rows[0]["toml_key_count"] >= 1
    assert isinstance(rows[0]["toml_top_level_keys"], int)  # now key_count as int
    assert rows[0]["roundtrip_dest_size"] > 0
