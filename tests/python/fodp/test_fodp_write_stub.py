"""Tests for write_fodp() read-only stub (QF-1-004).

Verifies that write_fodp raises NotImplementedError with a helpful message,
confirming that FODP is correctly documented as a read-only format.
"""
import pytest
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from fodp import write_fodp


def test_write_fodp_raises_not_implemented():
    with pytest.raises(NotImplementedError):
        write_fodp({}, "output.fodp")


def test_write_fodp_message_mentions_read_only():
    with pytest.raises(NotImplementedError, match="read-only"):
        write_fodp({}, "output.fodp")


def test_write_fodp_message_mentions_load():
    with pytest.raises(NotImplementedError, match="load"):
        write_fodp({}, Path("output.fodp"))


def test_write_fodp_message_mentions_export():
    with pytest.raises(NotImplementedError, match="export"):
        write_fodp({}, "output.fodp")


def test_write_fodp_exported_from_package():
    import fodp
    assert hasattr(fodp, "write_fodp")
    assert callable(fodp.write_fodp)


def test_write_fodp_in_all():
    import fodp
    assert "write_fodp" in fodp.__all__
