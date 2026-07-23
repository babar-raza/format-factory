"""Tests for authority-bound SAL candidate seeding."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "tools" / "spec" / "seed_sal_candidates.py"
SPEC = importlib.util.spec_from_file_location("seed_sal_candidates_under_test", MODULE_PATH)
assert SPEC and SPEC.loader
seed_sal_candidates = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(seed_sal_candidates)


@pytest.fixture
def sandbox(tmp_path: Path, monkeypatch):
    queue_dir = tmp_path / ".local" / "supervisor" / "sal-candidates"
    sal_dir = tmp_path / "shared" / "sal-facts"
    research_dir = tmp_path / "shared" / "format-contracts" / "research"
    queue_dir.mkdir(parents=True)
    research_dir.mkdir(parents=True)
    registry = tmp_path / "registry" / "format-registry.yaml"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        yaml.safe_dump(
            {"formats": [{"format_id": "ora", "display_name": "OpenRaster"}]},
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(seed_sal_candidates, "QUEUE_DIR", queue_dir)
    monkeypatch.setattr(seed_sal_candidates, "SAL_DIR", sal_dir)
    monkeypatch.setattr(seed_sal_candidates, "RESEARCH_DIR", research_dir)
    monkeypatch.setattr(seed_sal_candidates, "FORMAT_REGISTRY", registry)
    monkeypatch.setattr(seed_sal_candidates, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(seed_sal_candidates, "MERGE", tmp_path / "merge.py")
    monkeypatch.setattr(
        seed_sal_candidates.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, stderr=""),
    )
    return {
        "queue": queue_dir / "ora.yaml",
        "store": sal_dir / "ora.yaml",
        "research": research_dir / "ora.yaml",
    }


def _write_inputs(sandbox: dict[str, Path], *, source_ids=True) -> None:
    digest = "a" * 64
    sandbox["research"].write_text(
        yaml.safe_dump(
            {
                "format_id": "ora",
                "source_records": [
                    {
                        "source_id": "SRC-ORA-001",
                        "acquisition_status": "ACQUIRED",
                        "content_hash": digest,
                    }
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    candidate = {
        "claim": "An OpenRaster file is a ZIP container with required members.",
        "element_qname": "ora:archive",
        "section": "File Layout",
        "authority": "OpenRaster 0.0.5",
    }
    if source_ids:
        candidate["source_ids"] = ["SRC-ORA-001"]
        candidate["source_sha256"] = digest
    sandbox["queue"].write_text(
        yaml.safe_dump({"format_id": "ora", "candidates": [candidate]}, sort_keys=False),
        encoding="utf-8",
    )


def test_initializes_missing_store_with_authority_digest(sandbox) -> None:
    _write_inputs(sandbox)

    result = seed_sal_candidates.seed("ora", "TC-TEST")

    assert result == {"seeded": 1, "skipped": 0, "total_facts": 1}
    store = yaml.safe_load(sandbox["store"].read_text(encoding="utf-8"))
    assert store["display_name"] == "OpenRaster"
    fact = store["facts"][0]
    assert fact["fact_id"] == "SAL-ORA-00001"
    assert fact["provenance"]["authority_sources"] == [
        {"source_id": "SRC-ORA-001", "sha256": "a" * 64}
    ]


def test_rejects_new_candidate_without_acquired_source(sandbox) -> None:
    _write_inputs(sandbox, source_ids=False)

    with pytest.raises(RuntimeError, match="no acquired source_ids"):
        seed_sal_candidates.seed("ora", "TC-TEST")

    assert not sandbox["store"].exists()


def test_second_run_is_idempotent(sandbox) -> None:
    _write_inputs(sandbox)

    seed_sal_candidates.seed("ora", "TC-TEST")
    result = seed_sal_candidates.seed("ora", "TC-TEST")

    assert result == {"seeded": 0, "skipped": 1, "total_facts": 1}
