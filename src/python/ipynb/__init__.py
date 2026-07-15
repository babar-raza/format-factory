"""Format Factory ipynb (Jupyter Notebook) FOSS Python codec."""

from __future__ import annotations

from ipynb.ipynb_codec import (
    get_cell_count,
    get_code_cells,
    get_markdown_cells,
    ipynb_installed_workflow,
    load_ipynb,
    probe_ipynb,
    roundtrip,
    write_ipynb,
)
from ipynb.exceptions import IpynbError, IpynbParseError, IpynbWriteError
from ipynb.models import IpynbDocument

__all__ = [
    "get_cell_count",
    "get_code_cells",
    "get_markdown_cells",
    "ipynb_installed_workflow",
    "load_ipynb",
    "probe_ipynb",
    "roundtrip",
    "write_ipynb",
    "IpynbDocument",
    "IpynbError",
    "IpynbParseError",
    "IpynbWriteError",
]

__version__ = "0.1.0.dev0"
__track__ = "python-foss"
__commercial_ready__ = False

probe = probe_ipynb
load = load_ipynb
write = write_ipynb
