"""Production NRRD lifecycle API."""

from __future__ import annotations

from ._convenience import (
    decode_nrrd_data,
    encode_nrrd_data,
    get_array,
    get_dimension,
    get_encoding,
    load_nrrd,
    nrrd_installed_workflow,
    preservation_report,
    probe_nrrd,
    roundtrip,
    write_nrrd,
)
from .analytics import axis_sizes, element_count, is_compressed
from .codec import (
    NrrdHeader,
    NrrdLazyPayload,
    PayloadAccess,
    PayloadAccessMode,
    dump,
    dump_detached,
    dump_multifile,
    dump_multifile_printf,
    dumps,
    load,
    loads,
    open_lazy_payload,
    probe,
    read_header,
)
from .codec.payload import available_encodings
from .convert import (
    AttachmentConversionReport,
    ConversionReport,
    EncodingConversionReport,
    OverflowPolicy,
    RoundingPolicy,
    convert_dtype,
    convert_encoding,
    convert_endian,
    convert_to_attached,
    convert_to_detached_list,
    convert_to_detached_printf,
)
from .errors import NrrdArrayError, NrrdError, NrrdParseError, NrrdWriteError
from .measurement_frame import (
    MeasurementFrameTransform,
    build_measurement_frame_transform,
)
from .space import (
    SpaceTransform,
    build_space_transform,
    named_space_dimension,
    parse_space_directions,
    parse_space_origin,
)
from .model import (
    DOMAIN_KINDS,
    AxisMetadata,
    AxisOrderReport,
    NrrdArrayView,
    NrrdDocument,
    NrrdDtype,
    PreservationIssue,
    PreservationReport,
    array_view,
    axis_order_report,
    flatten_nrrd_array,
    reshape_nrrd_array,
)
from .security import NRRD_DEFAULT_LIMITS
from .validation import validate

__all__ = [
    "AttachmentConversionReport",
    "AxisMetadata",
    "AxisOrderReport",
    "ConversionReport", "DOMAIN_KINDS", "EncodingConversionReport",
    "MeasurementFrameTransform",
    "NRRD_DEFAULT_LIMITS", "NrrdArrayError", "NrrdArrayView", "NrrdDocument", "NrrdDtype",
    "NrrdError", "NrrdHeader", "NrrdLazyPayload", "NrrdParseError",
    "NrrdWriteError", "OverflowPolicy", "PayloadAccess", "PayloadAccessMode",
    "PreservationIssue", "PreservationReport", "RoundingPolicy",
    "SpaceTransform",
    "array_view",
    "available_encodings",
    "axis_order_report",
    "axis_sizes", "build_measurement_frame_transform", "build_space_transform",
    "convert_dtype", "convert_encoding",
    "convert_endian", "convert_to_attached", "convert_to_detached_list",
    "convert_to_detached_printf",
    "decode_nrrd_data", "dump", "dump_detached", "dump_multifile", "dump_multifile_printf",
    "dumps", "element_count",
    "encode_nrrd_data",
    "flatten_nrrd_array",
    "get_array", "get_dimension", "get_encoding", "is_compressed", "load",
    "load_nrrd", "loads", "named_space_dimension", "nrrd_installed_workflow",
    "open_lazy_payload",
    "parse_space_directions", "parse_space_origin", "preservation_report",
    "probe", "probe_nrrd", "read_header", "reshape_nrrd_array", "roundtrip",
    "validate", "write_nrrd",
]

__version__ = "0.2.0.dev0"
