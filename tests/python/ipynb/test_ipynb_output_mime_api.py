"""Tests for the output MIME-bundle API (FACT-IPYNB-103).

Prior to this fix, ``ipynb.spec.notebook.output.Output`` existed but was
never used by anything — outputs survived round-trip only as an
accidental side effect of whole-object passthrough, with no first-class
way to inspect/add/remove a specific MIME representation. These tests
prove Output is now real, wired-in behavior: a multi-representation
execute_result output can have each MIME type retrieved independently,
a new representation added, and one removed — without corrupting the
others or the surrounding output/cell/notebook structure.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from ipynb.ipynb_codec import (
    add_output_representation,
    get_output_representation,
    load_ipynb,
    remove_output_mime_type,
    write_ipynb,
)
from ipynb.spec.notebook.output import Output


def _multi_mime_output() -> dict:
    return {
        "output_type": "execute_result",
        "execution_count": 1,
        "metadata": {},
        "data": {
            "text/plain": "<Figure>",
            "text/html": "<b>Figure</b>",
        },
    }


class TestOutputClassDirect:
    def test_get_representation_returns_existing_mime_value(self):
        out = Output(_multi_mime_output())
        assert out.get_representation("text/plain") == "<Figure>"
        assert out.get_representation("text/html") == "<b>Figure</b>"

    def test_get_representation_missing_mime_returns_none(self):
        out = Output(_multi_mime_output())
        assert out.get_representation("image/png") is None

    def test_add_representation_adds_new_mime_type(self):
        data = _multi_mime_output()
        out = Output(data)
        out.add_representation("image/png", "base64pngdata")
        assert data["data"]["image/png"] == "base64pngdata"
        # existing representations untouched
        assert data["data"]["text/plain"] == "<Figure>"
        assert data["data"]["text/html"] == "<b>Figure</b>"

    def test_add_representation_creates_data_bundle_if_absent(self):
        data = {"output_type": "execute_result", "execution_count": 1}
        out = Output(data)
        out.add_representation("text/plain", "hi")
        assert data["data"] == {"text/plain": "hi"}

    def test_remove_representation_removes_only_target_mime(self):
        data = _multi_mime_output()
        out = Output(data)
        removed = out.remove_representation("text/html")
        assert removed is True
        assert "text/html" not in data["data"]
        assert data["data"]["text/plain"] == "<Figure>"

    def test_remove_representation_missing_mime_returns_false(self):
        data = _multi_mime_output()
        out = Output(data)
        removed = out.remove_representation("image/png")
        assert removed is False
        # nothing else touched
        assert data["data"] == {"text/plain": "<Figure>", "text/html": "<b>Figure</b>"}

    def test_full_add_get_remove_sequence_preserves_other_representations(self):
        data = _multi_mime_output()
        out = Output(data)

        assert out.get_representation("text/plain") == "<Figure>"
        assert out.get_representation("text/html") == "<b>Figure</b>"

        out.add_representation("image/png", "pngbytes")
        assert out.get_representation("image/png") == "pngbytes"

        removed = out.remove_representation("text/html")
        assert removed is True

        # Final state: text/plain and image/png survive, text/html gone.
        assert data["data"] == {"text/plain": "<Figure>", "image/png": "pngbytes"}


class TestCodecLevelWrappers:
    def test_get_output_representation_wraps_output_class(self):
        output = _multi_mime_output()
        assert get_output_representation(output, "text/plain") == "<Figure>"

    def test_add_output_representation_mutates_and_returns_output(self):
        output = _multi_mime_output()
        result = add_output_representation(output, "image/png", "b64data")
        assert result is output
        assert output["data"]["image/png"] == "b64data"

    def test_remove_output_mime_type_returns_bool(self):
        output = _multi_mime_output()
        assert remove_output_mime_type(output, "text/html") is True
        assert remove_output_mime_type(output, "text/html") is False

    def test_mutations_survive_full_notebook_write_reload(self):
        """Exercise the whole notebook, not just an isolated output dict."""
        model = {
            "nbformat": 4,
            "nbformat_minor": 5,
            "metadata": {},
            "cells": [
                {
                    "cell_type": "code",
                    "source": "render()",
                    "metadata": {},
                    "outputs": [_multi_mime_output()],
                }
            ],
        }
        output = model["cells"][0]["outputs"][0]
        add_output_representation(output, "image/png", "pngbytes")
        remove_output_mime_type(output, "text/html")

        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.ipynb"
            write_ipynb(model, dest)
            reloaded = load_ipynb(dest)

        reloaded_data = reloaded["cells"][0]["outputs"][0]["data"]
        assert reloaded_data == {"text/plain": "<Figure>", "image/png": "pngbytes"}

    def test_stream_output_get_representation_returns_none(self):
        """data bundle API is a no-op (not a crash) on stream outputs,
        which carry text/name instead of a MIME data bundle."""
        stream_output = {"output_type": "stream", "name": "stdout", "text": "hi\n"}
        assert get_output_representation(stream_output, "text/plain") is None
