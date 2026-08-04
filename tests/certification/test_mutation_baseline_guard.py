"""The mutation tester must refuse a red baseline (GAP-023).

A mutation is scored `killed` when the suite exits non-zero. So a suite that
exits non-zero on *unmutated* source scores every mutation killed and reports
100% -- a number that would be identical had no mutation ever been applied.

That is not hypothetical: it produced this program's first certification-gate
result, which was retracted the same day. These tests exist so the guard cannot
be removed without a failing test, and so the failure mode stays legible to
whoever reads them next.
"""

from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.certification.mutation_tester import (  # noqa: E402
    BaselineNotGreen,
    assert_baseline_green,
    run_mutation_testing,
)

PASSING_TEST = "def test_passes():\n    assert True\n"
FAILING_TEST = "def test_fails():\n    assert False\n"

TARGET_MODULE = textwrap.dedent(
    """
    def classify(value):
        if value > 10:
            return "big"
        return "small"
    """
).lstrip()


@pytest.fixture
def suite(tmp_path: Path) -> Path:
    directory = tmp_path / "suite"
    directory.mkdir()
    return directory


def test_green_baseline_is_accepted(suite: Path) -> None:
    (suite / "test_ok.py").write_text(PASSING_TEST, encoding="utf-8")

    assert_baseline_green(str(suite))  # must not raise


def test_red_baseline_is_refused(suite: Path) -> None:
    """The exact shape of the retracted gate: a suite that can never exit zero."""
    (suite / "test_ok.py").write_text(PASSING_TEST, encoding="utf-8")
    (suite / "test_broken.py").write_text(FAILING_TEST, encoding="utf-8")

    with pytest.raises(BaselineNotGreen) as raised:
        assert_baseline_green(str(suite))

    assert "unmutated source" in str(raised.value)


def test_red_baseline_stops_the_campaign_before_any_kill_rate(
    suite: Path, tmp_path: Path
) -> None:
    """Refusal must happen before mutations are scored, not be a warning beside them."""
    (suite / "test_broken.py").write_text(FAILING_TEST, encoding="utf-8")
    target = tmp_path / "target.py"
    target.write_text(TARGET_MODULE, encoding="utf-8")
    original = target.read_text(encoding="utf-8")

    with pytest.raises(BaselineNotGreen):
        run_mutation_testing(str(target), str(suite), max_mutations=2)

    assert target.read_text(encoding="utf-8") == original, (
        "the target was mutated despite the refusal; the baseline check must run first"
    )


def test_deselect_can_clear_an_environmental_failure(suite: Path) -> None:
    """--deselect is the sanctioned escape, and it must actually work.

    Real use: tests asserting the package lives in site-packages fail under an
    editable install and cannot be killed by any source mutation. Without a
    working deselect the only options are a vacuous run or no run at all.
    """
    (suite / "test_ok.py").write_text(PASSING_TEST, encoding="utf-8")
    (suite / "test_env.py").write_text(FAILING_TEST, encoding="utf-8")

    with pytest.raises(BaselineNotGreen):
        assert_baseline_green(str(suite))

    assert_baseline_green(str(suite), ("test_env.py::test_fails",))


def test_cli_exits_2_on_red_baseline(suite: Path, tmp_path: Path) -> None:
    (suite / "test_broken.py").write_text(FAILING_TEST, encoding="utf-8")
    target = tmp_path / "target.py"
    target.write_text(TARGET_MODULE, encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "tools" / "certification" / "mutation_tester.py"),
            "--target",
            str(target),
            "--tests",
            str(suite),
            "--max-mutations",
            "1",
        ],
        capture_output=True,
        text=True,
        timeout=300,
    )

    assert completed.returncode == 2, completed.stdout + completed.stderr
    assert "BASELINE NOT GREEN" in completed.stderr
