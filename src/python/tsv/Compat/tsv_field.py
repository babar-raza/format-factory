"""TsvField — production facade for tsv:field.

Spec authority: tsv:field
Fact ref: SAL-TSV-00002
Canonical spec class: src/python/tsv/spec/record/field.py::Field
"""
from __future__ import annotations
from typing import ClassVar

from ..spec.record.field import Field as _SpecField


class TsvField(_SpecField):
    """Production facade for tsv:field."""

    spec_qname: ClassVar[str] = "tsv:field"
    spec_fact_ref: ClassVar[str] = "SAL-TSV-00002"
    namespace_uri: ClassVar[str] = "urn:iana:media-type:text:tab-separated-values"
