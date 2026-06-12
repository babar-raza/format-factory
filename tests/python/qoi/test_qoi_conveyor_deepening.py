"""
test_qoi_conveyor_deepening.py -- QOI product deepening tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-1
Tests parse, encode, probe, roundtrip for QOI codec.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from qoi.qoi_parser import (
    parse_qoi,
    parse_qoi_strict,
    probe_qoi,
    QoiImage,
    get_capabilities,
)
from qoi.qoi_encoder import encode_qoi, encode_qoi_to_file, get_encoder_capabilities


def _make_solid_image(w=2, h=2, channels=4, color=(255, 0, 0, 255)):
    pixels = [color] * (w * h)
    return QoiImage(width=w, height=h, channels=channels, colorspace=0, pixels=pixels)


def test_encode_decode_roundtrip(tmp_path):
    img = _make_solid_image()
    data = encode_qoi(img)
    fp = tmp_path / "solid.qoi"
    fp.write_bytes(data)
    result = parse_qoi(str(fp))
    assert result["ok"] is True
    assert result["width"] == 2
    assert result["height"] == 2


def test_encode_to_file(tmp_path):
    img = _make_solid_image()
    out = tmp_path / "out.qoi"
    path = encode_qoi_to_file(img, out)
    assert Path(path).exists()


def test_probe_header(tmp_path):
    img = _make_solid_image(w=4, h=3)
    fp = tmp_path / "probe.qoi"
    fp.write_bytes(encode_qoi(img))
    info = probe_qoi(str(fp))
    assert info["valid_header"] is True
    assert info["width"] == 4
    assert info["height"] == 3
    assert info["channels"] == 4


def test_probe_nonexistent():
    info = probe_qoi("/nonexistent/file.qoi")
    assert info["exists"] is False


def test_3_channel_roundtrip(tmp_path):
    img = _make_solid_image(channels=3, color=(0, 128, 255))
    fp = tmp_path / "rgb.qoi"
    fp.write_bytes(encode_qoi(img))
    decoded = parse_qoi_strict(str(fp))
    assert decoded.channels == 3
    assert decoded.pixels[0] == (0, 128, 255)


def test_gradient_roundtrip(tmp_path):
    pixels = [(i, i, i, 255) for i in range(256)]
    img = QoiImage(width=16, height=16, channels=4, colorspace=0, pixels=pixels)
    fp = tmp_path / "gradient.qoi"
    fp.write_bytes(encode_qoi(img))
    decoded = parse_qoi_strict(str(fp))
    assert decoded.pixels == pixels


def test_parse_qoi_returns_ok_false_on_bad_file(tmp_path):
    fp = tmp_path / "bad.qoi"
    fp.write_bytes(b"not a qoi file")
    result = parse_qoi(str(fp))
    assert result["ok"] is False


def test_capabilities():
    caps = get_capabilities()
    assert caps["format"] == "qoi"
    assert "full_pixel_decode" in caps["supported"]


def test_encoder_capabilities():
    caps = get_encoder_capabilities()
    assert caps["operation"] == "encode"
    assert "QOI_OP_RGB" in caps["chunk_types"]


def test_large_image_roundtrip(tmp_path):
    w, h = 64, 64
    pixels = [((x * 4) % 256, (y * 4) % 256, 128, 255) for y in range(h) for x in range(w)]
    img = QoiImage(width=w, height=h, channels=4, colorspace=0, pixels=pixels)
    fp = tmp_path / "large.qoi"
    fp.write_bytes(encode_qoi(img))
    decoded = parse_qoi_strict(str(fp))
    assert len(decoded.pixels) == w * h
    assert decoded.pixels[0] == pixels[0]


def test_linear_colorspace_roundtrip(tmp_path):
    img = QoiImage(width=2, height=2, channels=4, colorspace=1,
                   pixels=[(100, 100, 100, 255)] * 4)
    fp = tmp_path / "linear.qoi"
    fp.write_bytes(encode_qoi(img))
    decoded = parse_qoi_strict(str(fp))
    assert decoded.colorspace == 1
