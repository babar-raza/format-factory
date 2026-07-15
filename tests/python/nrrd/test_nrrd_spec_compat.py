"""Tests for nrrd spec stub classes (spec/header/) and Compat facades (Compat/).

Tier notes (per taskcard TC-PROLIB-NRRD-001 rough classification):
  - TestSmokeImports        -> L0 (smoke/import)
  - TestHeaderSpecStub      -> L1 (parser/domain-model correctness for valid input)
  - TestDataSpecStub        -> L1
  - TestHeaderSpecStubEdge  -> L3 (malformed/boundary input)
  - TestDataSpecStubEdge    -> L3
  - TestNrrdHeaderFacade    -> L2 (facade binding/behavior)
  - TestNrrdDataFacade      -> L2 (facade binding/behavior)
"""
from __future__ import annotations

from pathlib import Path

import pytest

from nrrd.nrrd_codec import load_nrrd

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "nrrd"
VALID_DIR = SAMPLES / "valid"


class TestSmokeImports:
    """L0 — package importable, exception hierarchy defined."""

    def test_import_compat_package(self):
        from nrrd.Compat import NrrdData, NrrdHeader

        assert NrrdHeader is not None
        assert NrrdData is not None

    def test_compat_all_exports(self):
        import nrrd.Compat as compat_pkg

        assert set(compat_pkg.__all__) == {"NrrdHeader", "NrrdData"}

    def test_import_spec_header_stub(self):
        from nrrd.spec.header.header import Header

        assert Header is not None

    def test_import_spec_data_stub(self):
        from nrrd.spec.header.data import Data

        assert Data is not None

    def test_import_spec_package_reexports(self):
        from nrrd.spec import Data, Header

        assert Header is not None
        assert Data is not None

    def test_exceptions_hierarchy_defined(self):
        from nrrd.exceptions import NrrdError, NrrdParseError, NrrdWriteError

        assert issubclass(NrrdParseError, NrrdError)
        assert issubclass(NrrdWriteError, NrrdError)


class TestHeaderSpecStub:
    """L1 — Header stub correctly reflects parsed header data for valid input."""

    def test_header_type_1d_int8(self):
        from nrrd.spec.header.header import Header

        model = load_nrrd(VALID_DIR / "1d-int8.nrrd")
        h = Header(model["header"])
        assert h.type == "int8"

    def test_header_dimension_1d_int8(self):
        from nrrd.spec.header.header import Header

        model = load_nrrd(VALID_DIR / "1d-int8.nrrd")
        h = Header(model["header"])
        assert h.dimension == 1

    def test_header_sizes_2d_float32(self):
        from nrrd.spec.header.header import Header

        model = load_nrrd(VALID_DIR / "2d-float32.nrrd")
        h = Header(model["header"])
        assert h.sizes == [2, 3]

    def test_header_encoding_gzip_sample(self):
        from nrrd.spec.header.header import Header

        model = load_nrrd(VALID_DIR / "gzip-encoded.nrrd")
        h = Header(model["header"])
        assert h.encoding == "gzip"

    def test_header_endian_2d_float32(self):
        from nrrd.spec.header.header import Header

        model = load_nrrd(VALID_DIR / "2d-float32.nrrd")
        h = Header(model["header"])
        assert h.endian == "little"

    def test_header_to_dict_matches_source(self):
        from nrrd.spec.header.header import Header

        model = load_nrrd(VALID_DIR / "1d-int8.nrrd")
        h = Header(model["header"])
        assert h.to_dict() == model["header"]

    def test_header_repr(self):
        from nrrd.spec.header.header import Header

        model = load_nrrd(VALID_DIR / "1d-int8.nrrd")
        h = Header(model["header"])
        assert "Header(" in repr(h)
        assert "int8" in repr(h)


class TestDataSpecStub:
    """L1 — Data stub correctly reflects payload metadata for valid input."""

    def test_data_encoding_raw(self):
        from nrrd.spec.header.data import Data

        model = load_nrrd(VALID_DIR / "1d-int8.nrrd")
        d = Data({"encoding": model["header"].get("encoding", "raw"),
                   "data_size": model["data_size"],
                   "element_count": model["element_count"]})
        assert d.encoding == "raw"

    def test_data_size_1d_int8(self):
        from nrrd.spec.header.data import Data

        model = load_nrrd(VALID_DIR / "1d-int8.nrrd")
        d = Data({"data_size": model["data_size"]})
        assert d.data_size == 4

    def test_data_element_count_2d_float32(self):
        from nrrd.spec.header.data import Data

        model = load_nrrd(VALID_DIR / "2d-float32.nrrd")
        d = Data({"element_count": model["element_count"]})
        assert d.element_count == 6

    def test_data_is_compressed_true_for_gzip(self):
        from nrrd.spec.header.data import Data

        model = load_nrrd(VALID_DIR / "gzip-encoded.nrrd")
        d = Data({"encoding": model["header"].get("encoding", "raw")})
        assert d.is_compressed is True

    def test_data_is_compressed_false_for_raw(self):
        from nrrd.spec.header.data import Data

        model = load_nrrd(VALID_DIR / "1d-int8.nrrd")
        d = Data({"encoding": model["header"].get("encoding", "raw")})
        assert d.is_compressed is False

    def test_data_to_dict(self):
        from nrrd.spec.header.data import Data

        d = Data({"encoding": "gzip", "data_size": 10, "element_count": 5})
        assert d.to_dict() == {"encoding": "gzip", "data_size": 10, "element_count": 5}

    def test_data_repr(self):
        from nrrd.spec.header.data import Data

        d = Data({"encoding": "raw", "data_size": 4, "element_count": 4})
        assert "Data(" in repr(d)
        assert "raw" in repr(d)


class TestHeaderSpecStubEdge:
    """L3 — Header stub against malformed/boundary input."""

    def test_header_missing_fields_defaults(self):
        from nrrd.spec.header.header import Header

        h = Header({})
        assert h.type == ""
        assert h.dimension == 0
        assert h.sizes == []
        assert h.encoding == "raw"
        assert h.endian == ""

    def test_header_non_numeric_dimension_defaults_zero(self):
        from nrrd.spec.header.header import Header

        h = Header({"dimension": "not-a-number"})
        assert h.dimension == 0

    def test_header_empty_sizes_string(self):
        from nrrd.spec.header.header import Header

        h = Header({"sizes": ""})
        assert h.sizes == []


class TestDataSpecStubEdge:
    """L3 — Data stub against malformed/boundary input."""

    def test_data_missing_fields_defaults(self):
        from nrrd.spec.header.data import Data

        d = Data({})
        assert d.encoding == "raw"
        assert d.data_size == 0
        assert d.element_count == 0
        assert d.is_compressed is False

    def test_data_non_numeric_data_size_defaults_zero(self):
        from nrrd.spec.header.data import Data

        d = Data({"data_size": "bad"})
        assert d.data_size == 0

    def test_data_unsupported_encoding_still_marked_compressed(self):
        from nrrd.spec.header.data import Data

        # bzip2/zlib are declared UNSUPPORTED_FEATURES by the codec but the
        # spec stub still correctly classifies them as non-raw (compressed).
        d = Data({"encoding": "bzip2"})
        assert d.is_compressed is True


class TestNrrdHeaderFacade:
    """L2 — Compat facade for nrrd:header binds spec_qname exactly."""

    def test_facade_spec_qname_matches_registry(self):
        from nrrd.Compat import NrrdHeader

        assert NrrdHeader.spec_qname == "nrrd:header"

    def test_facade_spec_fact_ref_matches_registry(self):
        from nrrd.Compat import NrrdHeader

        assert NrrdHeader.spec_fact_ref == "FACT-NRRD-002"

    def test_facade_namespace_uri_matches_registry(self):
        from nrrd.Compat import NrrdHeader

        assert NrrdHeader.namespace_uri == "urn:format:nrrd:5.0"

    def test_facade_is_subclass_of_spec_stub(self):
        from nrrd.Compat import NrrdHeader
        from nrrd.spec.header.header import Header

        assert issubclass(NrrdHeader, Header)

    def test_facade_inherits_properties(self):
        from nrrd.Compat import NrrdHeader

        model = load_nrrd(VALID_DIR / "2d-float32.nrrd")
        facade = NrrdHeader(model["header"])
        assert facade.type == "float"
        assert facade.sizes == [2, 3]

    def test_facade_repr_uses_spec_stub_format(self):
        from nrrd.Compat import NrrdHeader

        model = load_nrrd(VALID_DIR / "1d-int8.nrrd")
        facade = NrrdHeader(model["header"])
        assert "Header(" in repr(facade)


class TestNrrdDataFacade:
    """L2 — Compat facade for nrrd:data binds spec_qname exactly."""

    def test_facade_spec_qname_matches_registry(self):
        from nrrd.Compat import NrrdData

        assert NrrdData.spec_qname == "nrrd:data"

    def test_facade_spec_fact_ref_matches_registry(self):
        from nrrd.Compat import NrrdData

        assert NrrdData.spec_fact_ref == "FACT-NRRD-003"

    def test_facade_namespace_uri_matches_registry(self):
        from nrrd.Compat import NrrdData

        assert NrrdData.namespace_uri == "urn:format:nrrd:5.0"

    def test_facade_is_subclass_of_spec_stub(self):
        from nrrd.Compat import NrrdData
        from nrrd.spec.header.data import Data

        assert issubclass(NrrdData, Data)

    def test_facade_inherits_properties(self):
        from nrrd.Compat import NrrdData

        facade = NrrdData({"encoding": "gzip", "data_size": 24, "element_count": 4})
        assert facade.encoding == "gzip"
        assert facade.is_compressed is True

    def test_facade_repr_uses_spec_stub_format(self):
        from nrrd.Compat import NrrdData

        facade = NrrdData({"encoding": "raw", "data_size": 4, "element_count": 4})
        assert "Data(" in repr(facade)


class TestQNameRegistryConsistency:
    """L2 — cross-check facades against shared/qname-registry/nrrd.yaml (loaded literal)."""

    EXPECTED = {
        "nrrd:header": {"fact": "FACT-NRRD-002", "ns": "urn:format:nrrd:5.0"},
        "nrrd:data": {"fact": "FACT-NRRD-003", "ns": "urn:format:nrrd:5.0"},
    }

    def test_header_matches_expected_registry_entry(self):
        from nrrd.Compat import NrrdHeader

        expected = self.EXPECTED["nrrd:header"]
        assert NrrdHeader.spec_qname == "nrrd:header"
        assert NrrdHeader.spec_fact_ref == expected["fact"]
        assert NrrdHeader.namespace_uri == expected["ns"]

    def test_data_matches_expected_registry_entry(self):
        from nrrd.Compat import NrrdData

        expected = self.EXPECTED["nrrd:data"]
        assert NrrdData.spec_qname == "nrrd:data"
        assert NrrdData.spec_fact_ref == expected["fact"]
        assert NrrdData.namespace_uri == expected["ns"]
