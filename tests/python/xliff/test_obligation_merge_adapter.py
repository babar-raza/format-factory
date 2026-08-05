"""XLIFF-MERGE-001 against the shipped namespace.

SAL-XLIFF-00017 (SHOULD): provide extraction/merge adapter interfaces with
reversible skeleton mappings; detect source drift and stale skeletons before
merge; never claim generic extraction without format-specific adapters.

Written directly against format_factory.xliff, not ported from the shadow
xliff.* package (GAP-018).
"""

from __future__ import annotations

import pytest

from format_factory.xliff import (
    MergeAdapter,
    Skeleton,
    SourceDriftError,
    TemplateMergeAdapter,
    check_drift,
    compute_source_digest,
    merge_with_drift_check,
)

TEMPLATE_SOURCE = b"HEADER: My App\n%%TR%%Hello world%%TR%%\n%%TR%%Goodbye%%TR%%\nFOOTER: v1.0\n"


# ── Protocol conformance ─────────────────────────────────────────────────────


def test_template_adapter_satisfies_the_merge_adapter_protocol() -> None:
    assert isinstance(TemplateMergeAdapter(), MergeAdapter)


def test_custom_adapter_conforming_to_protocol_works() -> None:
    class NullAdapter:
        def extract(self, source: bytes):
            raise NotImplementedError

        def merge(self, document, skeleton) -> bytes:
            return skeleton.template

    assert isinstance(NullAdapter(), MergeAdapter)


# ── Extraction produces a reversible skeleton mapping ───────────────────────


def test_extraction_finds_every_translatable_block() -> None:
    document, skeleton = TemplateMergeAdapter().extract(TEMPLATE_SOURCE)

    units = list(document.iter_units())
    assert len(units) == 2
    assert [unit.segments[0].source[0] for unit in units] == ["Hello world", "Goodbye"]


def test_skeleton_carries_the_non_translatable_structure() -> None:
    """"skeleton elements carry...the non-translatable document skeleton
    needed to reconstruct the original file on merge." """
    _document, skeleton = TemplateMergeAdapter().extract(TEMPLATE_SOURCE)

    assert b"HEADER: My App" in skeleton.template
    assert b"FOOTER: v1.0" in skeleton.template
    assert b"Hello world" not in skeleton.template
    assert b"Goodbye" not in skeleton.template


def test_skeleton_mapping_is_reversible_without_edits() -> None:
    """Merging an untranslated extraction back must reproduce the original
    byte-for-byte -- the mapping is reversible before any edit is made."""
    document, skeleton = TemplateMergeAdapter().extract(TEMPLATE_SOURCE)

    merged = TemplateMergeAdapter().merge(document, skeleton)

    assert merged == TEMPLATE_SOURCE


def test_merge_applies_translated_targets() -> None:
    document, skeleton = TemplateMergeAdapter().extract(TEMPLATE_SOURCE)
    for unit in document.iter_units():
        segment = unit.segments[0]
        segment.target = ["[" + segment.source[0] + "]"]

    merged = TemplateMergeAdapter().merge(document, skeleton)

    assert b"[Hello world]" in merged
    assert b"[Goodbye]" in merged
    assert b"HEADER: My App" in merged
    assert b"FOOTER: v1.0" in merged


def test_merge_falls_back_to_source_when_no_target_set() -> None:
    """An untranslated segment merges back as its own source text, not as an
    empty gap in the reconstructed file."""
    document, skeleton = TemplateMergeAdapter().extract(TEMPLATE_SOURCE)

    merged = TemplateMergeAdapter().merge(document, skeleton)

    assert b"Hello world" in merged


# ── Drift detection ──────────────────────────────────────────────────────────


def test_check_drift_is_none_when_source_is_unchanged() -> None:
    _document, skeleton = TemplateMergeAdapter().extract(TEMPLATE_SOURCE)

    assert check_drift(skeleton, TEMPLATE_SOURCE) is None


def test_check_drift_reports_when_source_has_changed() -> None:
    _document, skeleton = TemplateMergeAdapter().extract(TEMPLATE_SOURCE)
    changed_source = TEMPLATE_SOURCE.replace(b"v1.0", b"v2.0")

    report = check_drift(skeleton, changed_source)

    assert report is not None
    assert "drift" in report.lower()


def test_skeleton_digest_matches_compute_source_digest() -> None:
    _document, skeleton = TemplateMergeAdapter().extract(TEMPLATE_SOURCE)

    assert skeleton.source_digest == compute_source_digest(TEMPLATE_SOURCE)


# ── Merge refuses drifted sources with a report ─────────────────────────────


def test_merge_with_drift_check_succeeds_against_intact_source() -> None:
    """"Merge with intact and drifted sources; drift refused with report." --
    the intact half."""
    document, skeleton = TemplateMergeAdapter().extract(TEMPLATE_SOURCE)

    merged = merge_with_drift_check(
        TemplateMergeAdapter(), document, skeleton, live_source=TEMPLATE_SOURCE
    )

    assert merged == TEMPLATE_SOURCE


def test_merge_with_drift_check_refuses_a_drifted_source() -> None:
    """The drifted half: a stale skeleton must be refused, not silently
    merged into a result claiming to reconstruct a source it no longer
    matches."""
    document, skeleton = TemplateMergeAdapter().extract(TEMPLATE_SOURCE)
    changed_source = TEMPLATE_SOURCE.replace(b"My App", b"My Renamed App")

    with pytest.raises(SourceDriftError) as raised:
        merge_with_drift_check(
            TemplateMergeAdapter(), document, skeleton, live_source=changed_source
        )

    assert "drift" in str(raised.value).lower()


def test_merge_with_drift_check_skips_the_check_when_no_live_source_given() -> None:
    """A caller merging straight from the skeleton just extracted, with no
    independent live source, has nothing to compare against -- this must not
    be treated as drift."""
    document, skeleton = TemplateMergeAdapter().extract(TEMPLATE_SOURCE)

    merged = merge_with_drift_check(TemplateMergeAdapter(), document, skeleton)

    assert merged == TEMPLATE_SOURCE


def test_drift_report_names_both_digests() -> None:
    _document, skeleton = TemplateMergeAdapter().extract(TEMPLATE_SOURCE)
    changed_source = TEMPLATE_SOURCE + b"\nEXTRA\n"

    report = check_drift(skeleton, changed_source)

    assert skeleton.source_digest in report
    assert compute_source_digest(changed_source) in report
