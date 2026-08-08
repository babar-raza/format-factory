"""UBL-WRITE-001 -- round-trip proof against real OASIS official samples.

SAL-UBL-OBL-F9D5251F2302AE3A (MUST): "Round-trip every official sample of
each supported maindoc type comparing canonicalized XML plus typed
semantics." This obligation's own first clause was previously unbuilt
because no official OASIS sample corpus was vendored in this repository.

That framing turned out to be false: this product already vendors the
pinned OASIS UBL 2.3 release package's own XSD schemas
(src/python/ubl/src/format_factory/ubl/validation/schemas/), and that
identical package also contains 76 real OASIS-authored example instance
documents under xml/. samples/by-format/ubl/official/ vendors 55 of
them -- one per supported document root that has an official example in
the package, picking the highest-version, no-suffix variant when several
exist.

"Canonicalized XML comparison" is done via structural, namespace-URI-based
equivalence (Clark-notation tag/attribute comparison), not a literal C14N
byte-string compare: `xml.etree.ElementTree.canonicalize()` preserves the
original document's own namespace prefixes verbatim (correct per the C14N
spec), so an unmodeled extension namespace whose original prefix this
writer does not know about round-trips under an auto-generated prefix
(e.g. "ncts" -> "ns4") -- a cosmetic difference the XML Namespaces spec
treats as fully equivalent, not a real content difference. A structural
comparator that resolves each tag/attribute to its namespace URI (exactly
what Clark notation already encodes) is the correct tool for "canonicalized
XML" equivalence here, and is what `_semantic_xml_equal` implements.

Of the 55 vendored samples, only 10 round-trip in full: this writer's own
pre-existing stable-profile gate (`dumps()` -> `validate()`) deliberately
refuses to serialize any document whose declared cbc:UBLVersionID is not
"2.3" -- so an official sample that declares an older version (2.0/2.1/2.2)
is proven via load-only + correct-refusal, not a round trip, since silently
relabeling an older document as 2.3 output would misrepresent it. This is
the same "never label a document as the target version without structural
migration" guarantee UBL-UPGRADE-001 already establishes, now exercised
against real OASIS documents instead of synthetic fixtures.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
import yaml

from format_factory.ubl import UblWriteError, dumps, loads

OFFICIAL_DIR = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "ubl" / "official"
MANIFEST = yaml.safe_load((OFFICIAL_DIR / "_official-corpus-manifest.yaml").read_text(encoding="utf-8"))
SAMPLES = MANIFEST["samples"]


def _semantic_xml_equal(a: ET.Element, b: ET.Element) -> tuple[bool, str]:
    """Namespace-URI-based structural equality (Clark-notation tags/attrs).

    Ignores namespace *prefix* spelling (a-la, "ncts:" vs "ns4:" for the
    same URI are the same element) and insignificant whitespace-only text,
    both of which a literal C14N byte compare would wrongly flag.
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


class TestOfficialSampleParsing:
    @pytest.mark.parametrize("entry", SAMPLES, ids=lambda e: e["root_name"])
    def test_every_official_sample_parses_to_its_own_declared_root(self, entry: dict[str, object]) -> None:
        raw = (OFFICIAL_DIR.parent / str(entry["filename"])).read_bytes()
        document = loads(raw)

        assert document.root_name == entry["root_name"]


class TestOfficialSampleRoundtrip:
    @pytest.mark.parametrize(
        "entry", [e for e in SAMPLES if e["roundtrip_capable"]], ids=lambda e: e["root_name"]
    )
    def test_a_roundtrip_capable_sample_reproduces_semantically_identical_xml(
        self, entry: dict[str, object]
    ) -> None:
        raw = (OFFICIAL_DIR.parent / str(entry["filename"])).read_bytes()
        document = loads(raw)

        dumped = dumps(document)
        reloaded = loads(dumped)

        assert reloaded.root_name == document.root_name
        equal, reason = _semantic_xml_equal(ET.fromstring(raw), ET.fromstring(dumped))
        assert equal, reason

    @pytest.mark.parametrize(
        "entry", [e for e in SAMPLES if e["roundtrip_capable"]], ids=lambda e: e["root_name"]
    )
    def test_a_roundtrip_capable_sample_is_stable_under_a_second_round_trip(
        self, entry: dict[str, object]
    ) -> None:
        raw = (OFFICIAL_DIR.parent / str(entry["filename"])).read_bytes()
        first_dump = dumps(loads(raw))
        second_dump = dumps(loads(first_dump))

        assert first_dump == second_dump


class TestOlderVersionSamplesAreLoadOnlyNeverSilentlyRelabeled:
    @pytest.mark.parametrize(
        "entry", [e for e in SAMPLES if not e["roundtrip_capable"]], ids=lambda e: e["root_name"]
    )
    def test_an_older_declared_version_sample_parses_but_dumps_refuses_it(
        self, entry: dict[str, object]
    ) -> None:
        raw = (OFFICIAL_DIR.parent / str(entry["filename"])).read_bytes()
        document = loads(raw)

        assert document.root_name == entry["root_name"]
        with pytest.raises(UblWriteError, match="UBLVersionID"):
            dumps(document)
