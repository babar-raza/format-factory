"""Tests for verify_package_install.py (CT-INSTALL-001).

Uses temporary site-packages fixtures to isolate from the real environment.
"""
from __future__ import annotations

import io
import shutil
import sys
from contextlib import redirect_stdout
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "tools" / "assurance"))

import verify_package_install as vp


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_pkg_file(base: Path, pkg: str, rel: str, content: str) -> Path:
    p = base / pkg / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


def _make_src_pkg(tmp_path: Path, pkg: str = "testpkg") -> Path:
    src_dir = tmp_path / "src" / pkg
    _write_pkg_file(tmp_path / "src", pkg, "__init__.py", "# package\n")
    _write_pkg_file(tmp_path / "src", pkg, "core.py", "def hello(): return 1\n")
    return src_dir


# ---------------------------------------------------------------------------
# Test 1: NOT_INSTALLED → exit 1, no "All packages in sync"
# ---------------------------------------------------------------------------

def test_not_installed_exits_with_error(tmp_path, monkeypatch):
    """NOT_INSTALLED must produce exit code 1 and must not print 'All packages in sync'."""
    sp = tmp_path / "site-packages"
    sp.mkdir()
    src = tmp_path / "src" / "abw"
    src.mkdir(parents=True)
    (src / "__init__.py").write_text("", encoding="utf-8")

    monkeypatch.setattr(vp, "SRC_ROOT", tmp_path / "src")
    monkeypatch.setattr(vp, "VENV_ROOT", sp)
    monkeypatch.setattr(vp, "PACKAGES", ["abw"])

    buf = io.StringIO()
    with redirect_stdout(buf):
        exit_code = vp.main([])

    output = buf.getvalue()
    assert exit_code == 1, f"Expected exit 1 for NOT_INSTALLED, got {exit_code}"
    assert "All packages in sync" not in output, \
        "NOT_INSTALLED must NOT produce 'All packages in sync'"
    assert "NOT_INSTALLED" in output


# ---------------------------------------------------------------------------
# Test 2: EDITABLE_PTH → exit 0, shows editable message (not "in sync")
# ---------------------------------------------------------------------------

def test_editable_pth_exits_zero_with_editable_message(tmp_path, monkeypatch):
    """Editable (.pth) install: exit 0 and prints 'EDITABLE install', not 'in sync'."""
    sp = tmp_path / "site-packages"
    sp.mkdir()
    (sp / "__editable__.format_factory_abw-0.1.0.dev0.pth").write_text(
        str(tmp_path / "src") + "\n", encoding="utf-8"
    )
    src = tmp_path / "src" / "abw"
    src.mkdir(parents=True)
    (src / "__init__.py").write_text("", encoding="utf-8")

    monkeypatch.setattr(vp, "SRC_ROOT", tmp_path / "src")
    monkeypatch.setattr(vp, "VENV_ROOT", sp)
    monkeypatch.setattr(vp, "PACKAGES", ["abw"])

    buf = io.StringIO()
    with redirect_stdout(buf):
        exit_code = vp.main([])

    output = buf.getvalue()
    assert exit_code == 0
    assert "EDITABLE" in output
    assert "All packages in sync" not in output


# ---------------------------------------------------------------------------
# Test 3: DIRECTORY, stale files → exit 1
# ---------------------------------------------------------------------------

def test_stale_directory_install_exits_one(tmp_path, monkeypatch):
    """Non-editable directory install with stale files: exit 1."""
    sp = tmp_path / "site-packages"
    pkg = "abw"
    src = tmp_path / "src"
    _write_pkg_file(src, pkg, "__init__.py", "version = '2'\n")
    _write_pkg_file(sp, pkg, "__init__.py", "version = '1'\n")  # stale

    monkeypatch.setattr(vp, "SRC_ROOT", src)
    monkeypatch.setattr(vp, "VENV_ROOT", sp)
    monkeypatch.setattr(vp, "PACKAGES", ["abw"])

    buf = io.StringIO()
    with redirect_stdout(buf):
        exit_code = vp.main([])

    assert exit_code == 1
    output = buf.getvalue()
    assert "STALE" in output
    assert "All packages in sync" not in output


# ---------------------------------------------------------------------------
# Test 4: DIRECTORY, in sync → exit 0, prints "All packages verified"
# ---------------------------------------------------------------------------

def test_in_sync_directory_install_exits_zero(tmp_path, monkeypatch):
    """Non-editable directory install with all files in sync: exit 0."""
    sp = tmp_path / "site-packages"
    pkg = "abw"
    src = tmp_path / "src"
    content = "version = '1'\n"
    _write_pkg_file(src, pkg, "__init__.py", content)
    _write_pkg_file(sp, pkg, "__init__.py", content)  # identical

    monkeypatch.setattr(vp, "SRC_ROOT", src)
    monkeypatch.setattr(vp, "VENV_ROOT", sp)
    monkeypatch.setattr(vp, "PACKAGES", ["abw"])

    buf = io.StringIO()
    with redirect_stdout(buf):
        exit_code = vp.main([])

    assert exit_code == 0
    assert "All packages verified" in buf.getvalue()


# ---------------------------------------------------------------------------
# Test 5: SOURCE_MISSING → exit 1
# ---------------------------------------------------------------------------

def test_source_missing_exits_one(tmp_path, monkeypatch):
    """SOURCE_MISSING (src dir does not exist) must exit 1."""
    sp = tmp_path / "site-packages"
    sp.mkdir()
    src = tmp_path / "src"
    src.mkdir()
    # Do NOT create src/abw

    monkeypatch.setattr(vp, "SRC_ROOT", src)
    monkeypatch.setattr(vp, "VENV_ROOT", sp)
    monkeypatch.setattr(vp, "PACKAGES", ["abw"])

    buf = io.StringIO()
    with redirect_stdout(buf):
        exit_code = vp.main([])

    assert exit_code == 1
    assert "SOURCE_MISSING" in buf.getvalue()


# ---------------------------------------------------------------------------
# Test 6: --fix copies stale files and exits 0
# ---------------------------------------------------------------------------

def test_fix_copies_stale_files(tmp_path, monkeypatch):
    """--fix copies stale installed files from src and exits 0."""
    sp = tmp_path / "site-packages"
    pkg = "abw"
    src = tmp_path / "src"
    _write_pkg_file(src, pkg, "__init__.py", "version = 'new'\n")
    _write_pkg_file(sp, pkg, "__init__.py", "version = 'old'\n")

    monkeypatch.setattr(vp, "SRC_ROOT", src)
    monkeypatch.setattr(vp, "VENV_ROOT", sp)
    monkeypatch.setattr(vp, "PACKAGES", ["abw"])

    buf = io.StringIO()
    with redirect_stdout(buf):
        exit_code = vp.main(["--fix"])

    assert exit_code == 0
    installed = (sp / pkg / "__init__.py").read_text(encoding="utf-8")
    assert installed == "version = 'new'\n"
