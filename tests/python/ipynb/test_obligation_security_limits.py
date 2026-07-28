"""Failure-first adversarial tests for bounded notebook parsing."""

from __future__ import annotations

import json

import pytest

from format_factory.core import ResourceLimitError
from format_factory.ipynb import IPYNB_DEFAULT_LIMITS, IpynbParseError, loads


def _notebook(*, metadata: object = None, cells: list[object] | None = None) -> str:
    return json.dumps(
        {
            "nbformat": 4,
            "nbformat_minor": 5,
            "metadata": {} if metadata is None else metadata,
            "cells": [] if cells is None else cells,
        }
    )


def test_total_element_count_is_bounded() -> None:
    cells = [
        {
            "cell_type": "markdown",
            "id": f"cell-{index}",
            "metadata": {},
            "source": "x",
        }
        for index in range(20)
    ]
    limits = IPYNB_DEFAULT_LIMITS.with_overrides(max_entries=40)

    with pytest.raises(ResourceLimitError, match="max_entries exceeded"):
        loads(_notebook(cells=cells), limits=limits)


def test_nesting_depth_is_bounded_without_recursive_walker_failure() -> None:
    nested: object = "leaf"
    for _ in range(20):
        nested = {"nested": nested}
    limits = IPYNB_DEFAULT_LIMITS.with_overrides(max_nesting_depth=8)

    with pytest.raises(ResourceLimitError, match="max_nesting_depth exceeded"):
        loads(_notebook(metadata={"vendor": nested}), limits=limits)


def test_json_recursion_failure_is_a_deterministic_parse_error() -> None:
    deeply_nested = (
        '{"nbformat":4,"nbformat_minor":5,"metadata":{"x":'
        + ("[" * 1500)
        + "0"
        + ("]" * 1500)
        + '},"cells":[]}'
    )

    with pytest.raises(
        (IpynbParseError, ResourceLimitError),
        match="complexity|max_nesting_depth exceeded",
    ):
        loads(deeply_nested, mode="preservation")


def test_input_and_decoded_payload_bytes_are_bounded() -> None:
    encoded = _notebook(metadata={"payload": "x" * 200})
    limits = IPYNB_DEFAULT_LIMITS.with_overrides(
        max_input_bytes=100,
        max_decompressed_bytes=100,
    )

    with pytest.raises(ResourceLimitError, match="max_input_bytes exceeded"):
        loads(encoded, limits=limits)
