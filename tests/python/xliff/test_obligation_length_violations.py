"""XLIFF-QA-001 -- length violations, the one named QA category this
package's own qa.py previously left genuinely unimplemented.

SAL-XLIFF-6F42212680161FF2 (SHOULD): missing/unchanged targets, code
mismatches, whitespace/punctuation drift, length violations, and
inconsistent translations are pluggable QA checks kept separate from
conformance errors.

qa.py's own prior module docstring framed length checking as needing "the
same whole-tree, parent-aware resolution this package has deliberately
not built for xml:space/xml:lang inheritance." Investigated and found
that framing was inaccurate: effective_xml_space()/effective_xml_lang()'s
own top-down composition pattern (built for XLIFF-MODEL-001, already
proven by effective_attributes_by_unit()) directly applies to
sizeRestriction/storageRestriction's own identical nearest-ancestor-wins
shape. The pinned XLIFF 2.1 spec (Section 5.7.6 "Standard profiles")
fully and precisely defines all 4 standard profiles this file exercises:
xliff:codepoints (Unicode code point count) and the 3 storage profiles
xliff:utf8/utf16/utf32 (byte count under that encoding, without a byte
order mark).
"""

from __future__ import annotations

from format_factory.xliff import check_length_violations, loads

XLIFF_NS = "urn:oasis:names:tc:xliff:document:2.0"
SLR_NS = "urn:oasis:names:tc:xliff:sizerestriction:2.0"


def _document(file_body: str, *, trg_lang: str = "fr") -> bytes:
    return (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<xliff xmlns="{XLIFF_NS}" xmlns:slr="{SLR_NS}" '
        f'version="2.1" srcLang="en" trgLang="{trg_lang}">'
        f'<file id="f1">{file_body}</file>'
        f"</xliff>"
    ).encode("utf-8")


def _profiles(*, general: str | None = None, storage: str | None = None) -> str:
    attrs = ""
    if general is not None:
        attrs += f' generalProfile="{general}"'
    if storage is not None:
        attrs += f' storageProfile="{storage}"'
    return f"<slr:profiles{attrs}/>"


def _unit_with_segment(
    unit_id: str,
    target_text: str,
    *,
    size_restriction: str | None = None,
    storage_restriction: str | None = None,
) -> str:
    attrs = ""
    if size_restriction is not None:
        attrs += f' slr:sizeRestriction="{size_restriction}"'
    if storage_restriction is not None:
        attrs += f' slr:storageRestriction="{storage_restriction}"'
    return (
        f'<unit id="{unit_id}"{attrs}>'
        f'<segment id="s1"><source>x</source><target>{target_text}</target></segment>'
        f"</unit>"
    )


class TestCodepointsProfile:
    def test_a_target_exceeding_the_maximum_is_flagged(self) -> None:
        body = _profiles(general="xliff:codepoints") + _unit_with_segment(
            "u1", "this is way too long", size_restriction="5"
        )
        report = check_length_violations(loads(_document(body)))

        assert len(report) == 1
        assert report[0].code == "xliff.qa.length.size.over"

    def test_a_target_within_bounds_is_not_flagged(self) -> None:
        body = _profiles(general="xliff:codepoints") + _unit_with_segment(
            "u1", "ok", size_restriction="1,5"
        )
        report = check_length_violations(loads(_document(body)))

        assert report == []

    def test_a_target_below_the_minimum_is_flagged(self) -> None:
        body = _profiles(general="xliff:codepoints") + _unit_with_segment(
            "u1", "ab", size_restriction="3,10"
        )
        report = check_length_violations(loads(_document(body)))

        assert len(report) == 1
        assert report[0].code == "xliff.qa.length.size.under"

    def test_an_unbounded_maximum_never_flags(self) -> None:
        body = _profiles(general="xliff:codepoints") + _unit_with_segment(
            "u1", "this can be arbitrarily long with no restriction at all", size_restriction="*"
        )
        report = check_length_violations(loads(_document(body)))

        assert report == []


class TestStorageProfiles:
    def test_utf8_counts_encoded_bytes_not_codepoints(self) -> None:
        # 2 codepoints, each 2 bytes in UTF-8 -> 4 bytes total, over a max of 3.
        body = _profiles(storage="xliff:utf8") + _unit_with_segment(
            "u1", "éé", storage_restriction="3"
        )
        report = check_length_violations(loads(_document(body)))

        assert len(report) == 1
        assert report[0].code == "xliff.qa.length.storage.over"

    def test_the_same_text_is_within_bounds_under_the_codepoints_profile(self) -> None:
        # Same 2-codepoint text: 2 codepoints is within a codepoints-profile max of 3.
        body = _profiles(general="xliff:codepoints") + _unit_with_segment(
            "u1", "éé", size_restriction="3"
        )
        report = check_length_violations(loads(_document(body)))

        assert report == []

    def test_general_and_storage_restrictions_are_both_checked_independently(self) -> None:
        body = _profiles(
            general="xliff:codepoints", storage="xliff:utf8"
        ) + _unit_with_segment(
            "u1", "éé", size_restriction="1", storage_restriction="1"
        )
        report = check_length_violations(loads(_document(body)))

        codes = {d.code for d in report}
        assert codes == {"xliff.qa.length.size.over", "xliff.qa.length.storage.over"}


class TestInheritance:
    def test_a_unit_without_its_own_restriction_inherits_from_its_enclosing_group(self) -> None:
        body = _profiles(general="xliff:codepoints") + (
            '<group id="g1" slr:sizeRestriction="3">'
            + _unit_with_segment("u1", "this is too long")
            + "</group>"
        )
        report = check_length_violations(loads(_document(body)))

        assert len(report) == 1
        assert report[0].code == "xliff.qa.length.size.over"

    def test_a_unit_level_restriction_overrides_its_enclosing_group(self) -> None:
        body = _profiles(general="xliff:codepoints") + (
            '<group id="g1" slr:sizeRestriction="1">'
            + _unit_with_segment("u1", "short", size_restriction="100")
            + "</group>"
        )
        report = check_length_violations(loads(_document(body)))

        assert report == []

    def test_a_file_level_restriction_applies_when_no_group_or_unit_overrides_it(self) -> None:
        xml = (
            f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<xliff xmlns="{XLIFF_NS}" xmlns:slr="{SLR_NS}" '
            f'version="2.1" srcLang="en" trgLang="fr">'
            f'<file id="f1" slr:sizeRestriction="3">'
            f"{_profiles(general='xliff:codepoints')}"
            f"{_unit_with_segment('u1', 'too long here')}"
            f"</file></xliff>"
        ).encode("utf-8")
        report = check_length_violations(loads(xml))

        assert len(report) == 1
        assert report[0].code == "xliff.qa.length.size.over"


class TestNoRestrictionOrNoProfileMeansNoViolationsChecked:
    def test_no_slr_profiles_element_at_all_checks_nothing(self) -> None:
        body = _unit_with_segment("u1", "this is a very long target text", size_restriction="1")
        report = check_length_violations(loads(_document(body)))

        assert report == []

    def test_a_declared_but_unrecognized_profile_is_silently_skipped(self) -> None:
        body = _profiles(general="acme:custom") + _unit_with_segment(
            "u1", "this would violate a restriction of 1 if checked", size_restriction="1"
        )
        report = check_length_violations(loads(_document(body)))

        assert report == []

    def test_a_unit_with_no_restriction_declared_anywhere_is_not_checked(self) -> None:
        body = _profiles(general="xliff:codepoints") + _unit_with_segment(
            "u1", "no restriction applies to this at all, however long"
        )
        report = check_length_violations(loads(_document(body)))

        assert report == []

    def test_an_unparseable_restriction_value_is_treated_as_absent_not_a_crash(self) -> None:
        body = _profiles(general="xliff:codepoints") + _unit_with_segment(
            "u1", "some text", size_restriction="not-a-number"
        )
        report = check_length_violations(loads(_document(body)))

        assert report == []
