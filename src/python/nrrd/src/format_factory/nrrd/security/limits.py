"""NRRD resource-limit policy."""

from format_factory.core import DEFAULT_LIMITS, ResourceLimits

NRRD_DEFAULT_LIMITS = DEFAULT_LIMITS.with_overrides(
    max_input_bytes=256 * 1024 * 1024,
    max_header_bytes=1024 * 1024,
    max_decompressed_bytes=512 * 1024 * 1024,
    max_entries=64,
)


def effective_limits(limits: ResourceLimits | None) -> ResourceLimits:
    return limits or NRRD_DEFAULT_LIMITS
