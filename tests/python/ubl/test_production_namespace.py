"""Production namespace, security, root inventory, and packaging tests."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
_PACKAGE = _REPO / "src" / "python" / "ubl"
_SOURCE = _PACKAGE / "src"
_FIXTURES = Path(__file__).with_name("fixtures")
sys.path.insert(0, str(_SOURCE))
sys.path.insert(0, str(_REPO / "src" / "python" / "core" / "src"))

from format_factory.core import ResourceLimits
from format_factory.ubl import (
    ARCHIVE_MEMBER_NAMES_SHA256,
    AUTHORITY_SHA256,
    ROOT_CLASSES,
    ROOT_NAMES,
    ROOT_NAMES_SHA256,
    XmlNode,
    dumps,
    load,
    loads,
    probe,
    validate,
)
from format_factory.ubl.errors import UblParseError

CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"


def _minimal(root_name: str, *, extension: str = "") -> bytes:
    namespace = (
        "urn:oasis:names:specification:ubl:schema:xsd:" f"{root_name}-2"
    )
    return (
        f'<{root_name} xmlns="{namespace}" xmlns:cbc="{CBC}" '
        'xmlns:vendor="urn:example:vendor">'
        "<cbc:UBLVersionID>2.3</cbc:UBLVersionID>"
        f"{extension}"
        f"</{root_name}>"
    ).encode()


def test_authority_pinned_root_inventory_is_complete_and_stable() -> None:
    assert len(ROOT_NAMES) == 91
    assert len(set(ROOT_NAMES)) == 91
    assert tuple(sorted(ROOT_NAMES)) == ROOT_NAMES
    assert (
        hashlib.sha256("\n".join(ROOT_NAMES).encode()).hexdigest()
        == ROOT_NAMES_SHA256
    )
    assert (
        AUTHORITY_SHA256
        == "623bef8310db4d979ff28000a96bcc56dbcdda4f6206cf094c0aa79b75817970"
    )
    assert (
        ARCHIVE_MEMBER_NAMES_SHA256
        == "f9ab3f16a0ac89dbcd42f4e93d1eb5e59a4709bc7d151aedd8b2577c3fc114a2"
    )


@pytest.mark.parametrize("root_name", ROOT_NAMES)
def test_all_91_roots_have_typed_roundtrip(root_name: str) -> None:
    document = loads(_minimal(root_name))
    assert document.root_name == root_name
    assert type(document) is ROOT_CLASSES[root_name]
    assert validate(document).is_valid
    reloaded = loads(dumps(document))
    assert type(reloaded) is type(document)
    assert reloaded.root == document.root


def test_unknown_extension_is_preserved_semantically() -> None:
    original = loads(
        _minimal(
            "Invoice",
            extension=(
                '<vendor:Audit vendor:flag="yes"><vendor:Value>42</vendor:Value>'
                "</vendor:Audit>"
            ),
        )
    )
    reloaded = loads(dumps(original))
    assert reloaded.root.children[1].qname == "{urn:example:vendor}Audit"
    assert reloaded.root.children[1].attributes == (
        ("{urn:example:vendor}flag", "yes"),
    )
    assert reloaded.root.children[1].children[0].text == "42"


def test_probe_never_raises_for_malformed_or_unsupported_input() -> None:
    assert not probe(b"<")
    assert not probe(b"<Invoice/>")
    assert not probe(b"not XML")


def test_dtd_and_entity_declarations_are_rejected() -> None:
    payload = (
        b'<!DOCTYPE Invoice [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>'
        + _minimal("Invoice").replace(
            b"<cbc:UBLVersionID>2.3</cbc:UBLVersionID>",
            b"<cbc:UBLVersionID>&xxe;</cbc:UBLVersionID>",
        )
    )
    with pytest.raises(UblParseError, match="DTD and entity"):
        loads(payload)


def test_extension_payload_never_resolves_external_entities() -> None:
    fixture = _FIXTURES / "hostile-extension-entity.xml"
    with pytest.raises(UblParseError, match="DTD and entity"):
        load(fixture)
    assert not probe(fixture)


def test_wrong_namespace_and_preview_profile_fail_closed() -> None:
    with pytest.raises(UblParseError, match="namespace mismatch"):
        loads(
            b'<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Order-2"/>'
        )
    report = validate(loads(_minimal("Order")), profile="UBL-2.4-preview")
    assert not report.is_valid


def test_node_and_depth_limits_are_enforced() -> None:
    payload = _minimal("Invoice", extension="<a><b><c/></b></a>")
    tight = ResourceLimits(
        max_input_bytes=10_000,
        max_output_bytes=10_000,
        max_header_bytes=1,
        max_decompressed_bytes=10_000,
        max_compression_ratio=1,
        max_entries=100,
        max_nesting_depth=3,
        max_xml_nodes=100,
        max_tensor_count=1,
    )
    with pytest.raises(UblParseError, match="nesting limit"):
        loads(payload, limits=tight)


def test_edit_invalidates_signature_assertion() -> None:
    xml = _minimal(
        "Invoice",
        extension=(
            '<sig:Signature xmlns:sig="http://www.w3.org/2000/09/xmldsig#"/>'
        ),
    )
    signed = loads(xml)
    assert signed.signature_preserved
    edited = signed.with_root(
        signed.root.with_children(
            (*signed.root.children, XmlNode.create("{urn:example:vendor}Edited"))
        )
    )
    assert not edited.signature_preserved
    assert validate(edited).is_valid
    assert any(
        item.code == "ubl.signature.invalidated"
        for item in validate(edited).diagnostics
    )


def test_checked_in_generation_is_current() -> None:
    result = subprocess.run(
        [sys.executable, "tools/generate_roots.py", "--check"],
        cwd=_PACKAGE,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    manifest = json.loads(
        (
            _SOURCE
            / "format_factory"
            / "ubl"
            / "_generated"
            / "root_manifest.json"
        ).read_text(encoding="utf-8")
    )
    assert manifest["roots"] == list(ROOT_NAMES)


def test_production_namespace_does_not_create_parent_initializer() -> None:
    assert not (_SOURCE / "format_factory" / "__init__.py").exists()
    specification = importlib.util.find_spec("format_factory")
    assert specification is not None
    assert specification.origin is None


def test_wheel_configuration_excludes_legacy_top_level_package() -> None:
    pyproject = (_PACKAGE / "pyproject.toml").read_text(encoding="utf-8")
    assert 'include = ["format_factory.ubl*"]' in pyproject
    assert 'ff-ubl = "format_factory.ubl.cli:main"' in pyproject
    assert 'requires-python = ">=3.11"' in pyproject
