"""XLIFF-PARSE-001 / XLIFF-VALIDATE-001 / XLIFF-MODULE-001 / XLIFF-TEXT-001
-- the official XLIFF 2.1 schema distribution's own structural inventory:
exactly nine Schematron rule sets, one NVDL dispatch artifact, and exactly
nine first-party module XSDs, all bundled with this package.

MUST: three distinct SAL facts, each duplicated across several capability
IDs (SAL-XLIFF-OBL-07A1F5F6A9B3A95F / 1405C2E94EEF25E6 / 21B94445F4216B94;
SAL-XLIFF-OBL-191B67AD2A05CA4E / 56B240550D37E1BA; SAL-XLIFF-OBL-
3059D36881034046 / 9795E0B80A36DEBB / 9B0DC026A5B8E587 / B90CB93CF07C9917)
all describe the OFFICIAL XLIFF 2.1 SCHEMA BUNDLE's own contents -- an
inventory fact about the spec distribution, not product runtime behavior.

Every one of these nine obligations previously carried the same
missing_behavior claim: "No such schema, Schematron, or NVDL files are
vendored anywhere in this repository." That claim was already false for
the module XSDs (bundled at FF6-EVENT-000272) and is now false for the
Schematron/NVDL files too -- src-xlf-002.bin, the exact same pinned ZIP
already mined for the module XSDs, also contains all nine .sch files and
the one .nvdl file. This session's earlier extraction pulled only the
*.xsd entries out of that archive and never re-examined it for the rest.

Deliberately narrow: this proves the bundle's inventory (the files exist,
are the official OASIS-published artifacts, and match each obligation's
own exact count/coverage claim), not that this package can EXECUTE
Schematron rules -- see bundled_schematron_paths()'s own docstring and
test_lxml_isoschematron_cannot_execute_these_files_xslt2_unsupported
below for why that remains a confirmed, real toolchain gap rather than an
oversight.
"""

from __future__ import annotations

import pytest

from format_factory.xliff.validation.schema_validator import (
    _MODULE_SCHEMA_FILENAMES,
    _SCHEMATRON_FILENAMES,
    bundled_module_schema_paths,
    bundled_nvdl_path,
    bundled_schematron_paths,
)


def test_exactly_nine_schematron_rule_sets_are_bundled() -> None:
    paths = bundled_schematron_paths()

    assert len(paths) == 9
    assert all(path.is_file() for path in paths)
    assert all(path.suffix == ".sch" for path in paths)


def test_the_bundled_schematron_covers_core_plus_eight_modules() -> None:
    """ITS Mapping is the one standard module with no Schematron of its
    own -- eight module rule sets, not nine, plus the one core rule set."""
    names = {path.stem for path in bundled_schematron_paths()}

    assert names == {
        "xliff_core_2.1",
        "fs",
        "glossary",
        "its",
        "matches",
        "metadata",
        "resource_data",
        "size_restriction",
        "validation",
    }
    assert "itsm" not in names


def test_nvdl_advanced_validation_dispatch_artifact_is_bundled() -> None:
    path = bundled_nvdl_path()

    assert path.is_file()
    assert path.suffix == ".nvdl"
    assert path.stem == "xliff_2_advanced_validation"


def test_exactly_nine_module_xsds_are_bundled_covering_every_standard_module() -> None:
    paths = bundled_module_schema_paths()

    assert len(_MODULE_SCHEMA_FILENAMES) == 9
    assert len(paths) == 9
    assert all(path.is_file() for path in paths)
    assert {path.stem for path in paths} == {
        "fs",
        "glossary",
        "its",
        "itsm",
        "matches",
        "metadata",
        "resource_data",
        "size_restriction",
        "validation",
    }


def test_bundled_schematron_files_are_well_formed_xml() -> None:
    """Confirms these are genuine XML rule-set files, not truncated or
    corrupted during extraction from the pinned ZIP.

    lxml is not a dependency of this package (bundled_schematron_paths()
    itself needs only pathlib) -- this test only needs it to independently
    verify well-formedness, so it skips gracefully when unavailable rather
    than requiring a new hard dependency for that verification alone.
    """
    etree = pytest.importorskip("lxml.etree", reason="lxml not installed")

    for path in bundled_schematron_paths():
        tree = etree.parse(str(path))
        assert tree.getroot().tag.endswith("schema")


def test_bundled_nvdl_file_is_well_formed_xml() -> None:
    etree = pytest.importorskip("lxml.etree", reason="lxml not installed")

    tree = etree.parse(str(bundled_nvdl_path()))
    assert tree.getroot().tag.endswith("rules")


def test_lxml_isoschematron_cannot_execute_these_files_xslt2_unsupported() -> None:
    """Locks in the concrete, empirically-confirmed reason this package
    does not offer a schematron_validate() function: not an oversight, a
    real toolchain gap. If a future lxml/libxslt upgrade ever adds XSLT 2
    support, this test starts failing and is the signal to revisit."""
    etree = pytest.importorskip("lxml.etree", reason="lxml not installed")
    isoschematron = pytest.importorskip("lxml.isoschematron", reason="lxml not installed")

    core_path = next(p for p in bundled_schematron_paths() if p.stem == "xliff_core_2.1")
    doc = etree.parse(str(core_path))

    with pytest.raises(etree.XSLTApplyError, match="xslt2"):
        isoschematron.Schematron(doc)
