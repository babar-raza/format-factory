"""Tests for V104 (governance_validators_ext3.py: validate_constant_return_public_methods).

Standalone regression suite for the RULE-PQLM-005 semantic-stub-return detector. All
fixtures build a synthetic src/python/<fmt>/ tree under tmp_path and pass it as
repo_root, so none of these tests touch the real repository's src/python/ tree.

Covers the 2026-08 fix for an asymmetric bug: the emptiness gate already applied to
List returns (`return []` flagged, `return [1, 2, 3]` not) was missing for Dict and
Tuple, so ANY dict/tuple literal return -- including one built entirely from instance
state, e.g. `return {"tag": self.tag}` or `return (self.major, self.minor)` -- was
flagged as a "semantic stub" regardless of whether its contents were actually
constant. Confirmed against the real repo: 13 genuine `to_dict`/`as_tuple` methods
across 8 format packages (including 2 of FF6's own -- ipynb, xliff) were false
positives from this exact bug.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
_SUPERVISOR = _REPO / "tools" / "supervisor"
if str(_SUPERVISOR) not in sys.path:
    sys.path.insert(0, str(_SUPERVISOR))

from governance_validators_ext3 import (  # noqa: E402
    validate_constant_return_public_methods,
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class TestV104ConstantReturnPublicMethods:
    def test_scalar_constant_return_fails(self, tmp_path):
        """`return True` unconditionally -- the classic semantic-stub shape -- still
        FAILs; the fix must not weaken detection of genuine constant scalars."""
        pkg = tmp_path / "src" / "python" / "stubfmt"
        _write(pkg / "model.py", (
            "class Report:\n"
            "    def is_lossless(self) -> bool:\n"
            "        return True\n"
        ))

        result = validate_constant_return_public_methods({}, repo_root=tmp_path)

        assert result["validator_id"] == "V104"
        assert result["status"] == "FAIL"
        assert result["blocks_sprint"] is True
        assert any("is_lossless" in v for v in result["violations_new"])

    def test_empty_dict_return_still_fails(self, tmp_path):
        """`return {}` is still a degenerate, always-identical value -- must still FAIL,
        matching the existing behavior for `return []`."""
        pkg = tmp_path / "src" / "python" / "emptydictfmt"
        _write(pkg / "model.py", (
            "class Doc:\n"
            "    def metadata(self) -> dict:\n"
            "        return {}\n"
        ))

        result = validate_constant_return_public_methods({}, repo_root=tmp_path)

        assert result["status"] == "FAIL"
        assert any("metadata" in v for v in result["violations_new"])

    def test_empty_tuple_return_still_fails(self, tmp_path):
        pkg = tmp_path / "src" / "python" / "emptytuplefmt"
        _write(pkg / "model.py", (
            "class Doc:\n"
            "    def coordinates(self) -> tuple:\n"
            "        return ()\n"
        ))

        result = validate_constant_return_public_methods({}, repo_root=tmp_path)

        assert result["status"] == "FAIL"
        assert any("coordinates" in v for v in result["violations_new"])

    def test_dict_built_from_instance_attributes_passes(self, tmp_path):
        """The exact bug this fix closes: a `to_dict()` returning a dict literal whose
        VALUES are instance attributes (a fresh, per-call-varying result) must not be
        flagged just because the top-level AST node is a Dict literal."""
        pkg = tmp_path / "src" / "python" / "todictfmt"
        _write(pkg / "model.py", (
            "class Element:\n"
            "    def to_dict(self) -> dict:\n"
            "        return {\n"
            "            'tag': self.tag,\n"
            "            'attributes': dict(self.attributes),\n"
            "        }\n"
        ))

        result = validate_constant_return_public_methods({}, repo_root=tmp_path)

        assert result["status"] == "PASS"

    def test_tuple_built_from_instance_attributes_passes(self, tmp_path):
        """The Tuple analog of the same bug: `as_tuple()` returning `(self.a, self.b)`
        must not be flagged -- it varies with instance state, it is not a constant."""
        pkg = tmp_path / "src" / "python" / "astuplefmt"
        _write(pkg / "model.py", (
            "class Version:\n"
            "    def as_tuple(self) -> tuple:\n"
            "        return self.major, self.minor\n"
        ))

        result = validate_constant_return_public_methods({}, repo_root=tmp_path)

        assert result["status"] == "PASS"

    def test_nonempty_list_of_literals_still_passes(self, tmp_path):
        """Pre-existing behavior preserved: a non-empty List literal (even of only
        constants) is not flagged -- only List's emptiness gate is extended to
        Dict/Tuple, List's own existing semantics are untouched."""
        pkg = tmp_path / "src" / "python" / "listfmt"
        _write(pkg / "model.py", (
            "class Doc:\n"
            "    def supported_versions(self) -> list:\n"
            "        return [1, 2, 3]\n"
        ))

        result = validate_constant_return_public_methods({}, repo_root=tmp_path)

        assert result["status"] == "PASS"

    def test_docstring_then_dict_return_passes(self, tmp_path):
        """The two-statement body branch (docstring + return) gets the same fix."""
        pkg = tmp_path / "src" / "python" / "docdictfmt"
        _write(pkg / "model.py", (
            "class Element:\n"
            "    def to_dict(self) -> dict:\n"
            "        \"\"\"Serialize this element.\"\"\"\n"
            "        return {'tag': self.tag}\n"
        ))

        result = validate_constant_return_public_methods({}, repo_root=tmp_path)

        assert result["status"] == "PASS"

    def test_no_src_python_dir_passes(self, tmp_path):
        result = validate_constant_return_public_methods({}, repo_root=tmp_path)

        assert result["status"] == "PASS"
        assert result["blocks_sprint"] is False
