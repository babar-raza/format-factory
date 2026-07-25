from __future__ import annotations

from io import StringIO
from pathlib import Path

import pytest

from format_factory.safetensors import (
    SafeTensorsParseError,
    SafeTensorsShardIndex,
    dump_index,
    dumps_index,
    load_index,
    loads_index,
)


def test_sharded_index_is_deterministic_and_resolves_tensors(tmp_path: Path) -> None:
    index = loads_index(
        """
        {
          "weight_map": {
            "layer.z": "model-00002-of-00002.safetensors",
            "layer.a": "model-00001-of-00002.safetensors"
          },
          "metadata": {"total_size": 8}
        }
        """
    )

    assert index.shard_for("layer.a") == "model-00001-of-00002.safetensors"
    assert index.tensors_for_shard("model-00002-of-00002.safetensors") == ("layer.z",)
    assert index.resolve_shard("layer.a", tmp_path) == (
        tmp_path / "model-00001-of-00002.safetensors"
    ).resolve()
    first = dumps_index(index)
    assert first == dumps_index(index)
    assert first.index('"layer.a"') < first.index('"layer.z"')


@pytest.mark.parametrize(
    "reference",
    [
        "../outside.safetensors",
        "/absolute.safetensors",
        "nested\\windows-traversal.safetensors",
        "nested/../ambiguous.safetensors",
    ],
)
def test_shard_references_are_root_confined(reference: str) -> None:
    with pytest.raises(ValueError, match="relative normalized POSIX path"):
        SafeTensorsShardIndex(weight_map={"tensor": reference})


def test_duplicate_tensor_mapping_is_rejected() -> None:
    duplicate = (
        '{"metadata":{},"weight_map":{'
        '"tensor":"first.safetensors","tensor":"second.safetensors"}}'
    )
    with pytest.raises(SafeTensorsParseError, match="duplicate JSON key"):
        loads_index(duplicate)


def test_sharded_index_path_and_stream_lifecycle(tmp_path: Path) -> None:
    index = SafeTensorsShardIndex(
        weight_map={"tensor": "model.safetensors"},
        metadata={"total_size": 1},
    )
    destination = tmp_path / "model.safetensors.index.json"
    dump_index(index, destination)
    assert load_index(destination) == index

    stream = StringIO()
    dump_index(index, stream)
    stream.seek(0)
    assert load_index(stream) == index
