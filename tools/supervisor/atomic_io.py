"""
atomic_io.py — Atomic file write utilities for supervisor state files.

Guarantees that state files are either fully written (new content) or unchanged
(prior content) — never partially written. Uses write-to-temp + os.replace(),
which is atomic within the same filesystem on NTFS and POSIX.

REQ-AIO-001: All state file writes must be atomic
REQ-AIO-002: Atomic writes must work on Windows NTFS (same drive, same directory)
REQ-AIO-003: Atomic write failure must not silently corrupt target file
"""
import json
import os
import tempfile
from pathlib import Path
from typing import Any


def atomic_write_json(path: "str | Path", data: dict, **json_kwargs) -> None:
    """Write data as JSON to path atomically (write-to-temp then os.replace).

    The target file is either fully written with new content or left unchanged.
    On failure, any temporary file is cleaned up.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str, **json_kwargs)
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def atomic_write_text(path: "str | Path", content: str) -> None:
    """Write text content to path atomically (write-to-temp then os.replace).

    The target file is either fully written with new content or left unchanged.
    On failure, any temporary file is cleaned up.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
