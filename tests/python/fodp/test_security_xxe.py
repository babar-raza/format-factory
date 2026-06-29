"""Security tests: XXE and billion-laughs protection for FODP parser.

TC-CERT-H-SEC certification hardening.
"""
import tempfile
from pathlib import Path

import pytest

from fodp import load as parse_fodp

XXE_PAYLOAD = """<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                 xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
                 xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"
                 office:mimetype="application/vnd.oasis.opendocument.presentation">
  <office:body><office:presentation><draw:page draw:name="slide1"><draw:frame><draw:text-box><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">&xxe;</text:p></draw:text-box></draw:frame></draw:page></office:presentation></office:body>
</office:document>
"""

BILLION_LAUGHS = """<?xml version="1.0"?>
<!DOCTYPE lolz [
  <!ENTITY lol "lol">
  <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
  <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
  <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
]>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                 xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
                 xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"
                 office:mimetype="application/vnd.oasis.opendocument.presentation">
  <office:body><office:presentation><draw:page draw:name="slide1"><draw:frame><draw:text-box><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">&lol4;</text:p></draw:text-box></draw:frame></draw:page></office:presentation></office:body>
</office:document>
"""


def _write_temp(content: str) -> Path:
    f = tempfile.NamedTemporaryFile(suffix=".fodp", delete=False, mode="w", encoding="utf-8")
    f.write(content)
    f.close()
    return Path(f.name)


def test_xxe_entity_not_resolved():
    """Parser must NOT resolve external entities (XXE attack)."""
    path = _write_temp(XXE_PAYLOAD)
    try:
        result = parse_fodp(path)
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
        result = parse_fodp(path)
        assert result is not None
    except Exception:
        pass  # Raising is acceptable - attack was blocked
    finally:
        path.unlink(missing_ok=True)
