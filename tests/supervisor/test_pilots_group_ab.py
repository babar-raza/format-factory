"""Pilots 1-6: Control Layer Discovery and Inventory (TC-OCRD-C8-01).

Pilot 1: control_layers table has at least 1 row after ControlLayerIngestor runs
Pilot 2: feature inventory completeness — >= 20 features in control_features
Pilot 3: consumer map populated — control_feature_consumers has entries
Pilot 4: parity register populated — feature_parity_results has entries
Pilot 5: plan_ingestor populates plans table with correct plan types
Pilot 6: upstream_validator rejects a missing file cleanly (not crash)
"""
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
_TOOLS = str(REPO / "tools" / "supervisor")
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)

from control_index.db import init_db, get_connection
from control_index.sync import IngestResult


def _fresh_conn(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    conn = get_connection(db_path)
    return conn, db_path


# ---------------------------------------------------------------------------
# Pilot 1: control_layers table has at least 1 row after ingestor runs
# ---------------------------------------------------------------------------

def test_pilot1_control_layers_table_populated(tmp_path):
    """Pilot 1: ControlLayerIngestor writes at least 1 row to control_layers."""
    conn, db_path = _fresh_conn(tmp_path)

    # Write a minimal control layers YAML
    control_dir = tmp_path / "reports" / "control-layer"
    control_dir.mkdir(parents=True)
    yaml_content = """mission_id: TEST
existing_control_layers:
  - layer_key: test_layer
    name: Test Layer
    status: ACTIVE
    authority_scope: test
    primary_purpose: Testing pilot 1
    implementation_paths: []
    data_paths: []
    consumers: []
    claimed_features: []
    observable_features: []
"""
    (control_dir / "existing-control-layers.yaml").write_text(yaml_content, encoding="utf-8")

    from control_index.ingestors.control_layer_ingestor import ControlLayerIngestor
    ingestor = ControlLayerIngestor(conn, tmp_path)
    result = ingestor.sync(force=True)

    count = conn.execute("SELECT COUNT(*) FROM control_layers").fetchone()[0]
    assert count >= 1, f"Pilot 1 FAIL: expected >= 1 control layer, got {count}"
    conn.close()


# ---------------------------------------------------------------------------
# Pilot 2: feature inventory completeness — >= 20 features after real repo sync
# ---------------------------------------------------------------------------

def test_pilot2_feature_inventory_completeness(tmp_path):
    """Pilot 2: After syncing real repo YAML, >= 20 features exist in control_features."""
    real_features = REPO / "reports" / "control-layer" / "existing-control-features.yaml"
    if not real_features.exists():
        pytest.skip("existing-control-features.yaml not present in repo")

    conn, db_path = _fresh_conn(tmp_path)
    # Write minimal control-layers YAML to satisfy FK constraint
    control_dir = tmp_path / "reports" / "control-layer"
    control_dir.mkdir(parents=True)
    import shutil
    shutil.copy(REPO / "reports" / "control-layer" / "existing-control-layers.yaml",
                control_dir / "existing-control-layers.yaml")
    shutil.copy(real_features, control_dir / "existing-control-features.yaml")

    from control_index.ingestors.control_layer_ingestor import ControlLayerIngestor
    ingestor = ControlLayerIngestor(conn, tmp_path)
    ingestor.sync(force=True)

    count = conn.execute("SELECT COUNT(*) FROM control_features").fetchone()[0]
    assert count >= 20, f"Pilot 2 FAIL: expected >= 20 features, got {count}"
    conn.close()


# ---------------------------------------------------------------------------
# Pilot 3: consumer map — control_feature_consumers has entries
# ---------------------------------------------------------------------------

def test_pilot3_consumer_map_populated(tmp_path):
    """Pilot 3: After syncing real YAMLs, control_feature_consumers has entries."""
    consumers_yaml = REPO / "reports" / "control-layer" / "control-feature-consumers.yaml"
    if not consumers_yaml.exists():
        pytest.skip("control-feature-consumers.yaml not present in repo")

    conn, db_path = _fresh_conn(tmp_path)
    control_dir = tmp_path / "reports" / "control-layer"
    control_dir.mkdir(parents=True)
    import shutil
    for f in ["existing-control-layers.yaml", "existing-control-features.yaml",
              "control-feature-consumers.yaml"]:
        src = REPO / "reports" / "control-layer" / f
        if src.exists():
            shutil.copy(src, control_dir / f)

    from control_index.ingestors.control_layer_ingestor import ControlLayerIngestor
    ingestor = ControlLayerIngestor(conn, tmp_path)
    ingestor.sync(force=True)

    count = conn.execute("SELECT COUNT(*) FROM control_feature_consumers").fetchone()[0]
    assert count >= 1, f"Pilot 3 FAIL: expected >= 1 consumer, got {count}"
    conn.close()


# ---------------------------------------------------------------------------
# Pilot 4: parity register — feature_parity_results has entries
# ---------------------------------------------------------------------------

def test_pilot4_parity_register_populated(tmp_path):
    """Pilot 4: After syncing parity register YAML, feature_parity_results has entries."""
    parity_yaml = REPO / "reports" / "control-layer" / "feature-parity-register.yaml"
    if not parity_yaml.exists():
        pytest.skip("feature-parity-register.yaml not present in repo")

    conn, db_path = _fresh_conn(tmp_path)
    control_dir = tmp_path / "reports" / "control-layer"
    control_dir.mkdir(parents=True)
    import shutil
    for f in ["existing-control-layers.yaml", "existing-control-features.yaml",
              "feature-parity-register.yaml"]:
        src = REPO / "reports" / "control-layer" / f
        if src.exists():
            shutil.copy(src, control_dir / f)

    from control_index.ingestors.control_layer_ingestor import ControlLayerIngestor
    ingestor = ControlLayerIngestor(conn, tmp_path)
    ingestor.sync(force=True)

    count = conn.execute("SELECT COUNT(*) FROM feature_parity_results").fetchone()[0]
    assert count >= 1, f"Pilot 4 FAIL: expected >= 1 parity result, got {count}"
    conn.close()


# ---------------------------------------------------------------------------
# Pilot 5: plan_ingestor populates plans table correctly
# ---------------------------------------------------------------------------

def test_pilot5_plan_ingestor_populates_plans_table(tmp_path):
    """Pilot 5: PlanIngestor scans plans/ and writes rows to plans table."""
    # Create a synthetic plans/ dir
    plans_dir = tmp_path / "plans"
    plans_dir.mkdir()
    (plans_dir / "test-plan.md").write_text(
        "# Test Plan\n\n| TC-ID | Status |\n|---|---|\n| TC-TEST-001 | OPEN |\n",
        encoding="utf-8",
    )

    conn, db_path = _fresh_conn(tmp_path)
    from control_index.ingestors.plan_ingestor import PlanIngestor
    ingestor = PlanIngestor(conn, tmp_path)
    result = ingestor.sync(force=True)

    count = conn.execute("SELECT COUNT(*) FROM plans").fetchone()[0]
    assert count >= 1, f"Pilot 5 FAIL: expected >= 1 plan, got {count}"

    row = conn.execute("SELECT * FROM plans WHERE plan_id = 'test-plan'").fetchone()
    assert row is not None, "Pilot 5 FAIL: test-plan not found in plans table"
    assert row["plan_type"] == "general"
    conn.close()


# ---------------------------------------------------------------------------
# Pilot 6: upstream_validator rejects a missing file cleanly
# ---------------------------------------------------------------------------

def test_pilot6_upstream_validator_missing_file(tmp_path):
    """Pilot 6: validate_upstream_source() returns ValidationResult with quarantine=True for missing file."""
    from control_index.upstream_validator import validate_upstream_source

    result = validate_upstream_source(tmp_path / "nonexistent.yaml")
    assert result.valid is False
    assert result.quarantine is True
    assert any("NOT_FOUND" in f for f in result.failures)
