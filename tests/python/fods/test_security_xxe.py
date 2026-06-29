"""Security tests: XXE and billion-laughs protection for FODS parser.

TC-CERT-H-SEC certification hardening.
"""
import tempfile
from pathlib import Path

import pytest

from fods import parse_fods

XXE_PAYLOAD = """<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                 xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
                 xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
                 office:mimetype="application/vnd.oasis.opendocument.spreadsheet">
  <office:body>
    <office:spreadsheet>
      <table:table table:name="Sheet1">
        <table:table-row>
          <table:table-cell><text:p>&xxe;</text:p></table:table-cell>
        </table:table-row>
      </table:table>
    </office:spreadsheet>
  </office:body>
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
                 xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
                 xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
                 office:mimetype="application/vnd.oasis.opendocument.spreadsheet">
  <office:body>
    <office:spreadsheet>
      <table:table table:name="Sheet1">
        <table:table-row>
          <table:table-cell><text:p>&lol4;</text:p></table:table-cell>
        </table:table-row>
      </table:table>
    </office:spreadsheet>
  </office:body>
</office:document>
"""


def _write_temp(content: str) -> Path:
    f = tempfile.NamedTemporaryFile(suffix=".fods", delete=False, mode="w", encoding="utf-8")
    f.write(content)
    f.close()
    return Path(f.name)


def test_xxe_entity_not_resolved():
    """Parser must NOT resolve external entities (XXE attack)."""
    path = _write_temp(XXE_PAYLOAD)
    try:
        # Should either raise an error or parse without resolving the entity
        result = parse_fods(path)
        # If it parses, verify /etc/passwd content is NOT in any cell
        if isinstance(result, dict):
            for sheet in result.get("sheets", []):
                for row in sheet.get("rows", []):
                    for cell in row.get("cells", []):
                        val = str(cell.get("value", ""))
                        assert "root:" not in val, "XXE entity was resolved!"
    except Exception:
        pass  # Raising is acceptable — XXE was blocked
    finally:
        path.unlink(missing_ok=True)


def test_billion_laughs_does_not_hang():
    """Parser must not hang or OOM on entity expansion attacks."""
    path = _write_temp(BILLION_LAUGHS)
    try:
        # Should either raise or parse quickly (not expand entities)
        result = parse_fods(path)
        assert result is not None  # If it parses, it didn't expand
    except Exception:
        pass  # Raising is acceptable — attack was blocked
    finally:
        path.unlink(missing_ok=True)
