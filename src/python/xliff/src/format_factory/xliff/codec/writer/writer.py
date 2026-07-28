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
from ..reader import SUPPORTED_VERSIONS, XLIFF_NAMESPACE


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


def _write_unit(parent: ET.Element, value: Unit) -> None:
    element = ET.SubElement(parent, f"{{{XLIFF_NAMESPACE}}}unit")
    if value.id:
        element.set("id", value.id)
    _set_attributes(element, value.attributes, reserved={"id"})
    _write_notes(element, value.notes)
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
    profile: str | None = None,
    limits: ResourceLimits | None = None,
) -> str:
    """Serialize canonical UTF-8 XLIFF without formatting mixed content."""

    version = profile or document.version
    if version not in SUPPORTED_VERSIONS:
        raise XliffWriteError(f"unsupported stable XLIFF profile: {version!r}")
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
    profile: str | None = None,
    limits: ResourceLimits | None = None,
) -> None:
    data = dumps(document, profile=profile, limits=limits)
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
