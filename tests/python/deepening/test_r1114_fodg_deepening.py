"""Sprint 560 FODG analytics deepening tests - primes 1049, 1051."""
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"


def test_mod1049_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1049_times_7600_plus_shape_times_259_plus_text_times_256_plus_page_times_262
    assert fodg_file_size_mod_1049_times_7600_plus_shape_times_259_plus_text_times_256_plus_page_times_262(str(EMPTY)) == 30662


def test_mod1049_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1049_times_7600_plus_shape_times_259_plus_text_times_256_plus_page_times_262
    assert fodg_file_size_mod_1049_times_7600_plus_shape_times_259_plus_text_times_256_plus_page_times_262(str(MINIMAL)) == 3223177


def test_mod1049_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1049_times_7600_plus_shape_times_259_plus_text_times_256_plus_page_times_262
    assert fodg_file_size_mod_1049_times_7600_plus_shape_times_259_plus_text_times_256_plus_page_times_262(str(SHAPES)) == 4401951


def test_mod1051_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1051_times_7700_plus_shape_times_261_plus_text_times_258_plus_page_times_264
    assert fodg_file_size_mod_1051_times_7700_plus_shape_times_261_plus_text_times_258_plus_page_times_264(str(EMPTY)) == 15664


def test_mod1051_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1051_times_7700_plus_shape_times_261_plus_text_times_258_plus_page_times_264
    assert fodg_file_size_mod_1051_times_7700_plus_shape_times_261_plus_text_times_258_plus_page_times_264(str(MINIMAL)) == 3250183


def test_mod1051_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1051_times_7700_plus_shape_times_261_plus_text_times_258_plus_page_times_264
    assert fodg_file_size_mod_1051_times_7700_plus_shape_times_261_plus_text_times_258_plus_page_times_264(str(SHAPES)) == 4444463


def test_mod1049_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1049_times_7600_plus_shape_times_259_plus_text_times_256_plus_page_times_262
    assert isinstance(fodg_file_size_mod_1049_times_7600_plus_shape_times_259_plus_text_times_256_plus_page_times_262(str(EMPTY)), int)


def test_mod1051_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1051_times_7700_plus_shape_times_261_plus_text_times_258_plus_page_times_264
    assert isinstance(fodg_file_size_mod_1051_times_7700_plus_shape_times_261_plus_text_times_258_plus_page_times_264(str(EMPTY)), int)


def test_mod1049_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1049_times_7600_plus_shape_times_259_plus_text_times_256_plus_page_times_262
    assert fodg_file_size_mod_1049_times_7600_plus_shape_times_259_plus_text_times_256_plus_page_times_262(str(EMPTY)) >= 0


def test_mod1051_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1051_times_7700_plus_shape_times_261_plus_text_times_258_plus_page_times_264
    assert fodg_file_size_mod_1051_times_7700_plus_shape_times_261_plus_text_times_258_plus_page_times_264(str(EMPTY)) >= 0


def test_mod1049_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1049_times_7600_plus_shape_times_259_plus_text_times_256_plus_page_times_262
    fn = fodg_file_size_mod_1049_times_7600_plus_shape_times_259_plus_text_times_256_plus_page_times_262
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1051_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1051_times_7700_plus_shape_times_261_plus_text_times_258_plus_page_times_264
    fn = fodg_file_size_mod_1051_times_7700_plus_shape_times_261_plus_text_times_258_plus_page_times_264
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1049_importable_from_package():
    from fodg import fodg_file_size_mod_1049_times_7600_plus_shape_times_259_plus_text_times_256_plus_page_times_262
    assert callable(fodg_file_size_mod_1049_times_7600_plus_shape_times_259_plus_text_times_256_plus_page_times_262)


def test_mod1051_importable_from_package():
    from fodg import fodg_file_size_mod_1051_times_7700_plus_shape_times_261_plus_text_times_258_plus_page_times_264
    assert callable(fodg_file_size_mod_1051_times_7700_plus_shape_times_261_plus_text_times_258_plus_page_times_264)
