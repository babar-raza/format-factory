"""XLIFF resource-limit policy."""

from format_factory.core import DEFAULT_LIMITS, ResourceLimits

XLIFF_DEFAULT_LIMITS = DEFAULT_LIMITS.with_overrides(
    max_input_bytes=64 * 1024 * 1024,
    max_output_bytes=128 * 1024 * 1024,
    max_nesting_depth=64,
    max_xml_nodes=1_000_000,
)


def effective_limits(limits: ResourceLimits | None) -> ResourceLimits:
    return limits or XLIFF_DEFAULT_LIMITS
