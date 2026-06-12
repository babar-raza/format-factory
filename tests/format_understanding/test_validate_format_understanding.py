"""
Tests for tools/format_understanding/validate_format_understanding.py

Read-only validator tests. No file writes.
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
VALIDATOR = REPO / "tools" / "format_understanding" / "validate_format_understanding.py"
FODS_PACK = str(REPO / "acquisition-packs" / "fods")
FODT_PACK = str(REPO / "acquisition-packs" / "fodt")


def run_validator(*extra_args):
    result = subprocess.run(
        [sys.executable, str(VALIDATOR)] + list(extra_args),
        capture_output=True, text=True, cwd=str(REPO)
    )
    return result


def test_fods_ful_validates_after_repair():
    """FODS FUL package must validate with 20+ facts and 20+ requirements after run050 repair."""
    r = run_validator("--format", "fods", "--pack", FODS_PACK,
                      "--min-facts", "20", "--min-requirements", "20")
    assert "FORMAT_UNDERSTANDING_VALIDATION: PASS" in r.stdout, (
        f"Expected PASS after repair:\n{r.stdout}\n{r.stderr}"
    )


def test_fodt_ful_validates_partial_after_repair():
    """FODT FUL package (partial) must validate with 15+ facts and 15+ requirements."""
    r = run_validator("--format", "fodt", "--pack", FODT_PACK,
                      "--min-facts", "15", "--min-requirements", "15",
                      "--allow-partial-product-readiness")
    assert "FORMAT_UNDERSTANDING_VALIDATION: PASS" in r.stdout, (
        f"Expected PASS after repair:\n{r.stdout}\n{r.stderr}"
    )


def test_too_few_facts_fails(tmp_path):
    """Requesting more facts than present must fail."""
    r = run_validator("--format", "fods", "--pack", FODS_PACK,
                      "--min-facts", "999", "--min-requirements", "1")
    assert "FORMAT_UNDERSTANDING_VALIDATION: FAIL" in r.stdout


def test_too_few_requirements_fails(tmp_path):
    """Requesting more reqs than present must fail."""
    r = run_validator("--format", "fods", "--pack", FODS_PACK,
                      "--min-facts", "1", "--min-requirements", "999")
    assert "FORMAT_UNDERSTANDING_VALIDATION: FAIL" in r.stdout


def test_fodt_fails_without_allow_partial(tmp_path):
    """A pack with partial:true product-readiness must fail without --allow-partial-product-readiness."""
    import shutil
    pack_dir = tmp_path / "fodt-partial"
    shutil.copytree(str(FODT_PACK), str(pack_dir))
    pr_path = pack_dir / "product-readiness.yaml"
    pr_txt = pr_path.read_text(encoding="utf-8")
    # Inject partial: true into the body to simulate pre-repair state
    pr_path.write_text(pr_txt + "\npartial: true\n", encoding="utf-8")
    r = run_validator("--format", "fodt", "--pack", str(pack_dir),
                      "--min-facts", "15", "--min-requirements", "15")
    assert "FORMAT_UNDERSTANDING_VALIDATION: FAIL" in r.stdout


def test_validator_writes_no_files(tmp_path):
    """Validator must not write any files."""
    import os
    before = set(os.listdir(str(REPO)))
    run_validator("--format", "fods", "--pack", FODS_PACK,
                  "--min-facts", "20", "--min-requirements", "20")
    after = set(os.listdir(str(REPO)))
    assert before == after, f"Validator wrote files: {after - before}"


def test_missing_pack_dir_fails():
    """Missing pack directory must fail gracefully."""
    r = run_validator("--format", "xyz", "--pack", "/nonexistent/pack/dir",
                      "--min-facts", "1", "--min-requirements", "1")
    assert r.returncode != 0 or "FAIL" in r.stdout or "Missing" in r.stdout
