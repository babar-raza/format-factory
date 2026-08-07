"""Deterministic semantic XLIFF 2.0/2.1 writer."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from os import PathLike
from pathlib import Path
from collections.abc import Set
from typing import TextIO, cast

from format_factory.core import ResourceLimits, TextDestination

from ...errors import XliffWriteError
from ...model import (
    DataElement,
    ExtensionNode,
    Group,
    InlineNode,
    Note,
    Segment,
    Unit,
    XliffDocument,
    XliffFile,
)
from ...security import effective_limits
from ..preservation import PreservationMode, canonicalize
from ..reader import SUPPORTED_VERSIONS, XLIFF_NAMESPACE

#: Per the XLIFF 2.1 specification's own Appendix C change summary, native
#: ITS 2.0 support is one of exactly two content-level features 2.1 adds
#: over 2.0 (the other, Advanced Validation, is Schematron-level and never
#: appears in document content) -- the core namespace and grammar are
#: otherwise explicitly stated to be unchanged between the two versions.
_ITS_NAMESPACES = (
    "http://www.w3.org/2005/11/its",
    "urn:oasis:names:tc:xliff:itsm:2.1",
)


def _its_namespace_of(key: str) -> str | None:
    if not key.startswith("{"):
        return None
    namespace = key[1:].split("}", 1)[0]
    return namespace if namespace in _ITS_NAMESPACES else None


def _attrs_have_its(attributes: dict[str, str]) -> bool:
    return any(_its_namespace_of(key) for key in attributes)


def _inline_has_its(nodes: list[InlineNode]) -> bool:
    for node in nodes:
        if isinstance(node, str):
            continue
        if _its_namespace_of(node.tag) or _attrs_have_its(node.attributes):
            return True
        if _inline_has_its(node.content):
            return True
    return False


def _notes_have_its(notes: list[Note]) -> bool:
    return any(_attrs_have_its(note.attributes) for note in notes)


def _segment_has_its(segment: Segment) -> bool:
    if (
        _attrs_have_its(segment.attributes)
        or _attrs_have_its(segment.source_attributes)
        or _attrs_have_its(segment.target_attributes)
    ):
        return True
    if any(_its_namespace_of(extension.tag) for extension in segment.extensions):
        return True
    if _inline_has_its(segment.source):
        return True
    if segment.target is not None and _inline_has_its(segment.target):
        return True
    return False


def _container_has_its(container: XliffFile | Group | Unit) -> bool:
    if _attrs_have_its(container.attributes) or _notes_have_its(container.notes):
        return True
    for child in container.children:
        if isinstance(child, ExtensionNode):
            if _its_namespace_of(child.tag):
                return True
        elif isinstance(child, Segment):
            if _segment_has_its(child):
                return True
        elif _container_has_its(child):
            return True
    return False


def _its_content_present(document: XliffDocument) -> bool:
    """XLIFF-WRITE-001: "report any version-downgrade loss before writing."

    Writing ITS 2.0 content under a ``profile="2.0"`` declaration would
    misrepresent the document as conformant to a profile that defines no
    ITS support -- this is the one genuinely checkable, spec-grounded
    downgrade-loss case (see the module-level comment on _ITS_NAMESPACES).
    """
    if _attrs_have_its(document.attributes):
        return True
    for child in document.children:
        if isinstance(child, ExtensionNode):
            if _its_namespace_of(child.tag):
                return True
        elif _container_has_its(child):
            return True
    return False


def _set_attributes(
    element: ET.Element,
    attributes: dict[str, str],
    *,
    reserved: Set[str] = frozenset(),
) -> None:
    for key in sorted(attributes):
        if key not in reserved:
            element.set(key, attributes[key])


def _append_extension(parent: ET.Element, node: ExtensionNode) -> None:
    try:
        child = ET.fromstring(node.xml)
    except ET.ParseError as exc:
        raise XliffWriteError(f"preserved extension is malformed: {exc}") from exc
    if child.tag != node.tag:
        raise XliffWriteError("preserved extension tag does not match its XML payload")
    parent.append(child)


def _serialize_inline(parent: ET.Element, content: list[InlineNode]) -> None:
    parent.text = None
    last: ET.Element | None = None
    for node in content:
        if isinstance(node, str):
            if last is None:
                parent.text = (parent.text or "") + node
            else:
                last.tail = (last.tail or "") + node
            continue
        tag = node.tag if node.tag.startswith("{") else f"{{{XLIFF_NAMESPACE}}}{node.tag}"
        child = ET.SubElement(parent, tag)
        _set_attributes(child, node.attributes)
        _serialize_inline(child, node.content)
        child.tail = node.tail or None
        last = child


def _write_notes(parent: ET.Element, notes: list[Note]) -> None:
    if not notes:
        return
    container = ET.SubElement(parent, f"{{{XLIFF_NAMESPACE}}}notes")
    for value in notes:
        note = ET.SubElement(container, f"{{{XLIFF_NAMESPACE}}}note")
        if value.id:
            note.set("id", value.id)
        if value.applies_to:
            note.set("appliesTo", value.applies_to)
        if value.category:
            note.set("category", value.category)
        if value.priority is not None:
            note.set("priority", str(value.priority))
        _set_attributes(
            note,
            value.attributes,
            reserved={"id", "appliesTo", "category", "priority"},
        )
        note.text = value.text


def _write_segment(parent: ET.Element, value: Segment) -> None:
    if value.kind not in {"segment", "ignorable"}:
        raise XliffWriteError(f"invalid unit child kind: {value.kind!r}")
    element = ET.SubElement(parent, f"{{{XLIFF_NAMESPACE}}}{value.kind}")
    if value.id:
        element.set("id", value.id)
    if value.state:
        element.set("state", value.state)
    if value.sub_state:
        element.set("subState", value.sub_state)
    _set_attributes(
        element, value.attributes, reserved={"id", "state", "subState"}
    )
    source = ET.SubElement(element, f"{{{XLIFF_NAMESPACE}}}source")
    _set_attributes(source, value.source_attributes)
    _serialize_inline(source, value.source)
    if value.target is not None:
        target = ET.SubElement(element, f"{{{XLIFF_NAMESPACE}}}target")
        _set_attributes(target, value.target_attributes)
        _serialize_inline(target, value.target)
    for extension in value.extensions:
        _append_extension(element, extension)


def _write_original_data(parent: ET.Element, items: list[DataElement]) -> None:
    if not items:
        return
    container = ET.SubElement(parent, f"{{{XLIFF_NAMESPACE}}}originalData")
    for value in items:
        data = ET.SubElement(container, f"{{{XLIFF_NAMESPACE}}}data")
        if value.id:
            data.set("id", value.id)
        if value.dir:
            data.set("dir", value.dir)
        _set_attributes(data, value.attributes, reserved={"id", "dir"})
        _serialize_inline(data, value.content)


def _write_unit(parent: ET.Element, value: Unit) -> None:
    element = ET.SubElement(parent, f"{{{XLIFF_NAMESPACE}}}unit")
    if value.id:
        element.set("id", value.id)
    _set_attributes(element, value.attributes, reserved={"id"})
    _write_notes(element, value.notes)
    _write_original_data(element, value.original_data)
    for child in value.children:
        if isinstance(child, Segment):
            _write_segment(element, child)
        else:
            _append_extension(element, child)


def _write_group(parent: ET.Element, value: Group) -> None:
    element = ET.SubElement(parent, f"{{{XLIFF_NAMESPACE}}}group")
    if value.id:
        element.set("id", value.id)
    _set_attributes(element, value.attributes, reserved={"id"})
    _write_notes(element, value.notes)
    for child in value.children:
        if isinstance(child, Group):
            _write_group(element, child)
        elif isinstance(child, Unit):
            _write_unit(element, child)
        else:
            _append_extension(element, child)


def _write_file(parent: ET.Element, value: XliffFile) -> None:
    element = ET.SubElement(parent, f"{{{XLIFF_NAMESPACE}}}file")
    if value.id:
        element.set("id", value.id)
    _set_attributes(element, value.attributes, reserved={"id"})
    _write_notes(element, value.notes)
    for child in value.children:
        if isinstance(child, Group):
            _write_group(element, child)
        elif isinstance(child, Unit):
            _write_unit(element, child)
        else:
            _append_extension(element, child)


def dumps(
    document: XliffDocument,
    *,
    mode: PreservationMode = PreservationMode.LOSSLESS,
    profile: str | None = None,
    limits: ResourceLimits | None = None,
) -> str:
    """Serialize canonical UTF-8 XLIFF without formatting mixed content.

    ``mode`` selects LOSSLESS (default; the tree is serialized exactly as
    constructed, unchanged from this function's historical behavior) or
    CANONICAL (every ``ExtensionNode`` is dropped before serializing --
    see ``codec.preservation`` for what is and is not eligible to drop).
    """

    if mode == PreservationMode.CANONICAL:
        document, _dropped = canonicalize(document)
    elif mode != PreservationMode.LOSSLESS:
        raise XliffWriteError(f"unknown preservation mode: {mode!r}")

    version = profile or document.version
    if version not in SUPPORTED_VERSIONS:
        raise XliffWriteError(f"unsupported stable XLIFF profile: {version!r}")
    if version == "2.0" and _its_content_present(document):
        raise XliffWriteError(
            "cannot write to XLIFF 2.0: document contains ITS 2.0 content "
            "(elements or attributes in the ITS namespaces), which is a "
            "content-level feature XLIFF 2.0 does not define support for; "
            "writing it anyway would silently misrepresent the document as "
            "conformant to a profile with no defined meaning for that content"
        )
    if document.namespace != XLIFF_NAMESPACE:
        raise XliffWriteError("document namespace is not the stable XLIFF 2.x namespace")
    if not document.source_language:
        raise XliffWriteError("srcLang is required")

    ET.register_namespace("", XLIFF_NAMESPACE)
    root = ET.Element(f"{{{XLIFF_NAMESPACE}}}xliff")
    root.set("version", version)
    root.set("srcLang", document.source_language)
    if document.target_language:
        root.set("trgLang", document.target_language)
    _set_attributes(
        root,
        document.attributes,
        reserved={"version", "srcLang", "trgLang"},
    )
    for child in document.children:
        if isinstance(child, XliffFile):
            _write_file(root, child)
        else:
            _append_extension(root, child)
    encoded = cast(
        bytes,
        ET.tostring(
            root,
            encoding="utf-8",
            xml_declaration=True,
            short_empty_elements=True,
        ),
    )
    effective_limits(limits).enforce("max_output_bytes", len(encoded))
    return encoded.decode("utf-8")


def dump(
    document: XliffDocument,
    destination: TextDestination,
    *,
    mode: PreservationMode = PreservationMode.LOSSLESS,
    profile: str | None = None,
    limits: ResourceLimits | None = None,
) -> None:
    data = dumps(document, mode=mode, profile=profile, limits=limits)
    if isinstance(destination, (str, PathLike)):
        try:
            Path(destination).write_text(data, encoding="utf-8", newline="\n")
        except OSError as exc:
            raise XliffWriteError(f"cannot write {destination}: {exc}") from exc
        return
    stream: TextIO = destination
    written = stream.write(data)
    if written != len(data):
        raise XliffWriteError(f"short write: expected {len(data)}, wrote {written}")
