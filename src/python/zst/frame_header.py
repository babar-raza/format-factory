"""
frame_header.py — ZST frame header parsing (RFC 8878).

RFC 8878: Zstandard Compression and the 'application/zstd' Media Type

Reads the first few bytes of a ZST frame to extract header metadata without
performing full decompression. Covers:
  - Zstandard frame magic detection (0x28 0xB5 0x2F 0xFD)
  - Skippable frame magic detection (0x184D2A50-0x184D2A5F)
  - Frame Header Descriptor (FHD) byte parsing
  - Content_Size extraction (when present)
  - Dictionary ID extraction (when present)
  - Checksum flag detection

Promoted from prototypes/by-format/zst/frame_header.py (Gate 4 evidence) into
production source: zst_codec.probe_frame() needs header-declared content_size
without a full decompress, which only this parser provides (TC-PA-014).
"""

from __future__ import annotations
import struct
from dataclasses import dataclass, field
from typing import Optional

# RFC 8878 §3.1.1: Zstandard frame magic number (little-endian)
ZSTD_MAGIC = b"\x28\xb5\x2f\xfd"

# RFC 8878 §3.1.2: Skippable frame magic range (little-endian)
SKIPPABLE_MAGIC_MIN = 0x184D2A50
SKIPPABLE_MAGIC_MAX = 0x184D2A5F


@dataclass
class FrameHeaderInfo:
    """Parsed frame header metadata from a ZST file."""
    is_zstandard_frame: bool = False
    is_skippable_frame: bool = False
    is_unknown: bool = False

    # FHD byte fields (only populated for Zstandard frames)
    fcs_flag: Optional[int] = None          # Frame Content Size flag (bits 7:6)
    single_segment: Optional[bool] = None   # Single_Segment_Flag (bit 5)
    content_checksum: Optional[bool] = None # Content_Checksum_Flag (bit 2)
    dict_id_flag: Optional[int] = None      # Dictionary_ID_Flag (bits 1:0)

    # Derived fields
    content_size: Optional[int] = None      # Decompressed size (if present in header)
    dict_id: Optional[int] = None           # Dictionary ID (if present)
    content_size_present: bool = False      # True if Content_Size is in header

    raw_magic: bytes = field(default_factory=bytes)
    parse_error: Optional[str] = None


def parse_frame_header(data: bytes) -> FrameHeaderInfo:
    """
    Parse the frame header from the first bytes of a ZST file.
    Returns FrameHeaderInfo with extracted metadata.
    Does NOT decompress. Does NOT require python-zstandard.
    """
    info = FrameHeaderInfo()

    if len(data) < 4:
        info.is_unknown = True
        info.parse_error = f"Too short: {len(data)} bytes (need at least 4)"
        return info

    magic_bytes = data[:4]
    info.raw_magic = magic_bytes
    magic_le = struct.unpack("<I", magic_bytes)[0]

    # Check Zstandard frame
    if magic_bytes == ZSTD_MAGIC:
        info.is_zstandard_frame = True
        _parse_zstd_header(data, info)
        return info

    # Check skippable frame
    if SKIPPABLE_MAGIC_MIN <= magic_le <= SKIPPABLE_MAGIC_MAX:
        info.is_skippable_frame = True
        return info

    info.is_unknown = True
    info.parse_error = f"Unknown magic: {magic_bytes.hex()}"
    return info


def _parse_zstd_header(data: bytes, info: FrameHeaderInfo) -> None:
    """Parse FHD byte and subsequent header fields for a Zstandard frame."""
    if len(data) < 5:
        info.parse_error = "Frame too short for FHD byte"
        return

    fhd = data[4]  # Frame Header Descriptor byte

    # Bits [7:6] — Frame_Content_Size_flag
    info.fcs_flag = (fhd >> 6) & 0x3
    # Bit [5] — Single_Segment_Flag
    info.single_segment = bool((fhd >> 5) & 0x1)
    # Bit [2] — Content_Checksum_Flag
    info.content_checksum = bool((fhd >> 2) & 0x1)
    # Bits [1:0] — Dictionary_ID_Flag
    info.dict_id_flag = fhd & 0x3

    # Content_Size is present if FCS != 0 OR Single_Segment == 1
    content_size_present = (info.fcs_flag != 0) or info.single_segment
    info.content_size_present = content_size_present

    # Parse from byte 5 onward
    offset = 5

    # Window_Descriptor: present if Single_Segment == 0
    if not info.single_segment:
        offset += 1  # skip Window_Descriptor byte

    # Dictionary ID (0, 1, 2, or 4 bytes depending on dict_id_flag)
    did_sizes = {0: 0, 1: 1, 2: 2, 3: 4}
    did_size = did_sizes.get(info.dict_id_flag, 0)
    if did_size > 0:
        if len(data) < offset + did_size:
            info.parse_error = "Frame truncated in Dictionary_ID field"
            return
        did_bytes = data[offset:offset + did_size]
        info.dict_id = int.from_bytes(did_bytes, "little")
    offset += did_size

    # Frame Content Size (FCS)
    if content_size_present:
        # FCS size: 0→use single_segment rule, 1→1byte, 2→2bytes, 3→4or8bytes
        fcs_sizes = {0: 1 if info.single_segment else 0, 1: 1, 2: 2, 3: 4}
        # For FCS_Flag==3 and result>=256, it's 8 bytes; we detect by trying
        fcs_size = fcs_sizes.get(info.fcs_flag, 0)
        if fcs_size > 0 and len(data) >= offset + fcs_size:
            fcs_bytes = data[offset:offset + fcs_size]
            value = int.from_bytes(fcs_bytes, "little")
            # For 2-byte FCS: add 256 (RFC 8878 §3.1.1.2)
            if info.fcs_flag == 2:
                value += 256
            info.content_size = value
        elif fcs_size == 0:
            # FCS_Flag==0 and Single_Segment: content size in last block
            pass


def describe(info: FrameHeaderInfo) -> str:
    """Return a human-readable description of the frame header."""
    if info.is_unknown:
        return f"UNKNOWN frame (magic: {info.raw_magic.hex()}) — {info.parse_error or 'unrecognized'}"
    if info.is_skippable_frame:
        return f"SKIPPABLE frame (magic: {info.raw_magic.hex()})"
    lines = ["ZSTANDARD frame"]
    if info.content_size_present and info.content_size is not None:
        lines.append(f"  content_size: {info.content_size} bytes")
    else:
        lines.append("  content_size: not in header (streaming required)")
    if info.dict_id is not None:
        lines.append(f"  dictionary_id: {info.dict_id}")
    if info.content_checksum is not None:
        lines.append(f"  content_checksum: {'yes' if info.content_checksum else 'no'}")
    if info.single_segment is not None:
        lines.append(f"  single_segment: {'yes' if info.single_segment else 'no'}")
    if info.parse_error:
        lines.append(f"  parse_error: {info.parse_error}")
    return "\n".join(lines)
