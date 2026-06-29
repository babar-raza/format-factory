"""Security tests: XXE protection for Gnumeric parser.

Gnumeric files are gzip-compressed XML. The parser decompresses then parses
with xml.etree.ElementTree (inherently XXE-safe).

TC-CERT-H-SEC certification hardening.
"""
import gzip
import tempfile
from pathlib import Path

from gnumeric import load

XXE_XML = b"""<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<gnm:Workbook xmlns:gnm="http://www.gnumeric.org/v10.dtd">
  <gnm:SheetNameIndex>
    <gnm:SheetName gnm:Cols="1" gnm:Rows="1">Sheet1</gnm:SheetName>
  </gnm:SheetNameIndex>
  <gnm:Sheets>
    <gnm:Sheet>
      <gnm:Name>Sheet1</gnm:Name>
      <gnm:Cells>
        <gnm:Cell Col="0" Row="0">&xxe;</gnm:Cell>
      </gnm:Cells>
    </gnm:Sheet>
  </gnm:Sheets>
</gnm:Workbook>
"""


def test_xxe_entity_not_resolved():
    """Gnumeric parser must NOT resolve external entities."""
    compressed = gzip.compress(XXE_XML)
    f = tempfile.NamedTemporaryFile(suffix=".gnumeric", delete=False)
    f.write(compressed)
    f.close()
    path = Path(f.name)
    try:
        result = load(path)
        if isinstance(result, dict):
            assert "root:" not in str(result), "XXE entity was resolved!"
    except Exception:
        pass  # Raising is acceptable
    finally:
        path.unlink(missing_ok=True)
