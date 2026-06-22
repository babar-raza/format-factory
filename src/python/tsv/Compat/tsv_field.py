"""TsvField — production facade for tsv:field.

Spec authority: tsv:field
Fact ref: FACT-TSV-002
Canonical spec class: src/python/tsv/spec/record/field.py::Field
"""
from __future__ import annotations

from ..spec.record.field import Field as _SpecField


class TsvField(_SpecField):
    """Production facade for tsv:field."""

    spec_qname = "tsv:field"
    spec_fact_ref = "FACT-TSV-002"
    namespace_uri = "urn:iana:media-type:text:tab-separated-values"
