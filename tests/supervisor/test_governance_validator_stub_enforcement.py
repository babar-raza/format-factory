"""Regression tests for fail-closed source-stub governance.

generated_by: codex
"""

import sys
from pathlib import Path


SUPERVISOR_PATH = str(Path(__file__).resolve().parents[2] / "tools" / "supervisor")
if SUPERVISOR_PATH not in sys.path:
    sys.path.insert(0, SUPERVISOR_PATH)


def test_v149_does_not_mutate_syspath():
    from governance_validators_ext4 import validate_source_stubs

    before = list(sys.path)
    validate_source_stubs(
        {"planned_work_items": [{"id": "X", "work_item_type": "PRODUCT_SOURCE"}]}
    )
    assert sys.path == before


def test_v149_still_detects_stubs(tmp_path):
    from governance_validators_ext4 import validate_source_stubs

    stub = tmp_path / "src" / "python" / "badfmt" / "mod.py"
    stub.parent.mkdir(parents=True)
    stub.write_text(
        "def do_thing():\n    x = 1  # FIXME: broken\n    return x\n",
        encoding="utf-8",
    )
    result = validate_source_stubs(
        {"planned_work_items": [{"id": "X", "work_item_type": "PRODUCT_SOURCE"}]},
        repo_root=tmp_path,
    )
    assert result["result"] == "FAIL"
    assert result["blocks_sprint"] is True
    assert any("mod.py" in str(item.get("file", "")) for item in result.get("items", []))


def test_v149_fails_closed_when_scanner_unavailable(monkeypatch):
    import governance_validators_ext4 as ext4

    def unavailable():
        raise ImportError("simulated: no_stub_scan unavailable")

    monkeypatch.setattr(ext4, "_load_no_stub_report", unavailable)
    product = ext4.validate_source_stubs(
        {"planned_work_items": [{"id": "X", "work_item_type": "PRODUCT_SOURCE"}]}
    )
    empty = ext4.validate_source_stubs({"planned_work_items": []})
    assert (product["result"], product["blocks_sprint"]) == ("FAIL", True)
    assert (empty["result"], empty["blocks_sprint"]) == ("WARN", False)
