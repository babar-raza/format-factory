"""NRRD-MODEL-001 / independent-oracle -- NrrdDocument's own spec_qname.

MUST: this document's own construct maps to a fixed spec QName
("nrrd:header") regardless of any particular document's content. The
deprecated alpha model (src/python/nrrd/models.py) declared this as a
ClassVar; it was dropped when the production model (model/document.py)
was built, so to_dict()'s own callers -- including the independent
oracle, which checks exactly this property for case nrrd-valid-003 --
had no way to recover it. FF6-EVENT-000281 restores it on the real
production model.
"""

from __future__ import annotations

from format_factory.nrrd import NrrdDocument, load_nrrd


def test_spec_qname_is_a_fixed_class_level_value() -> None:
    assert NrrdDocument.spec_qname == "nrrd:header"


def test_to_dict_includes_spec_qname() -> None:
    header = {"type": "uint8", "dimension": "1", "sizes": "1", "encoding": "raw", "endian": "little"}
    document = NrrdDocument(version=5, header=header, payload=b"\x00", array=[0])

    assert document.to_dict()["spec_qname"] == "nrrd:header"


def test_load_nrrd_includes_spec_qname_for_a_real_file() -> None:
    result = load_nrrd("samples/by-format/nrrd/valid/1d-int8.nrrd")

    assert result["spec_qname"] == "nrrd:header"
