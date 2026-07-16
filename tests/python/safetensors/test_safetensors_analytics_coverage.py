"""Comprehensive coverage tests for the safetensors package's public surface.

Consolidates coverage across the full public API in one file: probe/load/write/
roundtrip, all tensor accessors (get_tensor, get_tensor_bytes, get_tensor_count,
get_tensor_names), the error class hierarchy, SafetensorsDocument, the analytics
module (safetensors_dtype_histogram, safetensors_total_tensor_bytes,
safetensors_largest_tensor_name), and the package's top-level __init__ exports.

This file intentionally exercises the same functions already covered by
test_safetensors_codec.py / test_safetensors_analytics.py / test_safetensors_tensor_data.py
from a different angle (full-surface smoke coverage, cross-function consistency,
and package-export integrity) rather than re-testing identical scenarios.
"""

from __future__ import annotations

import inspect
import json
import struct
import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

SAMPLES = _REPO / "samples" / "by-format" / "safetensors"
VALID_DIR = SAMPLES / "valid"
INVALID_DIR = SAMPLES / "invalid"

VALID_SAMPLE_FILES = sorted(VALID_DIR.glob("*.safetensors"))


# ---------------------------------------------------------------------------
# Imports — verified individually so a single missing symbol produces a
# targeted skip rather than an import-time collection failure for the module.
# ---------------------------------------------------------------------------

try:
    from safetensors.safetensors_codec import (
        get_tensor,
        get_tensor_bytes,
        get_tensor_count,
        get_tensor_names,
        load_safetensors,
        probe_safetensors,
        roundtrip,
        safetensors_installed_workflow,
        write_safetensors,
    )

    _CODEC_IMPORTED = True
except ImportError:
    _CODEC_IMPORTED = False

try:
    from safetensors.exceptions import (
        SafetensorsError,
        SafetensorsParseError,
        SafetensorsWriteError,
    )

    _EXCEPTIONS_IMPORTED = True
except ImportError:
    _EXCEPTIONS_IMPORTED = False

try:
    from safetensors.models import SafetensorsDocument

    _DOCUMENT_IMPORTED = True
except ImportError:
    _DOCUMENT_IMPORTED = False

try:
    from safetensors.safetensors_analytics import (
        safetensors_dtype_histogram,
        safetensors_largest_tensor_name,
        safetensors_total_tensor_bytes,
    )

    _ANALYTICS_IMPORTED = True
except ImportError:
    _ANALYTICS_IMPORTED = False


def _require_codec():
    if not _CODEC_IMPORTED:
        pytest.skip("safetensors_codec functions not found in source")


def _require_exceptions():
    if not _EXCEPTIONS_IMPORTED:
        pytest.skip("safetensors exception classes not found in source")


def _require_document():
    if not _DOCUMENT_IMPORTED:
        pytest.skip("SafetensorsDocument not found in source")


def _require_analytics():
    if not _ANALYTICS_IMPORTED:
        pytest.skip("safetensors analytics functions not found in source")


def _build_minimal_bytes(tensors: dict, metadata: dict | None = None) -> bytes:
    """Build a minimal valid safetensors byte blob for a given tensor header."""
    header = dict(tensors)
    if metadata:
        header["__metadata__"] = metadata
    header_json = json.dumps(header).encode("utf-8")
    total_size = max((info["data_offsets"][1] for info in tensors.values()), default=0)
    return struct.pack("<Q", len(header_json)) + header_json + b"\x00" * total_size


# ---------------------------------------------------------------------------
# 1. load_safetensors
# ---------------------------------------------------------------------------


class TestLoadSafetensorsStructure:
    """load_safetensors returns a dict with the documented canonical shape."""

    @pytest.mark.parametrize("sample", VALID_SAMPLE_FILES, ids=lambda p: p.name)
    def test_load_returns_dict_with_expected_top_level_keys(self, sample):
        _require_codec()
        model = load_safetensors(sample)
        assert isinstance(model, dict)
        for key in ("header_size", "tensors", "metadata", "data"):
            assert key in model, f"missing key {key!r} for sample {sample.name}"

    @pytest.mark.parametrize("sample", VALID_SAMPLE_FILES, ids=lambda p: p.name)
    def test_load_tensor_entries_have_dtype_shape_offsets(self, sample):
        _require_codec()
        model = load_safetensors(sample)
        assert model["tensors"], f"expected at least one tensor in {sample.name}"
        for name, info in model["tensors"].items():
            assert isinstance(name, str)
            assert "dtype" in info
            assert "shape" in info
            assert "data_offsets" in info
            assert isinstance(info["data_offsets"], list)
            assert len(info["data_offsets"]) == 2

    def test_load_header_size_is_positive_int(self):
        _require_codec()
        model = load_safetensors(VALID_DIR / "single-tensor.safetensors")
        assert isinstance(model["header_size"], int)
        assert model["header_size"] > 0

    def test_load_data_buffer_length_matches_file_minus_header(self):
        _require_codec()
        sample = VALID_DIR / "multi-tensor.safetensors"
        raw = sample.read_bytes()
        model = load_safetensors(sample)
        expected_data_len = len(raw) - 8 - model["header_size"]
        assert len(model["data"]) == expected_data_len

    def test_load_accepts_path_str_and_bytes_equally(self):
        _require_codec()
        sample = VALID_DIR / "single-tensor.safetensors"
        from_path_obj = load_safetensors(sample)
        from_str = load_safetensors(str(sample))
        from_bytes = load_safetensors(sample.read_bytes())
        assert from_path_obj["tensors"].keys() == from_str["tensors"].keys()
        assert from_path_obj["tensors"].keys() == from_bytes["tensors"].keys()

    def test_load_metadata_is_dict_of_strings(self):
        _require_codec()
        model = load_safetensors(VALID_DIR / "with-metadata.safetensors")
        assert isinstance(model["metadata"], dict)
        for k, v in model["metadata"].items():
            assert isinstance(k, str)
            assert isinstance(v, str)

    def test_load_nonexistent_file_raises_parse_error(self):
        _require_codec()
        _require_exceptions()
        with pytest.raises(SafetensorsParseError):
            load_safetensors(VALID_DIR / "does-not-exist.safetensors")

    def test_load_malformed_bytes_raises_parse_error(self):
        _require_codec()
        _require_exceptions()
        with pytest.raises(SafetensorsParseError):
            load_safetensors(b"not a safetensors file")


# ---------------------------------------------------------------------------
# 2. write_safetensors + roundtrip
# ---------------------------------------------------------------------------


class TestWriteAndRoundtripIdentity:
    """write_safetensors + reload proves structural and byte-level identity."""

    @pytest.mark.parametrize("sample", VALID_SAMPLE_FILES, ids=lambda p: p.name)
    def test_roundtrip_preserves_tensor_set(self, sample, tmp_path):
        _require_codec()
        dest = tmp_path / f"rt-{sample.name}"
        original = load_safetensors(sample)
        reloaded = roundtrip(sample, dest)
        assert set(original["tensors"].keys()) == set(reloaded["tensors"].keys())

    @pytest.mark.parametrize("sample", VALID_SAMPLE_FILES, ids=lambda p: p.name)
    def test_roundtrip_preserves_dtype_and_shape_per_tensor(self, sample, tmp_path):
        _require_codec()
        dest = tmp_path / f"rt-shape-{sample.name}"
        original = load_safetensors(sample)
        reloaded = roundtrip(sample, dest)
        for name, info in original["tensors"].items():
            assert reloaded["tensors"][name]["dtype"] == info["dtype"]
            assert reloaded["tensors"][name]["shape"] == info["shape"]

    @pytest.mark.parametrize("sample", VALID_SAMPLE_FILES, ids=lambda p: p.name)
    def test_roundtrip_preserves_real_tensor_bytes(self, sample, tmp_path):
        """FACT-SAFETENSORS-103: roundtrip must not zero-fill real tensor content."""
        _require_codec()
        dest = tmp_path / f"rt-bytes-{sample.name}"
        original = load_safetensors(sample)
        reloaded = roundtrip(sample, dest)
        for name in original["tensors"]:
            original_bytes = get_tensor_bytes(original, name)
            reloaded_bytes = get_tensor_bytes(reloaded, name)
            assert original_bytes == reloaded_bytes

    def test_roundtrip_preserves_metadata(self, tmp_path):
        _require_codec()
        sample = VALID_DIR / "with-metadata.safetensors"
        dest = tmp_path / "rt-metadata.safetensors"
        original = load_safetensors(sample)
        reloaded = roundtrip(sample, dest)
        assert reloaded["metadata"] == original["metadata"]

    def test_write_then_load_from_scratch_dict(self, tmp_path):
        _require_codec()
        model = {
            "tensors": {
                "weight": {"dtype": "F32", "shape": [2, 2], "data_offsets": [0, 16]},
                "bias": {"dtype": "F32", "shape": [2], "data_offsets": [16, 24]},
            },
            "metadata": {"framework": "test"},
        }
        dest = tmp_path / "scratch.safetensors"
        write_safetensors(model, dest)
        reloaded = load_safetensors(dest)
        assert set(reloaded["tensors"].keys()) == {"weight", "bias"}
        assert reloaded["metadata"] == {"framework": "test"}

    def test_write_without_dest_returns_bytes_only(self):
        _require_codec()
        model = {"tensors": {"w": {"dtype": "F32", "shape": [1], "data_offsets": [0, 4]}}, "metadata": {}}
        result = write_safetensors(model)
        assert isinstance(result, bytes)
        # Should be loadable directly from the returned bytes.
        reloaded = load_safetensors(result)
        assert "w" in reloaded["tensors"]

    def test_write_empty_tensors_produces_loadable_file(self):
        _require_codec()
        model = {"tensors": {}, "metadata": {"note": "empty"}}
        result = write_safetensors(model)
        reloaded = load_safetensors(result)
        assert reloaded["tensors"] == {}
        assert get_tensor_count(reloaded) == 0

    def test_write_invalid_tensor_data_raises_write_error(self):
        _require_codec()
        _require_exceptions()
        model = {
            "tensors": {"w": {"dtype": "F32", "shape": [4], "data_offsets": [0, 16], "data": b"\x00"}},
            "metadata": {},
        }
        with pytest.raises(SafetensorsWriteError):
            write_safetensors(model)


# ---------------------------------------------------------------------------
# 3. Tensor accessors: get_tensor, get_tensor_bytes, get_tensor_count,
#    get_tensor_names
# ---------------------------------------------------------------------------


class TestTensorAccessors:
    """All four tensor-accessor functions, exercised against real sample files."""

    @pytest.mark.parametrize("sample", VALID_SAMPLE_FILES, ids=lambda p: p.name)
    def test_get_tensor_count_matches_dict_length(self, sample):
        _require_codec()
        model = load_safetensors(sample)
        assert get_tensor_count(model) == len(model["tensors"])

    @pytest.mark.parametrize("sample", VALID_SAMPLE_FILES, ids=lambda p: p.name)
    def test_get_tensor_names_matches_dict_keys_sorted(self, sample):
        _require_codec()
        model = load_safetensors(sample)
        names = get_tensor_names(model)
        assert names == sorted(model["tensors"].keys())
        assert isinstance(names, list)

    def test_get_tensor_count_empty_model(self):
        _require_codec()
        assert get_tensor_count({"tensors": {}}) == 0

    def test_get_tensor_count_missing_tensors_key_defaults_zero(self):
        _require_codec()
        assert get_tensor_count({}) == 0

    def test_get_tensor_names_missing_tensors_key_returns_empty_list(self):
        _require_codec()
        assert get_tensor_names({}) == []

    @pytest.mark.parametrize("sample", VALID_SAMPLE_FILES, ids=lambda p: p.name)
    def test_get_tensor_bytes_length_matches_data_offsets_span(self, sample):
        _require_codec()
        model = load_safetensors(sample)
        for name, info in model["tensors"].items():
            start, end = info["data_offsets"]
            raw = get_tensor_bytes(model, name)
            assert len(raw) == end - start

    @pytest.mark.parametrize("sample", VALID_SAMPLE_FILES, ids=lambda p: p.name)
    def test_get_tensor_decodes_to_ndarray_with_matching_shape(self, sample):
        _require_codec()
        np = pytest.importorskip("numpy")
        model = load_safetensors(sample)
        for name, info in model["tensors"].items():
            arr = get_tensor(model, name)
            assert isinstance(arr, np.ndarray)
            assert list(arr.shape) == list(info["shape"])

    def test_get_tensor_bytes_unknown_name_raises(self):
        _require_codec()
        _require_exceptions()
        model = load_safetensors(VALID_DIR / "single-tensor.safetensors")
        with pytest.raises(SafetensorsParseError):
            get_tensor_bytes(model, "totally-unknown-tensor-name")

    def test_get_tensor_unknown_name_raises(self):
        _require_codec()
        model = load_safetensors(VALID_DIR / "single-tensor.safetensors")
        with pytest.raises((SafetensorsParseError, KeyError)):
            get_tensor(model, "totally-unknown-tensor-name")

    def test_get_tensor_count_and_names_are_consistent(self):
        _require_codec()
        model = load_safetensors(VALID_DIR / "multi-tensor.safetensors")
        assert get_tensor_count(model) == len(get_tensor_names(model))


# ---------------------------------------------------------------------------
# 4. probe_safetensors
# ---------------------------------------------------------------------------


class TestProbeSafetensors:
    """probe_safetensors is a boolean, never-raising format sniff."""

    @pytest.mark.parametrize("sample", VALID_SAMPLE_FILES, ids=lambda p: p.name)
    def test_probe_returns_true_for_all_valid_samples(self, sample):
        _require_codec()
        assert probe_safetensors(sample) is True

    def test_probe_returns_bool_type(self):
        _require_codec()
        result = probe_safetensors(VALID_DIR / "single-tensor.safetensors")
        assert result is True or result is False

    def test_probe_invalid_sample_returns_false(self):
        _require_codec()
        assert probe_safetensors(INVALID_DIR / "bad-header-length.safetensors") is False

    def test_probe_never_raises_on_garbage_input(self):
        _require_codec()
        for garbage in (b"", b"\x00", b"garbage-not-json-header" * 4, b"\xff" * 100):
            try:
                result = probe_safetensors(garbage)
            except Exception as exc:  # pragma: no cover - explicit failure path
                pytest.fail(f"probe_safetensors raised {exc!r} instead of returning False")
            assert result is False

    def test_probe_metadata_only_header_is_valid(self):
        _require_codec()
        header = json.dumps({"__metadata__": {"note": "meta-only"}}).encode("utf-8")
        data = struct.pack("<Q", len(header)) + header
        assert probe_safetensors(data) is True

    def test_probe_and_load_agree_on_valid_samples(self):
        """probe_safetensors returning True implies load_safetensors succeeds."""
        _require_codec()
        for sample in VALID_SAMPLE_FILES:
            assert probe_safetensors(sample) is True
            load_safetensors(sample)  # must not raise


# ---------------------------------------------------------------------------
# 5. Error classes
# ---------------------------------------------------------------------------


class TestErrorClasses:
    """SafetensorsError / SafetensorsParseError / SafetensorsWriteError hierarchy."""

    def test_base_error_is_exception_subclass(self):
        _require_exceptions()
        assert issubclass(SafetensorsError, Exception)

    def test_base_error_instantiable_with_message(self):
        _require_exceptions()
        err = SafetensorsError("boom")
        assert isinstance(err, Exception)
        assert str(err) == "boom"

    def test_parse_error_subclasses_base_error(self):
        _require_exceptions()
        assert issubclass(SafetensorsParseError, SafetensorsError)

    def test_write_error_subclasses_base_error(self):
        _require_exceptions()
        assert issubclass(SafetensorsWriteError, SafetensorsError)

    def test_parse_error_instantiable_and_raisable(self):
        _require_exceptions()
        with pytest.raises(SafetensorsParseError):
            raise SafetensorsParseError("bad header")

    def test_write_error_instantiable_and_raisable(self):
        _require_exceptions()
        with pytest.raises(SafetensorsWriteError):
            raise SafetensorsWriteError("cannot write")

    def test_parse_error_is_catchable_as_base_error(self):
        _require_exceptions()
        try:
            raise SafetensorsParseError("bad header")
        except SafetensorsError as exc:
            assert isinstance(exc, SafetensorsParseError)
        else:
            pytest.fail("SafetensorsParseError was not caught as SafetensorsError")

    def test_write_error_is_catchable_as_base_error(self):
        _require_exceptions()
        try:
            raise SafetensorsWriteError("cannot write")
        except SafetensorsError as exc:
            assert isinstance(exc, SafetensorsWriteError)
        else:
            pytest.fail("SafetensorsWriteError was not caught as SafetensorsError")

    def test_parse_and_write_errors_are_distinct_classes(self):
        _require_exceptions()
        assert SafetensorsParseError is not SafetensorsWriteError
        assert not issubclass(SafetensorsParseError, SafetensorsWriteError)
        assert not issubclass(SafetensorsWriteError, SafetensorsParseError)

    def test_load_actually_raises_parse_error_not_generic_exception(self):
        """End-to-end: a real malformed file raises the specific typed error."""
        _require_codec()
        _require_exceptions()
        with pytest.raises(SafetensorsParseError):
            load_safetensors(INVALID_DIR / "bad-header-length.safetensors")

    def test_write_actually_raises_write_error_not_generic_exception(self):
        _require_codec()
        _require_exceptions()
        model = {
            "tensors": {"w": {"dtype": "F32", "shape": [4], "data_offsets": [0, 16], "data": "not-bytes"}},
            "metadata": {},
        }
        with pytest.raises(SafetensorsWriteError):
            write_safetensors(model)


# ---------------------------------------------------------------------------
# 6. SafetensorsDocument
# ---------------------------------------------------------------------------


class TestSafetensorsDocument:
    """Domain model wrapping a parsed SafeTensors dict."""

    def test_document_from_file_valid_sample(self):
        _require_document()
        doc = SafetensorsDocument.from_file(str(VALID_DIR / "multi-tensor.safetensors"))
        assert doc.tensor_count >= 2

    def test_document_wraps_dict_directly(self):
        _require_document()
        data = {
            "header_size": 42,
            "tensors": {"weight": {"dtype": "F32", "shape": [3, 4], "data_offsets": [0, 48]}},
            "metadata": {"format": "pt"},
        }
        doc = SafetensorsDocument(data)
        assert doc.raw is data
        assert doc.tensors == data["tensors"]
        assert doc.metadata == {"format": "pt"}
        assert doc.tensor_count == 1
        assert doc.tensor_names == ["weight"]
        assert doc.header_size == 42
        assert doc.is_empty is False

    def test_document_is_empty_true_for_no_tensors(self):
        _require_document()
        doc = SafetensorsDocument({"tensors": {}, "metadata": {}})
        assert doc.is_empty is True
        assert doc.tensor_count == 0
        assert doc.tensor_names == []

    def test_document_to_dict_returns_shallow_copy(self):
        _require_document()
        data = {"header_size": 1, "tensors": {}, "metadata": {}}
        doc = SafetensorsDocument(data)
        copy = doc.to_dict()
        assert copy == data
        assert copy is not data

    def test_document_repr_reports_tensor_count(self):
        _require_document()
        doc = SafetensorsDocument({"tensors": {"a": {}, "b": {}}, "metadata": {}})
        assert repr(doc) == "SafetensorsDocument(tensors=2)"

    def test_document_get_tensor_bytes_delegates_to_codec(self):
        _require_document()
        _require_codec()
        model = load_safetensors(VALID_DIR / "single-tensor.safetensors")
        doc = SafetensorsDocument(model)
        name = next(iter(model["tensors"]))
        assert doc.get_tensor_bytes(name) == get_tensor_bytes(model, name)

    def test_document_get_tensor_delegates_to_codec(self):
        _require_document()
        _require_codec()
        np = pytest.importorskip("numpy")
        model = load_safetensors(VALID_DIR / "single-tensor.safetensors")
        doc = SafetensorsDocument(model)
        name = next(iter(model["tensors"]))
        assert np.array_equal(doc.get_tensor(name), get_tensor(model, name))

    def test_document_missing_metadata_key_defaults_empty_dict(self):
        _require_document()
        doc = SafetensorsDocument({"tensors": {}})
        assert doc.metadata == {}

    def test_document_missing_header_size_defaults_zero(self):
        _require_document()
        doc = SafetensorsDocument({"tensors": {}})
        assert doc.header_size == 0

    def test_document_spec_qname_class_attribute(self):
        _require_document()
        assert SafetensorsDocument.spec_qname == "safetensors:header"


# ---------------------------------------------------------------------------
# 7. Analytics: safetensors_dtype_histogram, safetensors_total_tensor_bytes,
#    safetensors_largest_tensor_name
# ---------------------------------------------------------------------------


class TestAnalyticsFunctions:
    """Analytics functions re-parse the source and derive tensor statistics."""

    @pytest.mark.parametrize("sample", VALID_SAMPLE_FILES, ids=lambda p: p.name)
    def test_dtype_histogram_total_equals_tensor_count(self, sample):
        _require_analytics()
        _require_codec()
        model = load_safetensors(sample)
        histogram = safetensors_dtype_histogram(sample)
        assert sum(histogram.values()) == get_tensor_count(model)

    @pytest.mark.parametrize("sample", VALID_SAMPLE_FILES, ids=lambda p: p.name)
    def test_total_tensor_bytes_matches_manual_sum(self, sample):
        _require_analytics()
        _require_codec()
        model = load_safetensors(sample)
        manual_total = sum(
            max(0, info["data_offsets"][1] - info["data_offsets"][0])
            for info in model["tensors"].values()
        )
        assert safetensors_total_tensor_bytes(sample) == manual_total

    @pytest.mark.parametrize("sample", VALID_SAMPLE_FILES, ids=lambda p: p.name)
    def test_largest_tensor_name_is_a_real_tensor_in_the_file(self, sample):
        _require_analytics()
        _require_codec()
        model = load_safetensors(sample)
        largest = safetensors_largest_tensor_name(sample)
        assert largest in model["tensors"]

    def test_largest_tensor_name_none_for_empty_model(self):
        _require_analytics()
        data = _build_minimal_bytes({}, metadata={"note": "empty"})
        assert safetensors_largest_tensor_name(data) is None

    def test_dtype_histogram_empty_model_is_empty_dict(self):
        _require_analytics()
        data = _build_minimal_bytes({}, metadata={"note": "empty"})
        assert safetensors_dtype_histogram(data) == {}

    def test_total_tensor_bytes_zero_for_empty_model(self):
        _require_analytics()
        data = _build_minimal_bytes({}, metadata={"note": "empty"})
        assert safetensors_total_tensor_bytes(data) == 0

    def test_analytics_functions_accept_bytes_source_directly(self):
        _require_analytics()
        data = _build_minimal_bytes(
            {
                "a": {"dtype": "F32", "shape": [1], "data_offsets": [0, 4]},
                "b": {"dtype": "I8", "shape": [1], "data_offsets": [4, 5]},
            }
        )
        assert safetensors_dtype_histogram(data) == {"F32": 1, "I8": 1}
        assert safetensors_total_tensor_bytes(data) == 5
        assert safetensors_largest_tensor_name(data) == "a"

    def test_analytics_functions_raise_on_malformed_input(self):
        _require_analytics()
        _require_exceptions()
        for fn in (
            safetensors_dtype_histogram,
            safetensors_total_tensor_bytes,
            safetensors_largest_tensor_name,
        ):
            with pytest.raises(SafetensorsParseError):
                fn(INVALID_DIR / "bad-header-length.safetensors")

    def test_analytics_functions_do_not_mutate_input_source_file(self, tmp_path):
        """Analytics functions re-parse rather than mutate; original bytes survive."""
        _require_analytics()
        sample = VALID_DIR / "multi-tensor.safetensors"
        before = sample.read_bytes()
        safetensors_dtype_histogram(sample)
        safetensors_total_tensor_bytes(sample)
        safetensors_largest_tensor_name(sample)
        after = sample.read_bytes()
        assert before == after


# ---------------------------------------------------------------------------
# 8. Package-level exports (__init__.py) — aliases and __all__ integrity
# ---------------------------------------------------------------------------


class TestPackageExports:
    """safetensors/__init__.py re-exports and short aliases (probe/load/write)."""

    def test_all_documented_symbols_are_importable_from_package_root(self):
        import safetensors as pkg

        expected = [
            "get_tensor",
            "get_tensor_bytes",
            "get_tensor_count",
            "get_tensor_names",
            "load_safetensors",
            "probe_safetensors",
            "roundtrip",
            "safetensors_installed_workflow",
            "write_safetensors",
            "SafetensorsDocument",
            "SafetensorsError",
            "SafetensorsParseError",
            "SafetensorsWriteError",
            "safetensors_dtype_histogram",
            "safetensors_largest_tensor_name",
            "safetensors_total_tensor_bytes",
        ]
        for name in expected:
            assert hasattr(pkg, name), f"safetensors package missing export {name!r}"
            assert name in pkg.__all__

    def test_short_aliases_point_to_underlying_functions(self):
        import safetensors as pkg

        assert pkg.probe is pkg.probe_safetensors
        assert pkg.load is pkg.load_safetensors
        assert pkg.write is pkg.write_safetensors

    def test_package_metadata_attributes_present(self):
        import safetensors as pkg

        assert isinstance(pkg.__version__, str)
        assert pkg.__track__ == "python-foss"
        assert isinstance(pkg.__commercial_ready__, bool)

    def test_probe_alias_behaves_identically_to_named_function(self):
        _require_codec()
        import safetensors as pkg

        for sample in VALID_SAMPLE_FILES:
            assert pkg.probe(sample) == probe_safetensors(sample)

    def test_load_alias_behaves_identically_to_named_function(self):
        _require_codec()
        import safetensors as pkg

        sample = VALID_DIR / "single-tensor.safetensors"
        assert pkg.load(sample)["tensors"].keys() == load_safetensors(sample)["tensors"].keys()


# ---------------------------------------------------------------------------
# 9. safetensors_installed_workflow — installed-package smoke workflow
# ---------------------------------------------------------------------------


class TestInstalledWorkflow:
    """safetensors_installed_workflow() end-to-end summary used by packaging proof."""

    @pytest.mark.parametrize("sample", VALID_SAMPLE_FILES, ids=lambda p: p.name)
    def test_installed_workflow_reports_correct_tensor_count(self, sample):
        _require_codec()
        result = safetensors_installed_workflow(sample)
        model = load_safetensors(sample)
        assert result["format"] == "safetensors"
        assert result["loaded"] is True
        assert result["tensor_count"] == get_tensor_count(model)
        assert sorted(result["tensor_names"]) == get_tensor_names(model)
        assert result["header_size"] == model["header_size"]

    def test_installed_workflow_signature_accepts_source_type(self):
        _require_codec()
        sig = inspect.signature(safetensors_installed_workflow)
        assert len(sig.parameters) == 1
