"""Comprehensive coverage test for ipynb codec/model/analytics surface.

Closes the gap-ledger ``missing_test_coverage`` findings for the full
ipynb capability set (GAP-IPYNB-FOSS-*): roundtrip, probe_ipynb,
get_cell_count, get_code_cells, get_markdown_cells, load_ipynb,
write_ipynb, ipynb_installed_workflow, ensure_cell_id,
get_output_representation, add_output_representation,
remove_output_mime_type, validate_notebook_schema, IpynbDocument,
IpynbError, IpynbParseError, IpynbWriteError, IpynbValidationError,
ipynb_average_source_length, ipynb_cell_type_histogram,
ipynb_has_execution_errors, ipynb_output_type_histogram.

This file is deliberately complementary to the existing per-topic suites
(test_ipynb_codec.py, test_ipynb_analytics.py, test_ipynb_validation.py,
test_ipynb_cell_id.py, test_ipynb_output_mime_api.py,
test_ipynb_document_mutation.py, test_ipynb_mutation_api.py) rather than
a duplicate of them: it targets edge cases, exception-hierarchy behavior,
and full end-to-end pipelines those files do not already exercise —
most notably the two real IpynbWriteError-raising paths (unserializable
model content, unwritable destination path), which no other test file
in this package currently triggers.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
import sys

sys.path.insert(0, str(_REPO / "src" / "python"))

SAMPLES = _REPO / "samples" / "by-format" / "ipynb"
VALID_DIR = SAMPLES / "valid"
INVALID_DIR = SAMPLES / "invalid"


def _nb(cells: list[dict]) -> bytes:
    return json.dumps(
        {"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": cells}
    ).encode("utf-8")


# --- roundtrip ---------------------------------------------------------


class TestRoundtripComprehensive:
    def test_roundtrip_returns_a_load_ipynb_shaped_dict(self):
        pytest.importorskip("ipynb")
        from ipynb.ipynb_codec import roundtrip

        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.ipynb"
            result = roundtrip(VALID_DIR / "minimal.ipynb", dest)
        assert set(result.keys()) >= {"nbformat", "nbformat_minor", "metadata", "cells"}

    def test_roundtrip_with_outputs_sample_preserves_output_count(self):
        from ipynb.ipynb_codec import load_ipynb, roundtrip

        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.ipynb"
            original = load_ipynb(VALID_DIR / "with-outputs.ipynb")
            reloaded = roundtrip(VALID_DIR / "with-outputs.ipynb", dest)

        orig_outputs = sum(len(c.get("outputs", [])) for c in original["cells"])
        new_outputs = sum(len(c.get("outputs", [])) for c in reloaded["cells"])
        assert orig_outputs == new_outputs
        assert orig_outputs > 0

    def test_roundtrip_from_bytes_source(self):
        from ipynb.ipynb_codec import roundtrip

        data = _nb([{"cell_type": "code", "source": "x = 1", "metadata": {}}])
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.ipynb"
            result = roundtrip(data, dest)
        assert result["cells"][0]["source"] == "x = 1"

    def test_roundtrip_actually_writes_file_to_dest(self):
        from ipynb.ipynb_codec import roundtrip

        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.ipynb"
            assert not dest.exists()
            roundtrip(VALID_DIR / "code-and-markdown.ipynb", dest)
            assert dest.exists()
            assert dest.stat().st_size > 0

    def test_roundtrip_dest_as_string_path(self):
        from ipynb.ipynb_codec import roundtrip

        with tempfile.TemporaryDirectory() as td:
            dest = str(Path(td) / "out.ipynb")
            result = roundtrip(VALID_DIR / "minimal.ipynb", dest)
        assert result["nbformat"] == 4

    def test_roundtrip_propagates_parse_error_on_bad_source(self):
        from ipynb.exceptions import IpynbParseError
        from ipynb.ipynb_codec import roundtrip

        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.ipynb"
            with pytest.raises(IpynbParseError):
                roundtrip(INVALID_DIR / "missing-nbformat.ipynb", dest)

    def test_roundtrip_all_valid_samples(self):
        from ipynb.ipynb_codec import get_cell_count, load_ipynb, roundtrip

        for name in ("minimal.ipynb", "code-and-markdown.ipynb", "with-outputs.ipynb"):
            with tempfile.TemporaryDirectory() as td:
                dest = Path(td) / "out.ipynb"
                original = load_ipynb(VALID_DIR / name)
                reloaded = roundtrip(VALID_DIR / name, dest)
                assert get_cell_count(original) == get_cell_count(reloaded)


# --- probe_ipynb ---------------------------------------------------------


class TestProbeIpynbEdgeCases:
    def test_probe_null_nbformat_value_still_true(self):
        """probe only checks key presence, not value validity."""
        from ipynb.ipynb_codec import probe_ipynb

        assert probe_ipynb(b'{"nbformat": null, "cells": []}') is True

    def test_probe_nbformat_zero_still_true(self):
        from ipynb.ipynb_codec import probe_ipynb

        assert probe_ipynb(b'{"nbformat": 0}') is True

    def test_probe_deeply_nested_valid_notebook(self):
        from ipynb.ipynb_codec import probe_ipynb

        data = _nb(
            [
                {
                    "cell_type": "code",
                    "source": "x",
                    "metadata": {"nested": {"a": {"b": [1, 2, 3]}}},
                }
            ]
        )
        assert probe_ipynb(data) is True

    def test_probe_string_source_not_starting_with_brace(self):
        from ipynb.ipynb_codec import probe_ipynb

        assert probe_ipynb("nbformat: 4") is False

    def test_probe_whitespace_only_string(self):
        from ipynb.ipynb_codec import probe_ipynb

        assert probe_ipynb("   \n\t  ") is False

    def test_probe_leading_whitespace_before_brace_valid_json(self):
        from ipynb.ipynb_codec import probe_ipynb

        assert probe_ipynb('   {"nbformat": 4, "cells": []}') is True

    def test_probe_never_raises_on_garbage_path(self):
        from ipynb.ipynb_codec import probe_ipynb

        # A syntactically valid-looking path that does not exist and is
        # not itself JSON -- must return False, never raise.
        assert probe_ipynb("C:/does/not/exist/anywhere.ipynb") is False


# --- get_cell_count / get_code_cells / get_markdown_cells ---------------


class TestCellHelpersEdgeCases:
    def test_get_cell_count_missing_cells_key(self):
        from ipynb.ipynb_codec import get_cell_count

        assert get_cell_count({}) == 0

    def test_get_code_cells_missing_cells_key(self):
        from ipynb.ipynb_codec import get_code_cells

        assert get_code_cells({}) == []

    def test_get_markdown_cells_missing_cells_key(self):
        from ipynb.ipynb_codec import get_markdown_cells

        assert get_markdown_cells({}) == []

    def test_get_code_cells_none_present(self):
        from ipynb.ipynb_codec import get_code_cells

        model = {"cells": [{"cell_type": "markdown"}, {"cell_type": "raw"}]}
        assert get_code_cells(model) == []

    def test_get_markdown_cells_none_present(self):
        from ipynb.ipynb_codec import get_markdown_cells

        model = {"cells": [{"cell_type": "code"}, {"cell_type": "raw"}]}
        assert get_markdown_cells(model) == []

    def test_helpers_agree_with_real_with_outputs_sample(self):
        from ipynb.ipynb_codec import (
            get_cell_count,
            get_code_cells,
            get_markdown_cells,
            load_ipynb,
        )

        model = load_ipynb(VALID_DIR / "with-outputs.ipynb")
        total = get_cell_count(model)
        code = len(get_code_cells(model))
        markdown = len(get_markdown_cells(model))
        # every cell in this fixture is code or markdown -- no raw cells.
        assert code + markdown == total


# --- load_ipynb / write_ipynb (defaults & structural edge cases) --------


class TestLoadWriteDefaults:
    def test_load_missing_cells_key_defaults_to_empty_list(self):
        from ipynb.ipynb_codec import load_ipynb

        model = load_ipynb(b'{"nbformat": 4}')
        assert model["cells"] == []

    def test_load_missing_metadata_key_defaults_to_empty_dict(self):
        from ipynb.ipynb_codec import load_ipynb

        model = load_ipynb(b'{"nbformat": 4, "cells": []}')
        assert model["metadata"] == {}

    def test_load_missing_nbformat_minor_defaults_to_zero(self):
        from ipynb.ipynb_codec import load_ipynb

        model = load_ipynb(b'{"nbformat": 4, "cells": []}')
        assert model["nbformat_minor"] == 0

    def test_write_missing_nbformat_defaults_to_four(self):
        from ipynb.ipynb_codec import write_ipynb

        result = json.loads(write_ipynb({}))
        assert result["nbformat"] == 4

    def test_write_missing_nbformat_minor_defaults_to_five(self):
        from ipynb.ipynb_codec import write_ipynb

        result = json.loads(write_ipynb({}))
        assert result["nbformat_minor"] == 5

    def test_write_missing_metadata_defaults_to_empty_dict(self):
        from ipynb.ipynb_codec import write_ipynb

        result = json.loads(write_ipynb({}))
        assert result["metadata"] == {}

    def test_write_missing_cells_defaults_to_empty_list(self):
        from ipynb.ipynb_codec import write_ipynb

        result = json.loads(write_ipynb({}))
        assert result["cells"] == []

    def test_load_raw_cell_type_defaults_when_absent(self):
        from ipynb.ipynb_codec import load_ipynb

        data = _nb([{"source": "no type here", "metadata": {}}])
        model = load_ipynb(data)
        assert model["cells"][0]["cell_type"] == "raw"

    def test_load_rejects_non_dict_cell(self):
        from ipynb.exceptions import IpynbParseError
        from ipynb.ipynb_codec import load_ipynb

        data = json.dumps(
            {"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": ["not-a-dict"]}
        ).encode("utf-8")
        with pytest.raises(IpynbParseError, match="not a JSON object"):
            load_ipynb(data)

    def test_load_rejects_non_object_top_level(self):
        from ipynb.exceptions import IpynbParseError
        from ipynb.ipynb_codec import load_ipynb

        with pytest.raises(IpynbParseError, match="Expected JSON object"):
            load_ipynb(b"[1, 2, 3]")


# --- ipynb_installed_workflow --------------------------------------------


class TestIpynbInstalledWorkflowRealSamples:
    def test_workflow_on_code_and_markdown_sample(self):
        from ipynb.ipynb_codec import ipynb_installed_workflow

        result = ipynb_installed_workflow(VALID_DIR / "code-and-markdown.ipynb")
        assert result["format"] == "ipynb"
        assert result["loaded"] is True
        assert result["code_cell_count"] == 4
        assert result["markdown_cell_count"] == 5
        assert result["cell_count"] == 9

    def test_workflow_on_with_outputs_sample(self):
        from ipynb.ipynb_codec import ipynb_installed_workflow

        result = ipynb_installed_workflow(VALID_DIR / "with-outputs.ipynb")
        assert result["cell_count"] >= result["code_cell_count"]
        assert result["nbformat"] == 4

    def test_workflow_return_type_is_plain_dict(self):
        from ipynb.ipynb_codec import ipynb_installed_workflow

        result = ipynb_installed_workflow(VALID_DIR / "minimal.ipynb")
        assert isinstance(result, dict)
        assert set(result.keys()) == {
            "format",
            "loaded",
            "nbformat",
            "cell_count",
            "code_cell_count",
            "markdown_cell_count",
        }

    def test_workflow_raises_on_invalid_source(self):
        from ipynb.exceptions import IpynbParseError
        from ipynb.ipynb_codec import ipynb_installed_workflow

        with pytest.raises(IpynbParseError):
            ipynb_installed_workflow(INVALID_DIR / "missing-nbformat.ipynb")


# --- ensure_cell_id (cross-cutting) --------------------------------------


class TestEnsureCellIdCrossCutting:
    def test_returns_same_cell_object_identity(self):
        from ipynb.ipynb_codec import ensure_cell_id

        cell = {"cell_type": "code", "source": "x", "metadata": {}}
        result = ensure_cell_id(cell, set())
        assert result is cell

    def test_used_ids_set_mutated_in_place_not_replaced(self):
        from ipynb.ipynb_codec import ensure_cell_id

        used: set[str] = set()
        cell = {"cell_type": "code", "id": "keep-me", "source": "x", "metadata": {}}
        ensure_cell_id(cell, used)
        assert "keep-me" in used
        assert len(used) == 1

    def test_threading_same_set_across_many_cells_stays_unique(self):
        from ipynb.ipynb_codec import ensure_cell_id

        used: set[str] = set()
        cells = [{"cell_type": "code", "source": str(i), "metadata": {}} for i in range(50)]
        for cell in cells:
            ensure_cell_id(cell, used)
        ids = [c["id"] for c in cells]
        assert len(ids) == len(set(ids)) == 50


# --- output MIME-bundle wrappers (edge cases) ----------------------------


class TestOutputRepresentationEdgeCases:
    def test_get_output_representation_no_data_key_returns_none(self):
        from ipynb.ipynb_codec import get_output_representation

        output = {"output_type": "error", "ename": "E", "evalue": "v", "traceback": []}
        assert get_output_representation(output, "text/plain") is None

    def test_add_output_representation_overwrites_existing_value(self):
        from ipynb.ipynb_codec import add_output_representation

        output = {
            "output_type": "execute_result",
            "execution_count": 1,
            "data": {"text/plain": "old"},
        }
        add_output_representation(output, "text/plain", "new")
        assert output["data"]["text/plain"] == "new"

    def test_remove_output_mime_type_on_output_without_data_key_returns_false(self):
        from ipynb.ipynb_codec import remove_output_mime_type

        output = {"output_type": "stream", "name": "stdout", "text": "hi"}
        assert remove_output_mime_type(output, "text/plain") is False

    def test_add_then_remove_then_get_returns_none(self):
        from ipynb.ipynb_codec import (
            add_output_representation,
            get_output_representation,
            remove_output_mime_type,
        )

        output = {"output_type": "display_data", "data": {}}
        add_output_representation(output, "image/png", "bytes")
        assert get_output_representation(output, "image/png") == "bytes"
        assert remove_output_mime_type(output, "image/png") is True
        assert get_output_representation(output, "image/png") is None

    def test_mime_api_end_to_end_through_a_real_sample_cell(self):
        from ipynb.ipynb_codec import (
            add_output_representation,
            get_code_cells,
            get_output_representation,
            load_ipynb,
        )

        model = load_ipynb(VALID_DIR / "with-outputs.ipynb")
        code_cells = get_code_cells(model)
        output = code_cells[0]["outputs"][0]
        add_output_representation(output, "application/vnd.custom+json", {"k": "v"})
        assert get_output_representation(output, "application/vnd.custom+json") == {"k": "v"}


# --- validate_notebook_schema (additional scenarios) ----------------------


class TestValidateNotebookSchemaAdditional:
    def test_raw_cells_never_checked_for_output_fields(self):
        from ipynb.ipynb_codec import validate_notebook_schema

        model = {
            "nbformat": 4,
            "nbformat_minor": 5,
            "metadata": {},
            "cells": [{"cell_type": "raw", "id": "r1", "source": "x", "metadata": {}}],
        }
        assert validate_notebook_schema(model) == []

    def test_empty_cells_list_is_valid(self):
        from ipynb.ipynb_codec import validate_notebook_schema

        assert validate_notebook_schema({"cells": []}) == []

    def test_missing_cells_key_entirely_is_valid(self):
        from ipynb.ipynb_codec import validate_notebook_schema

        assert validate_notebook_schema({}) == []

    def test_mixed_valid_and_invalid_cells_reports_only_the_invalid_one(self):
        from ipynb.ipynb_codec import validate_notebook_schema

        model = {
            "cells": [
                {"cell_type": "markdown", "id": "good-id", "source": "ok", "metadata": {}},
                {"cell_type": "markdown", "id": "bad id!", "source": "bad", "metadata": {}},
            ]
        }
        errors = validate_notebook_schema(model)
        assert len(errors) == 1
        assert "bad id!" in errors[0]

    def test_multiple_outputs_in_one_cell_each_validated_independently(self):
        from ipynb.ipynb_codec import validate_notebook_schema

        model = {
            "cells": [
                {
                    "cell_type": "code",
                    "id": "c1",
                    "source": "x",
                    "metadata": {},
                    "outputs": [
                        {"output_type": "stream", "name": "stdout", "text": "ok"},
                        {"output_type": "stream", "name": "stdout"},  # missing text
                    ],
                }
            ]
        }
        errors = validate_notebook_schema(model)
        assert len(errors) == 1
        assert "output 1" in errors[0]

    def test_real_valid_samples_pass_via_public_function(self):
        from ipynb.ipynb_codec import load_ipynb, validate_notebook_schema

        for name in ("minimal.ipynb", "code-and-markdown.ipynb", "with-outputs.ipynb"):
            model = load_ipynb(VALID_DIR / name)
            assert validate_notebook_schema(model) == []


# --- IpynbDocument (direct class coverage) --------------------------------


class TestIpynbDocumentDirect:
    def test_from_file_all_valid_samples(self):
        from ipynb.models import IpynbDocument

        for name in ("minimal.ipynb", "code-and-markdown.ipynb", "with-outputs.ipynb"):
            doc = IpynbDocument.from_file(str(VALID_DIR / name))
            assert doc.nbformat == 4
            assert isinstance(doc.cell_count, int)

    def test_raw_property_returns_underlying_dict_identity(self):
        from ipynb.models import IpynbDocument

        data = {"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": []}
        doc = IpynbDocument(data)
        assert doc.raw is data

    def test_nbformat_minor_property(self):
        from ipynb.models import IpynbDocument

        doc = IpynbDocument({"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": []})
        assert doc.nbformat_minor == 5

    def test_metadata_property(self):
        from ipynb.models import IpynbDocument

        doc = IpynbDocument(
            {"nbformat": 4, "nbformat_minor": 5, "metadata": {"lang": "python"}, "cells": []}
        )
        assert doc.metadata == {"lang": "python"}

    def test_is_empty_true_for_no_cells(self):
        from ipynb.models import IpynbDocument

        doc = IpynbDocument({"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": []})
        assert doc.is_empty is True

    def test_is_empty_false_when_cells_present(self):
        from ipynb.models import IpynbDocument

        doc = IpynbDocument.from_file(str(VALID_DIR / "minimal.ipynb"))
        doc.add_cell(cell_type="code", source="x")
        assert doc.is_empty is False

    def test_raw_cells_property(self):
        from ipynb.models import IpynbDocument

        data = {
            "nbformat": 4,
            "nbformat_minor": 5,
            "metadata": {},
            "cells": [
                {"cell_type": "raw", "id": "a", "source": "x", "metadata": {}},
                {"cell_type": "code", "id": "b", "source": "y", "metadata": {}},
            ],
        }
        doc = IpynbDocument(data)
        assert len(doc.raw_cells) == 1
        assert doc.raw_cells[0]["cell_type"] == "raw"

    def test_to_dict_is_shallow_copy_top_level_independent(self):
        from ipynb.models import IpynbDocument

        doc = IpynbDocument({"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": []})
        snapshot = doc.to_dict()
        snapshot["nbformat"] = 999
        assert doc.nbformat == 4  # top-level key reassignment does not leak back

    def test_to_dict_shares_nested_cells_list_reference(self):
        from ipynb.models import IpynbDocument

        doc = IpynbDocument({"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": []})
        snapshot = doc.to_dict()
        assert snapshot["cells"] is doc.raw["cells"]

    def test_repr_reflects_nbformat_and_cell_count(self):
        from ipynb.models import IpynbDocument

        doc = IpynbDocument.from_file(str(VALID_DIR / "code-and-markdown.ipynb"))
        assert repr(doc) == f"IpynbDocument(nbformat=4, cells={doc.cell_count})"

    def test_spec_qname_class_attribute(self):
        from ipynb.models import IpynbDocument

        assert IpynbDocument.spec_qname == "ipynb:notebook"


# --- exception hierarchy --------------------------------------------------


class TestExceptionHierarchy:
    def test_all_four_are_ipynb_error_subclasses(self):
        from ipynb.exceptions import (
            IpynbError,
            IpynbParseError,
            IpynbValidationError,
            IpynbWriteError,
        )

        assert issubclass(IpynbParseError, IpynbError)
        assert issubclass(IpynbWriteError, IpynbError)
        assert issubclass(IpynbValidationError, IpynbError)

    def test_ipynb_error_is_an_exception(self):
        from ipynb.exceptions import IpynbError

        assert issubclass(IpynbError, Exception)

    def test_direct_instantiation_carries_message(self):
        from ipynb.exceptions import (
            IpynbError,
            IpynbParseError,
            IpynbValidationError,
            IpynbWriteError,
        )

        for cls in (IpynbError, IpynbParseError, IpynbWriteError, IpynbValidationError):
            exc = cls("boom")
            assert str(exc) == "boom"

    def test_subclasses_are_catchable_via_base_class(self):
        from ipynb.exceptions import IpynbError, IpynbParseError

        with pytest.raises(IpynbError):
            raise IpynbParseError("nested failure")

    def test_parse_error_raised_by_load_ipynb_is_catchable_as_ipynb_error(self):
        from ipynb.exceptions import IpynbError
        from ipynb.ipynb_codec import load_ipynb

        with pytest.raises(IpynbError):
            load_ipynb(INVALID_DIR / "missing-nbformat.ipynb")

    def test_write_error_raised_on_unserializable_model_content(self):
        """The json.dumps(...) TypeError/ValueError branch of write_ipynb --
        not exercised by any other test file in this package."""
        from ipynb.exceptions import IpynbWriteError
        from ipynb.ipynb_codec import write_ipynb

        model = {
            "nbformat": 4,
            "nbformat_minor": 5,
            "metadata": {},
            # a set is not JSON serializable
            "cells": [{"cell_type": "code", "source": {1, 2, 3}, "metadata": {}}],
        }
        with pytest.raises(IpynbWriteError, match="Cannot serialize notebook"):
            write_ipynb(model)

    def test_write_error_raised_on_unwritable_destination_path(self):
        """The OSError branch of write_ipynb's path.write_text call --
        not exercised by any other test file in this package."""
        from ipynb.exceptions import IpynbWriteError
        from ipynb.ipynb_codec import write_ipynb

        model = {"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": []}
        with tempfile.TemporaryDirectory() as td:
            bad_dest = Path(td) / "does-not-exist-subdir" / "out.ipynb"
            with pytest.raises(IpynbWriteError, match="Cannot write to"):
                write_ipynb(model, bad_dest)

    def test_validation_error_message_matches_schema_errors(self):
        from ipynb.exceptions import IpynbValidationError
        from ipynb.ipynb_codec import validate_notebook

        model = {
            "cells": [{"cell_type": "code", "id": "bad id", "source": "x", "metadata": {}}]
        }
        with pytest.raises(IpynbValidationError, match="invalid or missing id"):
            validate_notebook(model)


# --- analytics functions (integration / extra edge cases) ----------------


class TestAnalyticsIntegration:
    def test_cell_type_histogram_matches_document_model_counts(self):
        from ipynb.ipynb_analytics import ipynb_cell_type_histogram
        from ipynb.models import IpynbDocument

        doc = IpynbDocument.from_file(str(VALID_DIR / "code-and-markdown.ipynb"))
        histogram = ipynb_cell_type_histogram(VALID_DIR / "code-and-markdown.ipynb")
        assert histogram.get("code", 0) == len(doc.code_cells)
        assert histogram.get("markdown", 0) == len(doc.markdown_cells)

    def test_output_type_histogram_matches_real_sample_output_count(self):
        from ipynb.ipynb_analytics import ipynb_output_type_histogram
        from ipynb.ipynb_codec import get_code_cells, load_ipynb

        model = load_ipynb(VALID_DIR / "with-outputs.ipynb")
        total_outputs = sum(len(c.get("outputs", [])) for c in get_code_cells(model))
        histogram = ipynb_output_type_histogram(VALID_DIR / "with-outputs.ipynb")
        assert sum(histogram.values()) == total_outputs

    def test_average_source_length_zero_for_empty_notebook(self):
        from ipynb.ipynb_analytics import ipynb_average_source_length

        assert ipynb_average_source_length(_nb([])) == 0.0

    def test_average_source_length_ignores_non_string_non_list_source(self):
        from ipynb.ipynb_analytics import ipynb_average_source_length

        data = _nb([{"cell_type": "code", "source": None, "metadata": {}}])
        assert ipynb_average_source_length(data) == 0.0

    def test_has_execution_errors_false_for_all_valid_samples(self):
        from ipynb.ipynb_analytics import ipynb_has_execution_errors

        for name in ("minimal.ipynb", "code-and-markdown.ipynb", "with-outputs.ipynb"):
            assert ipynb_has_execution_errors(VALID_DIR / name) is False

    def test_full_pipeline_mutation_write_reload_analytics(self):
        """End-to-end: load -> mutate (add error output via IpynbDocument
        mutation API) -> write -> analytics functions on the written file
        reflect the mutation."""
        from ipynb.ipynb_analytics import (
            ipynb_cell_type_histogram,
            ipynb_has_execution_errors,
        )
        from ipynb.ipynb_codec import write_ipynb
        from ipynb.models import IpynbDocument

        doc = IpynbDocument.from_file(str(VALID_DIR / "minimal.ipynb"))
        cell = doc.add_cell(cell_type="code", source="1/0")
        cell["outputs"] = [
            {
                "output_type": "error",
                "ename": "ZeroDivisionError",
                "evalue": "division by zero",
                "traceback": ["Traceback..."],
            }
        ]

        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "mutated.ipynb"
            write_ipynb(doc.to_dict(), dest)

            assert ipynb_has_execution_errors(dest) is True
            histogram = ipynb_cell_type_histogram(dest)
            assert histogram.get("code") == 1

    def test_all_four_analytics_functions_accept_path_string_and_bytes(self):
        from ipynb.ipynb_analytics import (
            ipynb_average_source_length,
            ipynb_cell_type_histogram,
            ipynb_has_execution_errors,
            ipynb_output_type_histogram,
        )

        for source in (
            VALID_DIR / "minimal.ipynb",
            str(VALID_DIR / "minimal.ipynb"),
            (VALID_DIR / "minimal.ipynb").read_bytes(),
        ):
            assert isinstance(ipynb_cell_type_histogram(source), dict)
            assert isinstance(ipynb_output_type_histogram(source), dict)
            assert isinstance(ipynb_average_source_length(source), float)
            assert isinstance(ipynb_has_execution_errors(source), bool)


# --- import surface (all target names importable together) ---------------


class TestFullImportSurface:
    def test_every_target_symbol_importable_from_package_root(self):
        import ipynb

        expected_names = [
            "roundtrip",
            "probe_ipynb",
            "get_cell_count",
            "get_code_cells",
            "get_markdown_cells",
            "load_ipynb",
            "write_ipynb",
            "ipynb_installed_workflow",
            "ensure_cell_id",
            "get_output_representation",
            "add_output_representation",
            "remove_output_mime_type",
            "validate_notebook_schema",
            "IpynbDocument",
            "IpynbError",
            "IpynbParseError",
            "IpynbWriteError",
            "IpynbValidationError",
            "ipynb_average_source_length",
            "ipynb_cell_type_histogram",
            "ipynb_has_execution_errors",
            "ipynb_output_type_histogram",
        ]
        for name in expected_names:
            assert hasattr(ipynb, name), f"missing top-level export: {name}"
