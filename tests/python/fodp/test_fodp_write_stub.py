"""Regression guard: FODP exposes no write path at all (TC-PA-012).

History
-------
QF-1-004 answered PQ-009 ("user tries to write FODP and gets no helpful error")
by adding a ``write_fodp()`` sentinel to ``fodp.fodp_codec`` that raised
``NotImplementedError`` unconditionally — and, in the same fix, quarantined it
out of the public API. That quarantine neutralised the sentinel's only benefit:
because it was never in ``fodp.__all__``, ``from fodp import write_fodp`` raised
ImportError and no user could reach the helpful message through the public API.
What remained was a non-abstract function that always raised — an EP-1 letter
violation kept alive by three ``no_stub_scan`` allowlist regexes.

TC-PA-012 (2026-07-17) removed the sentinel. FODP is read-only at this parser
level (PROB-006, deferred post-Gate 11).

This module previously asserted the sentinel's *raising behaviour*. Those
assertions are gone with the function. What is preserved — and what actually
protects users — is the property the sentinel was quarantined into anyway:
**FODP surfaces no write symbol on any import path.** These tests fail if a
write path is reintroduced without a governed decision.
"""
import pytest
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import fodp
import fodp.fodp_codec


def test_write_fodp_not_defined_in_codec():
    """The TC-PA-012 removal itself. Fails if the sentinel is restored."""
    assert not hasattr(fodp.fodp_codec, "write_fodp")


def test_write_fodp_not_importable_from_codec_module():
    with pytest.raises(ImportError):
        from fodp.fodp_codec import write_fodp  # noqa: F401


def test_write_fodp_not_exported_from_package():
    assert "write_fodp" not in fodp.__all__


def test_write_fodp_not_importable_from_package():
    with pytest.raises(ImportError):
        from fodp import write_fodp  # noqa: F401


def test_write_fodp_absent_from_package_namespace():
    assert not hasattr(fodp, "write_fodp")


def test_fodp_exposes_no_write_symbol_at_all():
    """Guard the general property, not just the one historical name."""
    write_symbols = [n for n in fodp.__all__ if n.startswith("write")]
    assert write_symbols == [], f"FODP is read-only but exports {write_symbols}"


def test_fodp_codec_defines_no_write_symbol():
    write_symbols = [
        n for n in dir(fodp.fodp_codec)
        if n.startswith("write") and callable(getattr(fodp.fodp_codec, n, None))
    ]
    assert write_symbols == [], f"fodp_codec defines write symbols: {write_symbols}"


def test_read_api_still_intact_after_removal():
    """Removal must not have disturbed the read/export surface."""
    for name in ("load", "export_to_txt", "export_to_csv", "export_to_json"):
        assert name in fodp.__all__, f"{name} missing from fodp.__all__"
        assert callable(getattr(fodp, name))


def test_codec_module_still_imports_cleanly():
    """The edit removed a top-level def; module must still be importable."""
    import importlib
    m = importlib.reload(fodp.fodp_codec)
    assert callable(m.load)
