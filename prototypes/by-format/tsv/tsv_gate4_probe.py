"""
TSV Gate 4 Evidence Wrapper — Gate 4 acquisition evidence.

This is a THIN EVIDENCE WRAPPER. It contains NO parsing logic.
All parsing is delegated to src/python/tsv/tsv_parser.py.

Purpose: provide a canonical Gate 4 evidence artifact for TSV that
  1. delegates to the existing production parser
  2. proves valid sample parsing via probe()
  3. proves invalid/missing input handling via probe_invalid()
  4. fails if the delegated API changes incompatibly (compatibility_check())

DO NOT add parsing logic here. The implementation authority is src/python/tsv/.
"""

from __future__ import annotations

import sys
from pathlib import Path

# ---- Dependency import (compatibility guard) ----
try:
    _REPO = Path(__file__).resolve().parents[3]
    if str(_REPO) not in sys.path:
        sys.path.insert(0, str(_REPO))
    from src.python.tsv import tsv_parser as _tsv_parser  # type: ignore[import]
    _REQUIRED_SYMBOLS = {"parse_tsv", "probe_tsv", "TsvInputError", "TsvParseError"}
    _missing = _REQUIRED_SYMBOLS - set(dir(_tsv_parser))
    if _missing:
        raise ImportError(f"tsv_parser missing expected symbols: {_missing}")
except ImportError as exc:
    raise ImportError(
        "tsv_gate4_probe: delegated source src/python/tsv/tsv_parser.py is "
        "unavailable or has changed incompatibly."
    ) from exc

GATE4_EVIDENCE_TYPE = "EVIDENCE_WRAPPER"
DELEGATED_SOURCE = "src/python/tsv/tsv_parser.py"
DELEGATED_SYMBOLS = ["parse_tsv", "probe_tsv", "TsvInputError", "TsvParseError"]


def probe(file_path: str | Path) -> dict:
    """Load and parse a TSV file via the delegated source.

    Delegates entirely to tsv_parser.parse_tsv(). No parsing logic here.
    """
    return _tsv_parser.parse_tsv(str(file_path))


def probe_invalid(file_path: str | Path | None = None) -> dict | None:
    """Prove that missing/non-existent input is handled.

    Returns a result dict with an error indicator, or raises TsvInputError.
    """
    path = file_path or "/nonexistent_gate4_probe_tsv.tsv"
    try:
        result = _tsv_parser.parse_tsv(str(path))
        return result
    except _tsv_parser.TsvInputError as e:
        return {"ok": False, "error": str(e), "error_type": "TsvInputError"}


def compatibility_check() -> bool:
    """Verify the delegated API has all required symbols."""
    missing = _REQUIRED_SYMBOLS - set(dir(_tsv_parser))
    if missing:
        raise ImportError(
            f"Delegated source tsv_parser is missing symbols: {missing}."
        )
    return True


if __name__ == "__main__":
    import json
    target = sys.argv[1] if len(sys.argv) > 1 else None
    if target:
        result = probe(target)
        print(json.dumps(result, default=str, indent=2))
    else:
        print("tsv_gate4_probe: EVIDENCE_WRAPPER for src/python/tsv/tsv_parser.py")
        compatibility_check()
        print("  Compatibility check: PASS")
