"""Production XLIFF 2.0/2.1 lifecycle API."""

from __future__ import annotations

from pathlib import Path
from typing import Iterator

from format_factory.core import BinarySource

from .analytics import (
    average_source_length,
    translated_segment_count,
    untranslated_segment_count,
)
from .codec import (
    SUPPORTED_VERSIONS,
    XLIFF_NAMESPACE,
    dump,
    dumps,
    load,
    loads,
    probe,
)
from .errors import (
    XliffError,
    XliffParseError,
    XliffValidationError,
    XliffWriteError,
)
from .model import (
    ExtensionNode,
    Group,
    InlineElement,
    InlineNode,
    Note,
    SegmentMapping,
    Segment,
    Unit,
    XliffDocument,
    XliffFile,
    copy_source_to_target,
    flatten_inline_content,
    join_segments,
    replace_text_slots,
    split_segment,
    text_slots,
)
from .modules import (
    STANDARD_MODULES,
    ModuleCoverage,
    ModuleInfo,
    is_production_complete,
    module_coverage_manifest,
)
from .security import XLIFF_DEFAULT_LIMITS
from .validation import validate

__all__ = [
    "STANDARD_MODULES",
    "SUPPORTED_VERSIONS",
    "XLIFF_DEFAULT_LIMITS",
    "XLIFF_NAMESPACE",
    "ExtensionNode",
    "Group",
    "InlineElement",
    "InlineNode",
    "ModuleCoverage",
    "ModuleInfo",
    "Note",
    "Segment",
    "SegmentMapping",
    "Unit",
    "XliffDocument",
    "XliffError",
    "XliffFile",
    "XliffParseError",
    "XliffValidationError",
    "XliffWriteError",
    "average_source_length",
    "copy_source_to_target",
    "dump",
    "dumps",
    "flatten_inline_content",
    "get_file_count",
    "get_unit_count",
    "is_production_complete",
    "iter_file_units",
    "load",
    "load_xliff",
    "join_segments",
    "loads",
    "module_coverage_manifest",
    "probe",
    "probe_xliff",
    "replace_text_slots",
    "roundtrip",
    "split_segment",
    "text_slots",
    "translated_segment_count",
    "untranslated_segment_count",
    "validate",
    "write_xliff",
    "xliff_installed_workflow",
]

__version__ = "0.2.0.dev0"

probe_xliff = probe
load_xliff = load
write_xliff = dumps


def iter_file_units(file: XliffFile) -> Iterator[Unit]:
    yield from file.iter_units()


def get_file_count(document: XliffDocument) -> int:
    return document.file_count


def get_unit_count(document: XliffDocument) -> int:
    return document.unit_count


def roundtrip(source: BinarySource, destination: str | Path) -> XliffDocument:
    document = load(source)
    dump(document, destination)
    return load(destination)


def xliff_installed_workflow(source: BinarySource) -> dict[str, object]:
    document = load(source)
    return {
        "format": "xliff",
        "loaded": True,
        "version": document.version,
        "file_count": document.file_count,
        "unit_count": document.unit_count,
    }
