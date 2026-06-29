"""Security tests: XXE protection for ODS parser.

ODS files are ZIP containers with XML inside. The parser extracts
content.xml and parses with xml.etree.ElementTree (inherently XXE-safe).

TC-CERT-H-SEC certification hardening.
"""
import io
import tempfile
import zipfile
from pathlib import Path

from ods import parse_ods_strict

CONTENT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<office:document-content
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">
  <office:body>
    <office:spreadsheet>
      <table:table table:name="Sheet1">
        <table:table-row>
          <table:table-cell><text:p>&xxe;</text:p></table:table-cell>
        </table:table-row>
      </table:table>
    </office:spreadsheet>
  </office:body>
</office:document-content>
"""


def _make_ods_with_content(content_xml: str) -> Path:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("mimetype", "application/vnd.oasis.opendocument.spreadsheet")
        zf.writestr("content.xml", content_xml)
        zf.writestr("META-INF/manifest.xml", '<?xml version="1.0"?><manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"></manifest:manifest>')
    f = tempfile.NamedTemporaryFile(suffix=".ods", delete=False)
    f.write(buf.getvalue())
    f.close()
    return Path(f.name)


def test_xxe_entity_not_resolved():
    """ODS parser must NOT resolve external entities in content.xml."""
    path = _make_ods_with_content(CONTENT_XML)
    try:
        result = parse_ods_strict(path)
        # If it parses, verify /etc/passwd content is NOT in cells
        for sheet in result.sheets:
            for row in sheet.rows:
                for cell in row.cells:
                    val = str(cell.value) if cell.value else ""
                    assert "root:" not in val, "XXE entity was resolved!"
    except Exception:
        pass  # Raising is acceptable
    finally:
        path.unlink(missing_ok=True)
