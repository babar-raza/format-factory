"""
test_package_install_proof_wave1.py -- Source-tree importability check (Wave 1).

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-1

HONESTY NOTE (GAP-FORENSIC-001, 2026-07-15): despite its filename, this test
does NOT prove pip-install behavior. It inserts src/python/ into sys.path and
checks that format modules import from the SOURCE TREE — a fast in-repo smoke
check, nothing more. The real package-install proof (wheel build -> pip install
into an ephemeral venv -> import -> API smoke) is:

    tests/python/packaging/test_package_install_proof_all_formats.py

run via `python tools/run_package_install_proof.py` (the /package-install-proof
skill) and enforced by governance validator V226. The filename is kept to
preserve test-history continuity; treat "install_proof" in this filename as a
historical misnomer.
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

# 19 format modules (csv excluded due to stdlib name collision)
_FORMAT_MODULES = [
    ("abw.abw_codec", "load"),
    ("dif.dif_parser", "parse_dif"),
    ("fodg.fodg_codec", "load"),
    ("fodp.fodp_codec", "load"),
    ("fods.parser", "parse_fods"),
    ("fodt.parser", "parse_fodt"),
    ("gnumeric.gnumeric_codec", "load"),
    ("ndjson.ndjson_codec", "load_ndjson"),
    ("ods.ods_parser", "parse_ods"),
    ("odt.odt_parser", "parse_odt"),
    ("pbm.pbm_parser", "parse_pbm"),
    ("pgm.pgm_parser", "parse_pgm"),
    ("ppm.ppm_parser", "parse_ppm"),
    ("qoi.qoi_parser", "parse_qoi"),
    ("sylk.sylk_parser", "parse_sylk"),
    ("toml.toml_codec", "load_toml"),
    ("tsv.tsv_parser", "parse_tsv"),
    ("xcf.xcf_parser", "parse_xcf"),
    ("zst.zst_codec", "compress_bytes"),
]


def test_all_format_modules_importable():
    """Every non-csv Python format module must be importable."""
    failed = []
    for mod_path, func_name in _FORMAT_MODULES:
        try:
            mod = importlib.import_module(mod_path)
            assert hasattr(mod, func_name), f"{mod_path} missing {func_name}"
        except Exception as exc:
            failed.append(f"{mod_path}: {exc}")
    assert not failed, "Import failures:\n" + "\n".join(failed)


def test_csv_module_importable():
    """CSV module importable via full repo path (stdlib collision)."""
    sys.path.insert(0, str(_REPO))
    mod = importlib.import_module("src.python.csv.csv_parser")
    assert hasattr(mod, "parse_csv_strict")


def test_pyproject_toml_exists_for_all_packaged_formats():
    """All 20 formats should have pyproject.toml."""
    expected = [
        "abw", "csv", "dif", "fodg", "fodp", "fods", "fodt",
        "gnumeric", "ndjson", "ods", "odt", "pbm", "pgm", "ppm",
        "qoi", "sylk", "toml", "tsv", "xcf", "zst",
    ]
    missing = []
    for fmt in expected:
        pp = _REPO / "src" / "python" / fmt / "pyproject.toml"
        if not pp.exists():
            missing.append(fmt)
    assert not missing, f"Missing pyproject.toml: {missing}"


def test_format_count():
    """We should cover all 20 Python format modules."""
    assert len(_FORMAT_MODULES) == 19  # + csv tested separately = 20
