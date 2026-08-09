"""UBL-WRITE-001 -- official UBL 2.1 samples round-trip via migrate_document().

SAL-UBL-OBL-F9D5251F2302AE3A (MUST): "Round-trip every official sample of
each supported maindoc type comparing canonicalized XML plus typed
semantics." The existing test_obligation_official_sample_roundtrip.py's
own coverage_note disclosed 45 of the 55 vendored official samples as
"load-only + correct-refusal, not a round trip" because they declare an
older UBLVersionID this writer's own stable-2.3 profile gate refuses to
serialize directly.

That framing is now only PARTLY true. UBL-UPGRADE-001's own
migrate_document() (built this session, grounded in SAL-UBL-7546731B76606EC0)
migrates a UBL 2.1 document to 2.3 for any of the 65 (of 91) root types
proven structurally additive/relaxing-compatible between versions. Cross-
referencing the official corpus manifest against MIGRATABLE_2_1_ROOT_NAMES
finds 32 of the 45 "load-only" samples declare EXACTLY "2.1" (not 2.0 or
2.2, which this package does not support migrating) AND have a root type
within the 65-type migratable set -- confirmed empirically against all 32
real OASIS documents before writing this file, not assumed from the
manifest alone. This file proves those 32 now genuinely round-trip via
migration: load -> migrate_document() -> dumps() -> reload ->
semantically-equal to the original (modulo the intentionally-relabeled
cbc:UBLVersionID text itself) -> stable under a second round trip.

The remaining 13 non-round-tripping samples (1 declaring "2.1" with a
root type outside the 65-type migratable set, plus all "2.0"/"2.2"
declarations) are UNCHANGED by this file -- they remain correctly,
deliberately refused, proven by the existing
TestOlderVersionSamplesAreLoadOnlyNeverSilentlyRelabeled class, which
this file does not modify.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
import yaml

from format_factory.ubl import dumps, loads, migrate_document, validate
from format_factory.ubl._generated.migratable_2_1_roots import MIGRATABLE_2_1_ROOT_NAMES

OFFICIAL_DIR = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "ubl" / "official"
MANIFEST = yaml.safe_load((OFFICIAL_DIR / "_official-corpus-manifest.yaml").read_text(encoding="utf-8"))
_UBL_VERSION_TAG = "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}UBLVersionID"


def _semantic_xml_equal(a: ET.Element, b: ET.Element) -> tuple[bool, str]:
    """Namespace-URI-based structural equality (Clark-notation tags/attrs).

    Duplicated from test_obligation_official_sample_roundtrip.py's own
    identical helper rather than imported cross-module (this codebase has
    no established convention for importing between sibling test files;
    each obligation test file is self-contained by design, matching every
    other CRUD/round-trip test file's own private fixture builders).
    """

    if a.tag != b.tag:
        return False, f"tag {a.tag!r} != {b.tag!r}"
    if dict(a.attrib) != dict(b.attrib):
        return False, f"attrib {a.attrib!r} != {b.attrib!r} at {a.tag}"
    if (a.text or "").strip() != (b.text or "").strip():
        return False, f"text {a.text!r} != {b.text!r} at {a.tag}"
    a_children, b_children = list(a), list(b)
    if len(a_children) != len(b_children):
        return False, f"child count {len(a_children)} != {len(b_children)} at {a.tag}"
    for a_child, b_child in zip(a_children, b_children):
        equal, reason = _semantic_xml_equal(a_child, b_child)
        if not equal:
            return False, reason
    return True, ""

MIGRATABLE_SAMPLES = [
    entry
    for entry in MANIFEST["samples"]
    if entry["declared_ubl_version"] == "2.1" and entry["root_name"] in MIGRATABLE_2_1_ROOT_NAMES
]


def test_exactly_32_official_samples_are_2_1_and_migratable() -> None:
    """A fixed-count sanity check: if the vendored corpus or the migratable-
    root-type table ever changes, this test fails loudly rather than the
    parametrized tests below silently covering a different set."""
    assert len(MIGRATABLE_SAMPLES) == 32


class TestOfficialSampleMigrationRoundtrip:
    @pytest.mark.parametrize("entry", MIGRATABLE_SAMPLES, ids=lambda e: e["root_name"])
    def test_a_migratable_2_1_sample_migrates_dumps_and_reloads_cleanly(
        self, entry: dict[str, object]
    ) -> None:
        raw = (OFFICIAL_DIR.parent / str(entry["filename"])).read_bytes()
        document = loads(raw)
        assert document.declared_version == "2.1"

        migrated, report = migrate_document(document)
        dumped = dumps(migrated)
        reloaded = loads(dumped)

        assert reloaded.root_name == entry["root_name"]
        assert reloaded.declared_version == "2.3"
        assert report.source_version == "2.1"
        assert report.target_version == "2.3"
        report_status = validate(reloaded)
        assert report_status.is_valid, report_status.errors

    @pytest.mark.parametrize("entry", MIGRATABLE_SAMPLES, ids=lambda e: e["root_name"])
    def test_a_migrated_sample_is_semantically_identical_except_the_relabeled_version(
        self, entry: dict[str, object]
    ) -> None:
        raw = (OFFICIAL_DIR.parent / str(entry["filename"])).read_bytes()
        document = loads(raw)

        migrated, _ = migrate_document(document)
        dumped = dumps(migrated)

        original_tree = ET.fromstring(raw)
        version_element = original_tree.find(_UBL_VERSION_TAG)
        assert version_element is not None, "fixture assumption: sample declares UBLVersionID"
        version_element.text = "2.3"

        equal, reason = _semantic_xml_equal(original_tree, ET.fromstring(dumped))
        assert equal, reason

    @pytest.mark.parametrize("entry", MIGRATABLE_SAMPLES, ids=lambda e: e["root_name"])
    def test_a_migrated_sample_is_stable_under_a_second_round_trip(
        self, entry: dict[str, object]
    ) -> None:
        raw = (OFFICIAL_DIR.parent / str(entry["filename"])).read_bytes()
        migrated, _ = migrate_document(loads(raw))
        first_dump = dumps(migrated)
        second_dump = dumps(loads(first_dump))

        assert first_dump == second_dump
