"""
qoi_encoder.py — QOI (Quite OK Image) encoder for format-factory-qoi.

Public API:
  encode_qoi(image)           — returns QOI bytes from QoiImage
  encode_qoi_to_file(image, output_path) — writes QOI file

Implements the QOI encoding algorithm (greedy, all 6 chunk types).
R33 deepening deliverable — first write capability for QOI.

Reference: https://qoiformat.org/qoi-specification.pdf

License: Apache-2.0
"""

from __future__ import annotations

import struct
from pathlib import Path
from typing import Any

from .qoi_parser import (
    QoiImage,
    QoiError,
    QOI_MAGIC,
    QOI_HEADER_SIZE,
    QOI_END_MARKER,
    MAX_DIMENSION,
    MAX_PIXELS,
    _color_hash,
)


class QoiEncodeError(QoiError):
    """Raised when encoding fails."""


def _validate_image(image: QoiImage) -> None:
    """Validate a QoiImage for encoding."""
    if image.width <= 0 or image.height <= 0:
        raise QoiEncodeError(
            f"Invalid dimensions: {image.width}x{image.height}"
        )
    if image.width > MAX_DIMENSION or image.height > MAX_DIMENSION:
        raise QoiEncodeError(
            f"Dimensions {image.width}x{image.height} exceed limit {MAX_DIMENSION}"
        )
    if image.width * image.height > MAX_PIXELS:
        raise QoiEncodeError(
            f"Pixel count {image.width * image.height} exceeds limit {MAX_PIXELS}"
        )
    if image.channels not in (3, 4):
        raise QoiEncodeError(f"Invalid channels: {image.channels}")
    if image.colorspace not in (0, 1):
        raise QoiEncodeError(f"Invalid colorspace: {image.colorspace}")

    expected = image.width * image.height
    if len(image.pixels) != expected:
        raise QoiEncodeError(
            f"Pixel count {len(image.pixels)} != expected {expected}"
        )

    for i, px in enumerate(image.pixels):
        if len(px) != image.channels:
            raise QoiEncodeError(
                f"Pixel {i} has {len(px)} channels, expected {image.channels}"
            )


def encode_qoi(image: QoiImage) -> bytes:
    """Encode a QoiImage to QOI format bytes.

    Uses greedy encoding: tries QOI_OP_RUN, QOI_OP_INDEX, QOI_OP_DIFF,
    QOI_OP_LUMA, then falls back to QOI_OP_RGB/QOI_OP_RGBA.

    Args:
        image: QoiImage with pixels populated.

    Returns:
        QOI file bytes (header + chunks + end marker).

    Raises:
        QoiEncodeError: If image is invalid.
    """
    _validate_image(image)

    # Build header
    header = QOI_MAGIC + struct.pack(
        ">IIBB", image.width, image.height, image.channels, image.colorspace
    )

    # Encode pixels
    chunks = bytearray()
    index = [(0, 0, 0, 0)] * 64
    prev_r, prev_g, prev_b, prev_a = 0, 0, 0, 255
    run = 0

    for px in image.pixels:
        if image.channels == 3:
            r, g, b = px
            a = 255
        else:
            r, g, b, a = px

        # Check for run
        if r == prev_r and g == prev_g and b == prev_b and a == prev_a:
            run += 1
            if run == 62:
                chunks.append(0xC0 | (run - 1))
                run = 0
            continue

        # Flush pending run
        if run > 0:
            chunks.append(0xC0 | (run - 1))
            run = 0

        # Check index
        idx = _color_hash(r, g, b, a)
        if index[idx] == (r, g, b, a):
            chunks.append(0x00 | idx)
            prev_r, prev_g, prev_b, prev_a = r, g, b, a
            continue

        index[idx] = (r, g, b, a)

        if a == prev_a:
            # Try QOI_OP_DIFF
            dr = (r - prev_r) & 0xFF
            dg = (g - prev_g) & 0xFF
            db = (b - prev_b) & 0xFF
            # Convert to signed
            if dr > 127:
                dr -= 256
            if dg > 127:
                dg -= 256
            if db > 127:
                db -= 256

            if -2 <= dr <= 1 and -2 <= dg <= 1 and -2 <= db <= 1:
                chunks.append(
                    0x40 | ((dr + 2) << 4) | ((dg + 2) << 2) | (db + 2)
                )
                prev_r, prev_g, prev_b, prev_a = r, g, b, a
                continue

            # Try QOI_OP_LUMA
            dr_dg = dr - dg
            db_dg = db - dg
            if -32 <= dg <= 31 and -8 <= dr_dg <= 7 and -8 <= db_dg <= 7:
                chunks.append(0x80 | (dg + 32))
                chunks.append(((dr_dg + 8) << 4) | (db_dg + 8))
                prev_r, prev_g, prev_b, prev_a = r, g, b, a
                continue

            # Fall back to QOI_OP_RGB
            chunks.append(0xFE)
            chunks.extend([r, g, b])
        else:
            # QOI_OP_RGBA
            chunks.append(0xFF)
            chunks.extend([r, g, b, a])

        prev_r, prev_g, prev_b, prev_a = r, g, b, a

    # Flush final run
    if run > 0:
        chunks.append(0xC0 | (run - 1))

    return header + bytes(chunks) + QOI_END_MARKER


def encode_qoi_to_file(image: QoiImage, output_path: str | Path) -> str:
    """Encode a QoiImage and write to a file.

    Args:
        image: QoiImage with pixels populated.
        output_path: Path to write the QOI file.

    Returns:
        Absolute path of the written file.

    Raises:
        QoiEncodeError: If encoding fails.
    """
    data = encode_qoi(image)
    path = Path(output_path)
    path.write_bytes(data)
    return str(path.resolve())


def get_encoder_capabilities() -> dict[str, Any]:
    """Return capability declarations for QOI encoder."""
    return {
        "format": "qoi",
        "operation": "encode",
        "chunk_types": [
            "QOI_OP_RGB",
            "QOI_OP_RGBA",
            "QOI_OP_INDEX",
            "QOI_OP_DIFF",
            "QOI_OP_LUMA",
            "QOI_OP_RUN",
        ],
        "features": [
            "greedy_encoding",
            "3_channel_mode",
            "4_channel_mode",
            "srgb_colorspace",
            "linear_colorspace",
            "end_marker",
            "round_trip_with_decoder",
            "file_output",
        ],
        "limitations": [
            "no_streaming_encode",
            "no_animation",
            "no_metadata_embedding",
        ],
        "max_dimension": MAX_DIMENSION,
        "max_pixels": MAX_PIXELS,
    }
