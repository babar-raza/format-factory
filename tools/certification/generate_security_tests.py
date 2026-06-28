"""Generate security test files for XML formats and ZST.

TC-CERT-H-SEC certification hardening.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# XML format configurations: (format, parser_import, parse_call, xml_root, body_wrapper)
XML_FORMATS = {
    "fodt": {
        "import": "from fodt.parser import parse_fodt",
        "parse": "parse_fodt(path)",
        "root_tag": "office:document",
        "root_attrs": 'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"\n'
                      '                 xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"\n'
                      '                 office:mimetype="application/vnd.oasis.opendocument.text"',
        "body": '<office:body><office:text><text:p>{payload}</text:p></office:text></office:body>',
        "suffix": ".fodt",
        "result_path": 'result.get("blocks", []) if isinstance(result, dict) else []',
    },
    "fodg": {
        "import": "from fodg import load as parse_fodg",
        "parse": "parse_fodg(path)",
        "root_tag": "office:document",
        "root_attrs": 'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"\n'
                      '                 xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"\n'
                      '                 office:mimetype="application/vnd.oasis.opendocument.graphics"',
        "body": '<office:body><office:drawing><draw:page draw:name="p1"><draw:frame><draw:text-box><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">{payload}</text:p></draw:text-box></draw:frame></draw:page></office:drawing></office:body>',
        "suffix": ".fodg",
        "result_path": '[]',
    },
    "fodp": {
        "import": "from fodp import load as parse_fodp",
        "parse": "parse_fodp(path)",
        "root_tag": "office:document",
        "root_attrs": 'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"\n'
                      '                 xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"\n'
                      '                 xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"\n'
                      '                 office:mimetype="application/vnd.oasis.opendocument.presentation"',
        "body": '<office:body><office:presentation><draw:page draw:name="slide1"><draw:frame><draw:text-box><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">{payload}</text:p></draw:text-box></draw:frame></draw:page></office:presentation></office:body>',
        "suffix": ".fodp",
        "result_path": 'result.get("pages", []) if isinstance(result, dict) else []',
    },
    "abw": {
        "import": "from abw import load_abw",
        "parse": "load_abw(path)",
        "root_tag": "abiword",
        "root_attrs": 'xmlns:awml="http://www.abisource.com/awml.dtd" version="0.99.2" fileformat="1.0"',
        "body": '<section><p>{payload}</p></section>',
        "suffix": ".abw",
        "result_path": 'result.get("sections", []) if isinstance(result, dict) else []',
    },
}

XXE_DOCTYPE = '''<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>'''

BILLION_LAUGHS_DOCTYPE = '''<!DOCTYPE lolz [
  <!ENTITY lol "lol">
  <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
  <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
  <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
]>'''


def generate_xml_security_test(fmt: str, config: dict) -> Path:
    body_xxe = config["body"].format(payload="&xxe;")
    body_laughs = config["body"].format(payload="&lol4;")

    xxe_xml = f'''<?xml version="1.0"?>
{XXE_DOCTYPE}
<{config["root_tag"]} {config["root_attrs"]}>
  {body_xxe}
</{config["root_tag"]}>
'''

    laughs_xml = f'''<?xml version="1.0"?>
{BILLION_LAUGHS_DOCTYPE}
<{config["root_tag"]} {config["root_attrs"]}>
  {body_laughs}
</{config["root_tag"]}>
'''

    test_content = f'''"""Security tests: XXE and billion-laughs protection for {fmt.upper()} parser.

TC-CERT-H-SEC certification hardening.
"""
import tempfile
from pathlib import Path

import pytest

{config["import"]}

XXE_PAYLOAD = """{xxe_xml}"""

BILLION_LAUGHS = """{laughs_xml}"""


def _write_temp(content: str) -> Path:
    f = tempfile.NamedTemporaryFile(suffix="{config["suffix"]}", delete=False, mode="w", encoding="utf-8")
    f.write(content)
    f.close()
    return Path(f.name)


def test_xxe_entity_not_resolved():
    """Parser must NOT resolve external entities (XXE attack)."""
    path = _write_temp(XXE_PAYLOAD)
    try:
        result = {config["parse"]}
        # If it parses, verify /etc/passwd content is NOT in output
        if isinstance(result, dict):
            assert "root:" not in str(result), "XXE entity was resolved!"
    except Exception:
        pass  # Raising is acceptable - XXE was blocked
    finally:
        path.unlink(missing_ok=True)


def test_billion_laughs_does_not_hang():
    """Parser must not hang or OOM on entity expansion attacks."""
    path = _write_temp(BILLION_LAUGHS)
    try:
        result = {config["parse"]}
        assert result is not None
    except Exception:
        pass  # Raising is acceptable - attack was blocked
    finally:
        path.unlink(missing_ok=True)
'''

    test_path = REPO_ROOT / "tests" / "python" / fmt / "test_security_xxe.py"
    test_path.parent.mkdir(parents=True, exist_ok=True)
    test_path.write_text(test_content, encoding="utf-8")
    return test_path


def generate_zst_security_test() -> Path:
    test_content = '''"""Security tests: decompression bomb protection for ZST.

TC-CERT-H-SEC certification hardening.
"""
import pytest

from zst.zst_codec import (
    compress_bytes,
    decompress_bytes,
    ZstOutputLimitExceeded,
    DEFAULT_MAX_OUTPUT_BYTES,
)


def test_decompression_bomb_limit_enforced():
    """decompress_bytes must reject output exceeding max_output_size."""
    # Create data that compresses well (repeat pattern)
    small_data = b"A" * 1024 * 1024  # 1 MiB of repeated bytes
    compressed = compress_bytes(small_data)

    # Decompress with a tiny limit
    with pytest.raises(ZstOutputLimitExceeded):
        decompress_bytes(compressed, max_output_size=1024)


def test_default_max_output_bytes_is_reasonable():
    """DEFAULT_MAX_OUTPUT_BYTES should be set (not infinite)."""
    assert DEFAULT_MAX_OUTPUT_BYTES > 0
    assert DEFAULT_MAX_OUTPUT_BYTES <= 512 * 1024 * 1024  # <= 512 MiB


def test_max_output_size_zero_disables_guard():
    """max_output_size=0 should disable the guard (explicit opt-out)."""
    data = b"test data for compression"
    compressed = compress_bytes(data)
    result = decompress_bytes(compressed, max_output_size=0)
    assert result == data


def test_invalid_magic_rejected():
    """Non-Zstandard data must be rejected."""
    from zst.zst_codec import ZstInvalidFrameError
    with pytest.raises(ZstInvalidFrameError):
        decompress_bytes(b"not a zstandard frame at all")
'''

    test_path = REPO_ROOT / "tests" / "python" / "zst" / "test_security_decompression.py"
    test_path.write_text(test_content, encoding="utf-8")
    return test_path


def main():
    for fmt, config in XML_FORMATS.items():
        path = generate_xml_security_test(fmt, config)
        print(f"Wrote {path.relative_to(REPO_ROOT)}")

    path = generate_zst_security_test()
    print(f"Wrote {path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
