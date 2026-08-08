"""product-goal.yaml's own "resource" completion invariant -- the writer's
own max_output_bytes ceiling.

Found while consolidating safetensors' existing resource-limit evidence
into a dedicated certification-gate record: SAFETENSORS_LIMITS
(security/limits.py) already declares max_output_bytes=512 MiB, and the
reader already enforces its own max_input_bytes/max_header_bytes/
max_entries/max_tensor_count/max_nesting_depth ceilings -- but dumps()/
dump() never consulted max_output_bytes at all, confirmed directly by
reading writer.py before this fix (no `limits` parameter existed on
either function). A caller building an oversized in-memory document had
no way to bound the writer's own output, unlike every other resource
dimension this format already governs on the read side.

dumps() now accepts an optional `limits` keyword (defaulting to
SAFETENSORS_LIMITS, the same effective_limits() resolution every other
entry point in this package already uses) and enforces max_output_bytes
against the final encoded byte length -- header length-prefix, header
JSON, and every tensor's payload combined -- before returning, matching
the identical pattern already proven for ipynb's own writer
(codec/writer/writer.py::IPYNB_DEFAULT_LIMITS.enforce("max_output_bytes",
...)) earlier this session.
"""

from __future__ import annotations

import dataclasses

import pytest

from format_factory.core import ResourceLimitError, ResourceLimits
from format_factory.safetensors import (
    DType,
    SafeTensorsDocument,
    TensorDescriptor,
    dump,
    dumps,
)
from format_factory.safetensors.security import SAFETENSORS_LIMITS


def _document() -> SafeTensorsDocument:
    descriptor = TensorDescriptor(name="w", dtype=DType.F32, shape=(2,), data_offsets=(0, 8))
    return SafeTensorsDocument(
        tensors={"w": descriptor}, payload=b"\x00\x00\x80?\x00\x00\x00@"
    )


def test_default_limits_permit_a_small_document():
    with _document() as document:
        result = dumps(document)
    assert len(result) > 0


def test_a_document_exceeding_max_output_bytes_is_refused():
    tiny = dataclasses.replace(SAFETENSORS_LIMITS, max_output_bytes=10)
    with _document() as document:
        with pytest.raises(ResourceLimitError, match="max_output_bytes"):
            dumps(document, limits=tiny)


def test_a_document_within_an_explicit_larger_limit_still_writes():
    generous = dataclasses.replace(SAFETENSORS_LIMITS, max_output_bytes=1_000_000)
    with _document() as document:
        result = dumps(document, limits=generous)
    assert len(result) > 0


def test_dump_to_a_path_also_enforces_the_limit(tmp_path):
    tiny = dataclasses.replace(SAFETENSORS_LIMITS, max_output_bytes=10)
    destination = tmp_path / "out.safetensors"
    with _document() as document:
        with pytest.raises(ResourceLimitError, match="max_output_bytes"):
            dump(document, destination, limits=tiny)
    assert not destination.exists()


def test_the_refusal_message_names_both_the_actual_and_allowed_size():
    tiny = ResourceLimits(max_output_bytes=10)
    with _document() as document:
        with pytest.raises(ResourceLimitError) as excinfo:
            dumps(document, limits=tiny)
    assert "10" in str(excinfo.value)
