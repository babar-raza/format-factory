"""Every managed distribution carries the canonical reproducible-build backend.

Each distribution needs its own copy of the PEP 517 adapter -- `backend-path` is
resolved relative to the package directory and every distribution here must stay
independently publishable, so a shared import is not available at build time.
Copies without a source of truth drift, and these had: the adapter existed as
three different formattings across the four packages that carried it, while
`core` and `safetensors` had none and failed the reproducible-build gate with
differing sdists on consecutive builds.

`core` matters most: it is the shared dependency of all six libraries, so its
sdist being irreproducible undermined the claim for every distribution that
passed on its own.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.packaging import sync_build_backends as sync  # noqa: E402


def test_no_managed_package_has_drifted() -> None:
    """The real check, against the real tree. This is the regression guard."""
    problems = sync.check()

    assert problems == [], "build-backend drift:\n  " + "\n  ".join(problems)


def test_core_is_managed() -> None:
    """core is every library's dependency; excluding it would hollow out the gate."""
    assert "core" in sync.MANAGED_PACKAGES


@pytest.mark.parametrize("name", sync.MANAGED_PACKAGES)
def test_backend_is_byte_identical_to_the_template(name: str) -> None:
    canonical = sync.TEMPLATE.read_text(encoding="utf-8")
    backend = sync.package_dir(name) / sync.BACKEND_FILENAME

    assert backend.read_text(encoding="utf-8") == canonical


@pytest.mark.parametrize("name", sync.MANAGED_PACKAGES)
def test_sdist_ships_the_backend_it_selects(name: str) -> None:
    """A distribution that selects an in-tree backend without shipping it in the
    sdist cannot be built from that sdist -- `python -m build` fails at
    "Building wheel from sdist" with "Backend '_build_backend' is not
    available". Both core and safetensors were in exactly that state after the
    backend was added and before MANIFEST.in was."""
    manifest = sync.package_dir(name) / "MANIFEST.in"

    assert manifest.exists(), f"{name} has no MANIFEST.in"
    assert sync.BACKEND_FILENAME in manifest.read_text(encoding="utf-8")


# ── The check must be able to fail, or the tests above certify nothing ──────


def _fake_package(root: Path, name: str, *, backend: str | None, manifest: bool) -> None:
    directory = root / "src" / "python" / name
    directory.mkdir(parents=True)
    (directory / "pyproject.toml").write_text(
        '[build-system]\nbuild-backend = "_build_backend"\nbackend-path = ["."]\n',
        encoding="utf-8",
    )
    if backend is not None:
        (directory / sync.BACKEND_FILENAME).write_text(backend, encoding="utf-8")
    if manifest:
        (directory / "MANIFEST.in").write_text(
            f"include {sync.BACKEND_FILENAME}\n", encoding="utf-8"
        )


@pytest.fixture
def fake_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(sync, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(sync, "MANAGED_PACKAGES", ("alpha",))
    return tmp_path


def test_check_detects_a_drifted_backend(fake_repo: Path) -> None:
    canonical = sync.TEMPLATE.read_text(encoding="utf-8")
    _fake_package(fake_repo, "alpha", backend=canonical + "# edited\n", manifest=True)

    problems = sync.check()

    assert any("drifted" in problem for problem in problems), problems


def test_check_detects_an_absent_backend(fake_repo: Path) -> None:
    _fake_package(fake_repo, "alpha", backend=None, manifest=True)

    problems = sync.check()

    assert any("absent" in problem for problem in problems), problems


def test_check_detects_a_sdist_that_omits_the_backend(fake_repo: Path) -> None:
    canonical = sync.TEMPLATE.read_text(encoding="utf-8")
    _fake_package(fake_repo, "alpha", backend=canonical, manifest=False)

    problems = sync.check()

    assert any("MANIFEST" in problem for problem in problems), problems
