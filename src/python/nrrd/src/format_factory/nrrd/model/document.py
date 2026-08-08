"""Typed NRRD document model with no eager I/O dependencies."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar, Mapping


DOMAIN_KINDS = frozenset({"domain", "space", "time"})

#: NRRD-SHAPE-001 (SAL-NRRD-00010): "The baseline per-axis metadata fields
#: spacings, axis mins, axis maxs, centers, labels, and units each carry
#: exactly one value per declared dimension." Header keys as stored by the
#: reader (lowercased, spaces preserved -- see codec/reader/reader.py).
_NUMERIC_AXIS_FIELDS = ("spacings", "axis mins", "axis maxs", "centers")
_QUOTED_AXIS_FIELDS = ("labels", "units")


def _parse_quoted_list(value: str) -> list[str]:
    """Quote-delimited per-axis strings (SAL-NRRD-00009): each value is
    `"..."`-delimited; `\\"` escapes a literal quote and no other escaping
    is recognized."""
    tokens: list[str] = []
    index = 0
    length = len(value)
    while index < length:
        if value[index].isspace():
            index += 1
            continue
        if value[index] != '"':
            raise ValueError(f"expected a quoted per-axis value at position {index}: {value!r}")
        index += 1
        chars: list[str] = []
        closed = False
        while index < length:
            if value[index] == "\\" and index + 1 < length and value[index + 1] == '"':
                chars.append('"')
                index += 2
                continue
            if value[index] == '"':
                closed = True
                break
            chars.append(value[index])
            index += 1
        if not closed:
            raise ValueError(f"unterminated quoted per-axis value: {value!r}")
        index += 1  # consume the closing quote
        tokens.append("".join(chars))
    return tokens


@dataclass(frozen=True, slots=True)
class PreservationIssue:
    """A construct that prevents an exact source-preserving write."""

    code: str
    message: str


@dataclass(frozen=True, slots=True)
class PreservationReport:
    """Explicit result of evaluating whether a document can be written losslessly."""

    issues: tuple[PreservationIssue, ...] = ()

    @property
    def is_lossless(self) -> bool:
        return not self.issues


def _dict_diff_issues(
    code_prefix: str, label: str, original: dict[str, str], current: dict[str, str]
) -> list[PreservationIssue]:
    """One `PreservationIssue` per key added, removed, or changed between
    `original` and `current` -- a per-construct diff, not a single "this
    dict changed" flag."""

    issues: list[PreservationIssue] = []
    for key in sorted(set(original) | set(current)):
        old_value = original.get(key)
        new_value = current.get(key)
        if old_value == new_value:
            continue
        if old_value is None:
            issues.append(
                PreservationIssue(f"{code_prefix}_added", f"{label} {key!r} was added: {new_value!r}")
            )
        elif new_value is None:
            issues.append(
                PreservationIssue(
                    f"{code_prefix}_removed", f"{label} {key!r} was removed (was {old_value!r})"
                )
            )
        else:
            issues.append(
                PreservationIssue(
                    f"{code_prefix}_changed",
                    f"{label} {key!r} changed from {old_value!r} to {new_value!r}",
                )
            )
    return issues


@dataclass(slots=True)
class NrrdDocument:
    """A decoded NRRD document with preserved headers and comments."""

    #: The spec QName this document's own root construct maps to. Fixed
    #: for every NRRD document -- carried over from the deprecated alpha
    #: model (src/python/nrrd/models.py), which had this as a ClassVar
    #: but was dropped when this production model was built, leaving
    #: to_dict()'s own consumers with no way to recover it.
    spec_qname: ClassVar[str] = "nrrd:header"

    version: int
    header: dict[str, str]
    payload: bytes
    array: list[Any]
    detected_version: int | None = None
    comments: list[str] = field(default_factory=list)
    key_value_pairs: dict[str, str] = field(default_factory=dict)
    raw_header: bytes = b""
    source_path: str | None = None
    data_offset: int = 0
    recovery_actions: tuple[str, ...] = ()
    source_bytes: bytes | None = field(default=None, repr=False, compare=False)
    _original_header: dict[str, str] | None = field(default=None, repr=False, compare=False)
    _original_comments: list[str] | None = field(default=None, repr=False, compare=False)
    _original_key_value_pairs: dict[str, str] | None = field(
        default=None, repr=False, compare=False
    )
    _original_array: list[Any] | None = field(default=None, repr=False, compare=False)

    @property
    def dimension(self) -> int:
        return int(self.header["dimension"])

    @property
    def sizes(self) -> list[int]:
        return [int(value) for value in self.header["sizes"].split()]

    @property
    def encoding(self) -> str:
        return self.header.get("encoding", "raw").lower()

    @property
    def nrrd_type(self) -> str:
        return self.header["type"].lower()

    @property
    def data_size(self) -> int:
        return len(self.payload)

    @property
    def element_count(self) -> int:
        result = 1
        for size in self.sizes:
            result *= size
        return result

    @property
    def array_shape(self) -> list[int]:
        return self.sizes

    @property
    def kinds(self) -> list[str]:
        value = self.header.get("kinds", "")
        return value.split() if value else []

    @property
    def domain_axes(self) -> list[int]:
        return [
            index
            for index, value in enumerate(self.kinds)
            if value.lower() in DOMAIN_KINDS
        ]

    @property
    def range_axes(self) -> list[int]:
        return [
            index
            for index, value in enumerate(self.kinds)
            if value.lower() not in DOMAIN_KINDS
        ]

    @property
    def space(self) -> str:
        return self.header.get("space", "")

    @property
    def labels(self) -> list[str]:
        value = self.header.get("labels", "")
        return _parse_quoted_list(value) if value else []

    @property
    def units(self) -> list[str]:
        value = self.header.get("units", "")
        return _parse_quoted_list(value) if value else []

    @property
    def spacings(self) -> list[float]:
        value = self.header.get("spacings", "")
        return [float(token) for token in value.split()] if value else []

    @property
    def axis_mins(self) -> list[float]:
        value = self.header.get("axis mins", "")
        return [float(token) for token in value.split()] if value else []

    @property
    def axis_maxs(self) -> list[float]:
        value = self.header.get("axis maxs", "")
        return [float(token) for token in value.split()] if value else []

    @property
    def centers(self) -> list[str]:
        value = self.header.get("centers", "")
        return value.split() if value else []

    @property
    def thicknesses(self) -> list[float]:
        value = self.header.get("thicknesses", "")
        return [float(token) for token in value.split()] if value else []

    @property
    def sample_units(self) -> str | None:
        """`sample units:` (or `sampleunits:`) -- NRRD0004+, always optional.
        "The units of measurement associated with the scalar values stored
        in the array itself," a single unquoted string distinct from the
        per-axis `units` field and from `space units` (SAL-NRRD-00023)."""
        value = self.header.get("sample units", self.header.get("sampleunits"))
        return value.strip() if value is not None else None

    @property
    def content(self) -> str | None:
        """`content:` -- always optional, baseline (no version gate). "A
        very concise textual description," an unquoted string running to
        the line's end with no explicit delimiting (SAL-NRRD-00026)."""
        return self.header.get("content")

    @property
    def min_value(self) -> float | None:
        """`min:` -- always optional, baseline. "The minimum value in the
        array." Any value is legal, including infinite or NaN (SAL-NRRD-00026)."""
        value = self.header.get("min")
        return float(value) if value is not None else None

    @property
    def max_value(self) -> float | None:
        """`max:` -- always optional, baseline. Same as `min`, but the
        maximum value in the array (SAL-NRRD-00026)."""
        value = self.header.get("max")
        return float(value) if value is not None else None

    @property
    def old_min(self) -> float | None:
        """`old min:` (or `oldmin:`) -- always optional, baseline, but
        "meaningless for floating-point and block nrrds." For integral
        data produced by linear quantization, the lowest input value
        mapped to the lowest output integer (SAL-NRRD-00026)."""
        value = self.header.get("old min", self.header.get("oldmin"))
        return float(value) if value is not None else None

    @property
    def old_max(self) -> float | None:
        """`old max:` (or `oldmax:`) -- same as `old min`, but the highest
        of the input values mapped to the highest output integer
        (SAL-NRRD-00026)."""
        value = self.header.get("old max", self.header.get("oldmax"))
        return float(value) if value is not None else None

    @property
    def number(self) -> str | None:
        """`number:` -- an obsolete, vestigial field from pre-NRRD0001.01
        magics. The spec's own instruction is followed exactly: "the number
        field should never be written, and always ignored on reading,
        without even an attempt to parse the field as an integer"
        (SAL-NRRD-00026) -- exposed as raw text only, deliberately never
        parsed as a number, carried through lossless output like any other
        obsolete/legacy field."""
        return self.header.get("number")

    def per_axis_field_arities(self) -> dict[str, int]:
        """The declared length of every per-axis field actually present.

        Only fields present in the header are reported -- a per-axis field
        the document does not use at all is not an arity violation, only a
        mismatched count for a field it DOES use is (NRRD-SHAPE-001).
        """
        fields: dict[str, list[Any]] = {
            "spacings": self.spacings,
            "axis mins": self.axis_mins,
            "axis maxs": self.axis_maxs,
            "centers": self.centers,
            "labels": self.labels,
            "units": self.units,
            "kinds": self.kinds,
            "thicknesses": self.thicknesses,
        }
        return {name: len(values) for name, values in fields.items() if name in self.header}

    def version_requirements(self) -> list[tuple[int, str]]:
        """Which populated fields force which minimum NRRD profile version.

        Cumulative feature gates per SAL-NRRD-00020 (profile-version), backed
        by SAL-NRRD-00021 (key/value, NRRD0002+), SAL-NRRD-00022 (kinds,
        NRRD0003+), SAL-NRRD-00023/00019 (thicknesses and space/orientation
        fields, NRRD0004+), SAL-NRRD-00006 (multi-file data file, NRRD0004+),
        and SAL-NRRD-00024 (measurement frame, NRRD0005+). Fields that are
        version-independent baseline (spacings, axis mins/maxs, centers,
        labels, units -- SAL-NRRD-00010) are not represented here.
        """

        requirements: list[tuple[int, str]] = []
        if self.key_value_pairs:
            requirements.append((2, "key/value pairs"))
        if "kinds" in self.header:
            requirements.append((3, "kinds"))
        if "thicknesses" in self.header:
            requirements.append((4, "thicknesses"))
        if "sample units" in self.header or "sampleunits" in self.header:
            requirements.append((4, "sample units"))
        for field_name in ("space", "space dimension", "space units", "space origin", "space directions"):
            if field_name in self.header:
                requirements.append((4, field_name))
        data_file = self.header.get("data file", "")
        if data_file and (data_file.upper().startswith("LIST") or "%" in data_file):
            requirements.append((4, "data file (multi-file)"))
        if "measurement frame" in self.header:
            requirements.append((5, "measurement frame"))
        return requirements

    def minimal_version_for(self) -> int:
        """The oldest NRRD profile version able to represent this document."""

        return max((version for version, _ in self.version_requirements()), default=1)

    def preservation_report(self) -> PreservationReport:
        """Report every construct that prevents an exact-preserving write.

        SAL-NRRD-OBL-0D0DBFB306769459 (NRRD-PRESERVE-001): "Report every
        construct that cannot be preserved before saving, through a loss
        report API, rather than failing silently." One issue per changed,
        added, or removed header field and key/value pair -- not a single
        coarse "something changed" flag -- so a caller can see exactly
        which constructs would be lost, not merely that some unspecified
        loss would occur. Comments and the decoded array are reported
        coarsely (as a single issue each when different): comments are an
        ordered list where per-index diffing is not obviously more useful
        than "the list changed", and the array can be arbitrarily large,
        where an issue per differing element would make the report itself
        an unbounded-size liability rather than a useful summary.

        Canonical output preserves represented NRRD semantics. Exact preservation
        is available only for an attached source document whose semantic state has
        not been modified after load.
        """

        issues: list[PreservationIssue] = []
        if self.source_bytes is None:
            issues.append(PreservationIssue(
                "nrrd.lossless.source_unavailable",
                "no attached source bytes are available for lossless output",
            ))
        if "data file" in self.header:
            issues.append(PreservationIssue(
                "nrrd.lossless.detached_payload",
                "detached payloads require an explicit detached writer",
            ))
        if self._original_header is None:
            issues.append(PreservationIssue(
                "nrrd.lossless.snapshot_unavailable",
                "the document was not loaded from a preservable source",
            ))
        else:
            # All 4 `_original_*` snapshots are set together, atomically, by
            # the reader (codec/reader/reader.py) -- `_original_header` being
            # non-None (checked above) guarantees the other three are too.
            assert self._original_comments is not None
            assert self._original_key_value_pairs is not None
            issues.extend(
                _dict_diff_issues(
                    "nrrd.lossless.header_field", "header field", self._original_header, self.header
                )
            )
            issues.extend(
                _dict_diff_issues(
                    "nrrd.lossless.key_value",
                    "key/value pair",
                    self._original_key_value_pairs,
                    self.key_value_pairs,
                )
            )
            if self.comments != self._original_comments:
                issues.append(PreservationIssue(
                    "nrrd.lossless.comments_changed",
                    f"comments changed from {len(self._original_comments)} to "
                    f"{len(self.comments)} entries",
                ))
            if self.array != self._original_array:
                issues.append(PreservationIssue(
                    "nrrd.lossless.array_changed",
                    "decoded array values changed after load",
                ))
        return PreservationReport(tuple(issues))

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> NrrdDocument:
        """Migrate a legacy model mapping without performing I/O."""

        header_value = value.get("header", {})
        if not isinstance(header_value, Mapping):
            raise TypeError("header must be a mapping")
        key_values = value.get("key_value_pairs", {})
        if not isinstance(key_values, Mapping):
            raise TypeError("key_value_pairs must be a mapping")
        payload_value = value.get("payload", b"")
        if not isinstance(payload_value, bytes):
            raise TypeError("payload must be bytes")
        return cls(
            version=int(value.get("version", 5)),
            header={str(key).lower(): str(item) for key, item in header_value.items()},
            payload=payload_value,
            array=list(value.get("array") or []),
            detected_version=(
                int(value["detected_version"])
                if value.get("detected_version") is not None
                else None
            ),
            comments=[str(item) for item in value.get("comments", [])],
            key_value_pairs={
                str(key): str(item) for key, item in key_values.items()
            },
            raw_header=bytes(value.get("raw_header", b"")),
            source_path=(
                str(value["source_path"])
                if value.get("source_path") is not None
                else None
            ),
            data_offset=int(value.get("data_offset", 0)),
            recovery_actions=tuple(str(item) for item in value.get("recovery_actions", ())),
            source_bytes=(
                bytes(value["source_bytes"])
                if isinstance(value.get("source_bytes"), bytes)
                else None
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a compatibility mapping without exposing internal dicts."""

        return {
            "spec_qname": self.spec_qname,
            "version": self.version,
            "detected_version": self.detected_version,
            "header": dict(self.header),
            "key_value_pairs": dict(self.key_value_pairs),
            "comments": list(self.comments),
            "raw_header": self.raw_header,
            "payload": self.payload,
            "data_size": self.data_size,
            "element_count": self.element_count,
            "data_offset": self.data_offset,
            "recovery_actions": list(self.recovery_actions),
            "kinds": self.kinds,
            "space": self.space,
            "labels": self.labels,
            "units": self.units,
            "spacings": self.spacings,
            "axis_mins": self.axis_mins,
            "axis_maxs": self.axis_maxs,
            "centers": self.centers,
            "thicknesses": self.thicknesses,
            "array": list(self.array),
            "array_shape": self.array_shape,
            "source_path": self.source_path,
        }

    def to_array(self) -> Any:
        return reshape_nrrd_array(self.array, self.sizes)


def reshape_nrrd_array(flat: list[Any], sizes: list[int]) -> Any:
    """Reshape flat values using NRRD's fastest-first axis convention."""

    if not sizes or len(sizes) == 1:
        return list(flat)
    strides = [1] * len(sizes)
    for axis in range(1, len(sizes)):
        strides[axis] = strides[axis - 1] * sizes[axis - 1]

    def build(axis: int, base: int) -> Any:
        if axis < 0:
            return flat[base]
        return [
            build(axis - 1, base + index * strides[axis])
            for index in range(sizes[axis])
        ]

    return build(len(sizes) - 1, 0)
