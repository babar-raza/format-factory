"""Configurable resource limits shared by format readers.

visibility: generated
generated_by: codex
"""

from __future__ import annotations

from dataclasses import dataclass, fields

from .errors import ResourceLimitError


@dataclass(frozen=True, slots=True)
class ResourceLimits:
    """Finite processing limits.

    Defaults are conservative library-wide ceilings. Individual formats may
    expose smaller defaults, but may not silently replace a caller-supplied
    instance with less restrictive values.
    """

    max_input_bytes: int = 512 * 1024 * 1024
    max_output_bytes: int = 512 * 1024 * 1024
    max_header_bytes: int = 16 * 1024 * 1024
    max_decompressed_bytes: int = 2 * 1024 * 1024 * 1024
    max_compression_ratio: float = 100.0
    max_entries: int = 100_000
    max_nesting_depth: int = 128
    max_xml_nodes: int = 5_000_000
    max_tensor_count: int = 1_000_000

    def __post_init__(self) -> None:
        for descriptor in fields(self):
            value = getattr(self, descriptor.name)
            if value <= 0:
                raise ValueError(f"{descriptor.name} must be greater than zero")

    def with_overrides(self, **values: int | float) -> "ResourceLimits":
        field_names = {item.name for item in fields(self)}
        unknown = set(values).difference(field_names)
        if unknown:
            raise TypeError(f"unknown resource limits: {', '.join(sorted(unknown))}")
        for name, value in values.items():
            if name == "max_compression_ratio":
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    raise TypeError(f"{name} must be numeric")
            elif isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an integer")
        return ResourceLimits(
            max_input_bytes=int(values.get("max_input_bytes", self.max_input_bytes)),
            max_output_bytes=int(values.get("max_output_bytes", self.max_output_bytes)),
            max_header_bytes=int(values.get("max_header_bytes", self.max_header_bytes)),
            max_decompressed_bytes=int(
                values.get("max_decompressed_bytes", self.max_decompressed_bytes)
            ),
            max_compression_ratio=float(
                values.get("max_compression_ratio", self.max_compression_ratio)
            ),
            max_entries=int(values.get("max_entries", self.max_entries)),
            max_nesting_depth=int(
                values.get("max_nesting_depth", self.max_nesting_depth)
            ),
            max_xml_nodes=int(values.get("max_xml_nodes", self.max_xml_nodes)),
            max_tensor_count=int(
                values.get("max_tensor_count", self.max_tensor_count)
            ),
        )

    def enforce(self, name: str, actual: int | float) -> None:
        if not hasattr(self, name):
            raise TypeError(f"unknown resource limit: {name}")
        maximum = getattr(self, name)
        if actual > maximum:
            raise ResourceLimitError(
                f"{name} exceeded: {actual} > {maximum}",
                context={"limit": name, "actual": actual, "maximum": maximum},
            )


DEFAULT_LIMITS = ResourceLimits()
