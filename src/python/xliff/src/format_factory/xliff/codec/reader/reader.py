"""Bounded XLIFF 2.0/2.1 reader with passive extension preservation."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from os import PathLike
from pathlib import Path

from format_factory.core import BinarySource, ProbeResult, ResourceLimits

from ...errors import XliffParseError
from ...model import (
    ExtensionNode,
    Group,
    InlineElement,
    InlineNode,
    Note,
    Segment,
    Unit,
    XliffDocument,
    XliffFile,
)
from ...security import effective_limits

XLIFF_NAMESPACE = "urn:oasis:names:tc:xliff:document:2.0"
SUPPORTED_VERSIONS = frozenset({"2.0", "2.1"})


def _read_source(source: BinarySource, limits: ResourceLimits) -> bytes:
    if isinstance(source, bytes):
        data = source
    elif isinstance(source, (bytearray, memoryview)):
        data = bytes(source)
    elif isinstance(source, (str, PathLike)):
        path = Path(source)
        try:
            limits.enforce("max_input_bytes", path.stat().st_size)
            data = path.read_bytes()
        except OSError as exc:
            raise XliffParseError(f"cannot read {path}: {exc}") from exc
    elif hasattr(source, "read"):
        data = source.read(limits.max_input_bytes + 1)
        if not isinstance(data, bytes):
            raise TypeError("binary source read() must return bytes")
    else:
        raise TypeError("source must be bytes, a path, or a binary stream")
    limits.enforce("max_input_bytes", len(data))
    return data


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if tag.startswith("{") else tag


def _namespace(tag: str) -> str:
    return tag[1:].split("}", 1)[0] if tag.startswith("{") else ""


def _unknown_attributes(
    element: ET.Element, known: set[str]
) -> dict[str, str]:
    return {
        key: value
        for key, value in element.attrib.items()
        if key not in known
    }


def _extension(element: ET.Element) -> ExtensionNode:
    return ExtensionNode(
        tag=element.tag,
        xml=ET.tostring(element, encoding="utf-8", short_empty_elements=True),
    )


def _parse_inline(element: ET.Element) -> list[InlineNode]:
    content: list[InlineNode] = []
    if element.text:
        content.append(element.text)
    for child in element:
        content.append(
            InlineElement(
                tag=(
                    _local(child.tag)
                    if _namespace(child.tag) == XLIFF_NAMESPACE
                    else child.tag
                ),
                attributes=dict(child.attrib),
                content=_parse_inline(child),
                tail=child.tail or "",
            )
        )
    return content


def _parse_notes(element: ET.Element) -> list[Note]:
    result: list[Note] = []
    for child in element:
        if child.tag != f"{{{XLIFF_NAMESPACE}}}notes":
            continue
        for note in child:
            if note.tag != f"{{{XLIFF_NAMESPACE}}}note":
                continue
            priority: int | None = None
            if "priority" in note.attrib:
                try:
                    priority = int(note.attrib["priority"])
                except ValueError as exc:
                    raise XliffParseError("note priority must be an integer") from exc
            result.append(
                Note(
                    text="".join(note.itertext()),
                    id=note.get("id", ""),
                    applies_to=note.get("appliesTo", ""),
                    category=note.get("category", ""),
                    priority=priority,
                    attributes=_unknown_attributes(
                        note, {"id", "appliesTo", "category", "priority"}
                    ),
                )
            )
    return result


def _parse_segment(element: ET.Element) -> Segment:
    source: list[InlineNode] | None = None
    target: list[InlineNode] | None = None
    source_attributes: dict[str, str] = {}
    target_attributes: dict[str, str] = {}
    extensions: list[ExtensionNode] = []
    for child in element:
        if child.tag == f"{{{XLIFF_NAMESPACE}}}source":
            if source is not None:
                raise XliffParseError("segment has duplicate source elements")
            source = _parse_inline(child)
            source_attributes = dict(child.attrib)
        elif child.tag == f"{{{XLIFF_NAMESPACE}}}target":
            if target is not None:
                raise XliffParseError("segment has duplicate target elements")
            target = _parse_inline(child)
            target_attributes = dict(child.attrib)
        else:
            extensions.append(_extension(child))
    if source is None:
        raise XliffParseError(f"{_local(element.tag)} is missing source")
    return Segment(
        id=element.get("id", ""),
        source=source,
        target=target,
        kind=_local(element.tag),
        state=element.get("state", ""),
        sub_state=element.get("subState", ""),
        attributes=_unknown_attributes(element, {"id", "state", "subState"}),
        source_attributes=source_attributes,
        target_attributes=target_attributes,
        extensions=extensions,
    )


def _parse_unit(element: ET.Element) -> Unit:
    unit = Unit(
        id=element.get("id", ""),
        notes=_parse_notes(element),
        attributes=_unknown_attributes(element, {"id"}),
    )
    for child in element:
        if child.tag == f"{{{XLIFF_NAMESPACE}}}notes":
            continue
        if child.tag in {
            f"{{{XLIFF_NAMESPACE}}}segment",
            f"{{{XLIFF_NAMESPACE}}}ignorable",
        }:
            unit.children.append(_parse_segment(child))
        else:
            unit.children.append(_extension(child))
    return unit


def _parse_group(element: ET.Element) -> Group:
    group = Group(
        id=element.get("id", ""),
        notes=_parse_notes(element),
        attributes=_unknown_attributes(element, {"id"}),
    )
    for child in element:
        if child.tag == f"{{{XLIFF_NAMESPACE}}}notes":
            continue
        if child.tag == f"{{{XLIFF_NAMESPACE}}}group":
            group.children.append(_parse_group(child))
        elif child.tag == f"{{{XLIFF_NAMESPACE}}}unit":
            group.children.append(_parse_unit(child))
        else:
            group.children.append(_extension(child))
    return group


def _parse_file(element: ET.Element) -> XliffFile:
    file = XliffFile(
        id=element.get("id", ""),
        notes=_parse_notes(element),
        attributes=_unknown_attributes(element, {"id"}),
    )
    for child in element:
        if child.tag == f"{{{XLIFF_NAMESPACE}}}notes":
            continue
        if child.tag == f"{{{XLIFF_NAMESPACE}}}group":
            file.children.append(_parse_group(child))
        elif child.tag == f"{{{XLIFF_NAMESPACE}}}unit":
            file.children.append(_parse_unit(child))
        else:
            file.children.append(_extension(child))
    return file


def _enforce_tree_limits(root: ET.Element, limits: ResourceLimits) -> None:
    count = 0
    stack: list[tuple[ET.Element, int]] = [(root, 1)]
    while stack:
        node, depth = stack.pop()
        count += 1
        limits.enforce("max_xml_nodes", count)
        limits.enforce("max_nesting_depth", depth)
        stack.extend((child, depth + 1) for child in node)


def _parse(data: bytes, limits: ResourceLimits) -> XliffDocument:
    declaration_scan = data[: limits.max_header_bytes].replace(b"\x00", b"").upper()
    if b"<!DOCTYPE" in declaration_scan or b"<!ENTITY" in declaration_scan:
        raise XliffParseError("DTD and entity declarations are prohibited")
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise XliffParseError(f"invalid XML: {exc}") from exc
    _enforce_tree_limits(root, limits)
    if root.tag != f"{{{XLIFF_NAMESPACE}}}xliff":
        raise XliffParseError("root is not an XLIFF 2.x document")
    version = root.get("version", "")
    if version not in SUPPORTED_VERSIONS:
        raise XliffParseError(
            f"stable profile supports XLIFF 2.0 and 2.1, got {version!r}"
        )
    source_language = root.get("srcLang", "")
    if not source_language:
        raise XliffParseError("XLIFF root is missing srcLang")
    children: list[XliffFile | ExtensionNode] = []
    for child in root:
        if child.tag == f"{{{XLIFF_NAMESPACE}}}file":
            children.append(_parse_file(child))
        else:
            children.append(_extension(child))
    return XliffDocument(
        version=version,
        source_language=source_language,
        target_language=root.get("trgLang"),
        children=children,
        attributes=_unknown_attributes(root, {"version", "srcLang", "trgLang"}),
    )


def probe(
    source: BinarySource, *, limits: ResourceLimits | None = None
) -> ProbeResult:
    try:
        data = _read_source(source, effective_limits(limits))
        document = _parse(data, effective_limits(limits))
        return ProbeResult(
            True,
            1.0,
            "xliff",
            profile=f"XLIFF-{document.version}",
            reason="recognized stable XLIFF 2.x document",
        )
    except Exception:
        return ProbeResult(False, 0.0, "xliff", reason="not a supported XLIFF document")


def loads(
    data: bytes | bytearray | memoryview | str,
    *,
    mode: str = "strict",
    limits: ResourceLimits | None = None,
) -> XliffDocument:
    if mode not in {"strict", "preservation"}:
        raise ValueError("mode must be 'strict' or 'preservation'")
    encoded = data.encode("utf-8") if isinstance(data, str) else bytes(data)
    active_limits = effective_limits(limits)
    active_limits.enforce("max_input_bytes", len(encoded))
    return _parse(encoded, active_limits)


def load(
    source: BinarySource,
    *,
    mode: str = "strict",
    limits: ResourceLimits | None = None,
) -> XliffDocument:
    if mode not in {"strict", "preservation"}:
        raise ValueError("mode must be 'strict' or 'preservation'")
    active_limits = effective_limits(limits)
    return _parse(_read_source(source, active_limits), active_limits)
