"""Tests for cell id preservation and generation (FACT-IPYNB-101).

nbformat >=4.5 requires every cell to carry a unique id matching
``^[a-zA-Z0-9_-]{1,64}$``. Prior to this fix, load_ipynb/write_ipynb used
an explicit key allow-list that silently dropped ``id`` on every
load->write round-trip. These tests prove the real fix: ids survive
unchanged, missing/invalid/colliding ids are regenerated, and uniqueness
holds across an entire notebook.
"""
from __future__ import annotations

import json
import re
import tempfile
from pathlib import Path

from ipynb.ipynb_codec import CELL_ID_PATTERN, ensure_cell_id, load_ipynb, write_ipynb
from ipynb.models import IpynbDocument

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "ipynb"
VALID_DIR = SAMPLES / "valid"


def _nb(cells: list[dict]) -> bytes:
    return json.dumps(
        {"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": cells}
    ).encode("utf-8")


class TestEnsureCellId:
    def test_generates_id_when_missing(self):
        cell = {"cell_type": "code", "source": "x = 1", "metadata": {}}
        used: set[str] = set()
        ensure_cell_id(cell, used)
        assert isinstance(cell["id"], str)
        assert CELL_ID_PATTERN.match(cell["id"])
        assert cell["id"] in used

    def test_preserves_valid_existing_id(self):
        cell = {"cell_type": "code", "id": "abc123", "source": "x", "metadata": {}}
        used: set[str] = set()
        ensure_cell_id(cell, used)
        assert cell["id"] == "abc123"

    def test_regenerates_invalid_format_id(self):
        # Contains a space and a '!' -- not in [a-zA-Z0-9_-]
        cell = {"cell_type": "code", "id": "not a valid id!", "source": "x", "metadata": {}}
        used: set[str] = set()
        ensure_cell_id(cell, used)
        assert cell["id"] != "not a valid id!"
        assert CELL_ID_PATTERN.match(cell["id"])

    def test_regenerates_too_long_id(self):
        cell = {"cell_type": "code", "id": "x" * 65, "source": "x", "metadata": {}}
        used: set[str] = set()
        ensure_cell_id(cell, used)
        assert len(cell["id"]) <= 64
        assert CELL_ID_PATTERN.match(cell["id"])

    def test_regenerates_on_collision(self):
        used = {"dupe123"}
        cell = {"cell_type": "code", "id": "dupe123", "source": "x", "metadata": {}}
        ensure_cell_id(cell, used)
        assert cell["id"] != "dupe123"
        assert CELL_ID_PATTERN.match(cell["id"])

    def test_two_cells_never_collide(self):
        used: set[str] = set()
        c1 = {"cell_type": "code", "source": "a", "metadata": {}}
        c2 = {"cell_type": "code", "source": "b", "metadata": {}}
        ensure_cell_id(c1, used)
        ensure_cell_id(c2, used)
        assert c1["id"] != c2["id"]

    def test_empty_string_id_regenerated(self):
        cell = {"cell_type": "code", "id": "", "source": "x", "metadata": {}}
        used: set[str] = set()
        ensure_cell_id(cell, used)
        assert cell["id"] != ""
        assert CELL_ID_PATTERN.match(cell["id"])

    def test_non_string_id_regenerated(self):
        cell = {"cell_type": "code", "id": 12345, "source": "x", "metadata": {}}
        used: set[str] = set()
        ensure_cell_id(cell, used)
        assert isinstance(cell["id"], str)


class TestLoadAssignsIds:
    def test_load_assigns_id_to_every_cell(self):
        data = _nb(
            [
                {"cell_type": "code", "source": "x = 1", "metadata": {}},
                {"cell_type": "markdown", "source": "hi", "metadata": {}},
            ]
        )
        model = load_ipynb(data)
        for cell in model["cells"]:
            assert isinstance(cell.get("id"), str)
            assert CELL_ID_PATTERN.match(cell["id"])

    def test_load_assigns_unique_ids_across_notebook(self):
        data = _nb([{"cell_type": "code", "source": f"x = {i}", "metadata": {}} for i in range(5)])
        model = load_ipynb(data)
        ids = [c["id"] for c in model["cells"]]
        assert len(ids) == len(set(ids))

    def test_load_preserves_real_notebook_ids_when_present(self):
        data = _nb(
            [
                {"cell_type": "code", "id": "cell-one", "source": "x", "metadata": {}},
                {"cell_type": "markdown", "id": "cell-two", "source": "y", "metadata": {}},
            ]
        )
        model = load_ipynb(data)
        assert model["cells"][0]["id"] == "cell-one"
        assert model["cells"][1]["id"] == "cell-two"

    def test_load_regenerates_duplicate_ids_across_notebook(self):
        data = _nb(
            [
                {"cell_type": "code", "id": "dup", "source": "a", "metadata": {}},
                {"cell_type": "markdown", "id": "dup", "source": "b", "metadata": {}},
            ]
        )
        model = load_ipynb(data)
        ids = [c["id"] for c in model["cells"]]
        assert len(ids) == len(set(ids))
        # first occurrence keeps the original id
        assert model["cells"][0]["id"] == "dup"
        assert model["cells"][1]["id"] != "dup"


class TestRoundTripPreservesIds:
    def test_real_ids_survive_load_write_reload_unchanged(self):
        """The core regression: a real notebook's cell ids must not be
        stripped or altered across a full load -> write -> reload cycle."""
        original = load_ipynb(VALID_DIR / "code-and-markdown.ipynb")
        original_ids = [c["id"] for c in original["cells"]]

        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "roundtrip.ipynb"
            write_ipynb(original, dest)
            reloaded = load_ipynb(dest)

        reloaded_ids = [c["id"] for c in reloaded["cells"]]
        assert reloaded_ids == original_ids

    def test_ids_stable_across_multiple_roundtrips(self):
        model = load_ipynb(VALID_DIR / "with-outputs.ipynb")
        ids_after_1 = [c["id"] for c in model["cells"]]

        with tempfile.TemporaryDirectory() as td:
            dest1 = Path(td) / "r1.ipynb"
            write_ipynb(model, dest1)
            model2 = load_ipynb(dest1)
            ids_after_2 = [c["id"] for c in model2["cells"]]

            dest2 = Path(td) / "r2.ipynb"
            write_ipynb(model2, dest2)
            model3 = load_ipynb(dest2)
            ids_after_3 = [c["id"] for c in model3["cells"]]

        assert ids_after_1 == ids_after_2 == ids_after_3

    def test_written_json_actually_contains_id_key(self):
        """Confirm real bytes on disk carry 'id', not just the in-memory model."""
        model = load_ipynb(VALID_DIR / "minimal.ipynb")
        model["cells"].append({"cell_type": "code", "source": "y = 2", "metadata": {}})

        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.ipynb"
            write_ipynb(model, dest)
            raw_text = dest.read_text(encoding="utf-8")
            raw_json = json.loads(raw_text)

        assert all("id" in cell for cell in raw_json["cells"])
        # And the id actually round-trips as a top-level JSON string field,
        # not merely present in the in-memory dict.
        assert isinstance(raw_json["cells"][0]["id"], str)

    def test_write_generates_id_for_cell_missing_one(self):
        model = {
            "nbformat": 4,
            "nbformat_minor": 5,
            "metadata": {},
            "cells": [{"cell_type": "code", "source": "z = 3", "metadata": {}}],
        }
        result = json.loads(write_ipynb(model))
        assert CELL_ID_PATTERN.match(result["cells"][0]["id"])


class TestMutationApiAssignsId:
    def test_new_cell_via_add_cell_has_valid_unique_id(self):
        doc = IpynbDocument.from_file(str(VALID_DIR / "code-and-markdown.ipynb"))
        existing_ids = {c["id"] for c in doc.cells}
        new_cell = doc.add_cell(cell_type="markdown", source="new")
        assert isinstance(new_cell["id"], str)
        assert CELL_ID_PATTERN.match(new_cell["id"])
        assert new_cell["id"] not in existing_ids

    def test_added_cell_id_survives_save_reload(self):
        doc = IpynbDocument.from_file(str(VALID_DIR / "minimal.ipynb"))
        new_cell = doc.add_cell(cell_type="code", source="q = 1")
        new_id = new_cell["id"]

        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "added.ipynb"
            write_ipynb(doc.to_dict(), dest)
            reloaded = load_ipynb(dest)

        assert reloaded["cells"][-1]["id"] == new_id
