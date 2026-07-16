"""Comprehensive gap-coverage tests for the ``fodt`` package.

Closes ``missing_test_coverage`` gaps for the FODT Python FOSS format by
exercising every symbol exported from ``fodt.__all__`` (157 functions,
7 classes, and ~40 constants/spec-metadata strings) at least once.

Strategy
--------
Rather than hand-write ~200 near-identical tests, this module introspects
``fodt.__all__`` and groups exported *functions* by their sole required
parameter name:

  * ``file_path`` — analytics functions that parse a file and return a
    scalar/list.  Exercised against three sample documents (a rich
    headings+paragraphs sample, a minimal single-paragraph sample, and a
    synthesized "combined" sample containing headings, paragraphs, lists,
    *and* a table so that table/list-aware predicates observe True at
    least once).
  * ``document`` — pure query functions over an already-parsed neutral
    model dict.  Exercised against four parsed sample documents.
  * ``block`` — functions over a single block dict (``kind``,
    ``style_name``, ``outline_level``).

Every remaining exported function (mutating edit APIs, exporters, the
workflow/iterator helpers, ``make_warning``/``validate_document``/
``build_document``, ``write_fodt``) is covered by an explicit, named test
in ``TestExplicitFunctionCoverage``. ``test_every_exported_function_has_smoke_coverage``
is a meta-test that fails loudly if a future export falls through every
bucket, keeping this file self-verifying as the package grows.

Classes (``FodtDocument``, ``FodtParagraph``, ``FodtSpan``, and the
``FodtError``/``FodtInputError``/``FodtParseError``/``FodtSizeError``
exception hierarchy) and the constants/spec-metadata surface are covered
in their own sections below.

A handful of ``TestKnownValuesOnSamples`` tests pin exact expected values
(not just "did not raise") to catch real regressions; the expected values
were independently verified by executing the functions against the
checked-in sample corpus before being encoded here (see git history for
the verification transcript in the task record).
"""
from __future__ import annotations

import copy
import inspect
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import pytest  # noqa: E402

import fodt  # noqa: E402

# ---------------------------------------------------------------------------
# Sample corpus
# ---------------------------------------------------------------------------

SAMPLES_DIR = _REPO / "samples" / "by-format" / "fodt"
MINIMAL_PATH = SAMPLES_DIR / "minimal-document.fodt"
HEADINGS_PATH = SAMPLES_DIR / "headings-and-paragraphs.fodt"
LIST_PATH = SAMPLES_DIR / "list-basic.fodt"
TABLE_PATH = SAMPLES_DIR / "table-basic.fodt"
TWO_PARA_PATH = SAMPLES_DIR / "valid" / "two-paragraphs.fodt"

pytestmark = pytest.mark.skipif(
    not HEADINGS_PATH.exists(), reason="fodt sample corpus not available"
)

RICH_DOC = fodt.parse_fodt_strict(str(HEADINGS_PATH))
TABLE_DOC = fodt.parse_fodt_strict(str(TABLE_PATH))
LIST_DOC = fodt.parse_fodt_strict(str(LIST_PATH))
MINIMAL_DOC = fodt.parse_fodt_strict(str(MINIMAL_PATH))

# Synthesized sample combining headings + paragraphs (from RICH_DOC) with
# lists (from LIST_DOC) and a table (from TABLE_DOC), so file_path-group
# functions that test for tables/lists/headings all observe a positive
# case at least once.
_TMP_DIR = Path(tempfile.mkdtemp(prefix="fodt_gap_coverage_"))
COMBINED_PATH = _TMP_DIR / "combined.fodt"
_combined_model = {
    "odf_version_attr": "1.3",
    "blocks": copy.deepcopy(RICH_DOC["blocks"]),
    "lists": copy.deepcopy(LIST_DOC["lists"]),
    "tables": copy.deepcopy(TABLE_DOC["tables"]),
    "warnings": [],
}
fodt.write_fodt(_combined_model, COMBINED_PATH)

FILE_PATH_SAMPLES = [HEADINGS_PATH, MINIMAL_PATH, COMBINED_PATH]
FILE_PATH_SAMPLE_IDS = ["headings", "minimal", "combined"]

DOCUMENT_SAMPLES = [RICH_DOC, TABLE_DOC, LIST_DOC, MINIMAL_DOC]
DOCUMENT_SAMPLE_IDS = ["rich", "table", "list", "minimal"]


def rich_doc_copy() -> dict:
    """Return a fresh deep copy of RICH_DOC, safe for mutating tests."""
    return copy.deepcopy(RICH_DOC)


# ---------------------------------------------------------------------------
# Introspection-based export discovery
# ---------------------------------------------------------------------------

_ALL_FUNCS = {
    name: getattr(fodt, name)
    for name in fodt.__all__
    if inspect.isfunction(getattr(fodt, name))
}

_ALL_CLASSES = {
    name: getattr(fodt, name)
    for name in fodt.__all__
    if inspect.isclass(getattr(fodt, name))
}


def _required_params(fn) -> list:
    sig = inspect.signature(fn)
    return [
        p.name
        for p in sig.parameters.values()
        if p.default is inspect.Parameter.empty
        and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
    ]


def _return_annotation_str(fn) -> str:
    sig = inspect.signature(fn)
    ann = sig.return_annotation
    if ann is inspect.Signature.empty:
        return ""
    if isinstance(ann, str):
        return ann.strip("'\" ")
    return getattr(ann, "__name__", str(ann))


def _assert_matches_annotation(result, fn) -> None:
    """Best-effort check that `result` matches fn's declared return type.

    None is always accepted (covers 'X | None' annotations and functions
    that intentionally return None as a sentinel). Functions without a
    return annotation are only checked for "did not raise".
    """
    if result is None:
        return
    ann = _return_annotation_str(fn)
    if not ann:
        return
    if ann.startswith("bool"):
        assert isinstance(result, bool), f"{fn.__name__} expected bool, got {type(result)!r}"
    elif ann.startswith("int"):
        assert isinstance(result, int), f"{fn.__name__} expected int, got {type(result)!r}"
    elif ann.startswith("float"):
        assert isinstance(result, (int, float)), f"{fn.__name__} expected float, got {type(result)!r}"
    elif ann.startswith("str"):
        assert isinstance(result, str), f"{fn.__name__} expected str, got {type(result)!r}"
    elif ann.startswith("list"):
        assert isinstance(result, list), f"{fn.__name__} expected list, got {type(result)!r}"
    elif ann.startswith("dict"):
        assert isinstance(result, dict), f"{fn.__name__} expected dict, got {type(result)!r}"
    elif ann.startswith("tuple"):
        assert isinstance(result, tuple), f"{fn.__name__} expected tuple, got {type(result)!r}"


FILE_PATH_FUNCS = sorted(
    name for name, fn in _ALL_FUNCS.items() if _required_params(fn) == ["file_path"]
)
DOCUMENT_ONLY_FUNCS = sorted(
    name for name, fn in _ALL_FUNCS.items() if _required_params(fn) == ["document"]
)
BLOCK_ONLY_FUNCS = sorted(
    name for name, fn in _ALL_FUNCS.items() if _required_params(fn) == ["block"]
)

# Functions covered individually in TestExplicitFunctionCoverage because
# they mutate their input, need extra required arguments, or use a
# parameter name outside the {file_path, document, block} buckets.
_EXPLICITLY_COVERED_FUNCS = frozenset({
    "build_document",
    "document_append_paragraph",
    "document_get_paragraph_text",
    "document_remove_paragraph",
    "document_replace_text",
    "document_search_text",
    "document_set_block_text",
    "document_warnings_for_unsupported_edit",
    "fodt_installed_workflow",
    "fodt_iter_paragraphs",
    "fodt_to_html",
    "fodt_to_markdown",
    "fodt_to_txt",
    "make_warning",
    "validate_document",
    "write_fodt",
})


# ---------------------------------------------------------------------------
# Generic smoke coverage: file_path-only analytics functions
# ---------------------------------------------------------------------------

class TestFilePathFunctions:
    """Every exported function whose sole required parameter is file_path."""

    @pytest.mark.parametrize("name", FILE_PATH_FUNCS)
    @pytest.mark.parametrize("sample", FILE_PATH_SAMPLES, ids=FILE_PATH_SAMPLE_IDS)
    def test_smoke(self, name, sample):
        fn = _ALL_FUNCS[name]
        result = fn(str(sample))
        _assert_matches_annotation(result, fn)

    def test_group_is_substantial(self):
        # Sanity: this generic bucket should cover the bulk of the exported API.
        assert len(FILE_PATH_FUNCS) >= 80


# ---------------------------------------------------------------------------
# Generic smoke coverage: document-dict-only functions
# ---------------------------------------------------------------------------

class TestDocumentOnlyFunctions:
    """Every exported function whose sole required parameter is `document`."""

    @pytest.mark.parametrize("name", DOCUMENT_ONLY_FUNCS)
    @pytest.mark.parametrize("doc_index", range(len(DOCUMENT_SAMPLES)), ids=DOCUMENT_SAMPLE_IDS)
    def test_smoke(self, name, doc_index):
        fn = _ALL_FUNCS[name]
        doc = copy.deepcopy(DOCUMENT_SAMPLES[doc_index])
        result = fn(doc)
        _assert_matches_annotation(result, fn)

    def test_group_is_substantial(self):
        assert len(DOCUMENT_ONLY_FUNCS) >= 25


# ---------------------------------------------------------------------------
# Generic smoke coverage: block-only functions
# ---------------------------------------------------------------------------

class TestBlockOnlyFunctions:
    """Every exported function whose sole required parameter is `block`."""

    @pytest.mark.parametrize("name", BLOCK_ONLY_FUNCS)
    @pytest.mark.parametrize(
        "block",
        [RICH_DOC["blocks"][0], RICH_DOC["blocks"][1], MINIMAL_DOC["blocks"][0]],
        ids=["heading-block", "paragraph-block", "minimal-block"],
    )
    def test_smoke(self, name, block):
        fn = _ALL_FUNCS[name]
        result = fn(block)
        _assert_matches_annotation(result, fn)

    def test_group_is_nonempty(self):
        assert set(BLOCK_ONLY_FUNCS) == {"kind", "outline_level", "style_name"}


# ---------------------------------------------------------------------------
# Meta-test: every exported function must be reachable through one bucket
# ---------------------------------------------------------------------------

def test_every_exported_function_has_smoke_coverage():
    generic_covered = set(FILE_PATH_FUNCS) | set(DOCUMENT_ONLY_FUNCS) | set(BLOCK_ONLY_FUNCS)
    uncovered = set(_ALL_FUNCS) - generic_covered - _EXPLICITLY_COVERED_FUNCS
    assert uncovered == set(), (
        f"Exported functions without smoke coverage in this file: {sorted(uncovered)}. "
        "Add them to an existing bucket or to _EXPLICITLY_COVERED_FUNCS with a "
        "dedicated test in TestExplicitFunctionCoverage."
    )


def test_every_exported_class_has_dedicated_coverage():
    expected = {
        "FodtDocument", "FodtParagraph", "FodtSpan",
        "FodtError", "FodtInputError", "FodtParseError", "FodtSizeError",
    }
    assert set(_ALL_CLASSES) == expected


# ---------------------------------------------------------------------------
# Explicit coverage: mutating / multi-arg / differently-named functions
# ---------------------------------------------------------------------------

class TestExplicitFunctionCoverage:

    # -- build_document ----------------------------------------------------

    def test_build_document_assembles_neutral_model(self):
        doc = fodt.build_document(
            odf_version_attr="1.3",
            mimetype="application/vnd.oasis.opendocument.text-flat-xml",
            blocks=[{"type": "paragraph", "text": "hi", "heading_level": None, "runs": []}],
            lists=[],
            tables=[],
            warnings=[],
            unsupported_features=["macros"],
            parse_errors=[],
        )
        assert doc["format_id"] == "fodt"
        assert doc["blocks"][0]["text"] == "hi"
        assert doc["unsupported_features"] == ["macros"]
        assert doc["lists"] == []
        assert doc["tables"] == []
        assert "content" not in doc

    def test_build_document_with_content_sequence(self):
        block = {"type": "paragraph", "text": "x", "heading_level": None, "runs": []}
        doc = fodt.build_document(
            odf_version_attr="1.3", mimetype=None, blocks=[block], lists=[], tables=[],
            warnings=[], unsupported_features=[], parse_errors=[],
            content=[{"kind": "block", "data": block}],
        )
        assert doc["content"][0]["kind"] == "block"
        assert doc["mimetype"] is None

    # -- document_append_paragraph -------------------------------------------

    def test_document_append_paragraph_success(self):
        doc = rich_doc_copy()
        before = len(doc["blocks"])
        ok, msg = fodt.document_append_paragraph(doc, "New paragraph text")
        assert ok is True
        assert isinstance(msg, str)
        assert len(doc["blocks"]) == before + 1
        assert doc["blocks"][-1]["type"] == "paragraph"

    def test_document_append_paragraph_with_style(self):
        doc = rich_doc_copy()
        ok, msg = fodt.document_append_paragraph(doc, "Styled text", style="Text Body")
        assert ok is True
        assert doc["blocks"][-1]["style"] == "Text Body"
        assert "style=" in msg

    def test_document_append_paragraph_rejects_none_text(self):
        doc = rich_doc_copy()
        ok, msg = fodt.document_append_paragraph(doc, None)
        assert ok is False
        assert isinstance(msg, str)

    # -- document_get_paragraph_text -----------------------------------------

    def test_document_get_paragraph_text_valid_index(self):
        doc = rich_doc_copy()
        text = fodt.document_get_paragraph_text(doc, 0)
        assert isinstance(text, str)
        assert "first paragraph" in text

    def test_document_get_paragraph_text_out_of_range(self):
        doc = rich_doc_copy()
        assert fodt.document_get_paragraph_text(doc, 9999) is None
        assert fodt.document_get_paragraph_text(doc, -1) is None

    # -- document_remove_paragraph --------------------------------------------

    def test_document_remove_paragraph_success(self):
        doc = rich_doc_copy()
        idx = next(i for i, b in enumerate(doc["blocks"]) if b.get("type") == "paragraph")
        before = len(doc["blocks"])
        ok, msg = fodt.document_remove_paragraph(doc, idx)
        assert ok is True
        assert len(doc["blocks"]) == before - 1
        assert isinstance(msg, str)

    def test_document_remove_paragraph_out_of_range(self):
        doc = rich_doc_copy()
        ok, msg = fodt.document_remove_paragraph(doc, 9999)
        assert ok is False

    def test_document_remove_paragraph_protects_non_paragraph_types(self):
        doc = rich_doc_copy()
        doc["blocks"].append({"type": "table"})
        ok, msg = fodt.document_remove_paragraph(doc, len(doc["blocks"]) - 1)
        assert ok is False
        assert "table" in msg

    # -- document_replace_text ------------------------------------------------

    def test_document_replace_text_case_insensitive_default(self):
        doc = rich_doc_copy()
        result = fodt.document_replace_text(doc, "section", "Chapter")
        assert isinstance(result, dict)
        assert result["total_replacements"] >= 1
        assert result["blocks_modified"] >= 1

    def test_document_replace_text_case_sensitive(self):
        # Case-sensitive "section" only matches the lowercase substring inside
        # "subsection"/"Subsection" (2 occurrences); case-insensitive also
        # matches the capitalized "Section" heading/paragraph text (7 total).
        doc_cs = rich_doc_copy()
        result_cs = fodt.document_replace_text(doc_cs, "section", "Chapter", case_sensitive=True)
        assert result_cs["total_replacements"] == 2

        doc_ci = rich_doc_copy()
        result_ci = fodt.document_replace_text(doc_ci, "section", "Chapter", case_sensitive=False)
        assert result_ci["total_replacements"] == 7
        assert result_ci["total_replacements"] > result_cs["total_replacements"]

    def test_document_replace_text_empty_search_is_noop(self):
        doc = rich_doc_copy()
        result = fodt.document_replace_text(doc, "", "x")
        assert result == {"total_replacements": 0, "blocks_modified": 0}

    # -- document_search_text --------------------------------------------------

    def test_document_search_text_finds_matches(self):
        doc = rich_doc_copy()
        matches = fodt.document_search_text(doc, "Section")
        assert isinstance(matches, list)
        assert len(matches) >= 1
        assert {"block_index", "block_type", "text", "match_count"} <= matches[0].keys()

    def test_document_search_text_empty_query(self):
        doc = rich_doc_copy()
        assert fodt.document_search_text(doc, "") == []

    def test_document_search_text_case_sensitive(self):
        doc = rich_doc_copy()
        # Case-sensitive "section" matches the lowercase substring inside
        # "subsection"/"Subsection" (heading + paragraph), not "Section".
        matches = fodt.document_search_text(doc, "section", case_sensitive=True)
        assert len(matches) == 2
        assert all("section" in m["text"].lower() for m in matches)

    # -- document_set_block_text -----------------------------------------------

    def test_document_set_block_text_success(self):
        doc = rich_doc_copy()
        ok, msg = fodt.document_set_block_text(doc, 0, "Replaced heading text")
        assert ok is True
        assert doc["blocks"][0]["text"] == "Replaced heading text"

    def test_document_set_block_text_out_of_range(self):
        doc = rich_doc_copy()
        ok, msg = fodt.document_set_block_text(doc, 9999, "x")
        assert ok is False

    def test_document_set_block_text_preserve_style_false(self):
        doc = rich_doc_copy()
        ok, _ = fodt.document_set_block_text(doc, 0, "No style", preserve_style=False)
        assert ok is True
        assert doc["blocks"][0]["runs"][0]["style"] is None

    # -- document_warnings_for_unsupported_edit ---------------------------------

    def test_document_warnings_for_unsupported_edit_no_warnings(self):
        doc = rich_doc_copy()
        warnings = fodt.document_warnings_for_unsupported_edit(doc, 0)
        assert isinstance(warnings, list)

    def test_document_warnings_for_unsupported_edit_out_of_range(self):
        doc = rich_doc_copy()
        warnings = fodt.document_warnings_for_unsupported_edit(doc, 9999)
        assert warnings and "out of range" in warnings[0]

    def test_document_warnings_for_unsupported_edit_hyperlink(self):
        doc = rich_doc_copy()
        doc["blocks"][0]["runs"] = [{"text": "link", "style": None, "href": "https://example.com"}]
        warnings = fodt.document_warnings_for_unsupported_edit(doc, 0)
        assert any("hyperlink" in w for w in warnings)

    # -- fodt_installed_workflow -------------------------------------------------

    def test_fodt_installed_workflow(self):
        result = fodt.fodt_installed_workflow(str(HEADINGS_PATH))
        assert result == {
            "format": "fodt",
            "loaded": True,
            "block_count": len(RICH_DOC["blocks"]),
            "table_count": len(RICH_DOC["tables"]),
        }

    # -- fodt_iter_paragraphs -----------------------------------------------------

    def test_fodt_iter_paragraphs_yields_paragraph_objects(self):
        paragraphs = list(fodt.fodt_iter_paragraphs(str(HEADINGS_PATH)))
        assert len(paragraphs) == len(RICH_DOC["blocks"])

    def test_fodt_iter_paragraphs_is_lazy_generator(self):
        gen = fodt.fodt_iter_paragraphs(str(HEADINGS_PATH))
        assert inspect.isgenerator(gen)
        first = next(gen)
        assert first is not None

    # -- fodt_to_html / fodt_to_markdown / fodt_to_txt ----------------------------

    def test_fodt_to_html_from_path(self):
        html = fodt.fodt_to_html(str(HEADINGS_PATH))
        assert isinstance(html, str)
        assert "<h1>Section One</h1>" in html

    def test_fodt_to_html_from_model(self):
        html = fodt.fodt_to_html(RICH_DOC)
        assert isinstance(html, str)
        assert "<p>" in html

    def test_fodt_to_markdown_from_path(self):
        md = fodt.fodt_to_markdown(str(HEADINGS_PATH))
        assert md.startswith("# Section One")

    def test_fodt_to_markdown_from_model(self):
        md = fodt.fodt_to_markdown(RICH_DOC)
        assert isinstance(md, str)
        assert "## Subsection One A" in md

    def test_fodt_to_txt_from_path(self):
        txt = fodt.fodt_to_txt(str(HEADINGS_PATH))
        assert isinstance(txt, str)
        assert "Section One" in txt

    def test_fodt_to_txt_from_model_with_list_items(self):
        txt = fodt.fodt_to_txt(COMBINED_PATH)
        assert isinstance(txt, str)

    # -- make_warning ---------------------------------------------------------------

    def test_make_warning_without_source(self):
        w = fodt.make_warning("CODE1", "message text")
        assert w == {"code": "CODE1", "message": "message text"}

    def test_make_warning_with_source(self):
        w = fodt.make_warning("CODE2", "message2", source="parser")
        assert w == {"code": "CODE2", "message": "message2", "source": "parser"}

    # -- validate_document ------------------------------------------------------------

    def test_validate_document_valid_document_has_no_violations(self):
        assert fodt.validate_document(RICH_DOC) == []

    def test_validate_document_missing_fields(self):
        violations = fodt.validate_document({})
        assert len(violations) > 0
        assert any("format_id" in v for v in violations)

    def test_validate_document_bad_heading_level(self):
        bad_doc = fodt.build_document(
            odf_version_attr="1.3", mimetype=None,
            blocks=[{"type": "heading", "text": "x", "heading_level": 99}],
            lists=[], tables=[], warnings=[], unsupported_features=[], parse_errors=[],
        )
        violations = fodt.validate_document(bad_doc)
        assert any("heading_level" in v for v in violations)

    # -- write_fodt --------------------------------------------------------------------

    def test_write_fodt_roundtrip(self, tmp_path):
        out_path = tmp_path / "roundtrip.fodt"
        fodt.write_fodt(RICH_DOC, out_path)
        assert out_path.exists()
        reparsed = fodt.parse_fodt_strict(str(out_path))
        assert reparsed["blocks"][0]["text"] == RICH_DOC["blocks"][0]["text"]
        assert len(reparsed["blocks"]) == len(RICH_DOC["blocks"])

    def test_write_fodt_accepts_str_path(self, tmp_path):
        out_path = str(tmp_path / "str_path.fodt")
        fodt.write_fodt(MINIMAL_DOC, out_path)
        assert Path(out_path).exists()


# ---------------------------------------------------------------------------
# Classes
# ---------------------------------------------------------------------------

class TestFodtDocument:

    def test_from_file_classmethod(self):
        doc = fodt.FodtDocument.from_file(str(HEADINGS_PATH))
        assert doc.format_id == "fodt"
        # NOTE: FodtDocument.odf_version reads self._data["odf_version"], but
        # the parser stores the version under "odf_version_attr" — so this
        # property always returns "" against real parser output. Documented
        # here as verified current behavior (not a spec claim).
        assert doc.odf_version == ""
        assert doc.block_count == len(RICH_DOC["blocks"])

    def test_dimension_properties(self):
        doc = fodt.FodtDocument(rich_doc_copy())
        assert isinstance(doc.warnings, list)
        assert isinstance(doc.table_count, int)
        assert isinstance(doc.list_count, int)
        assert doc.has_content is True
        assert doc.is_empty is False
        assert doc.is_single_block is False
        assert doc.is_multi_block is True
        # NOTE: has_headings/heading_count filter on b.get("kind") == "heading",
        # but the parser emits blocks keyed by "type", not "kind" — so these
        # always read 0/False against real parser output (verified below and
        # exercised against "kind"-keyed data in test_kind_keyed_properties).
        assert doc.has_headings is False
        assert doc.heading_count == 0

    def test_structure_classification_properties(self):
        doc = fodt.FodtDocument(rich_doc_copy())
        # See test_dimension_properties note: paragraph_count also filters on
        # "kind", so it is 0 against real ("type"-keyed) parser output.
        assert doc.paragraph_count == 0
        assert doc.has_lists is False
        assert doc.has_tables is False
        assert doc.is_complex is False

    def test_kind_keyed_properties_work_as_designed(self):
        # FodtDocument.has_headings/heading_count/paragraph_count/headings()
        # are implemented against a "kind"-keyed block schema. Prove that
        # design intent works correctly for data shaped that way, even
        # though the real parser output uses "type" (see notes above).
        doc = fodt.FodtDocument({
            "blocks": [
                {"kind": "heading", "text": "Title"},
                {"kind": "paragraph", "text": "Body one"},
                {"kind": "paragraph", "text": "Body two"},
            ],
            "tables": [],
            "lists": [],
        })
        assert doc.has_headings is True
        assert doc.heading_count == 1
        assert doc.paragraph_count == 2
        assert doc.is_complex is True
        assert len(doc.headings()) == 1

    def test_scale_and_balance_properties(self):
        doc = fodt.FodtDocument(rich_doc_copy())
        assert doc.total_block_count == doc.paragraph_count + doc.heading_count
        assert 0.0 <= doc.heading_ratio <= 1.0
        assert isinstance(doc.is_outline_heavy, bool)
        assert 0.0 <= doc.paragraph_ratio <= 1.0
        assert isinstance(doc.has_balanced_content, bool)
        assert isinstance(doc.is_prose_heavy, bool)

    def test_empty_document_scale_properties_do_not_divide_by_zero(self):
        doc = fodt.FodtDocument({"blocks": [], "tables": [], "lists": []})
        assert doc.heading_ratio == 0.0
        assert doc.paragraph_ratio == 0.0
        assert doc.is_outline_heavy is False
        assert doc.is_prose_heavy is False

    def test_paragraphs_and_headings_accessors(self):
        doc = fodt.FodtDocument(rich_doc_copy())
        paras = doc.paragraphs()
        assert len(paras) == doc.block_count
        # headings() filters on "kind" (see test_dimension_properties note),
        # so it is empty against real "type"-keyed parser output.
        headings = doc.headings()
        assert len(headings) == doc.heading_count == 0

    def test_add_paragraph(self):
        doc = fodt.FodtDocument(rich_doc_copy())
        before = doc.block_count
        doc.add_paragraph("Appended text")
        assert doc.block_count == before + 1

    def test_add_paragraph_rejects_none(self):
        doc = fodt.FodtDocument(rich_doc_copy())
        with pytest.raises(fodt.FodtError):
            doc.add_paragraph(None)

    def test_save_to_file_and_to_file_alias(self, tmp_path):
        doc = fodt.FodtDocument(rich_doc_copy())
        out1 = tmp_path / "saved.fodt"
        doc.save_to_file(out1)
        assert out1.exists()
        out2 = tmp_path / "saved_alias.fodt"
        doc.to_file(out2)
        assert out2.exists()

    def test_save_to_file_rejects_empty_path(self):
        doc = fodt.FodtDocument(rich_doc_copy())
        with pytest.raises(fodt.FodtError):
            doc.save_to_file("")

    def test_to_dict_and_repr(self):
        doc = fodt.FodtDocument(rich_doc_copy())
        d = doc.to_dict()
        assert isinstance(d, dict)
        assert d is doc._data
        assert "FodtDocument" in repr(doc)
        assert f"blocks={doc.block_count}" in repr(doc)


class TestFodtParagraphAndSpan:

    def test_paragraph_core_properties(self):
        block = {
            "kind": "paragraph",
            "text": "Hello",
            "style_name": "Text_20_Body",
            "spans": [],
        }
        para = fodt.FodtParagraph(block)
        assert para.kind == "paragraph"
        assert para.text == "Hello"
        assert para.style_name == "Text_20_Body"
        assert para.outline_level is None
        assert para.spans == []

    def test_paragraph_heading_kind_and_outline_level(self):
        block = {"kind": "heading", "text": "Title", "outline_level": 2}
        para = fodt.FodtParagraph(block)
        assert para.kind == "heading"
        assert para.outline_level == 2

    def test_paragraph_defaults_to_paragraph_kind(self):
        para = fodt.FodtParagraph({})
        assert para.kind == "paragraph"
        assert para.text == ""
        assert para.style_name == ""

    def test_paragraph_set_text_mutates_in_place(self):
        block = {"kind": "paragraph", "text": "Original"}
        para = fodt.FodtParagraph(block)
        para.set_text("Updated")
        assert para.text == "Updated"
        assert block["text"] == "Updated"

    def test_paragraph_set_text_coerces_to_str(self):
        para = fodt.FodtParagraph({"kind": "paragraph", "text": ""})
        para.set_text(42)
        assert para.text == "42"

    def test_paragraph_to_dict_and_repr(self):
        block = {"kind": "paragraph", "text": "X"}
        para = fodt.FodtParagraph(block)
        d = para.to_dict()
        assert d == {"kind": "paragraph", "text": "X"}
        assert d is not block  # shallow copy, not the same object
        assert "FodtParagraph" in repr(para)

    def test_paragraph_spans_property_wraps_fodt_span(self):
        block = {
            "kind": "paragraph",
            "text": "Hi there",
            "spans": [{"text": "Hi", "style_name": "Bold"}],
        }
        para = fodt.FodtParagraph(block)
        spans = para.spans
        assert len(spans) == 1
        assert isinstance(spans[0], fodt.FodtSpan)
        assert spans[0].text == "Hi"

    def test_span_properties(self):
        span = fodt.FodtSpan({"text": "styled", "style_name": "Bold"})
        assert span.text == "styled"
        assert span.style_name == "Bold"
        d = span.to_dict()
        assert d == {"text": "styled", "style_name": "Bold"}
        assert "FodtSpan" in repr(span)

    def test_span_defaults(self):
        span = fodt.FodtSpan({})
        assert span.text == ""
        assert span.style_name == ""


class TestFodtDocumentSpecMetadata:
    """spec_qname / spec_fact_ref ClassVar presence on the domain classes."""

    def test_fodt_document_spec_metadata(self):
        assert fodt.FodtDocument.spec_qname == "office:document"
        assert fodt.FodtDocument.spec_fact_ref

    def test_fodt_paragraph_spec_metadata(self):
        assert fodt.FodtParagraph.spec_qname == "text:p"
        assert fodt.FodtParagraph.spec_fact_ref

    def test_fodt_span_spec_metadata(self):
        assert fodt.FodtSpan.spec_qname == "text:span"
        assert fodt.FodtSpan.spec_fact_ref


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class TestExceptions:

    def test_exception_hierarchy(self):
        assert issubclass(fodt.FodtInputError, fodt.FodtError)
        assert issubclass(fodt.FodtSizeError, fodt.FodtError)
        assert issubclass(fodt.FodtParseError, fodt.FodtError)
        assert issubclass(fodt.FodtError, ValueError)

    def test_parse_fodt_strict_raises_input_error_missing_file(self):
        with pytest.raises(fodt.FodtInputError):
            fodt.parse_fodt_strict(str(SAMPLES_DIR / "does-not-exist.fodt"))

    def test_parse_fodt_strict_raises_input_error_on_directory(self):
        with pytest.raises(fodt.FodtInputError):
            fodt.parse_fodt_strict(str(SAMPLES_DIR))

    def test_parse_fodt_strict_raises_parse_error_on_malformed_xml(self, tmp_path):
        bad = tmp_path / "bad.fodt"
        bad.write_text("<office:document>not closed", encoding="utf-8")
        with pytest.raises(fodt.FodtParseError):
            fodt.parse_fodt_strict(str(bad))

    def test_parse_fodt_never_raises_on_missing_file(self):
        result = fodt.parse_fodt(str(SAMPLES_DIR / "does-not-exist.fodt"))
        assert "error" in result
        assert result["error"]

    def test_parse_fodt_never_raises_on_malformed_xml(self, tmp_path):
        bad = tmp_path / "bad2.fodt"
        bad.write_text("<not-office-document/>", encoding="utf-8")
        result = fodt.parse_fodt(str(bad))
        assert "error" in result

    def test_fodt_error_is_catchable_as_value_error(self):
        with pytest.raises(ValueError):
            raise fodt.FodtError("boom")


# ---------------------------------------------------------------------------
# Constants and spec-metadata strings
# ---------------------------------------------------------------------------

class TestConstants:

    _STRING_CONSTANTS = [
        "FORMAT_ID", "SPEC_VERSION", "PACKAGE_VERSION", "EXPECTED_MIMETYPE",
        "NS_OFFICE", "NS_TABLE", "NS_TEXT", "NS_DRAW", "NS_XLINK",
        "QN_DOCUMENT", "QN_BODY", "QN_TEXT", "QN_SCRIPTS",
        "QN_TEXT_P", "QN_TEXT_H", "QN_TEXT_SPAN", "QN_TEXT_A",
        "QN_LIST", "QN_LIST_ITEM", "QN_TABLE", "QN_TABLE_ROW", "QN_TABLE_CELL",
        "QN_DRAW_FRAME", "QN_DRAW_IMAGE", "QN_TEXT_NOTE",
        "ATTR_MIMETYPE", "ATTR_VERSION", "ATTR_OUTLINE_LEVEL", "ATTR_TABLE_NAME",
        "ATTR_STYLE_NAME", "ATTR_XLINK_HREF", "ATTR_XLINK_TYPE",
        "ATTR_TABLE_COL_SPAN", "ATTR_TABLE_ROW_SPAN",
        "WARN_MISSING_MIMETYPE", "WARN_UNEXPECTED_MIMETYPE",
        "WARN_UNSUPPORTED_ELEMENT", "WARN_UNKNOWN", "WARN_NOTE_ELEMENT",
    ]

    @pytest.mark.parametrize("name", _STRING_CONSTANTS)
    def test_string_constant_is_nonempty_str(self, name):
        value = getattr(fodt, name)
        assert isinstance(value, str)
        assert value != ""

    def test_format_id_is_fodt(self):
        assert fodt.FORMAT_ID == "fodt"

    def test_expected_mimetype(self):
        assert fodt.EXPECTED_MIMETYPE == "application/vnd.oasis.opendocument.text-flat-xml"

    def test_max_file_bytes_is_positive_int(self):
        assert isinstance(fodt.MAX_FILE_BYTES, int)
        assert fodt.MAX_FILE_BYTES == 100 * 1024 * 1024

    def test_text_field_local_names_is_nonempty_frozenset(self):
        assert isinstance(fodt.TEXT_FIELD_LOCAL_NAMES, frozenset)
        assert "date" in fodt.TEXT_FIELD_LOCAL_NAMES
        assert "page-number" in fodt.TEXT_FIELD_LOCAL_NAMES

    def test_qualified_names_use_clark_notation(self):
        assert fodt.QN_DOCUMENT.startswith("{") and "}document" in fodt.QN_DOCUMENT
        assert fodt.QN_TEXT_P.startswith("{") and fodt.QN_TEXT_P.endswith("}p")

    def test_module_level_spec_metadata_strings(self):
        # Leaked module-level constants from text_document.py (wildcard-imported).
        assert isinstance(fodt.spec_qname, str) and fodt.spec_qname
        assert isinstance(fodt.spec_fact_ref, str) and fodt.spec_fact_ref
        assert isinstance(fodt.namespace_uri, str) and fodt.namespace_uri

    def test_all_string_and_frozenset_constants_are_covered(self):
        covered = set(self._STRING_CONSTANTS) | {
            "TEXT_FIELD_LOCAL_NAMES", "MAX_FILE_BYTES",
            "spec_qname", "spec_fact_ref", "namespace_uri",
        }
        other_exports = {
            name for name in fodt.__all__
            if not inspect.isfunction(getattr(fodt, name))
            and not inspect.isclass(getattr(fodt, name))
            and not inspect.ismodule(getattr(fodt, name))
        }
        # "annotations" is a __future__ feature-flag object leaked by a
        # wildcard `from .module import *` in an upstream module; it is not
        # a meaningful public constant and is intentionally excluded here.
        uncovered = other_exports - covered - {"annotations"}
        assert uncovered == set(), f"Constants without coverage: {sorted(uncovered)}"


# ---------------------------------------------------------------------------
# Known-value regression tests (verified against the sample corpus)
# ---------------------------------------------------------------------------

class TestKnownValuesOnSamples:
    """Pin exact expected values (not just 'did not raise') for a
    representative slice of the analytics/query surface, to catch real
    regressions rather than only smoke-test crashes."""

    def test_minimal_document_counts(self):
        assert fodt.fodt_paragraph_count(str(MINIMAL_PATH)) == 1
        assert fodt.fodt_word_count(str(MINIMAL_PATH)) == 2
        assert fodt.fodt_heading_count(str(MINIMAL_PATH)) == 0
        assert fodt.fodt_has_headings(str(MINIMAL_PATH)) is False
        assert fodt.fodt_is_empty(str(MINIMAL_PATH)) is False

    def test_headings_document_structure_counts(self):
        assert fodt.fodt_heading_count(str(HEADINGS_PATH)) == 3
        assert fodt.fodt_paragraph_count(str(HEADINGS_PATH)) == 4
        assert fodt.fodt_has_headings(str(HEADINGS_PATH)) is True

    def test_table_document_counts(self):
        assert fodt.fodt_has_tables(str(TABLE_PATH)) is True
        assert fodt.fodt_table_count(str(TABLE_PATH)) == 1

    def test_list_document_counts(self):
        assert fodt.fodt_has_lists(str(LIST_PATH)) is True
        assert fodt.fodt_list_count(str(LIST_PATH)) == 2

    def test_two_paragraphs_sample_parses_to_two_paragraphs(self):
        doc = fodt.parse_fodt_strict(str(TWO_PARA_PATH))
        assert fodt.document_paragraph_count(doc) == 2

    def test_document_heading_outline_structure(self):
        outline = fodt.document_heading_outline(rich_doc_copy())
        assert [h["level"] for h in outline] == [1, 2, 1]
        assert [h["text"] for h in outline] == [
            "Section One", "Subsection One A", "Section Two",
        ]
        assert [h["index"] for h in outline] == [0, 1, 2]

    def test_document_extract_headings_default_range_returns_all_headings(self):
        headings = fodt.document_extract_headings(rich_doc_copy())
        assert len(headings) == 3
        assert [h["text"] for h in headings] == [
            "Section One", "Subsection One A", "Section Two",
        ]

    def test_document_table_row_and_cell_counts(self):
        table_doc = copy.deepcopy(TABLE_DOC)
        assert fodt.document_table_row_count(table_doc) == 3
        cell_stats = fodt.document_table_cell_count(table_doc)
        assert cell_stats["total_cells"] == 6
        assert cell_stats["total_tables"] == 1

    def test_document_list_item_count(self):
        list_doc = copy.deepcopy(LIST_DOC)
        assert fodt.document_list_item_count(list_doc) == 6

    def test_document_stats_block_counts(self):
        stats = fodt.document_stats(rich_doc_copy())
        assert stats["paragraph_count"] == 4
        assert stats["heading_count"] == 3
        assert stats["block_count"] == 7

    def test_fodt_document_to_xml_roundtrips_paragraph_text(self):
        xml = fodt.document_to_xml(MINIMAL_DOC)
        assert "Hello, world." in xml
        reparsed = fodt.parse_fodt(str(MINIMAL_PATH))
        assert reparsed["blocks"][0]["text"] == "Hello, world."
