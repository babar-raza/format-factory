"""
r154_netpbm_code_citations.py

Sprint: FORMAT-FACTORY-AUTHORITY-GATED-PRODUCT-DOGFOOD-FEATURES-AND-BACKFILL-001
Added: 2026-06-09

Tests that PBM/PGM/PPM magic constants are cited in source (code citation for P5/P6 promotion).
Authority: PBM P5, PGM P5, PPM P5 after these citations.

FACT-PBM-001: P1 magic (ASCII)
FACT-PBM-002: P4 magic (binary)
FACT-PGM-001: P2 magic (ASCII)
FACT-PGM-002: P5 magic (binary)
FACT-PPM-001: P3 magic (ASCII)
FACT-PPM-002: P6 magic (binary)
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = _REPO_ROOT
sys.path.insert(0, str(PROJECT_ROOT))


class TestPbmMagicCodeCitations:
    """PBM_MAGIC_ASCII and PBM_MAGIC_BINARY must be in source (FACT-PBM-001, FACT-PBM-002)."""

    def test_pbm_magic_ascii_constant_exists(self):
        from src.python.pbm.pbm_parser import PBM_MAGIC_ASCII
        assert PBM_MAGIC_ASCII == "P1"

    def test_pbm_magic_binary_constant_exists(self):
        from src.python.pbm.pbm_parser import PBM_MAGIC_BINARY
        assert PBM_MAGIC_BINARY == "P4"

    def test_pbm_source_has_fact_pbm_001_comment(self):
        src = (_REPO_ROOT / "src" / "python" / "pbm" / "pbm_parser.py").read_text()
        assert "FACT-PBM-001" in src

    def test_pbm_source_has_fact_pbm_002_comment(self):
        src = (_REPO_ROOT / "src" / "python" / "pbm" / "pbm_parser.py").read_text()
        assert "FACT-PBM-002" in src


class TestPgmMagicCodeCitations:
    """PGM_MAGIC_ASCII and PGM_MAGIC_BINARY must be in source (FACT-PGM-001, FACT-PGM-002)."""

    def test_pgm_magic_ascii_constant_exists(self):
        from src.python.pgm.pgm_parser import PGM_MAGIC_ASCII
        assert PGM_MAGIC_ASCII == "P2"

    def test_pgm_magic_binary_constant_exists(self):
        from src.python.pgm.pgm_parser import PGM_MAGIC_BINARY
        assert PGM_MAGIC_BINARY == "P5"

    def test_pgm_source_has_fact_pgm_001_comment(self):
        src = (_REPO_ROOT / "src" / "python" / "pgm" / "pgm_parser.py").read_text()
        assert "FACT-PGM-001" in src

    def test_pgm_source_has_fact_pgm_002_comment(self):
        src = (_REPO_ROOT / "src" / "python" / "pgm" / "pgm_parser.py").read_text()
        assert "FACT-PGM-002" in src


class TestPpmMagicCodeCitations:
    """PPM_MAGIC_ASCII and PPM_MAGIC_BINARY must be in source (FACT-PPM-001, FACT-PPM-002)."""

    def test_ppm_magic_ascii_constant_exists(self):
        from src.python.ppm.ppm_parser import PPM_MAGIC_ASCII
        assert PPM_MAGIC_ASCII == "P3"

    def test_ppm_magic_binary_constant_exists(self):
        from src.python.ppm.ppm_parser import PPM_MAGIC_BINARY
        assert PPM_MAGIC_BINARY == "P6"

    def test_ppm_source_has_fact_ppm_001_comment(self):
        src = (_REPO_ROOT / "src" / "python" / "ppm" / "ppm_parser.py").read_text()
        assert "FACT-PPM-001" in src

    def test_ppm_source_has_fact_ppm_002_comment(self):
        src = (_REPO_ROOT / "src" / "python" / "ppm" / "ppm_parser.py").read_text()
        assert "FACT-PPM-002" in src
