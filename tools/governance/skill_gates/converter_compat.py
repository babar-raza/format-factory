"""Converter information-model compatibility — is this source->target pair meaningful?

THE DEFECT THIS PREVENTS
------------------------
There are 222 `*_to_*.py` converters under src/python (measured 2026-07-17), of
which ~45 are meaningless projections: a document/tabular source mechanically
"converted" to a bitmap target (e.g. fods_to_pbm, abw_to_pbm) produces output
that encodes no information a user of the target format could want. They were
generated because the sprint machinery ASKED for a dogfood lane every sprint --
not because any pair was assessed as meaningful.

The check itself is one line of logic: a converter needs a registered
compatibility classification. The value is entirely in it being REQUIRED and
FAIL-CLOSED, at converter-creation time, before the code exists.

CLASSIFICATIONS (contract with registry/converter-compatibility-matrix.yaml)
---------------------------------------------------------------------------
  COMPATIBLE   -- source and target share an information model
                  (tabular->tabular, document->document, image->image)
  PROJECTION   -- cross-domain with DOCUMENTED, bounded loss
                  (document->tabular extracting text) -- requires `loss_note`
  INCOMPATIBLE -- no semantic relationship -> converter must NOT be generated

FAIL-CLOSED BY DESIGN
---------------------
This gate BLOCKS when the matrix is missing, unparseable, or has no entry for the
pair. That is intentional and it is the whole mechanism: "no converter without a
registered assessment" is only enforceable if absence blocks. An
`ALLOW-on-missing` version of this gate would be decorative -- every new pair is
by definition absent from the matrix, so allow-on-missing would never fire.

SEAM: registry/converter-compatibility-matrix.yaml does NOT exist at time of
writing. It is the deliverable of TC-PA-008 / V251, which is owned by a parallel
agent. This module defines the CONSUMER contract only and does not create the
registry. Until that registry lands, this gate blocks all converter generation --
which is the correct default given the 45 known-meaningless converters.

SCHEMA (as authored by TC-PA-008 / V251, reconciled 2026-07-17)

    schema_version: 1.0
    format_domains:
      abw: DOCUMENT
      csv: TABULAR
    converters:
      src/python/abw/abw_to_csv.py:          # keyed by FILE PATH
        pair: "abw->csv"
        source_domain: DOCUMENT
        target_domain: TABULAR
        category: PROJECTION                 # COMPATIBLE | PROJECTION | INCOMPATIBLE
        rationale: "Extracting each paragraph as a row is documented and useful;
                    loses styling, structure, and inline objects."
        disposition: PENDING                 # INCOMPATIBLE entries only

NOTE ON SCHEMA OWNERSHIP: the registry is TC-PA-008's deliverable and its shape is
authoritative. An earlier draft of this module expected `converters:` keyed by pair id
(`abw_to_csv`) with a `classification:` field. That was a *guess* made before the
registry existed, and it was wrong on both counts — it would have reported "no entry"
for all 222 registered pairs, i.e. a gate that blocks everything for a bogus reason.
This module was reconciled to the real schema rather than the registry being bent to
match it. Lookup accepts the path key, the `pair` field ("abw->csv"), and a bare pair
id ("abw_to_csv") so the caller does not need to know the storage layout.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MATRIX_PATH = REPO_ROOT / "registry" / "converter-compatibility-matrix.yaml"

CLASS_COMPATIBLE = "COMPATIBLE"
CLASS_PROJECTION = "PROJECTION"
CLASS_INCOMPATIBLE = "INCOMPATIBLE"
_VALID_CLASSES = frozenset({CLASS_COMPATIBLE, CLASS_PROJECTION, CLASS_INCOMPATIBLE})

VERDICT_ALLOW = "ALLOW"
VERDICT_BLOCK = "BLOCK"
VERDICT_CONFIG_ERROR = "CONFIG_ERROR"


@dataclass(frozen=True)
class CompatResult:
    pair: str
    verdict: str
    reason: str
    classification: str | None = None

    @property
    def blocked(self) -> bool:
        return self.verdict != VERDICT_ALLOW


class MatrixError(Exception):
    """The compatibility matrix is missing or malformed."""


def load_matrix(path: Path | str | None = None) -> dict[str, Any]:
    """Load the compatibility matrix. Raises MatrixError if absent/malformed.

    Never returns an empty dict for a missing file -- that would let a caller
    mistake "no matrix" for "no violations".
    """
    p = Path(path) if path else DEFAULT_MATRIX_PATH
    if not p.exists():
        raise MatrixError(
            f"compatibility matrix not found at {p}. It is the deliverable of "
            "TC-PA-008 / validator V251. Until it exists, no converter may be "
            "generated: there is no registry in which to assess the pair.")
    try:
        import yaml  # type: ignore
    except ImportError as exc:  # pragma: no cover - yaml is a repo dependency
        raise MatrixError(f"PyYAML unavailable, cannot read {p}: {exc}") from exc
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        raise MatrixError(f"could not parse {p}: {exc}") from exc
    if not isinstance(data, dict) or "converters" not in data:
        raise MatrixError(
            f"{p} has no top-level 'converters:' mapping; expected schema is "
            "documented in tools/governance/skill_gates/converter_compat.py")
    conv = data.get("converters")
    if not isinstance(conv, dict):
        raise MatrixError(f"{p}: 'converters' must be a mapping of pair -> entry")
    return data


def pair_id(source_format: str, target_format: str) -> str:
    return f"{source_format.strip().lower()}_to_{target_format.strip().lower()}"


def _normalise_pair(raw: str) -> str:
    """'abw->csv' | 'src/python/abw/abw_to_csv.py' | 'abw_to_csv' -> 'abw_to_csv'."""
    s = str(raw).strip().lower().replace("\\", "/")
    if s.endswith(".py"):
        s = s.rsplit("/", 1)[-1][:-3]
    if "->" in s:
        a, _, b = s.partition("->")
        s = f"{a.strip()}_to_{b.strip()}"
    return s


def _index_by_pair(matrix: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Index registry entries by normalised pair id, whatever the storage key is.

    The registry keys by file path; entries also carry a `pair` field. Both are
    indexed so a caller that only knows (source, target) can resolve an entry
    without knowing the layout.
    """
    out: dict[str, dict[str, Any]] = {}
    for key, entry in (matrix.get("converters") or {}).items():
        if not isinstance(entry, dict):
            continue
        for candidate in (entry.get("pair"), key):
            if candidate:
                out.setdefault(_normalise_pair(candidate), entry)
    return out


def _classification_of(entry: dict[str, Any]) -> str:
    """Read the class field. `category` is the registry's name; `classification`
    is accepted as an alias so a future rename does not silently read as blank
    (a blank would fall through to CONFIG_ERROR, not to ALLOW)."""
    for field in ("category", "classification"):
        val = str(entry.get(field, "")).strip().upper()
        if val:
            return val
    return ""


def _loss_documented(entry: dict[str, Any]) -> bool:
    """A PROJECTION must say what it drops. The registry records this in
    `rationale`; `loss_note` is accepted for entries that separate it out."""
    return bool(str(entry.get("loss_note", "")).strip()
                or str(entry.get("rationale", "")).strip())


def check_pair(source_format: str, target_format: str,
               matrix_path: Path | str | None = None) -> CompatResult:
    """Decide whether a converter may be generated for source -> target.

    ALLOW only for a registered COMPATIBLE or PROJECTION pair (PROJECTION also
    requires documented loss: an undocumented projection is exactly the
    meaningless-converter defect wearing a label).

    Loads the registry on every call — deliberately uncached, so a gate verdict
    always reflects the registry on disk. Callers evaluating many pairs should
    `load_matrix()` once and use `evaluate_pair()`.
    """
    pid = pair_id(source_format, target_format)
    if source_format.strip().lower() == target_format.strip().lower():
        return CompatResult(pid, VERDICT_BLOCK,
                            "source and target format are the same; this is not "
                            "an export. Use /add-same-format-writer-feature.")
    try:
        matrix = load_matrix(matrix_path)
    except MatrixError as exc:
        return CompatResult(pid, VERDICT_CONFIG_ERROR, str(exc))
    return evaluate_pair(matrix, source_format, target_format)


def allowed_pairs(matrix: dict[str, Any]) -> list[str]:
    """Every registered pair that may legally be generated, as sorted pair ids.

    A pair is allowed iff evaluate_pair() would ALLOW it. Callers that need "which
    converters may exist" (e.g. the sprint packet's dogfood lane) must use this
    rather than reading `category` themselves — the registry's field names are
    TC-PA-008's to change, and a caller that hardcodes them silently returns []
    after a rename, which reads as "no work available" instead of "I am broken".
    (This function exists because that exact bug shipped into
    generate_supervisor_packet.py on 2026-07-17 and was caught only by end-to-end
    verification.)
    """
    out: list[str] = []
    for pid in sorted(_index_by_pair(matrix)):
        if "_to_" not in pid:
            continue
        src, _, tgt = pid.partition("_to_")
        if evaluate_pair(matrix, src, tgt).verdict == VERDICT_ALLOW:
            out.append(pid)
    return out


def evaluate_pair(matrix: dict[str, Any], source_format: str,
                  target_format: str) -> CompatResult:
    """Same decision as check_pair, against an already-loaded matrix."""
    pid = pair_id(source_format, target_format)

    if source_format.strip().lower() == target_format.strip().lower():
        return CompatResult(pid, VERDICT_BLOCK,
                            "source and target format are the same; this is not "
                            "an export. Use /add-same-format-writer-feature.")

    entry = _index_by_pair(matrix).get(pid)
    if entry is None:
        return CompatResult(
            pid, VERDICT_BLOCK,
            f"no entry for '{pid}' in the compatibility matrix. A converter may "
            "not be created before its information-model compatibility is "
            "assessed and registered. Add an entry (pair, source_domain, "
            "target_domain, category, rationale) to "
            "registry/converter-compatibility-matrix.yaml, then re-run this gate.")

    cls = _classification_of(entry)
    if cls not in _VALID_CLASSES:
        return CompatResult(
            pid, VERDICT_CONFIG_ERROR,
            f"entry for '{pid}' has category {cls!r}; must be one of "
            f"{sorted(_VALID_CLASSES)}")

    if cls == CLASS_INCOMPATIBLE:
        rationale = str(entry.get("rationale", "")).strip() or "(no rationale recorded)"
        return CompatResult(
            pid, VERDICT_BLOCK,
            f"'{pid}' is classified INCOMPATIBLE: {rationale} Generating this "
            "converter would add another meaningless projection. If this "
            "classification is wrong, change the matrix entry (with a rationale) "
            "-- do not bypass the gate.", cls)

    if cls == CLASS_PROJECTION and not _loss_documented(entry):
        return CompatResult(
            pid, VERDICT_BLOCK,
            f"'{pid}' is classified PROJECTION but records no rationale/loss_note. "
            "A projection without documented loss is indistinguishable from a "
            "meaningless converter. Record what information is dropped.", cls)

    return CompatResult(pid, VERDICT_ALLOW,
                        f"'{pid}' is registered as {cls}", cls)
