"""ipynb.spec.notebook — spec-shaped scaffold classes for the ipynb QName entries.

Exports:
    Notebook — spec-shaped class for ipynb:notebook (FACT-IPYNB-001)
    Cell     — spec-shaped class for ipynb:cell     (FACT-IPYNB-002)
    Output   — spec-shaped class for ipynb:output   (FACT-IPYNB-003)
"""
from .notebook import Notebook
from .cell import Cell
from .output import Output

__all__ = ["Notebook", "Cell", "Output"]
