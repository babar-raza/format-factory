"""Notebook-specific resource-limit policy."""

from format_factory.core import DEFAULT_LIMITS, ResourceLimits

IPYNB_DEFAULT_LIMITS = DEFAULT_LIMITS.with_overrides(
    max_input_bytes=64 * 1024 * 1024,
    max_nesting_depth=64,
)


def effective_limits(limits: ResourceLimits | None) -> ResourceLimits:
    return limits or IPYNB_DEFAULT_LIMITS
