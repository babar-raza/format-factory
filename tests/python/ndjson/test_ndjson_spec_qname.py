"""V53 spec_qname compliance tests for NDJSON — TC-QHARD-POST-002.

Verifies:
  - NdjsonRecord in ndjson_codec.py has spec_qname = "ndjson:record"
  - NdjsonRecord.spec_fact_ref is set correctly
  - NdjsonRecord.authority_only is True
  - Canonical Record class in spec/record/record.py has spec_qname
  - NdjsonField in Compat/ has spec_qname
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.ndjson_codec import NdjsonRecord  # type: ignore
from ndjson.spec.record.record import Record  # type: ignore
from ndjson.Compat.ndjson_record import NdjsonRecord as CompatNdjsonRecord  # type: ignore


class TestNdjsonRecordCodecLevel:
    def test_spec_qname_is_correct(self):
        assert NdjsonRecord.spec_qname == "ndjson:record"

    def test_spec_qname_class_level(self):
        assert type(NdjsonRecord.__dict__["spec_qname"]) is str

    def test_spec_fact_ref_set(self):
        assert NdjsonRecord.spec_fact_ref == "FACT-NDJSON-001"

    def test_authority_only_true(self):
        assert NdjsonRecord.authority_only is True

    def test_namespace_uri_set(self):
        assert NdjsonRecord.namespace_uri == "https://ndjson.org"

    def test_local_name_is_record(self):
        assert NdjsonRecord.local_name == "record"

    def test_instantiation_works(self):
        r = NdjsonRecord()
        assert r.spec_qname == "ndjson:record"


class TestNdjsonRecordSpecLayer:
    def test_canonical_class_spec_qname(self):
        assert Record.spec_qname == "ndjson:record"

    def test_canonical_class_spec_fact_ref(self):
        assert Record.spec_fact_ref == "FACT-NDJSON-001"

    def test_canonical_class_accessible(self):
        assert Record.spec_qname == "ndjson:record"


class TestNdjsonRecordCompatLayer:
    def test_compat_spec_qname(self):
        assert CompatNdjsonRecord.spec_qname == "ndjson:record"

    def test_compat_spec_qname_class_level(self):
        assert CompatNdjsonRecord.spec_qname == "ndjson:record"
