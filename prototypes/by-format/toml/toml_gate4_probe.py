"""
TOML Gate 4 Evidence Wrapper — Gate 4 acquisition evidence (RETROSPECTIVE).

This is a THIN EVIDENCE WRAPPER. It contains NO parsing logic.
All parsing is delegated to src/python/toml/toml_codec.py.

RETROSPECTIVE NOTE: TOML Gate 4 evidence was never formally recorded despite
the format having a full production-quality implementation in src/python/toml/.
This wrapper reconstructs the Gate 4 evidence retrospectively from existing
source and samples. It is explicitly labeled retrospective.

DO NOT add parsing logic here. The implementation authority is src/python/toml/.
"""

from __future__ import annotations

import sys
from pathlib import Path

# ---- Dependency import (compatibility guard) ----
try:
    _REPO = Path(__file__).resolve().parents[3]
    if str(_REPO) not in sys.path:
        sys.path.insert(0, str(_REPO))
    from src.python.toml import toml_codec as _toml_codec  # type: ignore[import]
    _REQUIRED_SYMBOLS = {"load_toml", "probe_toml", "TomlParseError", "TomlInputError"}
    _missing = _REQUIRED_SYMBOLS - set(dir(_toml_codec))
    if _missing:
        raise ImportError(f"toml_codec missing expected symbols: {_missing}")
except ImportError as exc:
    raise ImportError(
        "toml_gate4_probe: delegated source src/python/toml/toml_codec.py "
        "is unavailable or has changed incompatibly."
    ) from exc

GATE4_EVIDENCE_TYPE = "EVIDENCE_WRAPPER"
RETROSPECTIVE = True
DELEGATED_SOURCE = "src/python/toml/toml_codec.py"
DELEGATED_SYMBOLS = ["load_toml", "probe_toml", "TomlParseError", "TomlInputError"]


def probe(file_path: str | Path) -> dict:
    """Load and parse a TOML file via the delegated source.

    Returns the result dict from toml_codec.load_toml(). Delegates entirely.
    """
    return _toml_codec.load_toml(str(file_path))


def probe_invalid(file_path: str | Path | None = None) -> dict:
    """Prove that missing/invalid input is handled gracefully.

    Returns error info dict. Wraps TomlInputError/TomlParseError.
    """
    path = file_path or "/nonexistent_gate4_probe_toml.toml"
    try:
        result = _toml_codec.load_toml(str(path))
        return result
    except _toml_codec.TomlInputError as e:
        return {"ok": False, "error": str(e), "error_type": "TomlInputError"}
    except _toml_codec.TomlParseError as e:
        return {"ok": False, "error": str(e), "error_type": "TomlParseError"}
    except Exception as e:
        return {"ok": False, "error": str(e), "error_type": type(e).__name__}


def compatibility_check() -> bool:
    """Verify the delegated API has all required symbols."""
    missing = _REQUIRED_SYMBOLS - set(dir(_toml_codec))
    if missing:
        raise ImportError(
            f"Delegated source toml_codec is missing symbols: {missing}."
        )
    return True


if __name__ == "__main__":
    import json
    target = sys.argv[1] if len(sys.argv) > 1 else None
    if target:
        result = probe(target)
        print(json.dumps(result, default=str, indent=2))
    else:
        print("toml_gate4_probe: EVIDENCE_WRAPPER (RETROSPECTIVE) for src/python/toml/toml_codec.py")
        compatibility_check()
        print("  Compatibility check: PASS")
