"""
test_python_release_manifests.py — Validates Python FOSS release manifests.

Sprint: FORMAT-FACTORY-R21-FOSS-RELEASE-READINESS-AND-GATE11-COMMERCIAL-PREEXECUTION-TRAIN-001
"""

from pathlib import Path
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MANIFESTS_DIR = REPO_ROOT / "release-manifests" / "python-foss"
MATRIX_PATH = MANIFESTS_DIR / "_matrix.yaml"

sys.path.insert(0, "C:/Users/prora/AppData/Roaming/Python/Python313/site-packages")

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

EXPECTED_FORMATS = ["zst", "fodp", "fodg", "gnumeric", "abw"]
REQUIRED_MANIFEST_FIELDS = [
    "format_id", "package_name", "module_import", "version",
    "source_path", "tests_path", "examples_path",
    "acquisition_gates_passed", "unsupported_capabilities",
    "security_limits", "dependencies", "license",
    "publication_status", "release_readiness",
    "commercial_product_ready", "capability_level",
]


def test_manifests_directory_exists():
    assert MANIFESTS_DIR.exists()


def test_matrix_file_exists():
    assert MATRIX_PATH.exists()


@pytest.mark.parametrize("fmt", EXPECTED_FORMATS)
def test_manifest_file_exists(fmt):
    assert (MANIFESTS_DIR / f"{fmt}.yaml").exists(), f"Missing manifest for {fmt}"


@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not available")
@pytest.mark.parametrize("fmt", EXPECTED_FORMATS)
def test_manifest_loads_and_has_required_fields(fmt):
    path = MANIFESTS_DIR / f"{fmt}.yaml"
    with open(path, encoding="utf-8") as f:
        m = yaml.safe_load(f)
    for field in REQUIRED_MANIFEST_FIELDS:
        assert field in m, f"{fmt}: manifest missing field '{field}'"


@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not available")
@pytest.mark.parametrize("fmt", EXPECTED_FORMATS)
def test_manifest_commercial_not_ready(fmt):
    path = MANIFESTS_DIR / f"{fmt}.yaml"
    with open(path, encoding="utf-8") as f:
        m = yaml.safe_load(f)
    assert m["commercial_product_ready"] is False, f"{fmt}: commercial_product_ready must be False"


@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not available")
@pytest.mark.parametrize("fmt", EXPECTED_FORMATS)
def test_manifest_publish_not_authorized(fmt):
    path = MANIFESTS_DIR / f"{fmt}.yaml"
    with open(path, encoding="utf-8") as f:
        m = yaml.safe_load(f)
    rr = m.get("release_readiness", {})
    assert rr.get("publish_authorized") is False, f"{fmt}: publish_authorized must be False"


@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not available")
@pytest.mark.parametrize("fmt", EXPECTED_FORMATS)
def test_manifest_capability_is_alpha(fmt):
    path = MANIFESTS_DIR / f"{fmt}.yaml"
    with open(path, encoding="utf-8") as f:
        m = yaml.safe_load(f)
    assert m.get("capability_level") == "alpha-foss-preview", (
        f"{fmt}: capability_level must be alpha-foss-preview"
    )


@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not available")
@pytest.mark.parametrize("fmt", EXPECTED_FORMATS)
def test_manifest_source_path_exists(fmt):
    path = MANIFESTS_DIR / f"{fmt}.yaml"
    with open(path, encoding="utf-8") as f:
        m = yaml.safe_load(f)
    src = REPO_ROOT / m["source_path"]
    assert src.exists(), f"{fmt}: source_path {src} does not exist"


@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not available")
@pytest.mark.parametrize("fmt", EXPECTED_FORMATS)
def test_manifest_tests_path_exists(fmt):
    path = MANIFESTS_DIR / f"{fmt}.yaml"
    with open(path, encoding="utf-8") as f:
        m = yaml.safe_load(f)
    tests = REPO_ROOT / m["tests_path"]
    assert tests.exists(), f"{fmt}: tests_path {tests} does not exist"


@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not available")
@pytest.mark.parametrize("fmt", EXPECTED_FORMATS)
def test_manifest_examples_path_exists(fmt):
    path = MANIFESTS_DIR / f"{fmt}.yaml"
    with open(path, encoding="utf-8") as f:
        m = yaml.safe_load(f)
    examples = REPO_ROOT / m["examples_path"]
    assert examples.exists(), f"{fmt}: examples_path {examples} does not exist"


@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not available")
@pytest.mark.parametrize("fmt", EXPECTED_FORMATS)
def test_manifest_has_gates_1_to_7(fmt):
    path = MANIFESTS_DIR / f"{fmt}.yaml"
    with open(path, encoding="utf-8") as f:
        m = yaml.safe_load(f)
    gates_passed = [g["gate"] for g in m.get("acquisition_gates_passed", [])]
    for gate_num in range(1, 8):
        assert gate_num in gates_passed, f"{fmt}: gate {gate_num} not in acquisition_gates_passed"


@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not available")
def test_matrix_file_has_all_formats():
    with open(MATRIX_PATH, encoding="utf-8") as f:
        matrix = yaml.safe_load(f)
    fmt_ids = [e["format_id"] for e in matrix["formats"]]
    for fmt in EXPECTED_FORMATS:
        assert fmt in fmt_ids, f"Matrix missing {fmt}"


@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not available")
def test_matrix_all_publish_not_authorized():
    with open(MATRIX_PATH, encoding="utf-8") as f:
        matrix = yaml.safe_load(f)
    for entry in matrix["formats"]:
        assert entry.get("publish_authorized") is False, (
            f"{entry['format_id']}: matrix publish_authorized must be False"
        )


@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not available")
def test_matrix_global_invariants():
    with open(MATRIX_PATH, encoding="utf-8") as f:
        matrix = yaml.safe_load(f)
    inv = matrix.get("global_invariants", {})
    assert inv.get("publication_authorized") is False
    assert inv.get("commercial_product_ready") is False
    assert inv.get("capability_level") == "alpha-foss-preview"
