"""UBL-PARSE-001 -- every specification document root recognized by QName
across namespace-variation forms.

MUST (SAL-UBL-OBL-0996E6D7B91D544F): "Reject namespace spoofing and
ambiguous QName resolution with diagnostics rather than best-effort
guessing." Release gate: "All specification document roots recognized by
QName with namespace-variation tests."

test_obligation_qname_resolution.py already proves default-vs-prefixed
namespace forms produce identical QNames for ONE root type (Invoice),
grounded in `xml.etree.ElementTree`'s own Clark-notation normalization at
parse time (prefix-independent by construction). This file proves the
SAME fact for every one of the 91 supported document root types, plus a
third form (a non-conventional prefix) proving prefix CHOICE itself is
irrelevant, not merely that "the specific prefix already tried" works --
directly closing this obligation's own release gate rather than
extrapolating it from a single sample.
"""

from __future__ import annotations

import pytest

from format_factory.ubl import load
from format_factory.ubl._generated.root_catalog import ROOT_NAMES, ROOT_NAMESPACES
from format_factory.ubl.model.root_types import ROOT_CLASSES


def _default_namespace_bytes(name: str, namespace: str) -> bytes:
    return f'<{name} xmlns="{namespace}"/>'.encode()


def _prefixed_bytes(name: str, namespace: str) -> bytes:
    return f'<ubl:{name} xmlns:ubl="{namespace}"/>'.encode()


def _reprefixed_bytes(name: str, namespace: str) -> bytes:
    return f'<zz:{name} xmlns:zz="{namespace}"/>'.encode()


@pytest.mark.parametrize("root_name", sorted(ROOT_NAMES))
def test_every_root_type_is_recognized_under_the_default_namespace_form(root_name: str) -> None:
    namespace = ROOT_NAMESPACES[root_name]
    document = load(_default_namespace_bytes(root_name, namespace))
    assert document.root_name == root_name
    assert document.namespace == namespace
    assert type(document) is ROOT_CLASSES[root_name]


@pytest.mark.parametrize("root_name", sorted(ROOT_NAMES))
def test_every_root_type_is_recognized_under_a_prefixed_form(root_name: str) -> None:
    namespace = ROOT_NAMESPACES[root_name]
    document = load(_prefixed_bytes(root_name, namespace))
    assert document.root_name == root_name
    assert document.namespace == namespace
    assert type(document) is ROOT_CLASSES[root_name]


@pytest.mark.parametrize("root_name", sorted(ROOT_NAMES))
def test_every_root_type_is_recognized_under_a_different_re_prefixed_form(root_name: str) -> None:
    """Proves prefix CHOICE is irrelevant, not merely that one specific
    prefix (matching the other two forms) happens to work."""
    namespace = ROOT_NAMESPACES[root_name]
    document = load(_reprefixed_bytes(root_name, namespace))
    assert document.root_name == root_name
    assert document.namespace == namespace
    assert type(document) is ROOT_CLASSES[root_name]


@pytest.mark.parametrize("root_name", sorted(ROOT_NAMES))
def test_all_three_namespace_forms_of_the_same_root_type_produce_identical_qnames(
    root_name: str,
) -> None:
    namespace = ROOT_NAMESPACES[root_name]
    default_ns = load(_default_namespace_bytes(root_name, namespace))
    prefixed = load(_prefixed_bytes(root_name, namespace))
    reprefixed = load(_reprefixed_bytes(root_name, namespace))

    assert default_ns.root.qname == prefixed.root.qname == reprefixed.root.qname
