"""Framework-neutral model for a SafeTensors sharded-index document."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from types import MappingProxyType
from typing import Any


def _validate_shard_reference(reference: object) -> str:
    if not isinstance(reference, str) or not reference or "\\" in reference:
        raise ValueError("shard reference must be a relative normalized POSIX path")
    path = PurePosixPath(reference)
    if (
        path.is_absolute()
        or path.as_posix() != reference
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        raise ValueError("shard reference must be a relative normalized POSIX path")
    return reference


@dataclass(frozen=True, slots=True)
class SafeTensorsShardIndex:
    """Deterministic tensor-to-shard mapping with root-confined resolution."""

    weight_map: Mapping[str, str]
    metadata: Mapping[str, Any] = field(default_factory=dict)
    unknown_fields: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        weights: dict[str, str] = {}
        for tensor_name, reference in self.weight_map.items():
            if not isinstance(tensor_name, str) or not tensor_name:
                raise ValueError("tensor names in weight_map must be non-empty strings")
            weights[tensor_name] = _validate_shard_reference(reference)
        if any(not isinstance(key, str) for key in self.metadata):
            raise ValueError("sharded-index metadata keys must be strings")
        if any(not isinstance(key, str) for key in self.unknown_fields):
            raise ValueError("sharded-index extension keys must be strings")
        if {"metadata", "weight_map"}.intersection(self.unknown_fields):
            raise ValueError("sharded-index extensions may not replace reserved fields")
        object.__setattr__(self, "weight_map", MappingProxyType(weights))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))
        object.__setattr__(
            self,
            "unknown_fields",
            MappingProxyType(dict(self.unknown_fields)),
        )

    def shard_for(self, tensor_name: str) -> str:
        """Return the normalized relative shard reference for a tensor."""

        return self.weight_map[tensor_name]

    def tensors_for_shard(self, reference: str) -> tuple[str, ...]:
        """Return tensor names mapped to one normalized shard reference."""

        selected = _validate_shard_reference(reference)
        return tuple(
            sorted(name for name, shard in self.weight_map.items() if shard == selected)
        )

    def resolve_shard(self, tensor_name: str, root: str | Path) -> Path:
        """Resolve one tensor's shard while proving it remains under ``root``."""

        root_path = Path(root).resolve()
        reference = PurePosixPath(self.shard_for(tensor_name))
        candidate = root_path.joinpath(*reference.parts).resolve()
        try:
            candidate.relative_to(root_path)
        except ValueError as exc:
            raise ValueError("resolved shard path escapes the configured root") from exc
        return candidate
