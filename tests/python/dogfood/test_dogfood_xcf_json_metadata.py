"""Dogfood export: XCF → JSON metadata using Format Factory XCF library.

Demonstrates a real-world pipeline: parse XCF images, extract metadata
(dimensions, type, layers, version), and export as structured JSON.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf.xcf_parser import (
    xcf_summary,
    xcf_is_rgb,
    xcf_is_grayscale,
    xcf_is_indexed,
    xcf_layer_count,
    xcf_width,
)

SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"


class TestDogfoodXcfJsonMetadata:
    @pytest.fixture
    def xcf_files(self):
        files = list(SAMPLES.glob("*.xcf"))
        if not files:
            pytest.skip("No XCF samples available")
        return files

    def test_export_single_file_to_json(self, xcf_files, tmp_path):
        """Export a single XCF file's metadata to JSON."""
        summary = xcf_summary(xcf_files[0])
        out = tmp_path / "metadata.json"
        out.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
        loaded = json.loads(out.read_text(encoding="utf-8"))
        assert "width" in loaded
        assert "height" in loaded
        assert "version" in loaded

    def test_batch_export_all_samples(self, xcf_files, tmp_path):
        """Export metadata for all XCF samples into a single JSON array."""
        records = []
        for f in xcf_files:
            summary = xcf_summary(f)
            summary["source_file"] = f.name
            summary["color_mode"] = (
                "RGB" if xcf_is_rgb(f) else
                "Grayscale" if xcf_is_grayscale(f) else
                "Indexed" if xcf_is_indexed(f) else
                "Unknown"
            )
            records.append(summary)

        out = tmp_path / "xcf-catalog.json"
        out.write_text(json.dumps(records, indent=2, default=str), encoding="utf-8")
        loaded = json.loads(out.read_text(encoding="utf-8"))
        assert len(loaded) == len(xcf_files)
        assert all("source_file" in r for r in loaded)
        assert all("color_mode" in r for r in loaded)

    def test_exported_json_has_correct_types(self, xcf_files, tmp_path):
        """Verify JSON output has correct types for key fields."""
        summary = xcf_summary(xcf_files[0])
        out = tmp_path / "typed.json"
        out.write_text(json.dumps(summary, default=str), encoding="utf-8")
        loaded = json.loads(out.read_text(encoding="utf-8"))
        assert isinstance(loaded["width"], int)
        assert isinstance(loaded["height"], int)
        assert isinstance(loaded["num_layers"], int)
        assert isinstance(loaded["pixel_count"], int)
        assert isinstance(loaded["version"], str)

    def test_pipeline_round_trip(self, xcf_files, tmp_path):
        """Full pipeline: XCF → JSON → verify against direct API call."""
        f = xcf_files[0]
        summary = xcf_summary(f)
        json_str = json.dumps(summary, default=str)
        loaded = json.loads(json_str)
        assert loaded["width"] == xcf_width(f)
        assert loaded["num_layers"] == xcf_layer_count(f)

    def test_color_mode_detection(self, xcf_files):
        """Verify color mode trio detection works for real files."""
        for f in xcf_files:
            modes = [xcf_is_rgb(f), xcf_is_grayscale(f), xcf_is_indexed(f)]
            assert sum(modes) == 1, f"Exactly one mode should be True for {f.name}"

    def test_ndjson_export(self, xcf_files, tmp_path):
        """Export as NDJSON (one JSON object per line)."""
        out = tmp_path / "xcf-catalog.ndjson"
        lines = []
        for f in xcf_files:
            summary = xcf_summary(f)
            summary["source_file"] = f.name
            lines.append(json.dumps(summary, default=str))
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
        read_lines = out.read_text(encoding="utf-8").strip().split("\n")
        assert len(read_lines) == len(xcf_files)
        for line in read_lines:
            parsed = json.loads(line)
            assert "width" in parsed
