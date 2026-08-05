"""XLIFF-MERGE-001 -- extraction/merge adapters with reversible skeleton
mappings and source-drift detection.

"(XLIFF core - skeleton) skeleton elements carry or reference the
non-translatable document skeleton needed to reconstruct the original file on
merge." required_behavior: "Provide extraction/merge adapter interfaces with
reversible skeleton mappings; detect source drift and stale skeletons before
merge; never claim generic extraction without format-specific adapters."

That last clause is why this module has no built-in "extract anything"
function: XLIFF itself does not define how to pull translatable text out of
an arbitrary source format -- that is inherently specific to the format being
localized (HTML, a resource file, a custom template). What XLIFF's own core
defines is the skeleton concept and the merge contract; MergeAdapter is that
contract, and TemplateMergeAdapter below is one concrete, honest example of
it -- not a claim of general extraction coverage.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from .model import Segment, Unit, XliffDocument, XliffFile


@dataclass(frozen=True, slots=True)
class Skeleton:
    """The non-translatable data needed to reconstruct the original file.

    ``template`` holds the source bytes with every translatable span replaced
    by a placeholder token; merging is finding each placeholder and
    substituting the corresponding unit's current text. ``source_digest`` is
    computed from the ORIGINAL source at extraction time -- what a merge
    checks the live source against before trusting the mapping still applies.
    """

    template: bytes
    source_digest: str
    placeholder_to_unit_id: dict[str, str] = field(default_factory=dict)


class SourceDriftError(Exception):
    """Raised when a live source no longer matches the skeleton it would merge against."""


@runtime_checkable
class MergeAdapter(Protocol):
    """Format-specific extraction and merge-back.

    "never claim generic extraction without format-specific adapters" --
    there is deliberately no adapter-less extract/merge path in this module.
    A caller wanting to merge XLIFF back into their own source format writes
    one of these; format_factory.xliff provides the contract and the drift
    check, not a claim of covering their format.
    """

    def extract(self, source: bytes) -> tuple[XliffDocument, Skeleton]: ...

    def merge(self, document: XliffDocument, skeleton: Skeleton) -> bytes: ...


def compute_source_digest(source: bytes) -> str:
    return hashlib.sha256(source).hexdigest()


def check_drift(skeleton: Skeleton, live_source: bytes) -> str | None:
    """Return None if ``live_source`` still matches what the skeleton was
    extracted from; otherwise a human-readable drift report.

    "detect source drift and stale skeletons before merge" -- this is the
    detection half; merge_with_drift_check is the refusal half.
    """
    live_digest = compute_source_digest(live_source)
    if live_digest == skeleton.source_digest:
        return None
    return (
        f"source drift detected: skeleton was extracted from digest "
        f"{skeleton.source_digest}, but the live source digest is "
        f"{live_digest}"
    )


def merge_with_drift_check(
    adapter: MergeAdapter,
    document: XliffDocument,
    skeleton: Skeleton,
    *,
    live_source: bytes | None = None,
) -> bytes:
    """Merge through ``adapter``, refusing with a report rather than
    corrupting output when ``live_source`` no longer matches the skeleton.

    Passing ``live_source=None`` skips the check -- a caller merging straight
    from the skeleton that was just extracted, with no independent live
    source to compare against, has nothing to detect drift from.
    """
    if live_source is not None:
        drift = check_drift(skeleton, live_source)
        if drift is not None:
            raise SourceDriftError(drift)
    return adapter.merge(document, skeleton)


# ── Reference adapter ────────────────────────────────────────────────────────

_BLOCK_PATTERN = re.compile(rb"%%TR%%(.*?)%%TR%%", re.DOTALL)


class TemplateMergeAdapter:
    """Reference MergeAdapter for a minimal ``%%TR%% ... %%TR%%``-delimited
    template format: text between a pair of markers is translatable, and
    everything else -- headers, footers, surrounding structure -- is
    skeleton, carried verbatim.

    This exists to prove MergeAdapter against a real, working extraction and
    merge-back, not to claim coverage of any real-world source format: no
    production template language uses exactly this marker syntax.
    """

    def extract(self, source: bytes) -> tuple[XliffDocument, Skeleton]:
        segments: list[Segment] = []
        placeholder_to_unit_id: dict[str, str] = {}
        parts: list[bytes] = []
        cursor = 0
        counter = 0

        for match in _BLOCK_PATTERN.finditer(source):
            # Keep both %%TR%% markers as literal skeleton bytes -- only the
            # captured text between them (group 1) is replaced. Consuming the
            # markers themselves would make an untranslated round trip lose
            # them, which is not "reconstruct the original file".
            parts.append(source[cursor : match.start(1)])
            counter += 1
            unit_id = f"u{counter}"
            placeholder = f"\x00XLIFF-PLACEHOLDER:{unit_id}\x00".encode("utf-8")
            parts.append(placeholder)
            placeholder_to_unit_id[placeholder.decode("utf-8")] = unit_id
            text = match.group(1).decode("utf-8")
            segments.append(Segment(id=unit_id, source=[text]))
            cursor = match.end(1)
        parts.append(source[cursor:])

        template = b"".join(parts)
        skeleton = Skeleton(
            template=template,
            source_digest=compute_source_digest(source),
            placeholder_to_unit_id=placeholder_to_unit_id,
        )
        document = XliffDocument(
            version="2.0",
            source_language="en",
            target_language=None,
            children=[
                XliffFile(
                    id="f1",
                    children=[Unit(id=segment.id, children=[segment]) for segment in segments],
                )
            ],
        )
        return document, skeleton

    def merge(self, document: XliffDocument, skeleton: Skeleton) -> bytes:
        units_by_id = {unit.id: unit for unit in document.iter_units()}
        output = skeleton.template
        for placeholder, unit_id in skeleton.placeholder_to_unit_id.items():
            unit = units_by_id.get(unit_id)
            if unit is None or not unit.segments:
                raise ValueError(
                    f"skeleton references unit {unit_id!r} which is not in the document"
                )
            segment = unit.segments[0]
            content = segment.target if segment.target is not None else segment.source
            text = "".join(node for node in content if isinstance(node, str))
            output = output.replace(placeholder.encode("utf-8"), text.encode("utf-8"))
        return output


__all__ = [
    "MergeAdapter",
    "Skeleton",
    "SourceDriftError",
    "TemplateMergeAdapter",
    "check_drift",
    "compute_source_digest",
    "merge_with_drift_check",
]
