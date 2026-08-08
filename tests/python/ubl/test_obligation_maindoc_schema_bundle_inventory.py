"""UBL-DOCTYPES-001 / UBL-PARSE-001 / UBL-VALIDATE-001 -- the pinned UBL
2.3 OASIS Standard distribution package's own structural inventory:
exactly 91 maindoc XSD files, one per supported root document type.

MUST: three obligations share byte-identical rule_text (SAL-UBL-OBL-
1549D8ECF079779C, 1EEEC2DD4CA2C80E, 2FCD900E00C1654E) describing the
official pinned package's own contents -- an inventory fact about the
spec distribution, not product runtime behavior. All three previously
carried a stale missing_behavior claim: "No XSD files from the official
package are vendored in this repository." That was already false --
FF6-EVENT-000274 bundled all 91 maindoc files (plus 15 common component
schemas) from the same pinned src-ubl-002.bin ZIP already used for the
official genericode code lists -- but the evidence was never linked to
these three specific obligation IDs, the same "resolved capability,
un-reconciled obligation" shape found for xliff's module-XSD-inventory
cluster at FF6-EVENT-000277.
"""

from __future__ import annotations

from format_factory.ubl import bundled_maindoc_schema_paths
from format_factory.ubl._generated.root_catalog import ROOT_NAME_SET


def test_exactly_ninety_one_maindoc_schemas_are_bundled() -> None:
    paths = bundled_maindoc_schema_paths()

    assert len(paths) == 91
    assert all(path.is_file() for path in paths)
    assert all(path.suffix == ".xsd" for path in paths)


def test_bundled_maindoc_schemas_cover_every_root_name_set_entry() -> None:
    """One schema per supported root document type, no more, no fewer --
    the exact claim this obligation cluster makes."""
    paths = bundled_maindoc_schema_paths()

    stems = {path.stem for path in paths}
    expected = {f"UBL-{name}-2.3" for name in ROOT_NAME_SET}

    assert stems == expected
    assert len(ROOT_NAME_SET) == 91
