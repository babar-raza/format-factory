"""OASIS genericode 1.0 code-list loader.

UBL-CODELIST-001's two loading obligations ask for: "Load official code
lists from their distribution artifacts" and "Load official code-list
resources, map them to coded properties." codelist.py's own module
docstring had correctly and honestly documented this as unbuilt:
"[this module] does NOT bundle actual official code-list data ... and
does not parse the OASIS genericode XML distribution format those lists
ship in. No SAL fact in this repository's committed spec cache
enumerates any such list's actual values or documents the genericode
schema with enough precision."

That was true of the SAL fact cache, but not of the pinned raw spec
acquisition cache: .local/format-contracts/acquired/ubl/src-ubl-002.bin
is a ZIP archive -- the actual official UBL 2.3 distribution package
(confirmed by its own "PK" magic bytes and 927 total archive entries),
not spec prose. Its cl/gc/default/ directory contains the genuine,
OASIS-published genericode files for UBL 2.3's own standard code lists
(CurrencyCode = ISO 4217, CountryIdentificationCode = ISO 3166,
UnitOfMeasureCode, PaymentMeansCode, LanguageCode, and others). This
module bundles 11 of those files verbatim (the "-incl-deprecated"/
"-incl-deleted" superset variants are excluded to keep bundled data to
current, non-deprecated values only) and parses the genericode format
directly against the OASIS Genericode 1.0 structure these files
themselves exhibit: Identification/ShortName names the list,
Identification/Version and Identification/Agency/Identifier provide
version/agency, ColumnSet/Key/ColumnRef names which column is the
list's own primary identifying value, and each SimpleCodeList/Row's
matching Value/SimpleValue supplies one member value.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from .codelist import CodeList, CodeListRegistry

_CODELISTS_DIR = Path(__file__).parent / "codelists"

_GC_NAMESPACE = "http://docs.oasis-open.org/codelist/ns/genericode/1.0/"
_ROOT_TAG = f"{{{_GC_NAMESPACE}}}CodeList"


def parse_genericode(source: bytes | str) -> CodeList:
    """Parse one OASIS genericode 1.0 document into a :class:`CodeList`.

    Only the document's own root element (gc:CodeList) carries the
    genericode namespace prefix in these bundled files -- confirmed
    directly against the actual parsed tree rather than assumed from the
    schema's own informal description: every descendant element
    (Identification, ColumnSet, Row, Value, ...) is unprefixed, in no
    namespace at all. Matched against the real files, not guessed.

    Extracts the list's own declared primary key column (ColumnSet/Key/
    ColumnRef), not a hardcoded column name -- genericode does not
    mandate calling the identifying column "code", it only requires a
    Key element naming whichever column is the identifier; every UBL 2.3
    standard code list bundled here happens to name it "code", but this
    reads the declaration rather than assuming that convention holds.
    """

    root = ET.fromstring(source)
    if root.tag != _ROOT_TAG:
        raise ValueError(f"expected a genericode {_ROOT_TAG!r} root, got {root.tag!r}")

    identification = root.find("Identification")
    if identification is None:
        raise ValueError("genericode document has no Identification element")
    short_name = identification.findtext("ShortName")
    if not short_name:
        raise ValueError("genericode Identification has no ShortName")
    version = identification.findtext("Version")
    agency = identification.find("Agency")
    agency_id = agency.findtext("Identifier") if agency is not None else None

    column_set = root.find("ColumnSet")
    if column_set is None:
        raise ValueError("genericode document has no ColumnSet element")
    key = column_set.find("Key")
    if key is None:
        raise ValueError("genericode ColumnSet has no Key element")
    key_ref_element = key.find("ColumnRef")
    if key_ref_element is None or "Ref" not in key_ref_element.attrib:
        raise ValueError("genericode Key has no ColumnRef/@Ref")
    key_column_ref = key_ref_element.attrib["Ref"]

    values: set[str] = set()
    simple_code_list = root.find("SimpleCodeList")
    if simple_code_list is not None:
        for row in simple_code_list.findall("Row"):
            for value_element in row.findall("Value"):
                if value_element.attrib.get("ColumnRef") != key_column_ref:
                    continue
                simple_value = value_element.findtext("SimpleValue")
                if simple_value:
                    values.add(simple_value)

    return CodeList(
        list_id=short_name,
        values=frozenset(values),
        agency_id=agency_id,
        version=version,
        source="OASIS genericode, bundled from the pinned UBL 2.3 distribution package",
    )


#: The 11 bundled genericode files, excluding "-incl-deprecated"/
#: "-incl-deleted" superset variants (current, non-deprecated values only).
_BUNDLED_FILENAMES = (
    "AllowanceChargeReasonCode-2.3.gc",
    "BinaryObjectMimeCode-2.3.gc",
    "ChannelCode-2.3.gc",
    "CountryIdentificationCode-2.3.gc",
    "CurrencyCode-2.3.gc",
    "LanguageCode-2.3.gc",
    "PackagingTypeCode-2.3.gc",
    "PaymentMeansCode-2.3.gc",
    "TransportEquipmentTypeCode-2.3.gc",
    "TransportModeCode-2.3.gc",
    "UnitOfMeasureCode-2.3.gc",
)


def load_bundled_code_lists() -> tuple[CodeList, ...]:
    """Parse and return every bundled official UBL 2.3 genericode list."""

    lists = []
    for filename in _BUNDLED_FILENAMES:
        data = (_CODELISTS_DIR / filename).read_bytes()
        lists.append(parse_genericode(data))
    return tuple(lists)


def official_code_list_registry() -> CodeListRegistry:
    """A :class:`CodeListRegistry` pre-populated with every bundled
    official UBL 2.3 code list, ready for :func:`validate_code`.

    A fresh registry every call -- the registry itself is a plain mutable
    object a caller may go on to extend with profile-/user-supplied
    lists via the same :meth:`CodeListRegistry.register` any custom list
    uses, matching codelist.py's own "no architectural difference
    between official and custom" design exactly.
    """

    registry = CodeListRegistry()
    for code_list in load_bundled_code_lists():
        registry.register(code_list)
    return registry


__all__ = ["load_bundled_code_lists", "official_code_list_registry", "parse_genericode"]
