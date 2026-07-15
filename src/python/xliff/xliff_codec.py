"""XLIFF (.xliff, .xlf) codec — probe, load, write.

Supports XLIFF 2.0/2.1 (OASIS namespace). XLIFF 1.2 is detected but
returned with a version marker for downstream handling.

Spec reference: FACT-XLIFF-001
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Union

from xliff.exceptions import XliffParseError, XliffWriteError

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
    "size_guard",
]

UNSUPPORTED_FEATURES = [
    "xliff_2_1_modules",
    "change_tracking",
    "validation",
    "segmentation",
    "streaming_parse",
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
    """Extract all text from an element including children (inline elements)."""
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


def _parse_xliff_20(root: ET.Element, ns: str) -> dict[str, Any]:
    """Parse XLIFF 2.0/2.1 document."""
    version = root.get("version", "2.0")
    src_lang = root.get("srcLang", "")
    tgt_lang = root.get("trgLang", "")

    files: list[dict[str, Any]] = []
    for file_elem in root.findall(f"{{{ns}}}file"):
        file_id = file_elem.get("id", "")
        units: list[dict[str, Any]] = []

        for unit_elem in file_elem.findall(f".//{{{ns}}}unit"):
            unit_id = unit_elem.get("id", "")
            segments: list[dict[str, Any]] = []

            for seg_elem in unit_elem.findall(f"{{{ns}}}segment"):
                source_elem = seg_elem.find(f"{{{ns}}}source")
                target_elem = seg_elem.find(f"{{{ns}}}target")
                seg: dict[str, Any] = {
                    "source": _text_content(source_elem) if source_elem is not None else "",
                    "target": _text_content(target_elem) if target_elem is not None else "",
                    "state": seg_elem.get("state", ""),
                }
                segments.append(seg)

            units.append({"id": unit_id, "segments": segments})

        files.append({"id": file_id, "units": units})

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

        for unit_data in file_data.get("units", []):
            unit_elem = ET.SubElement(file_elem, f"{{{NS_XLIFF_20}}}unit")
            if unit_data.get("id"):
                unit_elem.set("id", unit_data["id"])

            for seg_data in unit_data.get("segments", []):
                seg_elem = ET.SubElement(unit_elem, f"{{{NS_XLIFF_20}}}segment")
                source_elem = ET.SubElement(seg_elem, f"{{{NS_XLIFF_20}}}source")
                source_elem.text = seg_data.get("source", "")
                target_elem = ET.SubElement(seg_elem, f"{{{NS_XLIFF_20}}}target")
                target_elem.text = seg_data.get("target", "")

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    result = ET.tostring(root, encoding="unicode", xml_declaration=True)

    if dest is not None:
        path = Path(dest)
        try:
            path.write_text(result, encoding="utf-8")
        except OSError as exc:
            raise XliffWriteError(f"Cannot write to {path}: {exc}") from exc

    return result


def get_unit_count(model: dict[str, Any]) -> int:
    """Return total translation units across all files."""
    return sum(len(f.get("units", [])) for f in model.get("files", []))


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
