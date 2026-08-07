"""UBL-CODELIST-001 -- official code-list data and the genericode loader.

MUST (SAL-UBL-OBL-C717DEB32BC6F815, SAL-UBL-OBL-DE7D98EAE4344EDA):
"Load official code lists from their distribution artifacts" / "Load
official code-list resources, map them to coded properties." Before
this slice, confirmed genuinely absent: no official code-list data was
bundled, and no OASIS genericode XML loader existed -- codelist.py's
own module docstring had honestly documented this as unbuilt, citing
"no verified spec source for either the list content or the genericode
distribution schema."

That was true of the SAL fact cache but not of the pinned RAW spec
acquisition cache: .local/format-contracts/acquired/ubl/src-ubl-002.bin
is a ZIP archive -- confirmed directly by its own "PK" magic bytes and
927 total archive entries -- and is the actual official UBL 2.3
distribution package, not spec prose. Its cl/gc/default/ directory
contains the genuine, OASIS-published genericode files for UBL 2.3's
own standard code lists. 11 of them (excluding the "-incl-deprecated"/
"-incl-deleted" superset variants) are bundled verbatim in
src/format_factory/ubl/model/codelists/.

Deliberately narrow about ONE thing: this loads the 11 bundled lists as
their published genericode files declare them -- it does not attempt
UBL-UPGRADE-001's version-migration mapping between different UBL
schema revisions' own code-list versions, a separate, unrelated
obligation.
"""

from __future__ import annotations

import pytest

from format_factory.ubl import (
    Code,
    CodeList,
    CodeListRegistry,
    load_bundled_code_lists,
    official_code_list_registry,
    parse_genericode,
    validate_code,
)
from format_factory.ubl.model.genericode import _BUNDLED_FILENAMES, _CODELISTS_DIR

_EXPECTED_LIST_IDS = {
    "AllowanceChargeReasonCode",
    "BinaryObjectMimeCode",
    "ChannelCode",
    "CountryIdentificationCode",
    "CurrencyCode",
    "LanguageCode",
    "PackagingTypeCode",
    "PaymentMeansCode",
    "TransportEquipmentTypeCode",
    "TransportModeCode",
    "UnitOfMeasureCode",
}


def test_all_eleven_bundled_lists_load_successfully() -> None:
    lists = load_bundled_code_lists()

    assert {code_list.list_id for code_list in lists} == _EXPECTED_LIST_IDS
    assert len(lists) == 11


def test_every_bundled_list_carries_a_nonempty_value_set() -> None:
    for code_list in load_bundled_code_lists():
        assert isinstance(code_list, CodeList)
        assert len(code_list.values) > 0, code_list.list_id


def test_currency_code_list_contains_iso_4217_alpha_codes() -> None:
    lists = {code_list.list_id: code_list for code_list in load_bundled_code_lists()}
    currency = lists["CurrencyCode"]

    assert "USD" in currency.values
    assert "EUR" in currency.values
    assert "GBP" in currency.values
    assert "NOT-A-REAL-CURRENCY" not in currency.values


def test_country_identification_code_list_contains_iso_3166_codes() -> None:
    lists = {code_list.list_id: code_list for code_list in load_bundled_code_lists()}
    country = lists["CountryIdentificationCode"]

    assert "US" in country.values
    assert "DE" in country.values
    assert "ZZ" not in country.values


def test_unit_of_measure_code_list_contains_common_units() -> None:
    lists = {code_list.list_id: code_list for code_list in load_bundled_code_lists()}
    uom = lists["UnitOfMeasureCode"]

    assert "KGM" in uom.values  # kilogram
    assert "MTR" in uom.values  # metre


def test_currency_code_carries_iso_agency_and_version_metadata() -> None:
    lists = {code_list.list_id: code_list for code_list in load_bundled_code_lists()}
    currency = lists["CurrencyCode"]

    assert currency.agency_id == "5"  # UN/EDIFACT agency code for ISO
    assert currency.version is not None
    assert currency.source


def _currency_code(value: str) -> Code:
    lists = {code_list.list_id: code_list for code_list in load_bundled_code_lists()}
    currency = lists["CurrencyCode"]
    return Code(
        value, list_id="CurrencyCode", list_agency_id=currency.agency_id,
        list_version_id=currency.version,
    )


def test_official_code_list_registry_is_populated_and_ready_to_validate() -> None:
    registry = official_code_list_registry()

    assert isinstance(registry, CodeListRegistry)
    assert len(registry) == 11
    result = validate_code(registry, _currency_code("USD"))
    assert result.is_valid is True


def test_official_code_list_registry_rejects_an_unknown_code() -> None:
    registry = official_code_list_registry()

    result = validate_code(registry, _currency_code("ZZZ"))

    assert result.list_known is True
    assert result.is_valid is False


def test_official_code_list_registry_composes_with_a_user_supplied_list() -> None:
    """Official and user-/profile-supplied lists register identically --
    an official registry is just a pre-populated CodeListRegistry, not a
    separate mechanism, so a caller can extend it freely."""
    registry = official_code_list_registry()
    registry.register(CodeList(list_id="acme-status", values=frozenset({"OPEN", "CLOSED"})))

    assert len(registry) == 12
    assert validate_code(registry, Code("OPEN", list_id="acme-status")).is_valid is True
    assert validate_code(registry, _currency_code("USD")).is_valid


def test_official_code_list_registry_returns_a_fresh_registry_each_call() -> None:
    """Mutating one caller's registry (e.g. registering a custom list on
    it) must not leak into a separately obtained registry."""
    first = official_code_list_registry()
    first.register(CodeList(list_id="custom-only-on-first", values=frozenset({"X"})))

    second = official_code_list_registry()

    assert second.get("custom-only-on-first") is None
    assert len(second) == 11


def test_parse_genericode_extracts_the_declared_key_column_not_a_hardcoded_name() -> None:
    """Genericode does not mandate calling the identifying column "code"
    -- this parses the ColumnSet/Key/ColumnRef declaration rather than
    assuming a fixed column name, proven against a minimal fixture using
    a differently-named key column."""
    fixture = b"""<?xml version="1.0" encoding="UTF-8"?>
<gc:CodeList xmlns:gc="http://docs.oasis-open.org/codelist/ns/genericode/1.0/">
  <Identification>
    <ShortName>TestList</ShortName>
    <Version>1.0</Version>
  </Identification>
  <ColumnSet>
    <Column Id="shortcode" Use="required">
      <ShortName>ShortCode</ShortName>
      <Data Type="string"/>
    </Column>
    <Key Id="k">
      <ShortName>Key</ShortName>
      <ColumnRef Ref="shortcode"/>
    </Key>
  </ColumnSet>
  <SimpleCodeList>
    <Row>
      <Value ColumnRef="shortcode"><SimpleValue>ALPHA</SimpleValue></Value>
    </Row>
    <Row>
      <Value ColumnRef="shortcode"><SimpleValue>BETA</SimpleValue></Value>
    </Row>
  </SimpleCodeList>
</gc:CodeList>"""

    code_list = parse_genericode(fixture)

    assert code_list.list_id == "TestList"
    assert code_list.values == frozenset({"ALPHA", "BETA"})


def test_parse_genericode_rejects_a_non_genericode_root() -> None:
    with pytest.raises(ValueError, match="genericode"):
        parse_genericode(b'<?xml version="1.0"?><notGenericode/>')


def test_parse_genericode_rejects_a_document_missing_identification() -> None:
    fixture = (
        b'<?xml version="1.0"?>'
        b'<gc:CodeList xmlns:gc="http://docs.oasis-open.org/codelist/ns/genericode/1.0/">'
        b"<ColumnSet><Key><ColumnRef Ref=\"code\"/></Key></ColumnSet>"
        b"</gc:CodeList>"
    )

    with pytest.raises(ValueError, match="Identification"):
        parse_genericode(fixture)


def test_every_bundled_filename_is_present_on_disk() -> None:
    """Guards against a package-data configuration drift silently
    dropping a bundled list from the installed wheel."""
    for filename in _BUNDLED_FILENAMES:
        assert (_CODELISTS_DIR / filename).is_file(), filename
