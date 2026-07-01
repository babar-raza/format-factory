"""
CSV Gate 4 Evidence Wrapper — Gate 4 acquisition evidence.

This is a THIN EVIDENCE WRAPPER. It contains NO parsing logic.
All parsing is delegated to src/python/csv/csv_parser.py.

Purpose: provide a canonical Gate 4 evidence artifact for CSV that
  1. delegates to the existing production parser
  2. proves valid sample parsing via probe()
  3. proves invalid/missing input handling via probe_invalid()
  4. fails if the delegated API changes incompatibly (compatibility_check())

DO NOT add parsing logic here. The implementation authority is src/python/csv/.
"""

from __future__ import annotations

import sys
from pathlib import Path

# ---- Dependency import (compatibility guard) ----
try:
    # Add repo root to sys.path (parents[3] from prototypes/by-format/csv/)
    _REPO = Path(__file__).resolve().parents[3]
    if str(_REPO) not in sys.path:
        sys.path.insert(0, str(_REPO))
    from src.python.csv import csv_parser as _csv_parser  # type: ignore[import]
    _REQUIRED_SYMBOLS = {"parse_csv", "probe_csv", "CsvInputError", "CsvParseError"}
    _missing = _REQUIRED_SYMBOLS - set(dir(_csv_parser))
    if _missing:
        raise ImportError(f"csv_parser missing expected symbols: {_missing}")
except ImportError as exc:
    raise ImportError(
        "csv_gate4_probe: delegated source src/python/csv/csv_parser.py is "
        "unavailable or has changed incompatibly. Gate 4 evidence wrapper "
        "cannot operate without its delegate."
    ) from exc

# ---- Public evidence API ----

GATE4_EVIDENCE_TYPE = "EVIDENCE_WRAPPER"
DELEGATED_SOURCE = "src/python/csv/csv_parser.py"
DELEGATED_SYMBOLS = ["parse_csv", "probe_csv", "CsvInputError", "CsvParseError"]


def probe(file_path: str | Path) -> dict:
    """Load and parse a CSV file via the delegated source.

    Returns the parse result dict from csv_parser.parse_csv().
    This method delegates entirely — no parsing logic here.
    """
    return _csv_parser.parse_csv(str(file_path))


def probe_invalid(file_path: str | Path | None = None) -> dict:
    """Prove that missing/non-existent input is handled gracefully.

    Returns a result dict with ok=False or raises CsvInputError.
    Does NOT expose raw exceptions to callers — Gate 4 scope only.
    """
    path = file_path or "/nonexistent_gate4_probe_csv.csv"
    result = _csv_parser.parse_csv(str(path))
    # parse_csv returns ok=False for missing files — verify this
    if result.get("ok") is not False and "error" not in result:
        raise AssertionError(
            f"Expected ok=False or error key for missing path, got: {result}"
        )
    return result


def compatibility_check() -> bool:
    """Verify the delegated API has all required symbols.

    Returns True if compatible. Raises ImportError if any required symbol
    has been removed or renamed — this signals API drift in the delegate.
    """
    missing = _REQUIRED_SYMBOLS - set(dir(_csv_parser))
    if missing:
        raise ImportError(
            f"Delegated source csv_parser is missing symbols: {missing}. "
            "Gate 4 evidence wrapper is no longer compatible."
        )
    return True


if __name__ == "__main__":
    # Quick self-test: probe a valid sample if path provided
    import json
    target = sys.argv[1] if len(sys.argv) > 1 else None
    if target:
        result = probe(target)
        print(json.dumps(result, default=str, indent=2))
    else:
        print("csv_gate4_probe: EVIDENCE_WRAPPER for src/python/csv/csv_parser.py")
        print(f"  Delegated source: {DELEGATED_SOURCE}")
        print(f"  Symbols: {DELEGATED_SYMBOLS}")
        compatibility_check()
        print("  Compatibility check: PASS")
