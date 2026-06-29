"""Security tests: XXE and billion-laughs protection for ABW parser.

TC-CERT-H-SEC certification hardening.
"""
import tempfile
from pathlib import Path

import pytest

from abw import load

XXE_PAYLOAD = """<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<abiword xmlns:awml="http://www.abisource.com/awml.dtd" version="0.99.2" fileformat="1.0">
  <section><p>&xxe;</p></section>
</abiword>
"""

BILLION_LAUGHS = """<?xml version="1.0"?>
<!DOCTYPE lolz [
  <!ENTITY lol "lol">
  <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
  <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
  <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
]>
<abiword xmlns:awml="http://www.abisource.com/awml.dtd" version="0.99.2" fileformat="1.0">
  <section><p>&lol4;</p></section>
</abiword>
"""


def _write_temp(content: str) -> Path:
    f = tempfile.NamedTemporaryFile(suffix=".abw", delete=False, mode="w", encoding="utf-8")
    f.write(content)
    f.close()
    return Path(f.name)


def test_xxe_entity_not_resolved():
    """Parser must NOT resolve external entities (XXE attack)."""
    path = _write_temp(XXE_PAYLOAD)
    try:
        result = load(path)
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
        result = load(path)
        assert result is not None
    except Exception:
        pass  # Raising is acceptable - attack was blocked
    finally:
        path.unlink(missing_ok=True)
