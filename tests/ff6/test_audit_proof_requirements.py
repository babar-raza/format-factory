"""Tests for the proof-requirement audit instrument.

This tool reported two false findings on its very first run against real data --
class-qualified selectors read as missing tests, and a conditionally-skipped
parametrized case read as a wholly skipped one. A false positive here is
expensive: it argues for demoting an obligation that is actually fine. These
tests pin both directions.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from tools.ff6 import audit_proof_requirements as audit


@pytest.fixture
def fixture_format(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Build a self-contained format: register, ledger, and test files."""

    def build(
        *,
        selectors: list[str],
        required_tests: list[str] | None = None,
        test_body: str,
        test_filename: str = "test_thing.py",
        imports: str = "from format_factory.demo import thing",
    ) -> dict:
        register_dir = tmp_path / "register"
        evidence_dir = tmp_path / "evidence"
        tests_dir = tmp_path / "tests" / "python" / "demo"
        for directory in (register_dir, evidence_dir, tests_dir):
            directory.mkdir(parents=True, exist_ok=True)

        (register_dir / "demo.yaml").write_text(
            yaml.safe_dump(
                {
                    "obligations": [
                        {
                            "obligation_id": "OBL-1",
                            "level": "MUST",
                            "required_tests": required_tests or [],
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        (evidence_dir / "demo.yaml").write_text(
            yaml.safe_dump(
                {
                    "obligations": [
                        {
                            "obligation_id": "OBL-1",
                            "capability_id": "DEMO-001",
                            "status": "implemented",
                            "positive_test_selectors": selectors,
                            "negative_test_selectors": [],
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        (tests_dir / test_filename).write_text(
            f"{imports}\nimport pytest\n\n{test_body}\n", encoding="utf-8"
        )

        monkeypatch.setattr(audit, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(audit, "REGISTER_DIR", register_dir)
        monkeypatch.setattr(audit, "EVIDENCE_DIR", evidence_dir)
        return audit.audit_format("demo")

    return build


def _issues(result: dict) -> list[str]:
    return result["findings"][0]["issues"]


# ── The two false positives this tool actually produced ────────────────────


def test_class_qualified_selector_is_not_reported_missing(fixture_format) -> None:
    """`file::Class::method` is a normal pytest selector, not a missing test.

    Reading the whole remainder after the first `::` as the function name made
    every class-based test look absent, which nearly caused a real obligation to
    be demoted on a tool bug.
    """
    result = fixture_format(
        selectors=["tests/python/demo/test_thing.py::TestGroup::test_inside_a_class"],
        test_body="class TestGroup:\n    def test_inside_a_class(self):\n        assert True",
    )
    assert not any(i.startswith("MISSING_TEST") for i in _issues(result))


def test_parametrized_selector_is_not_reported_missing(fixture_format) -> None:
    result = fixture_format(
        selectors=["tests/python/demo/test_thing.py::test_p[case-1]"],
        test_body="def test_p():\n    assert True",
    )
    assert not any(i.startswith("MISSING_TEST") for i in _issues(result))


def test_conditional_skip_is_distinguished_from_a_dead_test(fixture_format) -> None:
    """One skipped branch of a parametrized test is weaker evidence, not absent
    evidence. Conflating them overstates the finding."""
    result = fixture_format(
        selectors=["tests/python/demo/test_thing.py::test_partial"],
        test_body=(
            "def test_partial(value=1):\n"
            "    if not value:\n"
            "        pytest.skip('only this branch')\n"
            "    assert True"
        ),
    )
    issues = _issues(result)
    assert any(i.startswith("PARTIAL_SKIP_PATH_IN_SELECTOR") for i in issues)
    assert not any(i.startswith("SKIPPED_TEST_AS_PROOF") for i in issues)


# ── The findings it must still catch ───────────────────────────────────────


def test_unconditionally_skipped_test_is_flagged(fixture_format) -> None:
    result = fixture_format(
        selectors=["tests/python/demo/test_thing.py::test_dead"],
        test_body="def test_dead():\n    pytest.skip('always')\n    assert True",
    )
    assert any(i.startswith("SKIPPED_TEST_AS_PROOF") for i in _issues(result))


def test_skip_decorated_test_is_flagged(fixture_format) -> None:
    result = fixture_format(
        selectors=["tests/python/demo/test_thing.py::test_marked"],
        test_body="@pytest.mark.skip('nope')\ndef test_marked():\n    assert True",
    )
    assert any(i.startswith("SKIPPED_TEST_AS_PROOF") for i in _issues(result))


def test_genuinely_absent_test_is_flagged(fixture_format) -> None:
    result = fixture_format(
        selectors=["tests/python/demo/test_thing.py::test_does_not_exist"],
        test_body="def test_something_else():\n    assert True",
    )
    assert any(i.startswith("MISSING_TEST") for i in _issues(result))


def test_shadow_package_selector_is_flagged(fixture_format) -> None:
    """A test file importing only the legacy package is not shipped-namespace
    evidence, however green it is."""
    result = fixture_format(
        selectors=["tests/python/demo/test_thing.py::test_ok"],
        test_body="def test_ok():\n    assert True",
        imports="from demo.legacy import thing",
    )
    assert any(i.startswith("SHADOW_PACKAGE_SELECTOR") for i in _issues(result))


def test_missing_file_is_flagged(fixture_format) -> None:
    result = fixture_format(
        selectors=["tests/python/demo/test_absent.py::test_ok"],
        test_body="def test_ok():\n    assert True",
    )
    assert any(i.startswith("MISSING_FILE") for i in _issues(result))


def test_obligation_with_no_selectors_is_flagged(fixture_format) -> None:
    result = fixture_format(
        selectors=[], test_body="def test_ok():\n    assert True"
    )
    assert "NO_SELECTORS" in _issues(result)


def test_more_declared_dimensions_than_selectors_is_flagged(fixture_format) -> None:
    """The "matrix with one axis tested" shape that motivated the whole rule."""
    result = fixture_format(
        selectors=["tests/python/demo/test_thing.py::test_ok"],
        required_tests=["Matrix by type and encoding; plus a negative case."],
        test_body="def test_ok():\n    assert True",
    )
    assert any(
        i.startswith("FEWER_SELECTORS_THAN_DECLARED_DIMENSIONS") for i in _issues(result)
    )


# ── A clean obligation reports clean ───────────────────────────────────────


def test_clean_obligation_has_no_issues(fixture_format) -> None:
    result = fixture_format(
        selectors=["tests/python/demo/test_thing.py::test_ok"],
        required_tests=["One dimension."],
        test_body="def test_ok():\n    assert True",
    )
    assert _issues(result) == []
    assert result["findings"][0]["audit_ready"] is True
    assert result["mechanically_clean"] == 1


def test_result_states_it_is_not_a_verdict(fixture_format) -> None:
    """A clean mechanical result must not read as "obligation proven"."""
    result = fixture_format(
        selectors=["tests/python/demo/test_thing.py::test_ok"],
        test_body="def test_ok():\n    assert True",
    )
    assert "does NOT mean" in result["truth_boundary"]


# ── Against the real repository ────────────────────────────────────────────


@pytest.mark.parametrize("format_id", ["ipynb", "nrrd"])
def test_real_formats_audit_without_error(format_id: str) -> None:
    result = audit.audit_format(format_id)
    assert result["obligations"] > 0
    assert result["mechanically_clean"] + result["with_issues"] == result["obligations"]
