"""
format-factory-odt — ODT (OpenDocument Text) parser prototype.

Gate 4 prototype. FOSS track. No third-party dependencies.
Acquisition gates 1-4 passed. Implementation authorized: R27.
commercial_product_ready: false
"""

from .odt_parser import (
    parse_odt,
    parse_odt_strict,
    probe_odt,
    get_capabilities,
    odt_word_count,
    odt_heading_count,
    odt_paragraph_count,
    odt_char_count,
    odt_list_count,
    OdtError,
    OdtInvalidContainerError,
    OdtSizeError,
    OdtParagraph,
    OdtHeading,
    OdtListItem,
    OdtDocument,
)

__version__ = "0.1.0.dev0"
__track__ = "python-foss"
__commercial_ready__ = False
__capability_level__ = "alpha-foss-preview"

__all__ = [
    "parse_odt",
    "parse_odt_strict",
    "probe_odt",
    "get_capabilities",
    "odt_word_count",
    "odt_heading_count",
    "odt_paragraph_count",
    "odt_char_count",
    "odt_list_count",
    "OdtError",
    "OdtInvalidContainerError",
    "OdtSizeError",
    "OdtParagraph",
    "OdtHeading",
    "OdtListItem",
    "OdtDocument",
]
