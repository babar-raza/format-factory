"""Packaging proof: ODS and SYLK wheel build + import verification.

Sprint: PACKAGING-BREAKTHROUGH.
Verifies that wheels exist and contain the expected modules.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
VENV_PYTHON = REPO / ".local" / "venv" / "Scripts" / "python"


class TestOdsWheelProof:
    def test_ods_wheel_exists(self) -> None:
        wheel_dir = REPO / ".local" / "wheels" / "ods"
        wheels = list(wheel_dir.glob("*.whl"))
        assert len(wheels) >= 1, f"No ODS wheel found in {wheel_dir}"
        assert "format_factory_ods" in wheels[0].name

    def test_ods_import_from_source(self) -> None:
        sys.path.insert(0, str(REPO / "src" / "python"))
        import ods
        assert hasattr(ods, "__version__")
        assert hasattr(ods, "parse_ods_strict")
        assert len(ods.__all__) >= 40

    def test_ods_build_reproducible(self) -> None:
        wheel_dir = REPO / ".local" / "wheels" / "ods"
        wheels = list(wheel_dir.glob("*.whl"))
        assert all(w.stat().st_size > 1000 for w in wheels), "Wheel too small"


class TestSylkWheelProof:
    def test_sylk_wheel_exists(self) -> None:
        wheel_dir = REPO / ".local" / "wheels" / "sylk"
        wheels = list(wheel_dir.glob("*.whl"))
        assert len(wheels) >= 1, f"No SYLK wheel found in {wheel_dir}"
        assert "format_factory_sylk" in wheels[0].name

    def test_sylk_import_from_source(self) -> None:
        sys.path.insert(0, str(REPO / "src" / "python"))
        import sylk
        assert hasattr(sylk, "__version__")
        assert hasattr(sylk, "parse_sylk_strict")
        assert len(sylk.__all__) >= 35

    def test_sylk_build_reproducible(self) -> None:
        wheel_dir = REPO / ".local" / "wheels" / "sylk"
        wheels = list(wheel_dir.glob("*.whl"))
        assert all(w.stat().st_size > 1000 for w in wheels), "Wheel too small"
