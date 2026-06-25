"""Type stubs for format-factory-fodt (PQ-020)."""
from fodt.parser import parse_fodt as parse_fodt
from fodt.parser import parse_fodt_strict as parse_fodt_strict
from fodt.writer import write_fodt as write_fodt
from fodt.neutral_model import document_paragraph_count as document_paragraph_count
from fodt.neutral_model import document_append_paragraph as document_append_paragraph
from fodt.exceptions import FodtError as FodtError
from fodt.exceptions import FodtInputError as FodtInputError
from fodt.exceptions import FodtParseError as FodtParseError
from fodt.exceptions import FodtSizeError as FodtSizeError
from fodt.models import FodtDocument as FodtDocument
from fodt.models import FodtParagraph as FodtParagraph
from fodt.models import FodtSpan as FodtSpan
from fodt.exporters import fodt_to_txt as fodt_to_txt
from fodt.exporters import fodt_to_markdown as fodt_to_markdown
from fodt.exporters import fodt_to_html as fodt_to_html

__all__: list[str]
