"""Tests for notebook schema/structural validation (FACT-IPYNB-105).

Checks: cell id uniqueness/format, output_type enum, and required fields
per output_type (stream: name+text; display_data: data; execute_result:
data+execution_count; error: ename+evalue+traceback).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from ipynb.exceptions import IpynbValidationError
from ipynb.ipynb_codec import load_ipynb, validate_notebook, validate_notebook_schema

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "ipynb"
VALID_DIR = SAMPLES / "valid"


def _valid_notebook() -> dict:
    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {},
        "cells": [
            {"cell_type": "markdown", "id": "c1", "source": "# hi", "metadata": {}},
            {
                "cell_type": "code",
                "id": "c2",
                "source": "print('hi')",
                "metadata": {},
                "execution_count": 1,
                "outputs": [
                    {"output_type": "stream", "name": "stdout", "text": "hi\n"},
                    {
                        "output_type": "execute_result",
                        "execution_count": 1,
                        "data": {"text/plain": "'hi'"},
                        "metadata": {},
                    },
                ],
            },
        ],
    }


class TestValidNotebooks:
    def test_well_formed_notebook_passes(self):
        errors = validate_notebook_schema(_valid_notebook())
        assert errors == []

    def test_well_formed_notebook_does_not_raise(self):
        validate_notebook(_valid_notebook())  # should not raise

    def test_real_sample_files_pass(self):
        for name in ("minimal.ipynb", "code-and-markdown.ipynb", "with-outputs.ipynb"):
            model = load_ipynb(VALID_DIR / name)
            assert validate_notebook_schema(model) == []

    def test_empty_notebook_passes(self):
        model = {"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": []}
        assert validate_notebook_schema(model) == []

    def test_display_data_output_passes(self):
        model = _valid_notebook()
        model["cells"][1]["outputs"] = [
            {"output_type": "display_data", "data": {"text/plain": "x"}, "metadata": {}}
        ]
        assert validate_notebook_schema(model) == []

    def test_error_output_passes(self):
        model = _valid_notebook()
        model["cells"][1]["outputs"] = [
            {"output_type": "error", "ename": "ValueError", "evalue": "bad", "traceback": ["line1"]}
        ]
        assert validate_notebook_schema(model) == []


class TestDuplicateCellId:
    def test_duplicate_id_fails(self):
        model = _valid_notebook()
        model["cells"][1]["id"] = model["cells"][0]["id"]  # force duplicate
        errors = validate_notebook_schema(model)
        assert errors != []
        assert any("duplicate" in e.lower() for e in errors)

    def test_duplicate_id_raises_via_validate_notebook(self):
        model = _valid_notebook()
        model["cells"][1]["id"] = model["cells"][0]["id"]
        with pytest.raises(IpynbValidationError, match="duplicate"):
            validate_notebook(model)


class TestCellIdFormat:
    def test_missing_id_fails(self):
        model = _valid_notebook()
        del model["cells"][0]["id"]
        errors = validate_notebook_schema(model)
        assert any("invalid or missing id" in e for e in errors)

    def test_malformed_id_fails(self):
        model = _valid_notebook()
        model["cells"][0]["id"] = "has a space"
        errors = validate_notebook_schema(model)
        assert any("invalid or missing id" in e for e in errors)

    def test_non_string_id_fails(self):
        model = _valid_notebook()
        model["cells"][0]["id"] = 42
        errors = validate_notebook_schema(model)
        assert any("invalid or missing id" in e for e in errors)


class TestOutputTypeEnum:
    def test_unknown_output_type_fails(self):
        model = _valid_notebook()
        model["cells"][1]["outputs"] = [{"output_type": "bogus_type"}]
        errors = validate_notebook_schema(model)
        assert any("invalid output_type" in e for e in errors)

    def test_missing_output_type_fails(self):
        model = _valid_notebook()
        model["cells"][1]["outputs"] = [{"data": {"text/plain": "x"}}]
        errors = validate_notebook_schema(model)
        assert any("invalid output_type" in e for e in errors)


class TestRequiredFieldsPerOutputType:
    def test_stream_missing_text_fails(self):
        model = _valid_notebook()
        model["cells"][1]["outputs"] = [{"output_type": "stream", "name": "stdout"}]
        errors = validate_notebook_schema(model)
        assert any("stream" in e and "text" in e for e in errors)

    def test_stream_missing_name_fails(self):
        model = _valid_notebook()
        model["cells"][1]["outputs"] = [{"output_type": "stream", "text": "hi\n"}]
        errors = validate_notebook_schema(model)
        assert any("stream" in e and "name" in e for e in errors)

    def test_display_data_missing_data_fails(self):
        model = _valid_notebook()
        model["cells"][1]["outputs"] = [{"output_type": "display_data", "metadata": {}}]
        errors = validate_notebook_schema(model)
        assert any("display_data" in e and "data" in e for e in errors)

    def test_execute_result_missing_execution_count_fails(self):
        model = _valid_notebook()
        model["cells"][1]["outputs"] = [
            {"output_type": "execute_result", "data": {"text/plain": "x"}}
        ]
        errors = validate_notebook_schema(model)
        assert any("execute_result" in e and "execution_count" in e for e in errors)

    def test_execute_result_missing_data_fails(self):
        model = _valid_notebook()
        model["cells"][1]["outputs"] = [
            {"output_type": "execute_result", "execution_count": 1}
        ]
        errors = validate_notebook_schema(model)
        assert any("execute_result" in e and "'data'" in e for e in errors)

    def test_error_missing_ename_fails(self):
        model = _valid_notebook()
        model["cells"][1]["outputs"] = [
            {"output_type": "error", "evalue": "bad", "traceback": []}
        ]
        errors = validate_notebook_schema(model)
        assert any("error" in e and "ename" in e for e in errors)

    def test_error_missing_traceback_fails(self):
        model = _valid_notebook()
        model["cells"][1]["outputs"] = [
            {"output_type": "error", "ename": "E", "evalue": "bad"}
        ]
        errors = validate_notebook_schema(model)
        assert any("error" in e and "traceback" in e for e in errors)

    def test_markdown_cell_outputs_not_checked(self):
        """Only code cells carry outputs -- markdown/raw cells are skipped
        entirely by the output-type checks."""
        model = _valid_notebook()
        model["cells"][0]["cell_type"] = "markdown"
        # markdown cells have no "outputs" key at all normally; ensure no
        # crash / no spurious errors are raised for it.
        errors = validate_notebook_schema(model)
        assert errors == []


class TestMultipleFailuresReported:
    def test_multiple_errors_all_present_in_raised_message(self):
        model = _valid_notebook()
        model["cells"][1]["id"] = model["cells"][0]["id"]
        model["cells"][1]["outputs"] = [{"output_type": "stream", "name": "stdout"}]
        errors = validate_notebook_schema(model)
        assert len(errors) >= 2
        with pytest.raises(IpynbValidationError) as exc_info:
            validate_notebook(model)
        message = str(exc_info.value)
        assert "duplicate" in message.lower()
        assert "text" in message
