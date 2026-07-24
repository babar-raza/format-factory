"""TC-PA-041: calculate_oracle_coverage must derive oracle status from the registry.

Root cause guarded here: oracle-package.yaml's `status:` was a duplicate mirror of the
registry's `product_oracle_status` with no producer. The select-6 acquisition committed
`status: VERIFIED` into 6 packages whose oracles actually ran 1/5 PASS, and
calculate_oracle_coverage.py published that as `summary.verified_formats` — a false green.

TC-PA-041 removed the mirror field and repointed the coverage tool at the registry. These
tests prove the coverage tool now IGNORES any package-authored status (even if a revert or
re-onboard writes one back) and counts `verified_formats` from the authoritative registry.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml

_REPO = Path(__file__).resolve().parents[2]
_MOD_PATH = _REPO / "tools" / "oracle" / "calculate_oracle_coverage.py"

_spec = importlib.util.spec_from_file_location("calc_oracle_coverage_under_test", _MOD_PATH)
coverage = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(coverage)  # type: ignore[union-attr]


def _write_registry(root: Path, entries: dict[str, str]) -> Path:
    reg_dir = root / "oracle" / "registry"
    reg_dir.mkdir(parents=True, exist_ok=True)
    path = reg_dir / "format-oracle-registry.yaml"
    path.write_text(
        yaml.safe_dump({
            "format_oracles": [
                {"format_id": fid, "product_oracle_status": status}
                for fid, status in entries.items()
            ]
        }),
        encoding="utf-8",
    )
    return path


def test_status_comes_from_registry_not_package(tmp_path):
    """A package that (illegally) reintroduces status: VERIFIED must NOT flip coverage —
    the registry says CASES_DEFINED, so coverage must report CASES_DEFINED."""
    reg_path = _write_registry(tmp_path, {"ipynb": "CASES_DEFINED"})
    reg_status = coverage.load_registry_status(reg_path)

    # package mirror lies (the exact 1adfdc47 false-green)
    metrics = coverage.compute_format_coverage("ipynb", {"status": "VERIFIED"}, reg_status)

    assert metrics["status"] == "CASES_DEFINED"  # registry wins, package ignored


def test_verified_formats_counts_registry_not_package_mirror(tmp_path):
    """summary.verified_formats must count registry VERIFIED, regardless of package mirror."""
    reg_path = _write_registry(
        tmp_path, {"fodp": "VERIFIED", "ipynb": "CASES_DEFINED", "mtlx": "CASES_DEFINED"}
    )
    reg_status = coverage.load_registry_status(reg_path)

    # All three packages carry NO status field (the TC-PA-041 desired state) ...
    pkgs = {"fodp": {}, "ipynb": {}, "mtlx": {}}
    cov = {f: coverage.compute_format_coverage(f, p, reg_status) for f, p in pkgs.items()}
    verified = sum(1 for m in cov.values() if m["status"] == "VERIFIED")
    assert verified == 1  # only fodp, from the registry

    # ... and even if a package reintroduces status: VERIFIED, the count is unchanged.
    pkgs_drifted = {"fodp": {}, "ipynb": {"status": "VERIFIED"}, "mtlx": {"status": "VERIFIED"}}
    cov2 = {f: coverage.compute_format_coverage(f, p, reg_status) for f, p in pkgs_drifted.items()}
    verified2 = sum(1 for m in cov2.values() if m["status"] == "VERIFIED")
    assert verified2 == 1  # STILL only fodp — false-green is structurally impossible


def test_format_absent_from_registry_is_unknown_not_package_authored(tmp_path):
    """A package not in the registry reports UNKNOWN — never a package-authored status."""
    reg_path = _write_registry(tmp_path, {"fodp": "VERIFIED"})
    reg_status = coverage.load_registry_status(reg_path)

    metrics = coverage.compute_format_coverage("orphan", {"status": "VERIFIED"}, reg_status)
    assert metrics["status"] == "UNKNOWN"


def test_real_repo_verified_formats_matches_registry():
    """Live proof: on the real tree, verified_formats == count of registry VERIFIED."""
    reg_status = coverage.load_registry_status()
    packages = coverage.load_all_oracle_packages(coverage.ORACLE_ROOT)
    cov = {f: coverage.compute_format_coverage(f, p, reg_status) for f, p in packages.items()}
    verified = sum(1 for m in cov.values() if m["status"] == "VERIFIED")

    registry_verified = sum(1 for s in reg_status.values() if s == "VERIFIED")
    # every on-disk package that is VERIFIED in coverage must be VERIFIED in the registry
    assert verified == sum(
        1 for f in packages if reg_status.get(f) == "VERIFIED"
    )
    # and none of the 6 select-6 formats may show VERIFIED (they are CASES_DEFINED)
    for f in ("ipynb", "mtlx", "nrrd", "safetensors", "ubl", "xliff"):
        if f in cov:
            assert cov[f]["status"] == "CASES_DEFINED", f"{f} must not be false-green"
    assert registry_verified >= verified
