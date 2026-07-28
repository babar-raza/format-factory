from format_factory.core import ResourceLimits

SAFETENSORS_LIMITS = ResourceLimits(
    max_input_bytes=512 * 1024 * 1024,
    max_output_bytes=512 * 1024 * 1024,
    max_header_bytes=16 * 1024 * 1024,
    max_decompressed_bytes=2 * 1024 * 1024 * 1024,
    max_compression_ratio=100.0,
    max_entries=100_000,
    max_nesting_depth=64,
    max_xml_nodes=5_000_000,
    max_tensor_count=1_000_000,
)


def effective_limits(limits: ResourceLimits | None) -> ResourceLimits:
    return limits if limits is not None else SAFETENSORS_LIMITS
