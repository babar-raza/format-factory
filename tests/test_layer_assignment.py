"""Validates that the root conftest.py marker auto-assignment is correct.

Uses subprocess to run pytest --collect-only with marker filters and
verifies the expected test counts and assignments.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# Allow direct import of runner internals for unit-level testing
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from test_runner import parse_junitxml, run_and_collect  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
PYTHON_EXE = sys.executable

# Baseline and tolerance are read from registry/test-layer-baseline.json dynamically.
# Update that file (not this constant) when the count drifts beyond tolerance.
# Fallback values used only if the registry file is missing or malformed.
_BASELINE_FALLBACK = 16473
_TOLERANCE_FALLBACK = 1000


def _read_baseline_from_registry() -> tuple[int, int]:
    """Read baseline total and tolerance from registry/test-layer-baseline.json.

    Returns (baseline_total, tolerance). Falls back to hard-coded defaults with a
    stderr warning if the registry file is missing or malformed.
    """
    registry_path = REPO_ROOT / "registry" / "test-layer-baseline.json"
    try:
        import json as _json
        data = _json.loads(registry_path.read_text(encoding="utf-8"))
        baseline = data["baseline"]["total_tests"]
        tolerance = data["baseline"]["tolerance"]
        return int(baseline), int(tolerance)
    except (FileNotFoundError, KeyError, ValueError, TypeError) as exc:
        import sys as _sys
        print(
            f"WARNING: could not read registry/test-layer-baseline.json ({exc}); "
            f"using fallback baseline={_BASELINE_FALLBACK}, tolerance={_TOLERANCE_FALLBACK}",
            file=_sys.stderr,
        )
        return _BASELINE_FALLBACK, _TOLERANCE_FALLBACK


def _collect_count(marker_expr: str | None = None) -> int:
    """Run pytest --collect-only and return the count of collected tests."""
    cmd = [PYTHON_EXE, "-m", "pytest", "--collect-only", "-q"]
    if marker_expr:
        cmd.extend(["-m", marker_expr])
    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=120,
    )
    # Parse "N tests collected" or "N/M tests collected (K deselected)"
    for line in result.stdout.strip().splitlines()[-3:]:
        if "tests collected" in line or "test collected" in line:
            # Extract first number
            parts = line.split()
            for part in parts:
                if part.isdigit():
                    return int(part)
                if "/" in part:
                    return int(part.split("/")[0])
    return 0


def _collect_paths(marker_expr: str) -> list[str]:
    """Collect test node IDs for a given marker expression."""
    cmd = [PYTHON_EXE, "-m", "pytest", "--collect-only", "-q", "-m", marker_expr]
    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=120,
    )
    paths = []
    for line in result.stdout.strip().splitlines():
        if "::" in line and not line.startswith(" "):
            paths.append(line.strip())
    return paths


class TestLayer0Structural:
    """Layer 0 should contain only structural/health tests."""

    def test_layer0_contains_health_check(self):
        paths = _collect_paths("layer0")
        health_tests = [p for p in paths if "test_health_check" in p]
        assert len(health_tests) > 0, "layer0 must contain test_health_check tests"

    def test_layer0_contains_smoke(self):
        paths = _collect_paths("layer0")
        smoke_tests = [p for p in paths if "public_api_smoke" in p]
        assert len(smoke_tests) > 0, "layer0 must contain public_api_smoke tests"

    def test_layer0_is_small(self):
        count = _collect_count("layer0")
        assert count < 30, f"layer0 should have <30 tests (structural only), got {count}"
        assert count > 0, "layer0 must have at least 1 test"

    def test_layer0_no_format_tests(self):
        paths = _collect_paths("layer0")
        format_tests = [
            p for p in paths
            if "tests/python/" in p.replace("\\", "/")
            and "public_api_smoke" not in p
        ]
        assert len(format_tests) == 0, (
            f"layer0 should not contain format tests, found: {format_tests[:5]}"
        )


class TestLayer1Focused:
    """Layer 1 should contain format-specific unit tests."""

    def test_layer1_contains_format_tests(self):
        paths = _collect_paths("layer1")
        tsv_tests = [p for p in paths if "tests/python/tsv" in p.replace("\\", "/")]
        assert len(tsv_tests) > 0, "layer1 must contain TSV format tests"

    def test_layer1_no_supervisor_tests(self):
        paths = _collect_paths("layer1")
        supervisor_tests = [
            p for p in paths if "tests/supervisor" in p.replace("\\", "/")
        ]
        assert len(supervisor_tests) == 0, (
            f"layer1 should not contain supervisor tests, found {len(supervisor_tests)}"
        )


class TestLayer3Integration:
    """Layer 3 should contain supervisor, evidence, and capability tests."""

    def test_layer3_contains_supervisor_tests(self):
        paths = _collect_paths("layer3")
        sup_tests = [p for p in paths if "tests/supervisor" in p.replace("\\", "/")]
        assert len(sup_tests) > 0, "layer3 must contain supervisor tests"

    def test_layer3_contains_evidence_tests(self):
        paths = _collect_paths("layer3")
        ev_tests = [p for p in paths if "tests/evidence" in p.replace("\\", "/")]
        assert len(ev_tests) > 0, "layer3 must contain evidence tests"


class TestLayer4Golden:
    """Layer 4 should contain roundtrip and export tests."""

    def test_layer4_contains_roundtrip_tests(self):
        paths = _collect_paths("layer4")
        rt_tests = [p for p in paths if "roundtrip" in p.lower()]
        assert len(rt_tests) > 0, "layer4 must contain roundtrip tests"


class TestLayer6Full:
    """Layer 6 must equal the full test suite."""

    def test_layer6_equals_total(self):
        total = _collect_count()
        layer6 = _collect_count("layer6")
        assert layer6 == total, f"layer6 ({layer6}) must equal total ({total})"


class TestLayerCompleteness:
    """Every test must have exactly one home layer (plus layer6)."""

    @pytest.mark.timeout(600)
    def test_all_layers_sum_to_total(self):
        """Every test must be assigned a home layer (layer0, layer1, layer3, layer4, or layer5).

        Redesigned from 6 sequential _collect_count() calls to 2, eliminating the
        inter-call race window where the supervisor pipeline can add test files between
        measurements. Two calls: one for total, one for all home-layer markers combined.
        """
        total = _collect_count()
        home_layers_expr = "layer0 or layer1 or layer3 or layer4 or layer5"
        marked = _collect_count(home_layers_expr)
        assert marked == total, (
            f"Not all tests have a home layer: marked={marked}, total={total}. "
            f"Delta {total - marked} tests missing from home-layer markers. "
            f"Check tests/conftest.py pytest_collection_modifyitems hook."
        )

    def test_bare_pytest_count_near_baseline(self):
        """Bare pytest count should be near baseline (within tolerance).

        Baseline and tolerance are read from registry/test-layer-baseline.json.
        To fix a drift failure: update registry/test-layer-baseline.json,
        do NOT update the hard-coded fallback constants in this file.
        """
        baseline, tolerance = _read_baseline_from_registry()
        total = _collect_count()
        assert abs(total - baseline) < tolerance, (
            f"Total tests ({total}) differs from baseline ({baseline}) "
            f"by more than {tolerance}. "
            f"Update registry/test-layer-baseline.json baseline.total_tests to {total}."
        )


class TestRunnerIntegration:
    """Validate the test_runner.py dry-run output."""

    def test_runner_layer0_dry_run(self):
        cmd = [
            PYTHON_EXE, "tools/test_runner.py",
            "--layer", "0", "--dry-run",
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=30,
        )
        data = json.loads(result.stdout)
        assert data["layer"] == 0
        assert data["layer_name"] == "structural"
        assert "layer0" in data["marker_expr"]

    def test_runner_auto_dry_run(self):
        cmd = [
            PYTHON_EXE, "tools/test_runner.py",
            "--auto", "--dry-run",
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=30,
        )
        data = json.loads(result.stdout)
        assert "layer" in data
        assert "layer_name" in data
        assert "layer_reason" in data
        assert data["dry_run"] is True

    def test_runner_shard_dry_run(self):
        cmd = [
            PYTHON_EXE, "tools/test_runner.py",
            "--layer", "6", "--shard", "1/4", "--dry-run",
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=30,
        )
        data = json.loads(result.stdout)
        assert data["shard"] == "1/4"
        assert "tests/python" in data["command"].replace("\\", "/").lower()


class TestPathSeparatorRegression:
    """Verify conftest path patterns work on both Windows and POSIX paths."""

    @staticmethod
    def _classify(fspath: str) -> int:
        """Reproduce conftest.py layer classification logic for a given path."""
        fspath = fspath.replace("\\", "/")
        name = fspath.rsplit("/", 1)[-1].lower() if "/" in fspath else fspath.lower()
        golden_kw = ("roundtrip", "cross_format", "cross-format", "dogfood")
        if "test_health_check" in fspath or "public_api_smoke" in fspath:
            return 0
        if any(kw in fspath.lower() or kw in name for kw in golden_kw):
            return 4
        if "/tests/python/" in fspath:
            return 1
        if ("/tests/supervisor/" in fspath or "/tests/evidence/" in fspath
                or "/tests/capability_layer/" in fspath):
            return 3
        return 5

    def test_path_matching_windows_style(self):
        assert self._classify(
            r"C:\Users\dev\repo\tests\python\tsv\test_foo.py"
        ) == 1
        assert self._classify(
            r"C:\Users\dev\repo\tests\supervisor\test_bar.py"
        ) == 3
        assert self._classify(
            r"C:\Users\dev\repo\tests\test_health_check.py"
        ) == 0

    def test_path_matching_posix_style(self):
        assert self._classify(
            "/home/runner/work/repo/tests/python/tsv/test_foo.py"
        ) == 1
        assert self._classify(
            "/home/runner/work/repo/tests/supervisor/test_bar.py"
        ) == 3
        assert self._classify(
            "/home/runner/work/repo/tests/test_health_check.py"
        ) == 0


class TestCumulativity:
    """Verify that higher layers include lower-layer tests (cumulative property)."""

    def test_layer1_format_includes_l0_files(self):
        """L1+format dry-run must include L0 test file paths in the command."""
        cmd = [
            PYTHON_EXE, "tools/test_runner.py",
            "--layer", "1", "--format", "tsv", "--dry-run",
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=30,
        )
        data = json.loads(result.stdout)
        command_lower = data["command"].replace("\\", "/").lower()
        assert "test_health_check" in command_lower, (
            "L1+format must include L0 test_health_check (cumulativity)"
        )
        assert "test_pige_public_api_smoke" in command_lower, (
            "L1+format must include L0 public_api_smoke (cumulativity)"
        )
        assert "tests/python/tsv" in command_lower, (
            "L1+format must include format test directory"
        )


class TestRunnerReliability:
    """Regression tests for test_results_reliable field (TC-LAYER-H010 guard).

    These tests protect against future refactors silently breaking the
    false-zero guard in run_and_collect(). They use both direct function calls
    and a real subprocess runner call to cover the full code path.
    """

    # --- Unit-level: parse_junitxml sentinel behavior ---

    def test_parse_junitxml_missing_file_returns_sentinel(self):
        """parse_junitxml must return _parse_error sentinel for missing files."""
        result = parse_junitxml("/nonexistent/path/that/does/not/exist.xml")
        assert "_parse_error" in result, (
            "parse_junitxml must return _parse_error key on FileNotFoundError"
        )
        assert result["_parse_error"] == "junitxml file not found"
        assert result["passed"] == 0
        assert result["failed"] == 0

    def test_parse_junitxml_malformed_xml_returns_sentinel(self, tmp_path):
        """parse_junitxml must return _parse_error sentinel for malformed XML."""
        bad_xml = tmp_path / "bad.xml"
        bad_xml.write_text("this is not xml <<>>")
        result = parse_junitxml(str(bad_xml))
        assert "_parse_error" in result, (
            "parse_junitxml must return _parse_error key on ET.ParseError"
        )
        assert result["_parse_error"] == "junitxml parse failed"

    def test_parse_junitxml_valid_empty_xml_no_sentinel(self, tmp_path):
        """parse_junitxml must NOT return _parse_error on valid (empty) XML."""
        valid_xml = tmp_path / "empty.xml"
        valid_xml.write_text('<?xml version="1.0"?><testsuites></testsuites>')
        result = parse_junitxml(str(valid_xml))
        assert "_parse_error" not in result, (
            "parse_junitxml must not return _parse_error on valid XML"
        )
        assert result["passed"] == 0

    def test_parse_junitxml_valid_nonempty_xml_no_sentinel(self, tmp_path):
        """parse_junitxml must parse a real junitxml correctly."""
        valid_xml = tmp_path / "result.xml"
        valid_xml.write_text(
            '<?xml version="1.0"?>'
            '<testsuite tests="3" failures="1" errors="0" skipped="0">'
            '<testcase name="a"/><testcase name="b"/>'
            '<testcase name="c"><failure>fail</failure></testcase>'
            '</testsuite>'
        )
        result = parse_junitxml(str(valid_xml))
        assert "_parse_error" not in result
        assert result["passed"] == 2
        assert result["failed"] == 1

    # --- Integration-level: test_results_reliable in real runner output ---

    def test_reliable_true_on_passing_l0_run(self, tmp_path):
        """Runner JSON must include test_results_reliable: true on a passing L0 run."""
        json_out = tmp_path / "result.json"
        cmd = [
            PYTHON_EXE, "tools/test_runner.py",
            "--layer", "0",
            "--json-out", str(json_out),
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=60,
        )
        assert result.returncode == 0, (
            f"L0 run must exit 0; got {result.returncode}.\nstderr: {result.stderr}"
        )
        assert json_out.exists(), "Runner must write JSON output file"
        data = json.loads(json_out.read_text())
        assert "test_results_reliable" in data, (
            "Runner JSON must contain test_results_reliable field"
        )
        assert data["test_results_reliable"] is True, (
            f"test_results_reliable must be true for passing L0 run, got: {data}"
        )
        assert data["test_results"]["passed"] > 0, (
            "L0 run must record at least 1 passing test"
        )

    def test_reliable_false_when_pytest_exits_nonzero_with_zero_tests(self):
        """run_and_collect must set test_results_reliable=False when pytest fails with 0 tests.

        This fires via either:
        (a) _parse_error sentinel: junitxml absent (FileNotFoundError in parse_junitxml), OR
        (b) returncode != 0 AND total_tests == 0 (pytest wrote empty junitxml or none at all).

        Both paths produce test_results_reliable=False. The unit test
        test_parse_junitxml_missing_file_returns_sentinel covers path (a) in isolation.
        """
        # Simulate by passing a junitxml path to a failing pytest run
        nonexistent_dir = str(REPO_ROOT / "tests" / "_nonexistent_for_reliability_test")
        cmd_fail = [
            sys.executable, "-m", "pytest",
            nonexistent_dir,
            "-q",
        ]
        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False, prefix="ff-test-") as f:
            junitxml_path = f.name
        # Delete the file so parse_junitxml will get FileNotFoundError
        os.unlink(junitxml_path)
        try:
            result = run_and_collect(
                cmd_fail + ["--junitxml", junitxml_path],
                layer=6,
                layer_reason="reliability test: forced failure",
            )
            assert result["test_results_reliable"] is False, (
                "test_results_reliable must be False when junitxml is absent "
                f"and pytest exits non-zero. Got: {result}"
            )
        finally:
            try:
                os.unlink(junitxml_path)
            except OSError:
                pass
