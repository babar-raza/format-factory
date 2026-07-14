"""Tests for FeatureFactory.generate_and_write_scaffold() — TC-INT-002-D."""
from __future__ import annotations

import pytest
from pathlib import Path

from tools.supervisor.product_feature_factory import FeatureFactory
from tools.supervisor.test_drivers import is_maintained_test


def test_generate_and_write_scaffold_creates_file(tmp_path):
    """Scaffold .py file is written to disk in the scaffold_dir."""
    factory = FeatureFactory()
    result = factory.generate_and_write_scaffold(
        format_id="ndjson",
        pattern_id="probe",
        function_name="probe_ndjson",
        module="ndjson",
        scaffold_dir=tmp_path / "scaffolds",
        promotion_tasks_dir=tmp_path / "promo",
    )
    scaffold = Path(result["scaffold_path"])
    assert scaffold.exists(), f"Expected scaffold at {scaffold}"
    assert scaffold.suffix == ".py"
    assert scaffold.stat().st_size > 0


def test_generate_and_write_scaffold_creates_promotion_task(tmp_path):
    """Promotion task .yaml file is written to disk in promotion_tasks_dir."""
    factory = FeatureFactory()
    result = factory.generate_and_write_scaffold(
        format_id="ndjson",
        pattern_id="getter",
        function_name="get_ndjson_count",
        module="ndjson",
        scaffold_dir=tmp_path / "scaffolds",
        promotion_tasks_dir=tmp_path / "promo",
    )
    task_path = Path(result["promotion_task_path"])
    assert task_path.exists(), f"Expected promotion task at {task_path}"
    assert task_path.suffix == ".yaml"


def test_generated_scaffold_is_not_maintained(tmp_path):
    """The scaffold contains incomplete markers and is_maintained_test() returns False."""
    factory = FeatureFactory()
    result = factory.generate_and_write_scaffold(
        format_id="ndjson",
        pattern_id="probe",
        function_name="probe_ndjson_v2",
        module="ndjson",
        scaffold_dir=tmp_path / "scaffolds",
        promotion_tasks_dir=tmp_path / "promo",
    )
    scaffold_content = Path(result["scaffold_path"]).read_text(encoding="utf-8")
    assert not is_maintained_test(scaffold_content), (
        "Scaffold must contain FIXTURE_REQUIRED/ORACLE_REQUIRED markers (is_maintained_test must return False)"
    )


def test_generate_and_write_scaffold_ndjson_probe(tmp_path):
    """End-to-end: return dict has all required keys with correct types."""
    factory = FeatureFactory()
    result = factory.generate_and_write_scaffold(
        format_id="ndjson",
        pattern_id="probe",
        function_name="probe_ndjson_full",
        module="ndjson",
        format_cap="Ndjson",
        format_lower="ndjson",
        scaffold_dir=tmp_path / "scaffolds",
        promotion_tasks_dir=tmp_path / "promo",
    )
    for key in ("scaffold_path", "promotion_task_path", "task_id", "status", "incomplete_markers"):
        assert key in result, f"Missing key {key!r} in result"
    assert result["task_id"].startswith("PROMO-")
    assert result["status"] in ("FORMAT_ADAPTATION_REQUIRED", "SCAFFOLD_GENERATED")
    assert isinstance(result["incomplete_markers"], list)


def test_generate_and_write_scaffold_invalid_pattern_raises(tmp_path):
    """Invalid pattern_id raises ValueError."""
    factory = FeatureFactory()
    with pytest.raises(ValueError, match="not in"):
        factory.generate_and_write_scaffold(
            format_id="ndjson",
            pattern_id="nonexistent",
            function_name="test_fn",
            module="ndjson",
            scaffold_dir=tmp_path / "scaffolds",
            promotion_tasks_dir=tmp_path / "promo",
        )
