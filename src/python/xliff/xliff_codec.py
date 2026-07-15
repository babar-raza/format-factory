"""XLIFF (.xliff, .xlf) codec — probe, load, write.

Supports XLIFF 2.0/2.1 (OASIS namespace). XLIFF 1.2 is detected but
returned with a version marker for downstream handling.

Spec reference: FACT-XLIFF-001

Structural fidelity fixes (2026-07-15, real-defect audit against the OASIS
XLIFF 2.1 Specification):
  - FACT-XLIFF-101: inline markup (pc/sc/ec/ph/mrk) is preserved as
    structured data (see `xliff.xliff_inline`) instead of being flattened
    to plain text and lost.
  - FACT-XLIFF-102: `segment/@state` is now written back on save (it was
    previously read but silently dropped by `write_xliff`).
  - FACT-XLIFF-103: `notes`/`note` elements attached to file/group/unit are
    preserved.
  - FACT-XLIFF-104: `group` element wrappers (id, notes, nested groups,
    nested units) are preserved instead of being flattened via a blind
    `.//unit` findall.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Iterator, Union

from xliff.exceptions import XliffParseError, XliffWriteError
from xliff.xliff_inline import (
    InlineElement,
    InlineNode,
    flatten_inline_content,
    parse_inline_content,
    serialize_inline_content,
)

MAX_FILE_SIZE = 64 * 1024 * 1024  # 64 MiB guard

NS_XLIFF_20 = "urn:oasis:names:tc:xliff:document:2.0"
NS_XLIFF_12 = "urn:oasis:names:tc:xliff:document:1.2"
KNOWN_NAMESPACES = {NS_XLIFF_20, NS_XLIFF_12}

SUPPORTED_FEATURES = [
    "probe",
    "load",
    "write",
    "xliff_2_0",
    "xliff_1_2",
    "translation_units",
    "source_target_pairs",
    "inline_elements",
    "inline_markup_preservation",
    "segment_state_write_back",
    "notes_preservation",
    "group_hierarchy_preservation",
    "size_guard",
]

UNSUPPORTED_FEATURES = [
    "xliff_2_1_modules",
    "change_tracking",
    "validation",
    "segmentation",
    "streaming_parse",
    "xliff_1_2_write",
]

SourceType = Union[str, Path, bytes]


def _read_source(source: SourceType) -> bytes:
    """Read source into bytes."""
    if isinstance(source, bytes):
        return source
    path = Path(source)
    if not path.exists():
        raise XliffParseError(f"File not found: {source}")
    size = path.stat().st_size
    if size > MAX_FILE_SIZE:
        raise XliffParseError(f"File exceeds {MAX_FILE_SIZE} byte limit: {size} bytes")
    return path.read_bytes()


def _get_ns(root: ET.Element) -> str | None:
    """Extract the XLIFF namespace from the root element tag."""
    tag = root.tag
    if tag.startswith("{"):
        ns = tag[1 : tag.index("}")]
        if ns in KNOWN_NAMESPACES:
            return ns
    return None


def _strip_ns(tag: str) -> str:
    """Remove namespace prefix from a tag."""
    if tag.startswith("{"):
        return tag[tag.index("}") + 1 :]
    return tag


def _text_content(elem: ET.Element) -> str:
    """Extract all text from an element including children (inline elements).

    Retained for the XLIFF 1.2 parsing path (`_parse_xliff_12`), which is
    out of scope for the 2026-07-15 structural-fidelity fixes (XLIFF 1.2
    write support is explicitly deferred — see UNSUPPORTED_FEATURES).
    """
    parts: list[str] = []
    if elem.text:
        parts.append(elem.text)
    for child in elem:
        parts.append(_text_content(child))
        if child.tail:
            parts.append(child.tail)
    return "".join(parts)


def probe_xliff(source: SourceType) -> bool:
    """Return True if source is a valid XLIFF file. Never raises."""
    try:
        data = _read_source(source)
        root = ET.fromstring(data)
        ns = _get_ns(root)
        if ns is not None:
            return True
        local = _strip_ns(root.tag)
        return local == "xliff" and ns is None and False
    except Exception:
        return False


def _content_to_json(nodes: list[InlineNode]) -> list[Any]:
    """Convert a structured content list (`str`/`InlineElement`) to JSON-safe form."""
    return [node if isinstance(node, str) else node.to_dict() for node in nodes]


def _content_from_json(data: list[Any] | None) -> list[InlineNode]:
    """Convert a JSON-safe structured content list back into `InlineNode` form."""
    if not data:
        return []
    nodes: list[InlineNode] = []
    for item in data:
        if isinstance(item, str):
            nodes.append(item)
        else:
            nodes.append(InlineElement.from_dict(item))
    return nodes


def _resolve_write_nodes(seg_data: dict[str, Any], plain_key: str, content_key: str) -> list[InlineNode]:
    """Return the inline-content node list to serialize for one segment field.

    Prefers the structured `content_key` (e.g. ``source_content``) when it is
    still in sync with the plain `plain_key` string (e.g. ``source``) — i.e.
    the caller has not mutated the plain text since load, so the original
    inline structure (pc/sc/ec/ph/mrk) is reproduced untouched (FACT-XLIFF-101).
    If the plain string was mutated directly (a supported convenience — see
    the semantic round-trip/mutation tests) without updating the structured
    field, the mismatch is detected and the plain text wins: the segment is
    written as a single flat text run, which is the caller's evident intent.
    """
    plain = str(seg_data.get(plain_key, "") or "")
    structured = seg_data.get(content_key)
    if structured is not None:
        nodes = _content_from_json(structured)
        if flatten_inline_content(nodes) == plain:
            return nodes
    return [plain] if plain else []


def _parse_notes(elem: ET.Element, ns: str) -> list[dict[str, Any]]:
    """Parse an element's optional ``<notes><note>...</note></notes>`` children.

    Notes may be attached to file/group/unit. Spec ref: FACT-XLIFF-103.
    """
    notes_elem = elem.find(f"{{{ns}}}notes")
    if notes_elem is None:
        return []
    notes: list[dict[str, Any]] = []
    for note_elem in notes_elem.findall(f"{{{ns}}}note"):
        notes.append({
            "id": note_elem.get("id", ""),
            "appliesTo": note_elem.get("appliesTo", ""),
            "category": note_elem.get("category", ""),
            "priority": note_elem.get("priority", ""),
            "text": note_elem.text or "",
        })
    return notes


def _parse_segment(seg_elem: ET.Element, ns: str) -> dict[str, Any]:
    """Parse one ``<segment>`` element into a canonical segment dict.

    Captures both the flattened plain-text convenience fields (`source`,
    `target`) and the structured inline-content fields (`source_content`,
    `target_content`) so pc/sc/ec/ph/mrk boundaries survive a load -> write
    round trip (FACT-XLIFF-101), alongside the `state` attribute
    (FACT-XLIFF-102).
    """
    source_elem = seg_elem.find(f"{{{ns}}}source")
    target_elem = seg_elem.find(f"{{{ns}}}target")
    source_nodes = parse_inline_content(source_elem) if source_elem is not None else []
    target_nodes = parse_inline_content(target_elem) if target_elem is not None else []
    return {
        "source": flatten_inline_content(source_nodes),
        "target": flatten_inline_content(target_nodes),
        "source_content": _content_to_json(source_nodes),
        "target_content": _content_to_json(target_nodes),
        "state": seg_elem.get("state", ""),
    }


def _parse_unit(unit_elem: ET.Element, ns: str) -> dict[str, Any]:
    """Parse a ``<unit>`` element into a canonical unit dict."""
    segments = [_parse_segment(seg_elem, ns) for seg_elem in unit_elem.findall(f"{{{ns}}}segment")]
    return {
        "id": unit_elem.get("id", ""),
        "notes": _parse_notes(unit_elem, ns),
        "segments": segments,
    }


def _parse_group(group_elem: ET.Element, ns: str) -> dict[str, Any]:
    """Parse a ``<group>`` element into a canonical group dict (recursive).

    Preserves the group's own id/notes plus its directly-nested groups and
    units — unlike a blind ``.//unit`` findall, grouped units are NOT
    hoisted into the owning file's flat unit list. Spec ref: FACT-XLIFF-104.
    """
    return {
        "id": group_elem.get("id", ""),
        "notes": _parse_notes(group_elem, ns),
        "groups": [_parse_group(g, ns) for g in group_elem.findall(f"{{{ns}}}group")],
        "units": [_parse_unit(u, ns) for u in group_elem.findall(f"{{{ns}}}unit")],
    }


def _parse_xliff_20(root: ET.Element, ns: str) -> dict[str, Any]:
    """Parse XLIFF 2.0/2.1 document."""
    version = root.get("version", "2.0")
    src_lang = root.get("srcLang", "")
    tgt_lang = root.get("trgLang", "")

    files: list[dict[str, Any]] = []
    for file_elem in root.findall(f"{{{ns}}}file"):
        files.append({
            "id": file_elem.get("id", ""),
            "notes": _parse_notes(file_elem, ns),
            # Direct-child findall (not ".//") is deliberate: it keeps units
            # nested inside <group> out of this flat list (FACT-XLIFF-104).
            "groups": [_parse_group(g, ns) for g in file_elem.findall(f"{{{ns}}}group")],
            "units": [_parse_unit(u, ns) for u in file_elem.findall(f"{{{ns}}}unit")],
        })

    return {
        "version": version,
        "source_language": src_lang,
        "target_language": tgt_lang,
        "files": files,
    }


def _parse_xliff_12(root: ET.Element, ns: str) -> dict[str, Any]:
    """Parse XLIFF 1.2 document."""
    version = root.get("version", "1.2")

    files: list[dict[str, Any]] = []
    for file_elem in root.findall(f"{{{ns}}}file"):
        src_lang = file_elem.get("source-language", "")
        tgt_lang = file_elem.get("target-language", "")
        body = file_elem.find(f"{{{ns}}}body")
        units: list[dict[str, Any]] = []

        if body is not None:
            for tu in body.findall(f"{{{ns}}}trans-unit"):
                tu_id = tu.get("id", "")
                source_elem = tu.find(f"{{{ns}}}source")
                target_elem = tu.find(f"{{{ns}}}target")
                segments = [{
                    "source": _text_content(source_elem) if source_elem is not None else "",
                    "target": _text_content(target_elem) if target_elem is not None else "",
                    "state": "",
                }]
                units.append({"id": tu_id, "segments": segments})

        files.append({"id": "", "units": units})

    src_lang = ""
    tgt_lang = ""
    for file_elem in root.findall(f"{{{ns}}}file"):
        src_lang = file_elem.get("source-language", src_lang)
        tgt_lang = file_elem.get("target-language", tgt_lang)

    return {
        "version": version,
        "source_language": src_lang,
        "target_language": tgt_lang,
        "files": files,
    }


def load_xliff(source: SourceType) -> dict[str, Any]:
    """Parse an XLIFF file and return a canonical model dict."""
    data = _read_source(source)
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise XliffParseError(f"Invalid XML: {exc}") from exc

    ns = _get_ns(root)
    if ns is None:
        raise XliffParseError("Not an XLIFF document: missing XLIFF namespace")

    if ns == NS_XLIFF_20:
        return _parse_xliff_20(root, ns)
    elif ns == NS_XLIFF_12:
        return _parse_xliff_12(root, ns)
    else:
        raise XliffParseError(f"Unsupported XLIFF namespace: {ns}")


#: Local (namespace-stripped) element names that never carry significant
#: mixed text content per the XLIFF 2.1 content model — safe to pretty-print
#: indentation into. Everything else (segment/source/target/note, and
#: anything nested inside them) must be left byte-for-byte as constructed.
_SAFE_CONTAINER_NAMES = frozenset({"xliff", "file", "group", "unit", "notes"})


def _indent_structural(elem: ET.Element, level: int = 0, space: str = "  ") -> None:
    """Pretty-indent only elements that can never carry significant mixed
    text content (xliff/file/group/unit/notes).

    `xml.etree.ElementTree.indent()` reformats *any* whitespace-only text or
    tail throughout the whole tree — including a whitespace-only tail that
    happens to be a single meaningful word-separator space between two
    inline codes inside `<source>`/`<target>` (e.g. between a `<ph/>` and a
    following `<mrk>`). That corrupts real translation content
    (FACT-XLIFF-101 requires byte-for-byte inline-markup fidelity), so this
    function recurses only into elements that the XLIFF 2.1 schema
    guarantees hold no significant text of their own — `<segment>`,
    `<source>`, `<target>`, `<note>`, and anything nested inside them are
    never touched, at any depth.
    """
    children = list(elem)
    if not children:
        return
    child_indent = "\n" + space * (level + 1)
    if not elem.text or not elem.text.strip():
        elem.text = child_indent
    for child in children:
        if _strip_ns(child.tag) in _SAFE_CONTAINER_NAMES:
            _indent_structural(child, level + 1, space)
        if not child.tail or not child.tail.strip():
            child.tail = child_indent
    last_tail = "\n" + space * level
    if not children[-1].tail or not children[-1].tail.strip():
        children[-1].tail = last_tail


def _write_notes(parent_elem: ET.Element, notes: list[dict[str, Any]], ns: str) -> None:
    """Emit an optional ``<notes><note>...</note></notes>`` block (FACT-XLIFF-103)."""
    if not notes:
        return
    notes_elem = ET.SubElement(parent_elem, f"{{{ns}}}notes")
    for note in notes:
        note_elem = ET.SubElement(notes_elem, f"{{{ns}}}note")
        for attr in ("id", "appliesTo", "category", "priority"):
            value = note.get(attr)
            if value:
                note_elem.set(attr, value)
        note_elem.text = note.get("text", "")


def _write_segment(unit_elem: ET.Element, seg_data: dict[str, Any], ns: str) -> None:
    """Emit a ``<segment>`` element with state (FACT-XLIFF-102) and structured
    inline source/target content (FACT-XLIFF-101)."""
    seg_elem = ET.SubElement(unit_elem, f"{{{ns}}}segment")
    state = seg_data.get("state", "")
    if state:
        seg_elem.set("state", state)
    source_elem = ET.SubElement(seg_elem, f"{{{ns}}}source")
    serialize_inline_content(source_elem, _resolve_write_nodes(seg_data, "source", "source_content"), ns)
    target_elem = ET.SubElement(seg_elem, f"{{{ns}}}target")
    serialize_inline_content(target_elem, _resolve_write_nodes(seg_data, "target", "target_content"), ns)


def _write_unit(parent_elem: ET.Element, unit_data: dict[str, Any], ns: str) -> None:
    """Emit a ``<unit>`` element with notes (FACT-XLIFF-103) and segments."""
    unit_elem = ET.SubElement(parent_elem, f"{{{ns}}}unit")
    if unit_data.get("id"):
        unit_elem.set("id", unit_data["id"])
    _write_notes(unit_elem, unit_data.get("notes", []), ns)
    for seg_data in unit_data.get("segments", []):
        _write_segment(unit_elem, seg_data, ns)


def _write_group(parent_elem: ET.Element, group_data: dict[str, Any], ns: str) -> None:
    """Emit a ``<group>`` element (recursive): notes, then nested groups, then
    units (FACT-XLIFF-104)."""
    group_elem = ET.SubElement(parent_elem, f"{{{ns}}}group")
    if group_data.get("id"):
        group_elem.set("id", group_data["id"])
    _write_notes(group_elem, group_data.get("notes", []), ns)
    for nested in group_data.get("groups", []):
        _write_group(group_elem, nested, ns)
    for unit_data in group_data.get("units", []):
        _write_unit(group_elem, unit_data, ns)


def write_xliff(
    model: dict[str, Any],
    dest: Union[str, Path, None] = None,
) -> str:
    """Serialize an XLIFF model dict to XLIFF 2.0 XML string."""
    version = model.get("version", "2.0")
    src_lang = model.get("source_language", "en")
    tgt_lang = model.get("target_language", "")

    ET.register_namespace("", NS_XLIFF_20)
    root = ET.Element(f"{{{NS_XLIFF_20}}}xliff")
    root.set("version", version if version.startswith("2") else "2.0")
    root.set("srcLang", src_lang)
    if tgt_lang:
        root.set("trgLang", tgt_lang)

    for file_data in model.get("files", []):
        file_elem = ET.SubElement(root, f"{{{NS_XLIFF_20}}}file")
        if file_data.get("id"):
            file_elem.set("id", file_data["id"])

        _write_notes(file_elem, file_data.get("notes", []), NS_XLIFF_20)
        for group_data in file_data.get("groups", []):
            _write_group(file_elem, group_data, NS_XLIFF_20)
        for unit_data in file_data.get("units", []):
            _write_unit(file_elem, unit_data, NS_XLIFF_20)

    _indent_structural(root)
    result = ET.tostring(root, encoding="unicode", xml_declaration=True)

    if dest is not None:
        path = Path(dest)
        try:
            path.write_text(result, encoding="utf-8")
        except OSError as exc:
            raise XliffWriteError(f"Cannot write to {path}: {exc}") from exc

    return result


def iter_file_units(file_data: dict[str, Any]) -> Iterator[dict[str, Any]]:
    """Yield every unit dict in a file — both top-level and nested inside
    any depth of ``<group>`` wrappers.

    Use this instead of ``file_data["units"]`` directly when all units are
    needed (e.g. for counts/analytics): the raw ``units`` list only holds
    units that are direct children of ``<file>`` (FACT-XLIFF-104).
    """
    yield from file_data.get("units", [])
    for group_data in file_data.get("groups", []):
        yield from _iter_group_units(group_data)


def _iter_group_units(group_data: dict[str, Any]) -> Iterator[dict[str, Any]]:
    """Yield every unit dict nested in `group_data`, at any depth."""
    yield from group_data.get("units", [])
    for nested in group_data.get("groups", []):
        yield from _iter_group_units(nested)


def get_unit_count(model: dict[str, Any]) -> int:
    """Return total translation units across all files, including units
    nested inside ``<group>`` wrappers at any depth."""
    return sum(len(list(iter_file_units(f))) for f in model.get("files", []))


def get_file_count(model: dict[str, Any]) -> int:
    """Return number of file elements."""
    return len(model.get("files", []))


def roundtrip(source: SourceType, dest: Union[str, Path]) -> dict[str, Any]:
    """Load an XLIFF file, write it, and reload to prove round-trip fidelity."""
    model = load_xliff(source)
    write_xliff(model, dest)
    return load_xliff(dest)


def xliff_installed_workflow(source: SourceType) -> dict[str, Any]:
    """Return format metadata for an XLIFF source (installed-package proof)."""
    model = load_xliff(source)
    return {
        "format": "xliff",
        "loaded": True,
        "version": model.get("version", ""),
        "file_count": get_file_count(model),
        "unit_count": get_unit_count(model),
    }
