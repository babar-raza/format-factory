"""Sprint 665 FODG analytics deepening tests - primes 1559, 1567."""
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"


def test_mod1559_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1559_times_14600_plus_shape_times_399_plus_text_times_396_plus_page_times_402
    assert fodg_file_size_mod_1559_times_14600_plus_shape_times_399_plus_text_times_396_plus_page_times_402(str(EMPTY)) == 15374202


def test_mod1559_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1559_times_14600_plus_shape_times_399_plus_text_times_396_plus_page_times_402
    assert fodg_file_size_mod_1559_times_14600_plus_shape_times_399_plus_text_times_396_plus_page_times_402(str(MINIMAL)) == 21506997


def test_mod1559_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1559_times_14600_plus_shape_times_399_plus_text_times_396_plus_page_times_402
    assert fodg_file_size_mod_1559_times_14600_plus_shape_times_399_plus_text_times_396_plus_page_times_402(str(SHAPES)) == 1009791


def test_mod1567_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1567_times_14700_plus_shape_times_401_plus_text_times_398_plus_page_times_404
    assert fodg_file_size_mod_1567_times_14700_plus_shape_times_401_plus_text_times_398_plus_page_times_404(str(EMPTY)) == 15479504


def test_mod1567_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1567_times_14700_plus_shape_times_401_plus_text_times_398_plus_page_times_404
    assert fodg_file_size_mod_1567_times_14700_plus_shape_times_401_plus_text_times_398_plus_page_times_404(str(MINIMAL)) == 21654303


def test_mod1567_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1567_times_14700_plus_shape_times_401_plus_text_times_398_plus_page_times_404
    assert fodg_file_size_mod_1567_times_14700_plus_shape_times_401_plus_text_times_398_plus_page_times_404(str(SHAPES)) == 899103


def test_mod1559_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1559_times_14600_plus_shape_times_399_plus_text_times_396_plus_page_times_402
    assert isinstance(fodg_file_size_mod_1559_times_14600_plus_shape_times_399_plus_text_times_396_plus_page_times_402(str(EMPTY)), int)


def test_mod1567_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1567_times_14700_plus_shape_times_401_plus_text_times_398_plus_page_times_404
    assert isinstance(fodg_file_size_mod_1567_times_14700_plus_shape_times_401_plus_text_times_398_plus_page_times_404(str(EMPTY)), int)


def test_mod1559_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1559_times_14600_plus_shape_times_399_plus_text_times_396_plus_page_times_402
    assert fodg_file_size_mod_1559_times_14600_plus_shape_times_399_plus_text_times_396_plus_page_times_402(str(EMPTY)) >= 0


def test_mod1567_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1567_times_14700_plus_shape_times_401_plus_text_times_398_plus_page_times_404
    assert fodg_file_size_mod_1567_times_14700_plus_shape_times_401_plus_text_times_398_plus_page_times_404(str(EMPTY)) >= 0


def test_mod1559_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1559_times_14600_plus_shape_times_399_plus_text_times_396_plus_page_times_402
    fn = fodg_file_size_mod_1559_times_14600_plus_shape_times_399_plus_text_times_396_plus_page_times_402
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1567_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1567_times_14700_plus_shape_times_401_plus_text_times_398_plus_page_times_404
    fn = fodg_file_size_mod_1567_times_14700_plus_shape_times_401_plus_text_times_398_plus_page_times_404
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1559_importable_from_package():
    from fodg import fodg_file_size_mod_1559_times_14600_plus_shape_times_399_plus_text_times_396_plus_page_times_402
    assert callable(fodg_file_size_mod_1559_times_14600_plus_shape_times_399_plus_text_times_396_plus_page_times_402)


def test_mod1567_importable_from_package():
    from fodg import fodg_file_size_mod_1567_times_14700_plus_shape_times_401_plus_text_times_398_plus_page_times_404
    assert callable(fodg_file_size_mod_1567_times_14700_plus_shape_times_401_plus_text_times_398_plus_page_times_404)
