"""ipynb.Compat — production facade layer for Jupyter Notebook.

Exports:
    IpynbNotebook — facade for ipynb:notebook (FACT-IPYNB-001)
    IpynbCell     — facade for ipynb:cell     (FACT-IPYNB-002)
    IpynbOutput   — facade for ipynb:output   (FACT-IPYNB-003)
"""
from .ipynb_notebook import IpynbNotebook
from .ipynb_cell import IpynbCell
from .ipynb_output import IpynbOutput

__all__ = ["IpynbNotebook", "IpynbCell", "IpynbOutput"]
