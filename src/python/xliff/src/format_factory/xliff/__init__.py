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
    LossReport,
    PreservationMode,
    canonicalize,
    check_preservation,
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
from .merge import (
    MergeAdapter,
    Skeleton,
    SourceDriftError,
    TemplateMergeAdapter,
    check_drift,
    compute_source_digest,
    merge_with_drift_check,
)
from .model import (
    DataElement,
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
from .qa import (
    QA_CHECKS,
    check_missing_targets,
    check_placeholder_mismatch,
    check_source_language_compatibility,
    check_target_language_compatibility,
    check_translation_consistency,
    check_unchanged_targets,
    check_whitespace_punctuation_drift,
    run_qa_checks,
)
from .security import XLIFF_DEFAULT_LIMITS
from .state_transitions import (
    DEFAULT_STATE,
    TransitionPolicy,
    TransitionReport,
    TransitionViolation,
    check_state_transitions,
)
from .validation import validate

__all__ = [
    "MergeAdapter",
    "QA_CHECKS",
    "Skeleton",
    "SourceDriftError",
    "STANDARD_MODULES",
    "SUPPORTED_VERSIONS",
    "TemplateMergeAdapter",
    "DEFAULT_STATE",
    "TransitionPolicy",
    "TransitionReport",
    "TransitionViolation",
    "XLIFF_DEFAULT_LIMITS",
    "XLIFF_NAMESPACE",
    "DataElement",
    "ExtensionNode",
    "Group",
    "InlineElement",
    "InlineNode",
    "LossReport",
    "ModuleCoverage",
    "ModuleInfo",
    "Note",
    "PreservationMode",
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
    "canonicalize",
    "check_drift",
    "check_missing_targets",
    "check_placeholder_mismatch",
    "check_preservation",
    "check_source_language_compatibility",
    "check_state_transitions",
    "check_target_language_compatibility",
    "check_translation_consistency",
    "check_unchanged_targets",
    "check_whitespace_punctuation_drift",
    "compute_source_digest",
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
    "merge_with_drift_check",
    "module_coverage_manifest",
    "probe",
    "probe_xliff",
    "replace_text_slots",
    "roundtrip",
    "run_qa_checks",
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
