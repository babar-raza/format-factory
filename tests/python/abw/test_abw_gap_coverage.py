"""
Comprehensive gap-coverage tests for the ABW (AbiWord) FOSS Python package.

Targets the missing_test_coverage gaps recorded against src/python/abw/ by
exercising every name exported from ``abw.__all__``: module constants,
exception classes, the ``AbwDocument`` domain model, the paragraph/section
spec-shaped iterators, the installed-workflow proof function, and all
module-level analytics/mutation functions -- both the ~125 file-path/source
based functions (defined across abw_codec.py, word_document.py, and
abw_paragraph_analytics.py) and the ~47 model-dict based functions (defined
across abw_codec.py and abw_word_stats.py).

Expected values below were captured by direct introspection of the current
implementation against the committed corpus samples in
samples/by-format/abw/ (minimal-document.abw, two-paragraphs.abw,
empty-section.abw) plus small in-test-generated fixtures. This makes the
suite a precise regression net: it will fail loudly if any of these ~170
public functions' behavior changes.

Run:
    .venv/Scripts/pytest tests/python/abw/test_abw_gap_coverage.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import abw
from abw.abw_codec import AbwError as _CodecAbwError
from abw.abw_codec import AbwParseError as _CodecAbwParseError

SAMPLES_DIR = _REPO / "samples" / "by-format" / "abw"
MINIMAL = SAMPLES_DIR / "minimal-document.abw"        # 1 paragraph: "Hello"
TWO_PARA = SAMPLES_DIR / "two-paragraphs.abw"          # 2 paragraphs, 1 section
EMPTY_SECTION = SAMPLES_DIR / "empty-section.abw"      # 1 section, 0 paragraphs

_LONG_PARA = (
    "Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod "
    "tempor incididunt ut labore et dolore magna aliqua ut enim ad minim "
    "veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex "
    "ea commodo consequat duis aute irure dolor."
)


@pytest.fixture(scope="module")
def multi_section_file(tmp_path_factory) -> Path:
    """Generated .abw file with 2 sections / 3 paragraphs, one paragraph >200 chars."""
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<abiword template="false" styles="unlocked" version="1.0" fileformat="1.0">
<section>
<p>Alpha.</p>
<p>Beta beta.</p>
</section>
<section>
<p>{_LONG_PARA}</p>
</section>
</abiword>"""
    dest = tmp_path_factory.mktemp("abw_multi") / "multi.abw"
    dest.write_text(xml, encoding="utf-8")
    return dest


@pytest.fixture()
def dup_model() -> dict:
    """Model with duplicate paragraphs, an empty paragraph, and a distinct paragraph."""
    return abw.create_abw(["Hello world", "Hello world", "", "Another line here"])


def _is_close(a, b) -> bool:
    if isinstance(a, float) or isinstance(b, float):
        return a == pytest.approx(b)
    return a == b


# ===========================================================================
# 1. Module-level constants
# ===========================================================================

def test_abw_mime_constant():
    assert abw.ABW_MIME == "application/x-abiword"


def test_abw_root_tag_constant():
    assert abw.ABW_ROOT_TAG == "abiword"


def test_max_file_size_constant():
    assert abw.MAX_FILE_SIZE == 64 * 1024 * 1024


def test_vowels_constant():
    assert "a" in abw.VOWELS
    assert "E" in abw.VOWELS
    assert "b" not in abw.VOWELS


def test_consonants_constant():
    assert "b" in abw.CONSONANTS
    assert "a" not in abw.CONSONANTS
    assert abw.VOWELS.isdisjoint(abw.CONSONANTS)


def test_namespace_uri_constant():
    assert isinstance(abw.namespace_uri, str)
    assert "abisource" in abw.namespace_uri


def test_spec_qname_constant():
    assert isinstance(abw.spec_qname, str)
    assert abw.spec_qname


def test_spec_fact_ref_constant():
    assert isinstance(abw.spec_fact_ref, str)
    assert abw.spec_fact_ref.startswith("SAL-ABW")


def test_annotations_future_feature_leaked_into_all():
    # __future__ annotations leaks into module namespace / __all__; just prove
    # it is present and importable rather than crash the export sweep below.
    import __future__ as _future
    assert abw.annotations is _future.annotations


# ===========================================================================
# 2. Exceptions
# ===========================================================================

def test_abw_error_is_exception_subclass():
    assert issubclass(abw.AbwError, Exception)


def test_abw_parse_error_subclasses_abw_error():
    assert issubclass(abw.AbwParseError, abw.AbwError)


def test_abw_write_error_subclasses_abw_error():
    assert issubclass(abw.AbwWriteError, abw.AbwError)


def test_format_factory_error_is_exception_subclass():
    assert issubclass(abw.FormatFactoryError, Exception)


def test_abw_error_instantiates_with_message():
    err = abw.AbwError("boom")
    assert str(err) == "boom"


def test_abw_write_error_instantiates_with_message():
    err = abw.AbwWriteError("cannot write")
    assert isinstance(err, abw.AbwError)


def test_load_missing_file_raises_codec_parse_error():
    with pytest.raises(_CodecAbwParseError):
        abw.load(_REPO / "does_not_exist_xyz.abw")


def test_load_invalid_xml_raises_codec_error():
    with pytest.raises(_CodecAbwError):
        abw.load(b"<not valid xml <<<<<")


def test_load_wrong_root_raises_codec_parse_error():
    with pytest.raises(_CodecAbwParseError):
        abw.load(b"<?xml version='1.0'?><root/>")


# ===========================================================================
# 3. Source/file-path based functions -- exact-value regression table
#    (single positional argument, evaluated against two-paragraphs.abw)
# ===========================================================================

SOURCE_FUNC_EXPECTED_TWO_PARA = {
    "abw_all_paragraphs_nonempty": True,
    "abw_all_words_unique": False,
    "abw_alpha_char_count": 29,
    "abw_alpha_ratio": 0.8787878787878788,
    "abw_average_paragraph_length": 16.5,
    "abw_average_word_length": 7.75,
    "abw_avg_chars_per_word": 8.25,
    "abw_avg_paragraph_char_count": 16.5,
    "abw_avg_paragraph_length": 16.5,
    "abw_avg_paragraph_word_count": 2.0,
    "abw_avg_paragraph_words": 2.0,
    "abw_avg_sentence_length": 15.5,
    "abw_avg_word_count": 2.0,
    "abw_avg_word_length_per_para": 15.5,
    "abw_avg_word_per_paragraph": 2.0,
    "abw_avg_words_per_paragraph": 2.0,
    "abw_capital_word_count": 2,
    "abw_char_count": 33,
    "abw_char_density": 16.5,
    "abw_char_per_paragraph": 16.5,
    "abw_chars_per_word": 8.25,
    "abw_consonant_ratio": 0.6896551724137931,
    "abw_consonant_to_vowel_ratio": 2.2222222222222223,
    "abw_digit_char_count": 0,
    "abw_digit_count": 0,
    "abw_digit_ratio": 0.0,
    "abw_distinct_word_ratio": 0.75,
    "abw_empty_paragraph_count": 0,
    "abw_empty_paragraph_ratio": 0.0,
    "abw_file_size_bytes": 369,
    "abw_first_paragraph": "First paragraph.",
    "abw_has_content": True,
    "abw_has_empty_paragraphs": False,
    "abw_has_headings": False,
    "abw_has_long_paragraphs": False,
    "abw_has_metadata": False,
    "abw_has_multi_para": True,
    "abw_has_multiple_paragraphs": True,
    "abw_has_numeric_content": False,
    "abw_has_punctuation": True,
    "abw_has_repeated_paragraphs": False,
    "abw_has_sections": True,
    "abw_has_single_paragraph": False,
    "abw_has_unicode": False,
    "abw_heading_count": 0,
    "abw_heading_density": 0.0,
    "abw_is_abw": True,
    "abw_is_content_rich": True,
    "abw_is_empty": False,
    "abw_is_empty_document": False,
    "abw_is_multi_paragraph": True,
    "abw_is_single_paragraph": False,
    "abw_last_paragraph": "Second paragraph.",
    "abw_letter_ratio": 0.8787878787878788,
    "abw_line_count": 2,
    "abw_longest_paragraph": "Second paragraph.",
    "abw_longest_paragraph_chars": 17,
    "abw_longest_paragraph_index": 1,
    "abw_longest_paragraph_length": 17,
    "abw_longest_paragraph_words": 2,
    "abw_longest_word_length": 9,
    "abw_lowercase_ratio": 0.9310344827586207,
    "abw_max_paragraph_char_count": 17,
    "abw_max_paragraph_length": 17,
    "abw_max_paragraph_word_count": 2,
    "abw_max_paragraph_words": 2,
    "abw_max_word_count_para": 2,
    "abw_median_paragraph_length": 16,
    "abw_min_paragraph_char_count": 16,
    "abw_min_paragraph_length": 16,
    "abw_min_word_count_para": 2,
    "abw_nonempty_para_ratio": 1.0,
    "abw_nonempty_paragraph_count": 2,
    "abw_nonempty_paragraph_ratio": 1.0,
    "abw_nonspace_char_count": 31,
    "abw_numeric_char_count": 0,
    "abw_numeric_word_count": 0,
    "abw_para_char_variance": 0.25,
    "abw_paragraph_char_counts": [16, 17],
    "abw_paragraph_count": 2,
    "abw_paragraph_length_variance": 0.25,
    "abw_paragraph_texts": ["First paragraph.", "Second paragraph."],
    "abw_punctuation_count": 2,
    "abw_section_count": 1,
    "abw_sentence_density": 1.0,
    "abw_short_paragraph_count": 2,
    "abw_short_word_count": 0,
    "abw_shortest_paragraph_chars": 16,
    "abw_shortest_word": "First",
    "abw_space_count": 2,
    "abw_text_density": 0.9117647058823529,
    "abw_total_char_count": 33,
    "abw_total_para_char_count": 33,
    "abw_total_section_paragraph_count": 2,
    "abw_total_sentence_count": 2,
    "abw_total_text_length": 33,
    "abw_total_word_count": 4,
    "abw_total_word_length": 29,
    "abw_unique_char_count": 17,
    "abw_unique_paragraph_count": 2,
    "abw_unique_word_count": 3,
    "abw_unique_words_per_paragraph": 1.5,
    "abw_uppercase_count": 2,
    "abw_uppercase_ratio": 0.06896551724137931,
    "abw_vocabulary_richness": 0.75,
    "abw_vowel_count": 9,
    "abw_vowel_ratio": 0.2647058823529412,
    "abw_whitespace_ratio": 0.06060606060606061,
    "abw_word_count": 4,
    "abw_word_length_variance": 5.1875,
    "abw_words_per_char": 0.11764705882352941,
    "abw_words_per_sentence": 2.0,
    "export_to_csv": "text\nFirst paragraph.\nSecond paragraph.\n",
    "export_to_html": (
        "<!DOCTYPE html>\n<html>\n<body>\n<p>First paragraph.</p>\n"
        "<p>Second paragraph.</p>\n</body>\n</html>"
    ),
    "export_to_json": (
        '{\n  "is_abw": true,\n  "section_count": 1,\n  "paragraph_count": 2,\n'
        '  "paragraphs": [\n    "First paragraph.",\n    "Second paragraph."\n  ]\n}'
    ),
    "export_to_txt": "First paragraph.\nSecond paragraph.",
    "extract_text": ["First paragraph.", "Second paragraph."],
    "get_metadata": {},
    "get_paragraph_count": 2,
    "get_section_count": 1,
    "load": {
        "is_abw": True,
        "section_count": 1,
        "paragraph_count": 2,
        "paragraphs": ["First paragraph.", "Second paragraph."],
    },
    "probe_abw": True,
}


@pytest.mark.parametrize("func_name", sorted(SOURCE_FUNC_EXPECTED_TWO_PARA))
def test_source_function_exact_value_two_paragraphs(func_name):
    """Every file-path based analytics function returns its known-good value."""
    func = getattr(abw, func_name)
    expected = SOURCE_FUNC_EXPECTED_TWO_PARA[func_name]
    actual = func(TWO_PARA)
    assert _is_close(actual, expected), f"{func_name}(TWO_PARA) = {actual!r}, expected {expected!r}"


def test_source_function_table_covers_all_single_arg_source_functions():
    """Guard against silently dropping coverage if new abw_* source functions appear."""
    import inspect

    covered = set(SOURCE_FUNC_EXPECTED_TWO_PARA) | {
        "abw_iter_paragraphs", "abw_iter_sections", "abw_installed_workflow",
    }
    missing = []
    for name in abw.__all__:
        obj = getattr(abw, name)
        if not inspect.isfunction(obj):
            continue
        try:
            sig = inspect.signature(obj)
        except (TypeError, ValueError):
            continue
        params = list(sig.parameters)
        if params and params[0] in ("source", "file_path") and name not in covered:
            missing.append(name)
    assert missing == [], f"Uncovered source-based functions: {missing}"


# ===========================================================================
# 4. Source/file-path based functions -- edge-case samples
#    (minimal-document.abw: 1 paragraph "Hello"; empty-section.abw: 0 paragraphs)
# ===========================================================================

MINIMAL_EXPECTED = {
    "abw_paragraph_count": 1,
    "abw_is_empty": False,
    "abw_has_content": True,
    "abw_word_count": 1,
    "abw_char_count": 5,
    "abw_first_paragraph": "Hello",
    "abw_last_paragraph": "Hello",
    "abw_longest_word_length": 5,
    "abw_is_single_paragraph": True,
    "abw_has_single_paragraph": True,
    "abw_section_count": 1,
    "abw_max_paragraph_length": 5,
    "probe_abw": True,
}


@pytest.mark.parametrize("func_name", sorted(MINIMAL_EXPECTED))
def test_source_function_exact_value_minimal_document(func_name):
    func = getattr(abw, func_name)
    expected = MINIMAL_EXPECTED[func_name]
    actual = func(MINIMAL)
    assert _is_close(actual, expected), f"{func_name}(MINIMAL) = {actual!r}, expected {expected!r}"


EMPTY_SECTION_EXPECTED = {
    "abw_paragraph_count": 0,
    "abw_is_empty": True,
    "abw_is_empty_document": True,
    "abw_has_content": False,
    "abw_word_count": 0,
    "abw_char_count": 0,
    "abw_first_paragraph": "",
    "abw_last_paragraph": "",
    "abw_longest_word_length": 0,
    "abw_section_count": 1,
    "abw_max_paragraph_length": 0,
    "abw_longest_paragraph": "",
    "abw_shortest_word": "",
    "abw_all_words_unique": True,
    "probe_abw": True,
}


@pytest.mark.parametrize("func_name", sorted(EMPTY_SECTION_EXPECTED))
def test_source_function_exact_value_empty_section(func_name):
    func = getattr(abw, func_name)
    expected = EMPTY_SECTION_EXPECTED[func_name]
    actual = func(EMPTY_SECTION)
    assert _is_close(actual, expected), f"{func_name}(EMPTY_SECTION) = {actual!r}, expected {expected!r}"


def test_probe_abw_rejects_non_abw_string():
    assert abw.probe_abw("not an abw document at all") is False


def test_probe_abw_rejects_garbage_bytes():
    assert abw.probe_abw(b"\x00\x01\x02garbage") is False


def test_probe_abw_rejects_nonexistent_path():
    assert abw.probe_abw("this/path/does/not/exist.abw") is False


def test_probe_abw_rejects_empty_bytes():
    assert abw.probe_abw(b"") is False


def test_all_corpus_samples_load_without_error():
    for path in sorted(SAMPLES_DIR.glob("*.abw")):
        model = abw.load(path)
        assert model["is_abw"] is True, f"{path.name} not recognized as ABW"
        assert "paragraphs" in model


# ===========================================================================
# 5. Model-dict based functions -- no extra arguments
# ===========================================================================

MODEL_FUNC_EXPECTED_DUP = {
    "abw_longest_word": "Another",
    "abw_sentence_count": 0,
    "all_paragraphs_nonempty": False,
    "average_paragraph_length": 9.75,
    "avg_words_per_paragraph": 1.75,
    "count_words": 7,
    "export_to_markdown": "Hello world\n\nHello world\n\n\n\nAnother line here",
    "export_to_plain_text": "Hello world\n\nHello world\n\n\n\nAnother line here",
    "first_paragraph": "Hello world",
    "get_char_count": 39,
    "get_paragraphs": ["Hello world", "Hello world", "", "Another line here"],
    "get_unique_words": ["another", "hello", "here", "line", "world"],
    "get_word_count": 7,
    "has_paragraphs": True,
    "is_empty": False,
    "last_paragraph": "Another line here",
    "longest_paragraph": "Another line here",
    "max_word_length": 7,
    "most_frequent_word": "hello",
    "nonempty_paragraph_count": 3,
    "paragraph_count": 4,
    "paragraph_lengths": [11, 11, 0, 17],
    "shortest_paragraph": "",
    "total_char_count": 39,
    "total_sentence_count": 0,
    "unique_word_count": 5,
    "text_stats": {
        "paragraph_count": 4,
        "word_count": 7,
        "char_count": 39,
        "avg_words_per_paragraph": 1.75,
    },
    "word_frequency": {"hello": 2, "world": 2, "another": 1, "line": 1, "here": 1},
}


@pytest.mark.parametrize("func_name", sorted(MODEL_FUNC_EXPECTED_DUP))
def test_model_function_exact_value(func_name, dup_model):
    func = getattr(abw, func_name)
    expected = MODEL_FUNC_EXPECTED_DUP[func_name]
    actual = func(dup_model)
    assert _is_close(actual, expected), f"{func_name}(dup_model) = {actual!r}, expected {expected!r}"


# ===========================================================================
# 6. Model-dict based functions -- functions that take extra arguments
# ===========================================================================

def test_append_paragraph(dup_model):
    result = abw.append_paragraph(dup_model, "New para")
    assert result["paragraphs"][-1] == "New para"
    assert result["paragraph_count"] == 5
    # original untouched
    assert dup_model["paragraph_count"] == 4


def test_contains_text_true_and_false(dup_model):
    assert abw.contains_text(dup_model, "line") is True
    assert abw.contains_text(dup_model, "zzz") is False


def test_contains_text_case_insensitive(dup_model):
    assert abw.contains_text(dup_model, "HELLO", case_sensitive=False) is True
    assert abw.contains_text(dup_model, "HELLO", case_sensitive=True) is False


def test_count_paragraphs_matching(dup_model):
    assert abw.count_paragraphs_matching(dup_model, "Hello") == 2


def test_count_paragraphs_matching_case_insensitive(dup_model):
    assert abw.count_paragraphs_matching(dup_model, "hello", case_sensitive=False) == 2


def test_edit_paragraph(dup_model):
    result = abw.edit_paragraph(dup_model, 0, "Edited")
    assert result["paragraphs"][0] == "Edited"
    assert result["paragraph_count"] == 4


def test_edit_paragraph_out_of_range_raises(dup_model):
    with pytest.raises(IndexError):
        abw.edit_paragraph(dup_model, 99, "x")


def test_get_paragraph(dup_model):
    assert abw.get_paragraph(dup_model, 3) == "Another line here"


def test_get_paragraph_out_of_range_raises(dup_model):
    with pytest.raises(IndexError):
        abw.get_paragraph(dup_model, 99)


def test_get_paragraph_at(dup_model):
    assert abw.get_paragraph_at(dup_model, 3) == "Another line here"


def test_get_paragraph_at_negative_index_raises(dup_model):
    # get_paragraph_at does NOT accept negative indices (unlike paragraph_at)
    with pytest.raises(IndexError):
        abw.get_paragraph_at(dup_model, -1)


def test_get_words(dup_model):
    assert abw.get_words(dup_model, 0) == ["Hello", "world"]


def test_get_words_empty_paragraph(dup_model):
    assert abw.get_words(dup_model, 2) == []


def test_get_words_out_of_range_returns_empty(dup_model):
    assert abw.get_words(dup_model, 99) == []


def test_has_paragraph_true_and_false(dup_model):
    assert abw.has_paragraph(dup_model, "Hello world") is True
    assert abw.has_paragraph(dup_model, "nope") is False


def test_join_paragraphs_default_separator(dup_model):
    assert abw.join_paragraphs(dup_model) == "Hello world\nHello world\n\nAnother line here"


def test_join_paragraphs_custom_separator(dup_model):
    assert abw.join_paragraphs(dup_model, sep=" | ") == (
        "Hello world | Hello world |  | Another line here"
    )


def test_paragraph_at_supports_negative_index(dup_model):
    assert abw.paragraph_at(dup_model, -1) == "Another line here"
    assert abw.paragraph_at(dup_model, 0) == "Hello world"


def test_paragraph_at_out_of_range_raises(dup_model):
    with pytest.raises(IndexError):
        abw.paragraph_at(dup_model, 99)
    with pytest.raises(IndexError):
        abw.paragraph_at(dup_model, -99)


def test_replace_in_paragraphs(dup_model):
    result = abw.replace_in_paragraphs(dup_model, "Hello", "Hi")
    assert result["paragraphs"] == ["Hi world", "Hi world", "", "Another line here"]


def test_reverse_paragraphs(dup_model):
    result = abw.reverse_paragraphs(dup_model)
    assert result["paragraphs"] == ["Another line here", "", "Hello world", "Hello world"]


def test_search_paragraph_case_sensitive(dup_model):
    assert abw.search_paragraph(dup_model, "Hello") == [0, 1]


def test_search_paragraph_case_insensitive(dup_model):
    assert abw.search_paragraph(dup_model, "hello", case_sensitive=False) == [0, 1]


def test_search_paragraph_no_match(dup_model):
    assert abw.search_paragraph(dup_model, "zzz") == []


def test_search_replace_paragraph(dup_model):
    result = abw.search_replace_paragraph(dup_model, "Hello", "Hi")
    assert result["paragraphs"] == ["Hi world", "Hi world", "", "Another line here"]


def test_search_replace_paragraph_empty_old_returns_copy(dup_model):
    result = abw.search_replace_paragraph(dup_model, "", "Hi")
    assert result["paragraphs"] == dup_model["paragraphs"]


def test_search_text_finds_indices(dup_model):
    assert abw.search_text(dup_model, "line") == [3]


def test_search_text_empty_query_returns_empty(dup_model):
    assert abw.search_text(dup_model, "") == []


def test_split_paragraphs(dup_model):
    chunks = abw.split_paragraphs(dup_model, 2)
    assert len(chunks) == 2
    assert chunks[0]["paragraphs"] == ["Hello world", "Hello world"]
    assert chunks[1]["paragraphs"] == ["", "Another line here"]


def test_split_paragraphs_invalid_chunk_size_raises(dup_model):
    with pytest.raises(ValueError):
        abw.split_paragraphs(dup_model, 0)


def test_truncate_paragraphs(dup_model):
    result = abw.truncate_paragraphs(dup_model, 2)
    assert result["paragraphs"] == ["Hello world", "Hello world"]
    assert result["paragraph_count"] == 2


def test_truncate_paragraphs_negative_raises(dup_model):
    with pytest.raises(ValueError):
        abw.truncate_paragraphs(dup_model, -1)


def test_word_wrap(dup_model):
    result = abw.word_wrap(dup_model, 5)
    assert result["paragraphs"] == [
        "Hello", "world", "Hello", "world", "", "Anoth", "er", "line", "here",
    ]


def test_write_abw_roundtrip(dup_model, tmp_path):
    dest = tmp_path / "out.abw"
    abw.write_abw(dup_model, dest)
    assert dest.exists()
    roundtrip = abw.load(dest)
    assert roundtrip["paragraphs"] == dup_model["paragraphs"]
    assert roundtrip["paragraph_count"] == dup_model["paragraph_count"]


def test_write_abw_rejects_invalid_model(tmp_path):
    with pytest.raises(_CodecAbwError):
        abw.write_abw({"is_abw": False}, tmp_path / "bad.abw")


def test_write_abw_rejects_non_dict_model(tmp_path):
    with pytest.raises(_CodecAbwError):
        abw.write_abw("not a dict", tmp_path / "bad2.abw")


# ===========================================================================
# 7. create_abw / merge_abw
# ===========================================================================

def test_create_abw_shape():
    model = abw.create_abw(["A1", "A2"])
    assert model == {
        "is_abw": True,
        "section_count": 1,
        "paragraph_count": 2,
        "paragraphs": ["A1", "A2"],
    }


def test_create_abw_empty_list():
    model = abw.create_abw([])
    assert model["paragraph_count"] == 0
    assert model["paragraphs"] == []


def test_merge_abw():
    a = abw.create_abw(["A1", "A2"])
    b = abw.create_abw(["B1"])
    merged = abw.merge_abw(a, b)
    assert merged["paragraphs"] == ["A1", "A2", "B1"]
    assert merged["paragraph_count"] == 3


def test_merge_abw_rejects_non_dict_a():
    with pytest.raises(TypeError):
        abw.merge_abw("not a dict", abw.create_abw([]))


def test_merge_abw_rejects_non_dict_b():
    with pytest.raises(TypeError):
        abw.merge_abw(abw.create_abw([]), "not a dict")


# ===========================================================================
# 8. TypeError contract -- model-based functions reject non-dict input
# ===========================================================================

TYPE_CHECKED_MODEL_FUNCS = {
    "count_words": (),
    "get_word_count": (),
    "search_paragraph": ("q",),
    "get_paragraph": (0,),
    "text_stats": (),
    "reverse_paragraphs": (),
    "has_paragraph": ("q",),
    "get_char_count": (),
    "append_paragraph": ("x",),
    "edit_paragraph": (0, "x"),
    "truncate_paragraphs": (1,),
    "join_paragraphs": (),
    "replace_in_paragraphs": ("a", "b"),
    "word_wrap": (10,),
    "merge_abw": (abw.create_abw([]),),
}


@pytest.mark.parametrize("func_name", sorted(TYPE_CHECKED_MODEL_FUNCS))
def test_model_function_rejects_non_dict(func_name):
    func = getattr(abw, func_name)
    extra_args = TYPE_CHECKED_MODEL_FUNCS[func_name]
    with pytest.raises(TypeError):
        func("not a dict", *extra_args)


# A handful of abw_word_stats.py functions are defensive rather than
# type-checked: they return a safe default for non-dict input instead of
# raising. Pin that contract explicitly so it isn't confused with the
# raise-on-non-dict contract exercised above.
DEFENSIVE_MODEL_FUNCS = {
    "average_paragraph_length": ((), 0.0),
    "unique_word_count": ((), 0),
    "search_text": (("q",), []),
    "get_words": ((0,), []),
    "longest_paragraph": ((), ""),
    "is_empty": ((), True),
    "shortest_paragraph": ((), ""),
    "contains_text": (("q",), False),
    "count_paragraphs_matching": (("q",), 0),
    "has_paragraphs": ((), False),
    "first_paragraph": ((), ""),
    "last_paragraph": ((), ""),
    "all_paragraphs_nonempty": ((), True),
    "total_sentence_count": ((), 0),
    "paragraph_count": ((), 0),
    "total_char_count": ((), 0),
    "most_frequent_word": ((), ""),
    "avg_words_per_paragraph": ((), 0.0),
    "nonempty_paragraph_count": ((), 0),
    "max_word_length": ((), 0),
}


@pytest.mark.parametrize("func_name", sorted(DEFENSIVE_MODEL_FUNCS))
def test_model_function_defensive_default_for_non_dict(func_name):
    func = getattr(abw, func_name)
    extra_args, expected = DEFENSIVE_MODEL_FUNCS[func_name]
    actual = func("not a dict", *extra_args)
    assert actual == expected, f"{func_name}('not a dict') = {actual!r}, expected {expected!r}"


def test_get_word_count_rejects_non_dict():
    with pytest.raises(TypeError):
        abw.get_word_count("not a dict")


def test_search_paragraph_rejects_non_str_query():
    with pytest.raises(TypeError):
        abw.search_paragraph(abw.create_abw(["x"]), 123)


# ===========================================================================
# 9. abw_installed_workflow
# ===========================================================================

def test_abw_installed_workflow_shape():
    result = abw.abw_installed_workflow(TWO_PARA)
    assert result["format"] == "abw"
    assert result["loaded"] is True
    assert result["paragraph_count"] == 2
    assert "section_count" in result


def test_abw_installed_workflow_minimal():
    result = abw.abw_installed_workflow(MINIMAL)
    assert result["paragraph_count"] == 1


def test_abw_installed_workflow_module_variant_reports_correct_section_count():
    # abw.abw_installed_workflow resolves (via __init__ import order) to the
    # abw_workflow module's variant, which reads model["sections"] (a key the
    # neutral model never populates) rather than model["section_count"], so
    # it always reports section_count=0. The abw_codec module-level variant
    # (shadowed in the package namespace) reads the correct field. Both are
    # pinned here so a fix to either implementation is caught as a behavior
    # change rather than silently passing.
    from abw import abw_codec as _abw_codec
    from abw import abw_workflow as _abw_workflow

    assert abw.abw_installed_workflow is _abw_workflow.abw_installed_workflow
    assert _abw_workflow.abw_installed_workflow(TWO_PARA)["section_count"] == 0
    assert _abw_codec.abw_installed_workflow(TWO_PARA)["section_count"] == 1


# ===========================================================================
# 10. Paragraph / Section spec-shaped iterators
# ===========================================================================

def test_abw_iter_paragraphs_yields_paragraph_objects():
    paras = list(abw.abw_iter_paragraphs(TWO_PARA))
    assert len(paras) == 2
    assert [p.text for p in paras] == ["First paragraph.", "Second paragraph."]
    assert paras[0].word_count == 2
    assert paras[0].char_count == len("First paragraph.")
    assert paras[0].is_empty() is False


def test_abw_iter_paragraphs_empty_document():
    paras = list(abw.abw_iter_paragraphs(EMPTY_SECTION))
    assert paras == []


def test_abw_iter_sections_single_section():
    sections = list(abw.abw_iter_sections(TWO_PARA))
    assert len(sections) == 1
    assert sections[0].paragraph_count == 2
    assert sections[0].paragraphs == ["First paragraph.", "Second paragraph."]
    assert sections[0].is_empty() is False


def test_abw_iter_sections_multi_section(multi_section_file):
    sections = list(abw.abw_iter_sections(multi_section_file))
    assert len(sections) == 2
    assert sections[0].index == 0
    assert sections[0].paragraph_count == 2
    assert sections[0].paragraphs == ["Alpha.", "Beta beta."]
    assert sections[1].index == 1
    assert sections[1].paragraph_count == 1
    assert sections[1].paragraphs == [_LONG_PARA]


def test_abw_iter_sections_paragraph_objects():
    sections = list(abw.abw_iter_sections(TWO_PARA))
    objs = sections[0].paragraph_objects()
    assert [p.text for p in objs] == ["First paragraph.", "Second paragraph."]


def test_abw_iter_paragraphs_multi_section(multi_section_file):
    paras = list(abw.abw_iter_paragraphs(multi_section_file))
    assert len(paras) == 3
    assert paras[2].char_count == len(_LONG_PARA)
    assert paras[2].word_count == 40


# ===========================================================================
# 11. AbwDocument domain model
# ===========================================================================

def test_abw_document_from_file_basic_properties():
    doc = abw.AbwDocument.from_file(TWO_PARA)
    assert doc.section_count == 1
    assert doc.paragraph_count == 2
    assert doc.paragraphs == ["First paragraph.", "Second paragraph."]
    assert doc.is_abw is True
    assert repr(doc) == "AbwDocument(section_count=1, paragraph_count=2)"


def test_abw_document_get_paragraph_in_and_out_of_range():
    doc = abw.AbwDocument.from_file(TWO_PARA)
    assert doc.get_paragraph(0) == "First paragraph."
    assert doc.get_paragraph(99) == ""
    assert doc.get_paragraph(-1) == ""


def test_abw_document_dimension_properties_two_paragraph():
    doc = abw.AbwDocument.from_file(TWO_PARA)
    assert doc.is_empty is False
    assert doc.has_content is True
    assert doc.is_single_paragraph is False
    assert doc.has_sections is True
    assert doc.has_multiple_paragraphs is True
    assert doc.is_multi_section is False


def test_abw_document_dimension_properties_minimal():
    doc = abw.AbwDocument.from_file(MINIMAL)
    assert doc.is_empty is False
    assert doc.is_single_paragraph is True
    assert doc.has_multiple_paragraphs is False


def test_abw_document_dimension_properties_empty():
    doc = abw.AbwDocument.from_file(EMPTY_SECTION)
    assert doc.is_empty is True
    assert doc.has_content is False
    assert doc.paragraph_count == 0
    assert doc.get_paragraph(0) == ""


def test_abw_document_text_content_properties():
    doc = abw.AbwDocument.from_file(TWO_PARA)
    assert doc.total_text_length == 33
    assert doc.avg_paragraph_length == pytest.approx(16.5)
    assert doc.has_long_paragraphs is False


def test_abw_document_scale_and_density_properties():
    doc = abw.AbwDocument.from_file(TWO_PARA)
    assert doc.is_large is False
    assert doc.is_text_heavy is False
    assert doc.paragraphs_per_section == pytest.approx(2.0)


def test_abw_document_content_balance_properties():
    doc = abw.AbwDocument.from_file(TWO_PARA)
    assert doc.avg_section_length == pytest.approx(33.0)
    assert doc.is_dense_text is False
    assert doc.is_sparse_text is True


def test_abw_document_structure_properties():
    doc = abw.AbwDocument.from_file(TWO_PARA)
    assert doc.is_moderate_text is False
    assert doc.has_rich_sections is False
    assert doc.is_long_document is False


def test_abw_document_properties_multi_section(multi_section_file):
    doc = abw.AbwDocument.from_file(multi_section_file)
    assert doc.section_count == 2
    assert doc.paragraph_count == 3
    assert doc.is_multi_section is True
    assert doc.has_long_paragraphs is True
    assert doc.total_text_length == 265
    assert doc.avg_paragraph_length == pytest.approx(265 / 3)
    assert doc.paragraphs_per_section == pytest.approx(1.5)
    assert doc.avg_section_length == pytest.approx(132.5)


def test_abw_document_add_paragraph_mutates_in_place():
    doc = abw.AbwDocument.from_file(TWO_PARA)
    doc.add_paragraph("Third paragraph.")
    assert doc.paragraph_count == 3
    assert doc.paragraphs[-1] == "Third paragraph."


def test_abw_document_add_paragraph_none_raises():
    doc = abw.AbwDocument.from_file(TWO_PARA)
    with pytest.raises(_CodecAbwError):
        doc.add_paragraph(None)


def test_abw_document_save_to_file_roundtrip(tmp_path):
    doc = abw.AbwDocument.from_file(TWO_PARA)
    doc.add_paragraph("Third paragraph.")
    dest = tmp_path / "saved.abw"
    doc.save_to_file(dest)
    assert dest.exists()
    reloaded = abw.AbwDocument.from_file(dest)
    assert reloaded.paragraph_count == 3
    assert reloaded.paragraphs[-1] == "Third paragraph."


def test_abw_document_save_to_file_empty_path_raises():
    doc = abw.AbwDocument.from_file(TWO_PARA)
    with pytest.raises(_CodecAbwError):
        doc.save_to_file("")


def test_abw_document_typed_children():
    doc = abw.AbwDocument.from_file(TWO_PARA)
    children = doc.typed_children()
    assert len(children) == 2
    assert [c.text for c in children] == ["First paragraph.", "Second paragraph."]
    assert children[0].word_count == 2
    assert children[0].upper() == "FIRST PARAGRAPH."
    assert children[0].lower() == "first paragraph."
    assert children[0].contains("First") is True
    assert children[0].contains("first", case_sensitive=False) is True


def test_abw_document_to_dict_returns_copy():
    doc = abw.AbwDocument.from_file(TWO_PARA)
    d = doc.to_dict()
    assert d == {
        "is_abw": True,
        "section_count": 1,
        "paragraph_count": 2,
        "paragraphs": ["First paragraph.", "Second paragraph."],
    }
    d["paragraphs"].append("mutated")
    # to_dict returns a shallow copy of the outer dict; the underlying
    # paragraphs list is shared, but paragraph_count is unaffected by
    # mutating the returned dict's list directly (no auto re-sync).
    assert doc.to_dict()["paragraph_count"] == 2


def test_abw_document_constructed_directly_from_dict():
    model = abw.create_abw(["One", "Two", "Three"])
    doc = abw.AbwDocument(model)
    assert doc.paragraph_count == 3
    assert doc.paragraphs == ["One", "Two", "Three"]


def test_abw_document_spec_metadata_class_vars():
    assert abw.AbwDocument.spec_qname == "abiword:document"
    assert abw.AbwDocument.spec_fact_ref == "FACT-ABW-001"
    assert "abisource" in abw.AbwDocument.namespace_uri
    assert abw.AbwDocument.local_name == "document"
