"""Format Factory ipynb (Jupyter Notebook) FOSS Python codec."""

from __future__ import annotations

from ipynb.ipynb_codec import (
    add_output_representation,
    ensure_cell_id,
    get_cell_count,
    get_code_cells,
    get_markdown_cells,
    get_output_representation,
    ipynb_installed_workflow,
    load_ipynb,
    probe_ipynb,
    remove_output_mime_type,
    roundtrip,
    validate_notebook,
    validate_notebook_schema,
    write_ipynb,
)
from ipynb.exceptions import (
    IpynbError,
    IpynbParseError,
    IpynbValidationError,
    IpynbWriteError,
)
from ipynb.models import IpynbDocument
from ipynb.ipynb_analytics import (
    ipynb_average_source_length,
    ipynb_cell_type_histogram,
    ipynb_has_execution_errors,
    ipynb_output_type_histogram,
)

__all__ = [
    "get_cell_count",
    "get_code_cells",
    "get_markdown_cells",
    "ipynb_installed_workflow",
    "load_ipynb",
    "probe_ipynb",
    "roundtrip",
    "write_ipynb",
    "ensure_cell_id",
    "get_output_representation",
    "add_output_representation",
    "remove_output_mime_type",
    "validate_notebook_schema",
    "validate_notebook",
    "IpynbDocument",
    "IpynbError",
    "IpynbParseError",
    "IpynbWriteError",
    "IpynbValidationError",
    "ipynb_average_source_length",
    "ipynb_cell_type_histogram",
    "ipynb_has_execution_errors",
    "ipynb_output_type_histogram",
]

__version__ = "0.1.0.dev0"
__track__ = "python-foss"
__commercial_ready__ = False

probe = probe_ipynb
load = load_ipynb
write = write_ipynb
