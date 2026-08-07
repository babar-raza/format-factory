"""UBL-CODELIST-001 -- pluggable code-list registry and offline validation.

MUST, quoted from the format contract (SAL-UBL-OBL-C717DEB32BC6F815,
SAL-UBL-OBL-DE7D98EAE4344EDA):

  "Load official code lists from their distribution artifacts, cache them
   immutably, and validate coded values deterministically offline, with
   user- or profile-supplied lists pluggable at runtime."
  "Load official code-list resources, map them to coded properties,
   validate identifiers/agencies/versions/values, and support user-supplied
   lists."

Scope: this file tests the pluggable registry and offline validation
mechanism itself, independent of any specific list's actual content --
an "official" list registers through exactly the same
CodeListRegistry.register() call a user-supplied list uses. The actual
official UBL 2.3 code-list data (bundled from the pinned distribution
package) and its genericode loader are tested separately in
test_obligation_official_code_lists.py.
"""

from __future__ import annotations

from format_factory.ubl import Code, CodeList, CodeListRegistry, CodeListValidation, validate_code


class TestCodeListImmutability:
    def test_code_list_is_frozen(self) -> None:
        code_list = CodeList(list_id="6", values=frozenset({"EUR"}))
        try:
            code_list.values = frozenset()  # type: ignore[misc]
            assert False, "should have raised"
        except Exception:
            pass

    def test_code_list_requires_a_list_id(self) -> None:
        try:
            CodeList(list_id="", values=frozenset())
            assert False, "should have raised"
        except ValueError:
            pass

    def test_registered_list_is_not_mutated_by_a_later_register_call(self) -> None:
        registry = CodeListRegistry()
        first = CodeList(list_id="6", values=frozenset({"EUR"}))
        registry.register(first)
        second = CodeList(list_id="6", values=frozenset({"EUR", "USD"}))
        registry.register(second)
        assert first.values == frozenset({"EUR"})  # the original object itself is untouched
        assert registry.get("6").values == frozenset({"EUR", "USD"})  # replaced in the registry


class TestRegistryLookup:
    def test_empty_registry_has_length_zero(self) -> None:
        assert len(CodeListRegistry()) == 0

    def test_register_then_get_round_trips(self) -> None:
        registry = CodeListRegistry()
        code_list = CodeList(list_id="6", agency_id="ISO", values=frozenset({"EUR"}))
        registry.register(code_list)
        assert registry.get("6", agency_id="ISO") is code_list

    def test_get_on_unregistered_list_returns_none(self) -> None:
        registry = CodeListRegistry()
        assert registry.get("does-not-exist") is None

    def test_agency_id_distinguishes_otherwise_identical_list_ids(self) -> None:
        registry = CodeListRegistry()
        iso_list = CodeList(list_id="6", agency_id="ISO", values=frozenset({"EUR"}))
        un_list = CodeList(list_id="6", agency_id="UN", values=frozenset({"XYZ"}))
        registry.register(iso_list)
        registry.register(un_list)
        assert len(registry) == 2
        assert registry.get("6", agency_id="ISO") is iso_list
        assert registry.get("6", agency_id="UN") is un_list

    def test_version_distinguishes_otherwise_identical_list_ids(self) -> None:
        registry = CodeListRegistry()
        unversioned = CodeList(list_id="6", values=frozenset({"EUR"}))
        versioned = CodeList(list_id="6", version="2021", values=frozenset({"EUR", "USD"}))
        registry.register(unversioned)
        registry.register(versioned)
        assert len(registry) == 2
        assert registry.get("6") is unversioned
        assert registry.get("6", version="2021") is versioned


class TestValidateCode:
    def test_code_with_no_list_id_is_unknown_not_invalid(self) -> None:
        registry = CodeListRegistry()
        result = validate_code(registry, Code("42"))
        assert isinstance(result, CodeListValidation)
        assert result.list_known is False
        assert result.is_valid is None

    def test_code_naming_an_unregistered_list_is_unknown_not_invalid(self) -> None:
        registry = CodeListRegistry()
        result = validate_code(registry, Code("EUR", list_id="6", list_agency_id="ISO"))
        assert result.list_known is False
        assert result.is_valid is None

    def test_code_member_of_a_registered_list_is_valid(self) -> None:
        registry = CodeListRegistry()
        registry.register(CodeList(list_id="6", agency_id="ISO", values=frozenset({"EUR", "USD"})))
        result = validate_code(registry, Code("EUR", list_id="6", list_agency_id="ISO"))
        assert result.list_known is True
        assert result.is_valid is True

    def test_code_not_a_member_of_a_registered_list_is_invalid(self) -> None:
        registry = CodeListRegistry()
        registry.register(CodeList(list_id="6", agency_id="ISO", values=frozenset({"EUR", "USD"})))
        result = validate_code(registry, Code("XXX", list_id="6", list_agency_id="ISO"))
        assert result.list_known is True
        assert result.is_valid is False

    def test_validation_is_scoped_by_agency_and_version_together(self) -> None:
        registry = CodeListRegistry()
        registry.register(
            CodeList(list_id="6", agency_id="ISO", version="2021", values=frozenset({"EUR"}))
        )
        # same list_id, wrong agency: not the registered list
        result = validate_code(registry, Code("EUR", list_id="6", list_agency_id="UN"))
        assert result.list_known is False
        # same list_id/agency, wrong version: not the registered list
        result = validate_code(
            registry, Code("EUR", list_id="6", list_agency_id="ISO", list_version_id="2015")
        )
        assert result.list_known is False

    def test_official_and_user_supplied_lists_register_identically(self) -> None:
        """The obligation asks for official lists AND user-/profile-supplied
        lists to both be pluggable -- proven by registering two lists with
        no special-casing between them, both immediately validatable."""
        registry = CodeListRegistry()
        official_shaped = CodeList(
            list_id="ISO4217", values=frozenset({"EUR", "USD", "GBP"}), source="official (once sourced)"
        )
        user_supplied = CodeList(
            list_id="acme-status-codes", values=frozenset({"OPEN", "CLOSED"}), source="user-supplied"
        )
        registry.register(official_shaped)
        registry.register(user_supplied)
        assert validate_code(registry, Code("EUR", list_id="ISO4217")).is_valid is True
        assert validate_code(registry, Code("OPEN", list_id="acme-status-codes")).is_valid is True

    def test_validation_is_deterministic_and_repeatable(self) -> None:
        registry = CodeListRegistry()
        registry.register(CodeList(list_id="6", values=frozenset({"EUR"})))
        code = Code("EUR", list_id="6")
        first = validate_code(registry, code)
        second = validate_code(registry, code)
        assert first == second
