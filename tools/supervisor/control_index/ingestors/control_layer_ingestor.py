"""Control layer ingestor: existing-control-layers.yaml → control_layers + related tables.

TC-OCRD-C4-02: Reads the YAML produced by TC-OCRD-C1 and populates the
control_layers, control_features, control_feature_consumers, and
feature_parity_results tables. Validates with upstream_validator before insert.
Failed validation writes a quarantine record.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from . import BaseIngestor
from ..sync import register_ingestor
from ..upstream_validator import validate_upstream_source

_SOURCE = "reports/control-layer/existing-control-layers.yaml"
_FEATURES_SOURCE = "reports/control-layer/existing-control-features.yaml"
_PARITY_SOURCE = "reports/control-layer/feature-parity-register.yaml"
_CONSUMERS_SOURCE = "reports/control-layer/control-feature-consumers.yaml"


def _file_hash(path: Path) -> str:
    if not path.exists():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


@register_ingestor
class ControlLayerIngestor(BaseIngestor):
    """Ingest control layer inventory YAMLs into the control index."""

    entity_type = "control_layer"
    source_paths = [_SOURCE]

    def get_adapter(self, source_path: Path):
        # Not using standard adapter; we parse YAML directly in ingest_records
        return _YamlFileAdapter(source_path)

    def ingest_records(self, conn, records, source_path: str, source_hash: str) -> int:
        now = datetime.now(timezone.utc).isoformat()
        repo_root = self.repo_root

        # Validate primary source
        primary = repo_root / _SOURCE
        vr = validate_upstream_source(primary, required_fields=["existing_control_layers"])
        if not vr.valid:
            self._quarantine(conn, str(primary), vr.failures, now)
            return 0

        try:
            import yaml  # type: ignore[import]
            data = yaml.safe_load(primary.read_text(encoding="utf-8"))
        except Exception:
            return 0

        layers = data.get("existing_control_layers", [])
        count = 0
        for layer in layers:
            key = layer.get("layer_key")
            if not key:
                continue
            conn.execute(
                """INSERT OR REPLACE INTO control_layers
                   (layer_key, name, status, authority_scope, primary_purpose,
                    implementation_paths, data_paths, consumers,
                    observable_features_count, last_assessed, ingested_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    key,
                    layer.get("name", ""),
                    layer.get("status", "UNKNOWN"),
                    layer.get("authority_scope"),
                    layer.get("primary_purpose", "").strip(),
                    json.dumps(layer.get("implementation_paths", [])),
                    json.dumps(layer.get("data_paths", [])),
                    json.dumps(layer.get("consumers", [])),
                    0,  # observable_features_count — updated below
                    now,
                    now,
                ),
            )
            count += 1

        # Ingest features
        features_path = repo_root / _FEATURES_SOURCE
        if features_path.exists():
            try:
                fdata = yaml.safe_load(features_path.read_text(encoding="utf-8"))
                features = fdata.get("existing_control_features", [])
                feature_count_by_layer: dict[str, int] = {}
                for feat in features:
                    fid = feat.get("feature_id")
                    if not fid:
                        continue
                    layer_key = feat.get("control_layer_key", "")
                    behavior = feat.get("observable_behavior")
                    conn.execute(
                        """INSERT OR REPLACE INTO control_features
                           (feature_id, control_layer_key, feature_name, category,
                            entry_points, current_status, authority_effect,
                            observable_behavior, ingested_at)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            fid,
                            layer_key,
                            feat.get("feature_name", ""),
                            feat.get("category"),
                            json.dumps(feat.get("entry_points", [])),
                            feat.get("current_status", "UNKNOWN"),
                            feat.get("authority_effect"),
                            json.dumps(behavior) if isinstance(behavior, dict) else str(behavior or ""),
                            now,
                        ),
                    )
                    feature_count_by_layer[layer_key] = feature_count_by_layer.get(layer_key, 0) + 1

                # Update observable_features_count
                for lk, fcnt in feature_count_by_layer.items():
                    conn.execute(
                        "UPDATE control_layers SET observable_features_count = ? WHERE layer_key = ?",
                        (fcnt, lk),
                    )
            except Exception:
                pass

        # Ingest consumers
        consumers_path = repo_root / _CONSUMERS_SOURCE
        if consumers_path.exists():
            try:
                cdata = yaml.safe_load(consumers_path.read_text(encoding="utf-8"))
                # Navigate to control_feature_consumers sub-key if present
                consumer_map = cdata.get("control_feature_consumers") if isinstance(cdata, dict) else cdata
                if not isinstance(consumer_map, dict):
                    consumer_map = {}
                for fid, feature_data in consumer_map.items():
                    if not isinstance(feature_data, dict):
                        continue
                    consumer_list = feature_data.get("consumers", [])
                    for c in consumer_list:
                        cid = c.get("consumer_id")
                        if not cid:
                            continue
                        conn.execute(
                            """INSERT OR IGNORE INTO control_feature_consumers
                               (feature_id, consumer_id, consumer_type, consumer_path)
                               VALUES (?, ?, ?, ?)""",
                            (
                                fid,
                                cid,
                                c.get("consumer_type"),
                                c.get("consumer_path"),
                            ),
                        )
            except Exception:
                pass

        # Ingest parity register
        parity_path = repo_root / _PARITY_SOURCE
        if parity_path.exists():
            try:
                pdata = yaml.safe_load(parity_path.read_text(encoding="utf-8"))
                for entry in pdata.get("feature_parity_register", []):
                    fid = entry.get("feature_id")
                    if not fid:
                        continue
                    conn.execute(
                        """INSERT OR REPLACE INTO feature_parity_results
                           (feature_id, reuse_strategy, parity_status, intentional_changes, verified_at)
                           VALUES (?, ?, ?, ?, ?)""",
                        (
                            fid,
                            entry.get("disposition"),
                            "REGISTERED",
                            entry.get("rationale"),
                            now,
                        ),
                    )
            except Exception:
                pass

        return count

    def _quarantine(self, conn, artifact_path: str, failures: list[str], now: str) -> None:
        qid = f"q:{artifact_path}:{now}"
        try:
            conn.execute(
                """INSERT OR IGNORE INTO quarantines
                   (quarantine_id, artifact_path, detected_at, validation_failures, severity, status)
                   VALUES (?, ?, ?, ?, ?, 'ACTIVE')""",
                (qid, artifact_path, now, json.dumps(failures), "HIGH"),
            )
        except Exception:
            pass

    def delete_existing(self, conn, source_file: str) -> None:
        # Clear all control layer data before re-ingesting
        try:
            conn.execute("DELETE FROM feature_parity_results")
            conn.execute("DELETE FROM control_feature_consumers")
            conn.execute("DELETE FROM control_features")
            conn.execute("DELETE FROM control_layers")
        except Exception:
            pass


class _YamlFileAdapter:
    """Minimal adapter shim so BaseIngestor.sync() can call needs_sync() and file_hash()."""

    def __init__(self, path: Path):
        self._path = path

    def needs_sync(self, manifest: dict | None) -> bool:
        if not self._path.exists():
            return False
        current_hash = self.file_hash()
        if manifest is None:
            return True
        return manifest.get("last_hash") != current_hash

    def file_hash(self) -> str:
        return _file_hash(self._path)

    def file_size(self) -> int:
        return self._path.stat().st_size if self._path.exists() else 0

    def read_records(self):
        # Not called directly; ingest_records handles YAML parsing
        return iter([])
