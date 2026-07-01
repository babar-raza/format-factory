"""
NDJSON Gate 4 Evidence Wrapper — Gate 4 acquisition evidence (RETROSPECTIVE).

This is a THIN EVIDENCE WRAPPER. It contains NO parsing logic.
All parsing is delegated to src/python/ndjson/ndjson_codec.py.

RETROSPECTIVE NOTE: NDJSON Gate 4 evidence was never formally recorded despite
the format having a full production-quality implementation in src/python/ndjson/.
This wrapper reconstructs the Gate 4 evidence retrospectively from existing
source and samples. It is explicitly labeled retrospective.

DO NOT add parsing logic here. The implementation authority is src/python/ndjson/.
"""

from __future__ import annotations

import sys
from pathlib import Path

# ---- Dependency import (compatibility guard) ----
try:
    _REPO = Path(__file__).resolve().parents[3]
    if str(_REPO) not in sys.path:
        sys.path.insert(0, str(_REPO))
    from src.python.ndjson import ndjson_codec as _ndjson_codec  # type: ignore[import]
    _REQUIRED_SYMBOLS = {"load_ndjson", "probe_ndjson", "NdjsonParseError"}
    _missing = _REQUIRED_SYMBOLS - set(dir(_ndjson_codec))
    if _missing:
        raise ImportError(f"ndjson_codec missing expected symbols: {_missing}")
except ImportError as exc:
    raise ImportError(
        "ndjson_gate4_probe: delegated source src/python/ndjson/ndjson_codec.py "
        "is unavailable or has changed incompatibly."
    ) from exc

GATE4_EVIDENCE_TYPE = "EVIDENCE_WRAPPER"
RETROSPECTIVE = True
DELEGATED_SOURCE = "src/python/ndjson/ndjson_codec.py"
DELEGATED_SYMBOLS = ["load_ndjson", "probe_ndjson", "NdjsonParseError"]


def probe(file_path: str | Path) -> list:
    """Load all records from an NDJSON file via the delegated source.

    Returns list of parsed records. Delegates entirely to ndjson_codec.load_ndjson().
    """
    return _ndjson_codec.load_ndjson(str(file_path))


def probe_invalid(file_path: str | Path | None = None) -> dict:
    """Prove that missing/malformed input is handled.

    Returns error info dict. Wraps NdjsonParseError so callers receive
    a consistent evidence dict rather than a raw exception.
    """
    path = file_path or "/nonexistent_gate4_probe_ndjson.ndjson"
    try:
        records = _ndjson_codec.load_ndjson(str(path))
        # If no exception, check the result
        return {"ok": False, "error": "Expected failure for invalid input", "records": records}
    except _ndjson_codec.NdjsonParseError as e:
        return {"ok": False, "error": str(e), "error_type": "NdjsonParseError"}
    except FileNotFoundError as e:
        return {"ok": False, "error": str(e), "error_type": "FileNotFoundError"}
    except Exception as e:
        return {"ok": False, "error": str(e), "error_type": type(e).__name__}


def is_ndjson(file_path: str | Path) -> bool:
    """Check whether a file is parseable as NDJSON via probe_ndjson."""
    return bool(_ndjson_codec.probe_ndjson(str(file_path)))


def compatibility_check() -> bool:
    """Verify the delegated API has all required symbols."""
    missing = _REQUIRED_SYMBOLS - set(dir(_ndjson_codec))
    if missing:
        raise ImportError(
            f"Delegated source ndjson_codec is missing symbols: {missing}."
        )
    return True


if __name__ == "__main__":
    import json
    target = sys.argv[1] if len(sys.argv) > 1 else None
    if target:
        result = probe(target)
        print(json.dumps(result, default=str, indent=2))
    else:
        print("ndjson_gate4_probe: EVIDENCE_WRAPPER (RETROSPECTIVE) for src/python/ndjson/ndjson_codec.py")
        compatibility_check()
        print("  Compatibility check: PASS")
