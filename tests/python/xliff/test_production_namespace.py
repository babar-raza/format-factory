"""Production XLIFF namespace, safety, and preservation characterization."""

from __future__ import annotations

from io import StringIO
from pathlib import Path

import pytest

from format_factory.core import ResourceLimits
from format_factory.xliff import (
    InlineElement,
    Segment,
    Unit,
    XliffDocument,
    XliffFile,
    XliffParseError,
    dump,
    dumps,
    flatten_inline_content,
    load,
    loads,
    probe,
    validate,
)


SAMPLE = b"""<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0"
       xmlns:v="urn:vendor:test" version="2.1" srcLang="en" trgLang="fr">
  <file id="f1" v:fileFlag="retained">
    <notes><note id="n1" priority="2">Translator note</note></notes>
    <v:metadata v:key="value"><v:item>opaque</v:item></v:metadata>
    <group id="g1">
      <unit id="u1">
        <segment id="s1" state="translated">
          <source>Hello <pc id="1" dataRefStart="d1" dataRefEnd="d2">world</pc>!</source>
          <target>Bonjour <pc id="1" dataRefStart="d1" dataRefEnd="d2">monde</pc>!</target>
        </segment>
      </unit>
    </group>
  </file>
</xliff>
"""


def test_typed_core_and_inline_content_load() -> None:
    document = loads(SAMPLE)
    assert document.version == "2.1"
    assert document.source_language == "en"
    assert document.target_language == "fr"
    assert document.file_count == 1
    assert document.unit_count == 1
    file = document.files[0]
    assert file.attributes["{urn:vendor:test}fileFlag"] == "retained"
    assert file.notes[0].text == "Translator note"
    unit = next(document.iter_units())
    segment = unit.segments[0]
    assert flatten_inline_content(segment.source) == "Hello world!"
    assert isinstance(segment.source[1], InlineElement)
    assert segment.source[1].data_ref == "d1"
    assert validate(document).is_valid


def test_semantic_roundtrip_preserves_unknown_namespace_and_order() -> None:
    document = loads(SAMPLE, mode="preservation")
    first = dumps(document)
    second = dumps(document)
    assert first == second
    reloaded = loads(first)
    file = reloaded.files[0]
    assert file.children[0].tag == "{urn:vendor:test}metadata"
    assert next(reloaded.iter_units()).segments[0].state == "translated"
    assert dumps(reloaded) == first


def test_stream_and_path_lifecycle(tmp_path: Path) -> None:
    document = loads(SAMPLE)
    stream = StringIO()
    dump(document, stream)
    assert loads(stream.getvalue()).unit_count == 1
    path = tmp_path / "messages.xlf"
    dump(document, path, profile="2.0")
    assert load(path).version == "2.0"
    assert probe(path).matched


def test_dtd_and_entity_declarations_are_rejected() -> None:
    attack = (
        b'<!DOCTYPE xliff [<!ENTITY x "boom">]>'
        b'<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" '
        b'version="2.1" srcLang="en"><file id="f"/></xliff>'
    )
    with pytest.raises(XliffParseError, match="prohibited"):
        loads(attack)
    assert not probe(attack).matched


@pytest.mark.parametrize(
    "version,namespace",
    [
        ("2.2", "urn:oasis:names:tc:xliff:document:2.0"),
        ("1.2", "urn:oasis:names:tc:xliff:document:1.2"),
    ],
)
def test_preview_and_legacy_profiles_are_isolated(
    version: str, namespace: str
) -> None:
    data = (
        f'<xliff xmlns="{namespace}" version="{version}" srcLang="en">'
        '<file id="f"/></xliff>'
    )
    with pytest.raises(XliffParseError):
        loads(data)


def test_validation_detects_duplicate_ids_and_unpaired_inline_codes() -> None:
    bad = XliffDocument(
        version="2.1",
        source_language="en",
        target_language=None,
        children=[
            XliffFile(
                id="f",
                children=[
                    Unit(
                        id="u",
                        children=[
                            Segment(
                                id="s",
                                source=[
                                    InlineElement(
                                        "ec", {"id": "e", "startRef": "missing"}
                                    )
                                ],
                            ),
                            Segment(id="s", source=["duplicate"]),
                        ],
                    ),
                    Unit(id="u"),
                ],
            )
        ],
    )
    codes = {item.code for item in validate(bad).diagnostics}
    assert {
        "xliff.unit.id.duplicate",
        "xliff.segment.id.duplicate",
        "xliff.inline.ec.unpaired",
    } <= codes


def test_resource_limits_apply_before_xml_processing() -> None:
    limits = ResourceLimits(max_input_bytes=32)
    with pytest.raises(Exception, match="max_input_bytes"):
        loads(SAMPLE, limits=limits)


def test_production_package_has_no_parent_namespace_initializer() -> None:
    package = Path(__file__).parents[3] / "src/python/xliff/src/format_factory"
    assert not (package / "__init__.py").exists()
