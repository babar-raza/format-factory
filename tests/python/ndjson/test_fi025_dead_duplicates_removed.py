"""test_fi025_dead_duplicates_removed.py — closes FI-025 (2026-07-17).

registry/found-issue-register.yaml FI-025: ndjson_field_analytics.py defined
10 functions whose names collided with already-wired, already-tested
implementations in json_stream.py / ndjson_record_stats.py, but with a
narrower signature (raw source only, vs. the canonical versions' raw-source-
or-already-parsed-list). They were never imported into __init__.py and were
permanently dead code. This test asserts (a) the 10 duplicate names are
genuinely gone from the module, (b) the 8 legitimate, still-imported
functions are unaffected, and (c) the canonical implementations (same names,
different module) still behave correctly for the exact scenarios the deleted
duplicates used to claim to handle.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import ndjson.ndjson_field_analytics as fa  # noqa: E402
import ndjson  # noqa: E402

VALID = _REPO / "samples" / "by-format" / "ndjson" / "valid"
MINIMAL = VALID / "minimal.ndjson"

_DELETED_NAMES = [
    "ndjson_bool_value_count", "ndjson_null_field_count",
    "ndjson_numeric_field_count", "ndjson_string_field_count",
    "ndjson_max_field_count", "ndjson_record_count",
    "ndjson_dict_record_count", "ndjson_unique_key_count",
    "ndjson_min_field_count", "ndjson_total_field_count",
]

_KEPT_NAMES = [
    "ndjson_first_record_keys", "ndjson_first_record_field_count",
    "ndjson_has_consistent_keys", "ndjson_sorted_key_names",
    "ndjson_all_key_names", "ndjson_last_record_keys",
    "ndjson_has_nested_records", "ndjson_has_arrays",
]


def test_all_ten_duplicate_names_are_gone_from_the_module():
    for name in _DELETED_NAMES:
        assert not hasattr(fa, name), (
            f"{name} should have been deleted from ndjson_field_analytics.py "
            "(FI-025) but is still present"
        )


def test_all_eight_kept_names_still_present_and_callable():
    for name in _KEPT_NAMES:
        assert hasattr(fa, name), f"{name} should still exist"
        fn = getattr(fa, name)
        assert callable(fn)
        fn(MINIMAL)  # doesn't raise


def test_kept_functions_still_exported_from_package_init():
    for name in _KEPT_NAMES:
        assert hasattr(ndjson, name), (
            f"{name} should still be re-exported from ndjson/__init__.py"
        )


def test_canonical_implementations_cover_the_same_scenarios_correctly():
    """The canonical, still-wired versions of the 10 deleted names, reached
    via the public `ndjson` package, run without error and return sane values
    for the exact MINIMAL fixture the deleted duplicates were tested against.

    NOTE (discovered while writing this test, TC-FI025-001, not asserted
    against the deleted duplicates' own values): `ndjson_bool_value_count`
    and `ndjson_numeric_field_count` are NOT semantically identical to the
    deleted ndjson_field_analytics.py versions -- e.g. the deleted
    ndjson_bool_value_count counted only True values (2 for MINIMAL); the
    canonical one (json_stream.py) counts ALL boolean values, True and False
    (3 for MINIMAL). ndjson_numeric_field_count has a THIRD distinct
    behavior again: ndjson_record_stats.py's version (which wins over
    json_stream.py's differently-behaving same-named function via
    __init__.py's star-import order) counts unique numeric FIELD NAMES, not
    total numeric VALUES (1 for MINIMAL's single "score" field, not 3). This
    is a real, separate, pre-existing naming collision between two files
    that ARE both wired in -- registered as FI-029, explicitly NOT fixed
    here (out of this taskcard's scope: closing 10 confirmed-dead
    duplicates in one file, not resolving a live semantic collision between
    two already-wired, already-tested modules)."""
    assert ndjson.ndjson_bool_value_count(MINIMAL) == 3
    assert ndjson.ndjson_null_field_count(MINIMAL) == 0
    assert ndjson.ndjson_numeric_field_count(MINIMAL) == 1
    assert ndjson.ndjson_string_field_count(MINIMAL) == 3
    assert ndjson.ndjson_max_field_count(MINIMAL) == 3
    assert ndjson.ndjson_record_count(MINIMAL) == 3
    assert ndjson.ndjson_dict_record_count(MINIMAL) == 3
    assert ndjson.ndjson_unique_key_count(MINIMAL) == 3
    assert ndjson.ndjson_min_field_count(MINIMAL) == 3
    assert ndjson.ndjson_total_field_count(MINIMAL) == 9


def test_canonical_implementations_also_accept_pre_parsed_lists():
    """The reason the deleted duplicates were a strict subset, not merely
    duplicative: the canonical versions accept EITHER a raw source or an
    already-parsed list, while the deleted versions only accepted raw
    source (always called load_ndjson() unconditionally)."""
    records = [{"a": 1}, {"a": 2, "b": 3}]
    assert ndjson.ndjson_record_count(records) == 2
    assert ndjson.ndjson_min_field_count(records) == 1
    assert ndjson.ndjson_total_field_count(records) == 3
