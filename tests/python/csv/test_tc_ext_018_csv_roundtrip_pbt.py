"""Pilot property-based test for the CSV codec's write_csv/parse_csv_strict pair.

TC-EXT-018-03: pilot for the /property-based-testing skill
(.claude/commands/property-based-testing.md). Demonstrates the Roundtrip
property -- HIGH priority per the skill's activation table row
"serialization pair (parse_*/write_* or load/write_<fmt>) -> Roundtrip ->
HIGH" -- against format-factory's real `write_csv` / `parse_csv_strict`
function pair, using Hypothesis.

Scope note: the generated field alphabet is restricted to ASCII letters and
excludes the handful of letter-only spellings `float()` accepts ("nan",
"inf", "infinity", case-insensitively), so csv_parser.py's content-based
header heuristic (`_has_header_heuristic`) never reclassifies a data row as
a header row. Whether that heuristic itself behaves correctly is a separate,
orthogonal property this pilot does not test. Rows whose *last* row is a
lone empty field (`[""]`) are also excluded via `assume()`: the parser's
`_parse_rfc4180` strips a trailing row that looks like a blank
end-of-file line, which is a real (and separately known) asymmetry, not a
bug this pilot is scoped to fix or characterize.
"""
from __future__ import annotations

import string
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from hypothesis import assume, given, settings
from hypothesis import strategies as st

from src.python.csv.csv_parser import parse_csv_strict
from src.python.csv.csv_writer import write_csv


_NUMERIC_LOOKALIKES = frozenset({"nan", "inf", "infinity", "+inf", "-inf"})


def _non_numeric(field: str) -> bool:
    """Reject fields `float()` would accept (nan/inf spellings, any case).

    Keeps every generated row unambiguously non-numeric so
    `_has_header_heuristic` never fires and reclassifies a data row as a
    header -- that heuristic's own behavior is out of scope for this pilot.
    """
    return field.strip().lower() not in _NUMERIC_LOOKALIKES


_FIELD = st.text(alphabet=string.ascii_letters, min_size=0, max_size=8).filter(
    _non_numeric
)
_ROWS = st.lists(
    st.lists(_FIELD, min_size=1, max_size=5),
    min_size=0,
    max_size=6,
)


@given(rows=_ROWS)
@settings(max_examples=100)
def test_write_csv_then_parse_csv_strict_roundtrip(rows):
    """encode(write_csv) -> decode(parse_csv_strict) returns equivalent rows.

    This is the Roundtrip property from the /property-based-testing skill's
    property catalog, applied to FF's real csv `write_csv`/`parse_csv_strict`
    pair (see TC-EXT-018-03).
    """
    # Excludes the known trailing-blank-row asymmetry documented above --
    # not the property under test here.
    assume(not rows or rows[-1] != [""])

    csv_text = write_csv(rows)

    tmp_path = Path(tempfile.mktemp(suffix=".csv"))
    tmp_path.write_text(csv_text, encoding="utf-8")
    try:
        result = parse_csv_strict(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)

    assert result["headers"] is None
    assert result["rows"] == rows
