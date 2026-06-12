"""
test_public_api.py -- Public API contract tests for format-factory-fods.

Verifies: exports, exception hierarchy, return type contract, __version__.
"""


# ---------------------------------------------------------------------------
# Package-level exports
# ---------------------------------------------------------------------------

def test_parse_fods_importable():
    from fods import parse_fods
    assert callable(parse_fods)


def test_parse_fods_strict_importable():
    from fods import parse_fods_strict
    assert callable(parse_fods_strict)


def test_fods_error_importable():
    from fods import FodsError
    assert FodsError is not None


def test_fods_input_error_importable():
    from fods import FodsInputError
    assert FodsInputError is not None


def test_fods_size_error_importable():
    from fods import FodsSizeError
    assert FodsSizeError is not None


def test_fods_parse_error_importable():
    from fods import FodsParseError
    assert FodsParseError is not None


def test_format_id_importable():
    from fods import FORMAT_ID
    assert FORMAT_ID == "fods"


def test_spec_version_importable():
    from fods import SPEC_VERSION
    assert SPEC_VERSION == "ODF 1.3"


def test_package_version_importable():
    from fods import PACKAGE_VERSION
    assert isinstance(PACKAGE_VERSION, str)
    assert len(PACKAGE_VERSION) > 0


def test_max_file_bytes_importable():
    from fods import MAX_FILE_BYTES
    assert MAX_FILE_BYTES == 100 * 1024 * 1024


def test_dunder_version():
    import fods
    assert hasattr(fods, "__version__")
    assert fods.__version__ == fods.PACKAGE_VERSION


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------

def test_fods_error_is_value_error():
    from fods import FodsError
    assert issubclass(FodsError, ValueError)


def test_fods_input_error_is_fods_error():
    from fods import FodsError, FodsInputError
    assert issubclass(FodsInputError, FodsError)


def test_fods_size_error_is_fods_error():
    from fods import FodsError, FodsSizeError
    assert issubclass(FodsSizeError, FodsError)


def test_fods_parse_error_is_fods_error():
    from fods import FodsError, FodsParseError
    assert issubclass(FodsParseError, FodsError)


# ---------------------------------------------------------------------------
# Return type contract
# ---------------------------------------------------------------------------

def test_parse_fods_returns_dict():
    from fods import parse_fods
    result = parse_fods("/nonexistent/path.fods")
    assert isinstance(result, dict)


def test_parse_fods_error_has_parse_errors_key():
    from fods import parse_fods
    result = parse_fods("/nonexistent/path.fods")
    assert "error" in result
    assert "parse_errors" in result
    assert isinstance(result["parse_errors"], list)
