"""XLIFF-PARSE-001 / XLIFF-MODULE-001 -- Validation module constraint
types.

MUST (SAL-XLIFF-OBL-CC8F94A8623CA191 and its cross-capability duplicate
SAL-XLIFF-OBL-251C3608521B6A97): "the specific constraint types this
module defines (presence, occurrence, boundary, source-existence, case,
normalization, disabled) are not modeled or tested individually -- the
module is preserved only as opaque extension content." Confirmed
genuinely true before this slice by direct probing: validation content
round-trips (test_validation_module_round_trips in
test_obligation_module_coverage.py), but validate() never inspected it.

Grounded directly in the pinned XLIFF 2.1 specification text and schema
(.local/format-contracts/acquired/xliff/src-xliff-003.bin, Section 5.8
"Validation Module" and its bundled validation.xsd):

- presence/boundary: rule's own prose Constraints section -- "Exactly
  one of the following attributes: isPresent, isNotPresent, startsWith,
  endsWith, [or] a custom rule defined by attributes from any namespace
  ... is REQUIRED in any one rule element."
- source-existence: existsInSource's own prose Constraints section --
  "When existsInSource is specified, exactly one of isPresent,
  startsWith, [or] endsWith is REQUIRED in the same rule element" (note:
  isNotPresent is deliberately excluded from this compatible set).
- case/disabled: caseSensitive and disabled are both typed xlf:yesNo.
- normalization: typed val:normalization_type, enumeration none/nfc/nfd.
- occurrence: occurs is typed xs:positiveInteger.

Deliberately narrow, mirroring this package's own established pattern
for the Metadata/Resource Data/Matches/Glossary modules exactly: this
slice adds attribute-level grammar and constraint diagnostics only. It
does not evaluate any rule's condition against actual segment source/
target text -- a genuinely separate, much larger capability (cascading
validation scope resolution across file/group/unit levels, disabled-
attribute override semantics, and text matching under case/
normalization options) that remains unbuilt.
"""

from __future__ import annotations

from format_factory.xliff import ExtensionNode, XliffDocument, XliffFile, validate

_VAL_NS = "urn:oasis:names:tc:xliff:validation:2.0"
_VALIDATION_TAG = f"{{{_VAL_NS}}}validation"


def _document(validation_xml: bytes) -> XliffDocument:
    return XliffDocument(
        version="2.1",
        source_language="en",
        target_language=None,
        children=[
            XliffFile(
                id="f",
                children=[ExtensionNode(tag=_VALIDATION_TAG, xml=validation_xml)],
            )
        ],
    )


def _codes(document: XliffDocument) -> set[str]:
    return {item.code for item in validate(document).diagnostics if "validation" in item.code}


def test_a_rule_with_isPresent_alone_validates_cleanly() -> None:
    xml = f'<val:validation xmlns:val="{_VAL_NS}"><val:rule isPresent="store"/></val:validation>'.encode()

    assert _codes(_document(xml)) == set()


def test_isPresent_combined_with_occurs_validates_cleanly() -> None:
    xml = (
        f'<val:validation xmlns:val="{_VAL_NS}">'
        '<val:rule isPresent="store" occurs="2"/></val:validation>'
    ).encode()

    assert _codes(_document(xml)) == set()


def test_endsWith_combined_with_existsInSource_yes_validates_cleanly() -> None:
    xml = (
        f'<val:validation xmlns:val="{_VAL_NS}">'
        '<val:rule endsWith=":" existsInSource="yes"/></val:validation>'
    ).encode()

    assert _codes(_document(xml)) == set()


def test_a_rule_with_only_a_custom_namespace_attribute_validates_cleanly() -> None:
    """"a custom rule defined by attributes from any namespace" is the
    fifth alternative the spec's own Constraints text names -- valid on
    its own, with none of the four native condition attributes set."""
    xml = (
        f'<val:validation xmlns:val="{_VAL_NS}" xmlns:custom="urn:example:custom">'
        '<val:rule custom:myAttr="x"/></val:validation>'
    ).encode()

    assert _codes(_document(xml)) == set()


def test_an_empty_validation_is_a_violation() -> None:
    xml = f'<val:validation xmlns:val="{_VAL_NS}"/>'.encode()

    assert _codes(_document(xml)) == {"xliff.module.validation.rule.required"}


def test_a_rule_with_no_condition_attribute_is_a_violation() -> None:
    xml = f'<val:validation xmlns:val="{_VAL_NS}"><val:rule caseSensitive="no"/></val:validation>'.encode()

    assert "xliff.module.validation.rule.condition.required" in _codes(_document(xml))


def test_a_rule_with_two_condition_attributes_is_a_violation() -> None:
    xml = (
        f'<val:validation xmlns:val="{_VAL_NS}">'
        '<val:rule isPresent="a" endsWith=":"/></val:validation>'
    ).encode()

    assert "xliff.module.validation.rule.condition.conflict" in _codes(_document(xml))


def test_existsInSource_with_isNotPresent_is_a_violation() -> None:
    """existsInSource's own compatible set is isPresent/startsWith/
    endsWith only -- isNotPresent is deliberately excluded by the spec."""
    xml = (
        f'<val:validation xmlns:val="{_VAL_NS}">'
        '<val:rule isNotPresent="store" existsInSource="yes"/></val:validation>'
    ).encode()

    assert "xliff.module.validation.existsinsource.condition.required" in _codes(_document(xml))


def test_existsInSource_set_to_no_is_still_checked_for_a_compatible_condition() -> None:
    """"When existsInSource IS SPECIFIED" -- the constraint applies
    regardless of whether its own value is yes or no."""
    xml = (
        f'<val:validation xmlns:val="{_VAL_NS}">'
        '<val:rule isNotPresent="x" existsInSource="no"/></val:validation>'
    ).encode()

    assert "xliff.module.validation.existsinsource.condition.required" in _codes(_document(xml))


def test_an_invalid_yesno_value_is_a_violation() -> None:
    xml = (
        f'<val:validation xmlns:val="{_VAL_NS}">'
        '<val:rule isPresent="a" caseSensitive="maybe"/></val:validation>'
    ).encode()

    assert "xliff.module.validation.yesno.invalid" in _codes(_document(xml))


def test_an_invalid_normalization_value_is_a_violation() -> None:
    xml = (
        f'<val:validation xmlns:val="{_VAL_NS}">'
        '<val:rule isPresent="a" normalization="nfkc"/></val:validation>'
    ).encode()

    assert "xliff.module.validation.normalization.invalid" in _codes(_document(xml))


def test_every_enumerated_normalization_value_is_individually_accepted() -> None:
    for value in ("none", "nfc", "nfd"):
        xml = (
            f'<val:validation xmlns:val="{_VAL_NS}">'
            f'<val:rule isPresent="a" normalization="{value}"/></val:validation>'
        ).encode()

        assert "xliff.module.validation.normalization.invalid" not in _codes(_document(xml)), value


def test_an_occurs_value_of_zero_is_a_violation() -> None:
    xml = (
        f'<val:validation xmlns:val="{_VAL_NS}">'
        '<val:rule isPresent="a" occurs="0"/></val:validation>'
    ).encode()

    assert "xliff.module.validation.occurs.invalid" in _codes(_document(xml))


def test_a_non_integer_occurs_value_is_a_violation() -> None:
    xml = (
        f'<val:validation xmlns:val="{_VAL_NS}">'
        '<val:rule isPresent="a" occurs="abc"/></val:validation>'
    ).encode()

    assert "xliff.module.validation.occurs.invalid" in _codes(_document(xml))


def test_a_non_validation_extension_is_unaffected() -> None:
    document = XliffDocument(
        version="2.1",
        source_language="en",
        target_language=None,
        children=[
            XliffFile(
                id="f",
                children=[
                    ExtensionNode(
                        tag="{urn:example:other}thing",
                        xml=b'<other xmlns="urn:example:other"/>',
                    )
                ],
            )
        ],
    )

    assert _codes(document) == set()
