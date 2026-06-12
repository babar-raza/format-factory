"""
format-factory-qoi — QOI (Quite OK Image) parser prototype.

Gate 4 prototype. FOSS track. No third-party dependencies.
Acquisition gates 1-4 passed. Implementation authorized: R27.
commercial_product_ready: false
"""

from .qoi_parser import (
    parse_qoi,
    parse_qoi_strict,
    probe_qoi,
    get_capabilities,
    qoi_dimensions,
    qoi_pixel_count,
    QoiImage,
)
from .qoi_encoder import (
    encode_qoi,
    encode_qoi_to_file,
    get_encoder_capabilities,
)

__version__ = "0.1.0.dev0"
__track__ = "python-foss"
__commercial_ready__ = False
__capability_level__ = "alpha-foss-preview"

__all__ = [
    "parse_qoi",
    "parse_qoi_strict",
    "probe_qoi",
    "get_capabilities",
    "qoi_dimensions",
    "qoi_pixel_count",
    "QoiImage",
    "encode_qoi",
    "encode_qoi_to_file",
    "get_encoder_capabilities",
]
