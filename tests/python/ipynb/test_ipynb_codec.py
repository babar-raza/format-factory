"""Core tests for the ipynb codec — probe, load, write, roundtrip."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from ipynb.ipynb_codec import (
    get_cell_count,
    get_code_cells,
    get_markdown_cells,
    ipynb_installed_workflow,
    load_ipynb,
    probe_ipynb,
    roundtrip,
    write_ipynb,
)
from ipynb.exceptions import IpynbError, IpynbParseError, IpynbWriteError
from ipynb.models import IpynbDocument

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "ipynb"
VALID_DIR = SAMPLES / "valid"
INVALID_DIR = SAMPLES / "invalid"


class TestProbe:
    def test_probe_valid_minimal(self):
        assert probe_ipynb(VALID_DIR / "minimal.ipynb") is True

    def test_probe_valid_code_and_markdown(self):
        assert probe_ipynb(VALID_DIR / "code-and-markdown.ipynb") is True

    def test_probe_valid_with_outputs(self):
        assert probe_ipynb(VALID_DIR / "with-outputs.ipynb") is True

    def test_probe_invalid_missing_nbformat(self):
        assert probe_ipynb(INVALID_DIR / "missing-nbformat.ipynb") is False

    def test_probe_nonexistent_file(self):
        assert probe_ipynb("/nonexistent/file.ipynb") is False

    def test_probe_random_bytes(self):
        assert probe_ipynb(b"not json at all \x00\xff") is False

    def test_probe_empty_string(self):
        assert probe_ipynb(b"") is False

    def test_probe_json_array(self):
        assert probe_ipynb(b'[1, 2, 3]') is False

    def test_probe_json_object_without_nbformat(self):
        assert probe_ipynb(b'{"cells": [], "metadata": {}}') is False


class TestLoad:
    def test_load_minimal(self):
        model = load_ipynb(VALID_DIR / "minimal.ipynb")
        assert isinstance(model, dict)
        assert "nbformat" in model
        assert "cells" in model
        assert isinstance(model["cells"], list)

    def test_load_code_and_markdown(self):
        model = load_ipynb(VALID_DIR / "code-and-markdown.ipynb")
        types = [c["cell_type"] for c in model["cells"]]
        assert "code" in types or "markdown" in types

    def test_load_with_outputs(self):
        model = load_ipynb(VALID_DIR / "with-outputs.ipynb")
        code_cells = [c for c in model["cells"] if c["cell_type"] == "code"]
        has_outputs = any(len(c.get("outputs", [])) > 0 for c in code_cells)
        assert has_outputs

    def test_load_invalid_raises(self):
        with pytest.raises(IpynbParseError, match="Missing required key"):
            load_ipynb(INVALID_DIR / "missing-nbformat.ipynb")

    def test_load_bad_json_raises(self):
        with pytest.raises(IpynbParseError, match="Invalid JSON"):
            load_ipynb(b"{ not valid json }")

    def test_load_from_bytes(self):
        data = json.dumps({"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": []})
        model = load_ipynb(data.encode("utf-8"))
        assert model["nbformat"] == 4
        assert model["cells"] == []

    def test_load_from_string(self):
        data = json.dumps({"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": []})
        model = load_ipynb(data)
        assert model["nbformat"] == 4


class TestWrite:
    def test_write_returns_json_string(self):
        model = {"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": []}
        result = write_ipynb(model)
        parsed = json.loads(result)
        assert parsed["nbformat"] == 4

    def test_write_to_file(self):
        model = {
            "nbformat": 4,
            "nbformat_minor": 5,
            "metadata": {},
            "cells": [{"cell_type": "code", "source": "x = 1", "metadata": {}, "outputs": []}],
        }
        with tempfile.NamedTemporaryFile(suffix=".ipynb", delete=False) as f:
            dest = f.name
        try:
            write_ipynb(model, dest)
            content = Path(dest).read_text(encoding="utf-8")
            parsed = json.loads(content)
            assert parsed["cells"][0]["source"] == "x = 1"
        finally:
            Path(dest).unlink(missing_ok=True)

    def test_write_preserves_code_cell_outputs(self):
        model = {
            "nbformat": 4,
            "nbformat_minor": 5,
            "metadata": {},
            "cells": [
                {
                    "cell_type": "code",
                    "source": "print('hi')",
                    "metadata": {},
                    "outputs": [{"output_type": "stream", "name": "stdout", "text": "hi\n"}],
                }
            ],
        }
        result = json.loads(write_ipynb(model))
        assert result["cells"][0]["outputs"][0]["text"] == "hi\n"


class TestRoundtrip:
    def test_roundtrip_minimal(self):
        with tempfile.NamedTemporaryFile(suffix=".ipynb", delete=False) as f:
            dest = f.name
        try:
            original = load_ipynb(VALID_DIR / "minimal.ipynb")
            reloaded = roundtrip(VALID_DIR / "minimal.ipynb", dest)
            assert original["nbformat"] == reloaded["nbformat"]
            assert len(original["cells"]) == len(reloaded["cells"])
        finally:
            Path(dest).unlink(missing_ok=True)


class TestHelpers:
    def test_get_cell_count(self):
        model = {"cells": [{"cell_type": "code"}, {"cell_type": "markdown"}]}
        assert get_cell_count(model) == 2

    def test_get_code_cells(self):
        model = {"cells": [{"cell_type": "code"}, {"cell_type": "markdown"}, {"cell_type": "code"}]}
        assert len(get_code_cells(model)) == 2

    def test_get_markdown_cells(self):
        model = {"cells": [{"cell_type": "code"}, {"cell_type": "markdown"}]}
        assert len(get_markdown_cells(model)) == 1


class TestModel:
    def test_ipynb_document(self):
        data = {"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": [
            {"cell_type": "code", "source": "x = 1", "metadata": {}, "outputs": []},
            {"cell_type": "markdown", "source": "# Title", "metadata": {}},
        ]}
        doc = IpynbDocument(data)
        assert doc.nbformat == 4
        assert doc.cell_count == 2
        assert len(doc.code_cells) == 1
        assert len(doc.markdown_cells) == 1
        assert not doc.is_empty
        assert repr(doc) == "IpynbDocument(nbformat=4, cells=2)"


class TestImport:
    def test_import_probe_load(self):
        from ipynb import probe, load
        assert callable(probe)
        assert callable(load)

    def test_import_write(self):
        from ipynb import write
        assert callable(write)

    def test_installed_workflow(self):
        data = json.dumps({"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": []})
        result = ipynb_installed_workflow(data.encode("utf-8"))
        assert result["format"] == "ipynb"
        assert result["loaded"] is True
        assert result["cell_count"] == 0


class TestAdditionalCodecCoverage:
    """Phase 2 supplementary probe/load coverage (added alongside professional-tier build-out)."""

    def test_probe_with_path_object(self):
        assert probe_ipynb(Path(VALID_DIR / "minimal.ipynb")) is True

    def test_probe_with_string_path(self):
        assert probe_ipynb(str(VALID_DIR / "with-outputs.ipynb")) is True

    def test_get_cell_count_real_file(self):
        model = load_ipynb(VALID_DIR / "code-and-markdown.ipynb")
        assert get_cell_count(model) == 9

    def test_get_code_cells_real_file(self):
        model = load_ipynb(VALID_DIR / "code-and-markdown.ipynb")
        assert len(get_code_cells(model)) == 4

    def test_get_markdown_cells_real_file(self):
        model = load_ipynb(VALID_DIR / "code-and-markdown.ipynb")
        assert len(get_markdown_cells(model)) == 5

    def test_load_nbformat_minor_present(self):
        model = load_ipynb(VALID_DIR / "minimal.ipynb")
        assert model["nbformat_minor"] == 5

    def test_write_returns_string_without_writing_file(self):
        model = {"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": []}
        result = write_ipynb(model, dest=None)
        assert isinstance(result, str)
        assert json.loads(result)["nbformat"] == 4

    def test_probe_all_valid_samples(self):
        for name in ("minimal.ipynb", "code-and-markdown.ipynb", "with-outputs.ipynb"):
            assert probe_ipynb(VALID_DIR / name) is True

    def test_load_with_outputs_execution_count(self):
        model = load_ipynb(VALID_DIR / "with-outputs.ipynb")
        code_cells = get_code_cells(model)
        assert code_cells[0]["execution_count"] == 5

    def test_write_then_probe_roundtrip(self):
        model = {
            "nbformat": 4,
            "nbformat_minor": 5,
            "metadata": {},
            "cells": [{"cell_type": "code", "source": "x = 1", "metadata": {}, "outputs": []}],
        }
        with tempfile.NamedTemporaryFile(suffix=".ipynb", delete=False) as f:
            dest = f.name
        try:
            write_ipynb(model, dest)
            assert probe_ipynb(dest) is True
        finally:
            Path(dest).unlink(missing_ok=True)
