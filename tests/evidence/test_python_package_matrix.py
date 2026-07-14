"""
test_python_package_matrix.py — Validates the Python FOSS package matrix.

Sprint: FORMAT-FACTORY-R21-FOSS-RELEASE-READINESS-AND-GATE11-COMMERCIAL-PREEXECUTION-TRAIN-001
"""

from pathlib import Path
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MATRIX_PATH = REPO_ROOT / "packaging" / "python" / "package-matrix.yaml"
TEMPLATE_PATH = REPO_ROOT / "packaging" / "python" / "pyproject.template.toml"
BUILD_SCRIPT = REPO_ROOT / "packaging" / "python" / "build-local-packages.py"

# Add user site-packages to find yaml if needed
sys.path.insert(0, "C:/Users/prora/AppData/Roaming/Python/Python313/site-packages")

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

EXPECTED_PACKAGES = [
    "format-factory-zst",
    "format-factory-fodp",
    "format-factory-fodg",
    "format-factory-gnumeric",
    "format-factory-abw",
    "format-factory-fods",
    "format-factory-fodt",
]

EXPECTED_MODULES = ["zst", "fodp", "fodg", "gnumeric", "abw", "fods", "fodt"]


def test_package_matrix_file_exists():
    assert MATRIX_PATH.exists(), f"package-matrix.yaml not found at {MATRIX_PATH}"


def test_pyproject_template_exists():
    assert TEMPLATE_PATH.exists(), f"pyproject.template.toml not found at {TEMPLATE_PATH}"


def test_build_script_exists():
    assert BUILD_SCRIPT.exists(), f"build-local-packages.py not found at {BUILD_SCRIPT}"


@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not available")
def test_matrix_loads_as_yaml():
    with open(MATRIX_PATH, encoding="utf-8") as f:
        matrix = yaml.safe_load(f)
    assert "packages" in matrix
    assert isinstance(matrix["packages"], list)
    assert len(matrix["packages"]) >= 7


@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not available")
def test_all_expected_packages_present():
    with open(MATRIX_PATH, encoding="utf-8") as f:
        matrix = yaml.safe_load(f)
    names = [p["package_name"] for p in matrix["packages"]]
    for expected in EXPECTED_PACKAGES:
        assert expected in names, f"{expected} not in package matrix"


@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not available")
def test_no_package_publication_authorized():
    with open(MATRIX_PATH, encoding="utf-8") as f:
        matrix = yaml.safe_load(f)
    for pkg in matrix["packages"]:
        assert pkg.get("publication_authorized") is False, (
            f"{pkg['package_name']}: publication_authorized must be False"
        )


@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not available")
def test_no_package_commercial_ready():
    with open(MATRIX_PATH, encoding="utf-8") as f:
        matrix = yaml.safe_load(f)
    for pkg in matrix["packages"]:
        assert pkg.get("commercial_ready") is False, (
            f"{pkg['package_name']}: commercial_ready must be False"
        )


@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not available")
def test_all_packages_have_required_fields():
    required_fields = [
        "package_name", "module_import", "format_id", "license",
        "python_version", "dependencies", "capability_level",
        "source_path", "tests_path", "examples_path",
        "publish_status", "publication_authorized", "commercial_ready",
        "acquisition_gates_passed",
    ]
    with open(MATRIX_PATH, encoding="utf-8") as f:
        matrix = yaml.safe_load(f)
    for pkg in matrix["packages"]:
        for field in required_fields:
            assert field in pkg, f"{pkg['package_name']}: missing field '{field}'"


@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not available")
def test_all_packages_capability_is_alpha_preview():
    with open(MATRIX_PATH, encoding="utf-8") as f:
        matrix = yaml.safe_load(f)
    for pkg in matrix["packages"]:
        assert pkg.get("capability_level") == "alpha-foss-preview", (
            f"{pkg['package_name']}: capability_level must be 'alpha-foss-preview'"
        )


@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not available")
def test_all_packages_have_source_paths():
    with open(MATRIX_PATH, encoding="utf-8") as f:
        matrix = yaml.safe_load(f)
    for pkg in matrix["packages"]:
        src = REPO_ROOT / pkg["source_path"]
        assert src.exists(), f"{pkg['package_name']}: source_path {src} does not exist"


@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not available")
def test_all_packages_have_tests_paths():
    with open(MATRIX_PATH, encoding="utf-8") as f:
        matrix = yaml.safe_load(f)
    for pkg in matrix["packages"]:
        tests = REPO_ROOT / pkg["tests_path"]
        assert tests.exists(), f"{pkg['package_name']}: tests_path {tests} does not exist"


@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not available")
def test_all_packages_publish_status_is_local_only():
    with open(MATRIX_PATH, encoding="utf-8") as f:
        matrix = yaml.safe_load(f)
    for pkg in matrix["packages"]:
        assert "local_only" in pkg.get("publish_status", ""), (
            f"{pkg['package_name']}: publish_status must contain 'local_only'"
        )


def test_template_contains_no_publish_guard():
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    assert "publication_authorized: false" in template
    assert "commercial_product_ready: false" in template


def test_source_modules_importable():
    """All five FOSS source modules must be importable from src/python."""
    src_python = str(REPO_ROOT / "src" / "python")
    if src_python not in sys.path:
        sys.path.insert(0, src_python)
    for mod in EXPECTED_MODULES:
        m = __import__(mod)
        assert hasattr(m, "__version__"), f"{mod}: missing __version__"
        assert hasattr(m, "__commercial_ready__"), f"{mod}: missing __commercial_ready__"
        assert m.__commercial_ready__ is False, f"{mod}: __commercial_ready__ must be False"
        assert hasattr(m, "__capability_level__"), f"{mod}: missing __capability_level__"
        assert m.__capability_level__ == "alpha-foss-preview", f"{mod}: wrong capability_level"
