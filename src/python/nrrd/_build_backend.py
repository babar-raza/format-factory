"""Setuptools PEP 517 adapter with canonical source-distribution archives.

visibility: generated
generated_by: codex
"""

from __future__ import annotations

import gzip
import os
import tarfile
from io import BytesIO
from pathlib import Path
from typing import Any

from setuptools import build_meta as _setuptools


def _epoch() -> int:
    value = os.environ.get("SOURCE_DATE_EPOCH", "315532800")
    try:
        epoch = int(value)
    except ValueError as exc:
        raise ValueError("SOURCE_DATE_EPOCH must be an integer") from exc
    if epoch < 0:
        raise ValueError("SOURCE_DATE_EPOCH must be non-negative")
    return epoch


def _canonicalize_sdist(path: Path) -> None:
    entries: list[tuple[tarfile.TarInfo, bytes | None]] = []
    with tarfile.open(path, mode="r:gz") as source:
        for member in source.getmembers():
            stream = source.extractfile(member) if member.isfile() else None
            entries.append((member, stream.read() if stream is not None else None))

    temporary = path.with_name(f".{path.name}.normalized")
    epoch = _epoch()
    with temporary.open("wb") as raw:
        with gzip.GzipFile(
            filename="", mode="wb", compresslevel=9, fileobj=raw, mtime=epoch
        ) as compressed:
            with tarfile.open(
                fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT
            ) as target:
                for original, content in sorted(entries, key=lambda item: item[0].name):
                    member = tarfile.TarInfo(original.name)
                    member.type = original.type
                    member.linkname = original.linkname
                    member.mode = 0o755 if original.isdir() else 0o644
                    member.mtime = epoch
                    member.uid = member.gid = 0
                    member.uname = member.gname = ""
                    if content is not None:
                        member.size = len(content)
                        target.addfile(member, BytesIO(content))
                    else:
                        target.addfile(member)
    os.replace(temporary, path)


def build_sdist(
    sdist_directory: str, config_settings: dict[str, Any] | None = None
) -> str:
    filename = _setuptools.build_sdist(sdist_directory, config_settings)
    _canonicalize_sdist(Path(sdist_directory, filename))
    return filename


def build_wheel(
    wheel_directory: str,
    config_settings: dict[str, Any] | None = None,
    metadata_directory: str | None = None,
) -> str:
    return _setuptools.build_wheel(wheel_directory, config_settings, metadata_directory)


def build_editable(
    wheel_directory: str,
    config_settings: dict[str, Any] | None = None,
    metadata_directory: str | None = None,
) -> str:
    return _setuptools.build_editable(wheel_directory, config_settings, metadata_directory)


get_requires_for_build_sdist = _setuptools.get_requires_for_build_sdist
get_requires_for_build_wheel = _setuptools.get_requires_for_build_wheel
get_requires_for_build_editable = _setuptools.get_requires_for_build_editable
prepare_metadata_for_build_wheel = _setuptools.prepare_metadata_for_build_wheel
prepare_metadata_for_build_editable = _setuptools.prepare_metadata_for_build_editable
