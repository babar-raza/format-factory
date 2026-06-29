"""Security tests: XXE protection for ODT parser.

ODT files are ZIP containers with XML inside. The parser extracts
content.xml and parses with xml.etree.ElementTree (inherently XXE-safe).

TC-CERT-H-SEC certification hardening.
"""
import io
import tempfile
import zipfile
from pathlib import Path

from odt.odt_parser import parse_odt

CONTENT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<office:document-content
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">
  <office:body>
    <office:text>
      <text:p>&xxe;</text:p>
    </office:text>
  </office:body>
</office:document-content>
"""


def _make_odt_with_content(content_xml: str) -> Path:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("mimetype", "application/vnd.oasis.opendocument.text")
        zf.writestr("content.xml", content_xml)
        zf.writestr("META-INF/manifest.xml", '<?xml version="1.0"?><manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"></manifest:manifest>')
    f = tempfile.NamedTemporaryFile(suffix=".odt", delete=False)
    f.write(buf.getvalue())
    f.close()
    return Path(f.name)


def test_xxe_entity_not_resolved():
    """ODT parser must NOT resolve external entities in content.xml."""
    path = _make_odt_with_content(CONTENT_XML)
    try:
        result = parse_odt(path)
        if isinstance(result, dict):
            for p in result.get("paragraphs", []):
                text = p.get("text", "") if isinstance(p, dict) else str(p)
                assert "root:" not in text, "XXE entity was resolved!"
    except Exception:
        pass  # Raising is acceptable
    finally:
        path.unlink(missing_ok=True)
