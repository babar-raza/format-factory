"""Tests for package_install_proof.py — package install proof helper."""

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "tools" / "supervisor"))

from package_install_proof import (
    run_import_proof,
    run_proof,
    check_wheel_exists,
    run_dotnet_build_check,
    generate_blocker_report,
    PYTHON_PRODUCTS,
    DOTNET_PRODUCTS,
)


def test_python_products_has_known_formats():
    assert "fods" in PYTHON_PRODUCTS
    assert "fodt" in PYTHON_PRODUCTS
    assert "pbm" in PYTHON_PRODUCTS
    assert "ppm" in PYTHON_PRODUCTS
    assert "sylk" in PYTHON_PRODUCTS
    assert "zst" in PYTHON_PRODUCTS


def test_python_products_have_import_names():
    for fid, info in PYTHON_PRODUCTS.items():
        assert "import" in info
        assert "package" in info
        assert len(info["import"]) > 0


def test_run_import_proof_unknown_format(tmp_path):
    result = run_import_proof(sys.executable, "nonexistent_format", tmp_path)
    assert result["status"] == "SKIPPED"


def test_run_proof_with_known_format(tmp_path):
    result = run_proof(sys.executable, ["fods"], tmp_path)
    assert "results" in result
    assert len(result["results"]) == 1
    assert result["formats_tested"] == 1
    # May pass or fail depending on environment, but should not error
    assert result["results"][0]["status"] in ("PASS", "FAIL", "ERROR")


def test_run_proof_empty_list(tmp_path):
    result = run_proof(sys.executable, [], tmp_path)
    assert result["formats_tested"] == 0
    assert result["passed"] == 0
    assert result["failed"] == 0


# --- v3 (R101): .NET product mapping, wheel check, blocker report ---


def test_dotnet_products_mapping():
    assert "fods" in DOTNET_PRODUCTS
    assert "fodt" in DOTNET_PRODUCTS
    assert "netpbm" in DOTNET_PRODUCTS


def test_check_wheel_missing(tmp_path):
    result = check_wheel_exists("fods", tmp_path)
    assert result["status"] == "MISSING"


def test_check_wheel_found(tmp_path):
    artifacts = tmp_path / ".local" / "package-artifacts"
    artifacts.mkdir(parents=True)
    (artifacts / "format_factory_fods-0.1.0.dev0.whl").write_text("fake")
    result = check_wheel_exists("fods", tmp_path)
    assert result["status"] == "FOUND"


def test_dotnet_build_check_missing_project(tmp_path):
    result = run_dotnet_build_check("fods", tmp_path, tmp_path / "logs")
    assert result["status"] == "SKIPPED"


def test_dotnet_build_check_unknown_format(tmp_path):
    result = run_dotnet_build_check("nonexistent", tmp_path, tmp_path / "logs")
    assert result["status"] == "SKIPPED"


def test_generate_blocker_report_no_blockers():
    proof = {"timestamp": "now", "formats_tested": 2, "passed": 2, "failed": 0, "results": [
        {"format": "fods", "status": "PASS"},
        {"format": "fodt", "status": "PASS"},
    ]}
    report = generate_blocker_report(proof)
    assert "No blockers" in report


def test_generate_blocker_report_with_blockers():
    proof = {"timestamp": "now", "formats_tested": 2, "passed": 1, "failed": 1, "results": [
        {"format": "fods", "status": "PASS"},
        {"format": "fodt", "status": "FAIL", "error": "import failed"},
    ]}
    report = generate_blocker_report(proof)
    assert "Blockers" in report
    assert "fodt" in report
    assert "import failed" in report
