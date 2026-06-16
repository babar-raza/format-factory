"""Evidence test conftest — auto-skip in CI where .local/ artifacts are absent.

Evidence tests validate local build artifacts in .local/ (manifests, packages, review bundles).
These files are gitignored and only exist in the developer's working environment.

In CI (GitHub Actions), .local/ is not populated, so these tests are skipped automatically.
Run locally without CI=true to execute evidence tests against your local artifacts.
"""
import os
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_LOCAL_DIR = _REPO_ROOT / ".local"

_SKIP_REASON = (
    "evidence tests require .local/ artifacts (gitignored); "
    "set CI != 'true' and populate .local/ to run locally"
)


def pytest_collection_modifyitems(config, items):
    """Skip evidence tests in CI where .local/ artifacts are absent.

    Evaluates CI env and .local/ presence at collection time (not import time)
    to avoid caching stale values when other tests manipulate os.environ.
    """
    in_ci = os.getenv("CI") == "true"
    local_populated = _LOCAL_DIR.exists() and any(_LOCAL_DIR.iterdir())
    if not in_ci and local_populated:
        return
    skip_marker = pytest.mark.skip(reason=_SKIP_REASON)
    for item in items:
        fspath = str(item.fspath).replace("\\", "/")
        if "/tests/evidence/" in fspath:
            item.add_marker(skip_marker)
