"""Failure-first tests for lossless, read-only typed metadata adapters."""

from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from pathlib import Path

import pytest
from format_factory.ipynb import (
    IpynbDocument,
    MetadataShapeError,
    cell_metadata,
    dumps,
    load,
    loads,
    notebook_metadata,
    output_metadata,
)

VALID_DIR = (
    Path(__file__).resolve().parents[3]
    / "samples"
    / "by-format"
    / "ipynb"
    / "valid"
)


def _document() -> IpynbDocument:
    return IpynbDocument(
        {
            "nbformat": 4,
            "nbformat_minor": 5,
            "metadata": {
                "kernelspec": {
                    "name": "python3",
                    "display_name": "Python 3",
                    "language": "python",
                    "vendor_kernel": {"keep": True},
                },
                "language_info": {
                    "name": "python",
                    "version": "3.13",
                    "mimetype": "text/x-python",
                    "file_extension": ".py",
                    "codemirror_mode": {"name": "ipython", "version": 3},
                    "pygments_lexer": "ipython3",
                    "vendor_language": ["keep"],
                },
                "org.example": {"notebook": "keep"},
            },
            "cells": [
                {
                    "cell_type": "code",
                    "id": "code",
                    "metadata": {
                        "tags": ["parameters", "production"],
                        "slideshow": {
                            "slide_type": "slide",
                            "vendor_slide": "keep",
                        },
                        "execution": {
                            "iopub.status.busy": "2026-07-26T00:00:00Z",
                            "iopub.execute_input": "2026-07-26T00:00:01Z",
                            "shell.execute_reply.started": "2026-07-26T00:00:02Z",
                            "shell.execute_reply": "2026-07-26T00:00:03Z",
                            "vendor_timing": "4",
                        },
                        "org.example": {"cell": "keep"},
                    },
                    "source": "value = 1",
                    "execution_count": 1,
                    "outputs": [
                        {
                            "output_type": "display_data",
                            "data": {
                                "text/plain": "1",
                                "text/html": "<b>1</b>",
                            },
                            "metadata": {
                                "text/html": {
                                    "isolated": True,
                                    "vendor_render": "keep",
                                },
                                "org.example": {"output": "keep"},
                            },
                        }
                    ],
                }
            ],
        }
    )


def test_real_fixture_kernelspec_adapter_is_exact_and_non_mutating() -> None:
    document = load(VALID_DIR / "minimal.ipynb")
    before = deepcopy(document.raw)

    adapter = notebook_metadata(document)
    kernel = adapter.kernelspec

    assert kernel is not None
    assert kernel.name == "python3"
    assert kernel.display_name == "Python 3"
    assert kernel.language == "python"
    assert kernel.to_dict() == before["metadata"]["kernelspec"]
    assert adapter.language_info is None
    assert document.raw == before


def test_notebook_metadata_typed_fields_preserve_unknown_namespaces() -> None:
    document = _document()
    adapter = notebook_metadata(document)

    kernel = adapter.kernelspec
    language = adapter.language_info

    assert kernel is not None and language is not None
    assert kernel.extras == {"vendor_kernel": {"keep": True}}
    assert language.name == "python"
    assert language.version == "3.13"
    assert language.codemirror_mode == {"name": "ipython", "version": 3}
    assert language.extras == {"vendor_language": ["keep"]}
    assert adapter.extras == {"org.example": {"notebook": "keep"}}
    assert adapter.to_dict() == document.raw["metadata"]


def test_cell_and_output_adapters_cover_common_namespaces() -> None:
    document = _document()
    cell_adapter = cell_metadata(document.cell_objects[0])
    output_adapter = output_metadata(
        document.cell_objects[0].output_objects[0]
    )

    assert cell_adapter.tags == ("parameters", "production")
    assert cell_adapter.slideshow is not None
    assert cell_adapter.slideshow.slide_type == "slide"
    assert cell_adapter.slideshow.extras == {"vendor_slide": "keep"}
    assert cell_adapter.execution is not None
    assert (
        cell_adapter.execution.shell_execute_reply
        == "2026-07-26T00:00:03Z"
    )
    assert cell_adapter.execution.extras == {"vendor_timing": "4"}
    assert cell_adapter.extras == {"org.example": {"cell": "keep"}}

    html = output_adapter.mime("text/html")
    assert html is not None
    assert html.values == {
        "isolated": True,
        "vendor_render": "keep",
    }
    assert output_adapter.mime("image/png") is None
    assert output_adapter.extras == {
        "org.example": {"output": "keep"}
    }


def test_adapters_are_defensive_snapshots_and_roundtrip_is_lossless() -> None:
    document = _document()
    before = deepcopy(document.raw)
    adapter = notebook_metadata(document)
    exported = adapter.to_dict()

    exported["org.example"]["notebook"] = "changed copy"
    document.raw["metadata"]["org.example"]["notebook"] = "changed source"

    assert adapter.extras == {"org.example": {"notebook": "keep"}}
    document.raw.clear()
    document.raw.update(before)
    assert loads(dumps(document)).raw == before


@pytest.mark.parametrize(
    "mutate, access, message",
    [
        (
            lambda value: value.raw["metadata"].update(kernelspec="bad"),
            lambda value: notebook_metadata(value).kernelspec,
            "kernelspec",
        ),
        (
            lambda value: value.cells[0]["metadata"].update(
                tags=["duplicate", "duplicate"]
            ),
            lambda value: cell_metadata(value.cell_objects[0]).tags,
            "unique",
        ),
        (
            lambda value: value.cells[0]["outputs"][0]["metadata"].update(
                {"text/html": "bad"}
            ),
            lambda value: output_metadata(
                value.cell_objects[0].output_objects[0]
            ).mime("text/html"),
            "text/html",
        ),
    ],
)
def test_malformed_known_metadata_fails_explicitly(
    mutate: Callable[[IpynbDocument], object],
    access: Callable[[IpynbDocument], object],
    message: str,
) -> None:
    document = _document()
    mutate(document)

    with pytest.raises(MetadataShapeError, match=message):
        access(document)
