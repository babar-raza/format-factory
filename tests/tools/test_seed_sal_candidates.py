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
        "readiness_categories": ["syntax_encoding"],
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
    assert fact["fact_id"].startswith("SAL-ORA-")
    assert len(fact["fact_id"].removeprefix("SAL-ORA-")) == 16
    assert fact["readiness_categories"] == ["syntax_encoding"]
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


def test_stable_id_does_not_depend_on_candidate_position(sandbox) -> None:
    _write_inputs(sandbox)
    queue = yaml.safe_load(sandbox["queue"].read_text(encoding="utf-8"))
    second = {
        **queue["candidates"][0],
        "claim": "The mimetype member identifies an OpenRaster archive.",
        "element_qname": "ora:mimetype",
    }
    queue["candidates"].append(second)
    sandbox["queue"].write_text(
        yaml.safe_dump(queue, sort_keys=False),
        encoding="utf-8",
    )

    seed_sal_candidates.seed("ora", "TC-TEST")
    first_store = yaml.safe_load(sandbox["store"].read_text(encoding="utf-8"))
    ids_by_claim = {
        fact["claim"]: fact["fact_id"]
        for fact in first_store["facts"]
    }

    sandbox["store"].unlink()
    queue["candidates"].reverse()
    sandbox["queue"].write_text(
        yaml.safe_dump(queue, sort_keys=False),
        encoding="utf-8",
    )
    seed_sal_candidates.seed("ora", "TC-TEST")
    second_store = yaml.safe_load(sandbox["store"].read_text(encoding="utf-8"))

    assert {
        fact["claim"]: fact["fact_id"]
        for fact in second_store["facts"]
    } == ids_by_claim


def test_candidate_id_seeds_only_selected_row(sandbox) -> None:
    _write_inputs(sandbox)
    queue = yaml.safe_load(sandbox["queue"].read_text(encoding="utf-8"))
    selected = queue["candidates"][0]
    selected["candidate_id"] = "ORA-CAND-SELECTED"
    queue["candidates"].insert(
        0,
        {
            "candidate_id": "ORA-CAND-UNRELATED-LEGACY",
            "claim": (
                "An unrelated historical candidate intentionally lacks "
                "authority provenance."
            ),
            "element_qname": "ora:legacy",
            "section": "Historical queue residue",
        },
    )
    sandbox["queue"].write_text(
        yaml.safe_dump(queue, sort_keys=False),
        encoding="utf-8",
    )

    result = seed_sal_candidates.seed(
        "ora",
        "TC-TEST",
        candidate_id="ORA-CAND-SELECTED",
    )

    assert result == {"seeded": 1, "skipped": 0, "total_facts": 1}
    store = yaml.safe_load(sandbox["store"].read_text(encoding="utf-8"))
    assert [fact["claim"] for fact in store["facts"]] == [selected["claim"]]


def test_candidate_id_rejects_missing_row_before_write(sandbox) -> None:
    _write_inputs(sandbox)

    with pytest.raises(
        RuntimeError,
        match="candidate_id 'ORA-CAND-MISSING' must match exactly one queue row; matched 0",
    ):
        seed_sal_candidates.seed(
            "ora",
            "TC-TEST",
            candidate_id="ORA-CAND-MISSING",
        )

    assert not sandbox["store"].exists()


def test_candidate_id_rejects_duplicate_rows_before_write(sandbox) -> None:
    _write_inputs(sandbox)
    queue = yaml.safe_load(sandbox["queue"].read_text(encoding="utf-8"))
    queue["candidates"][0]["candidate_id"] = "ORA-CAND-DUPLICATE"
    queue["candidates"].append(dict(queue["candidates"][0]))
    sandbox["queue"].write_text(
        yaml.safe_dump(queue, sort_keys=False),
        encoding="utf-8",
    )

    with pytest.raises(
        RuntimeError,
        match="candidate_id 'ORA-CAND-DUPLICATE' must match exactly one queue row; matched 2",
    ):
        seed_sal_candidates.seed(
            "ora",
            "TC-TEST",
            candidate_id="ORA-CAND-DUPLICATE",
        )

    assert not sandbox["store"].exists()


def test_cli_forwards_candidate_id(monkeypatch, capsys) -> None:
    captured: dict[str, object] = {}

    def fake_seed(
        format_id: str,
        added_by: str,
        *,
        candidate_id: str | None = None,
    ) -> dict[str, int]:
        captured.update(
            format_id=format_id,
            added_by=added_by,
            candidate_id=candidate_id,
        )
        return {"seeded": 0, "skipped": 0, "total_facts": 3}

    monkeypatch.setattr(seed_sal_candidates, "seed", fake_seed)

    result = seed_sal_candidates.main(
        [
            "--format-id",
            "XLIFF",
            "--added-by",
            "TC-TEST",
            "--candidate-id",
            "XLF-SAL-CAND-SELECTED",
        ]
    )

    assert result == 0
    assert captured == {
        "format_id": "xliff",
        "added_by": "TC-TEST",
        "candidate_id": "XLF-SAL-CAND-SELECTED",
    }
    assert "seeded 0, skipped 0" in capsys.readouterr().out


def test_qname_alias_advances_from_existing_alias_not_hashed_sal_id(sandbox) -> None:
    _write_inputs(sandbox)
    sandbox["store"].parent.mkdir(parents=True)
    sandbox["store"].write_text(
        yaml.safe_dump(
            {
                "format_id": "ora",
                "display_name": "OpenRaster",
                "schema_version": "1.0",
                "canonical": True,
                "facts": [
                    {
                        "fact_id": "SAL-ORA-ABCDEF0123456789",
                        "qname": "FACT-ORA-31",
                        "claim": (
                            "An existing digest-stable fact already owns the "
                            "highest compatibility alias."
                        ),
                    }
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    seed_sal_candidates.seed("ora", "TC-TEST")

    store = yaml.safe_load(sandbox["store"].read_text(encoding="utf-8"))
    assert store["facts"][-1]["qname"] == "FACT-ORA-32"


def test_existing_canonical_store_bytes_are_preserved_when_appending(sandbox) -> None:
    _write_inputs(sandbox)
    sandbox["store"].parent.mkdir(parents=True)
    original = (
        "format_id: ora\n"
        "display_name: OpenRaster\n"
        "schema_version: '1.0'\n"
        "canonical: true\n"
        "note: 'Preserve  deliberate spacing and quoting.'\n"
        "facts:\n"
        "- fact_id: SAL-ORA-00001\n"
        "  qname: FACT-ORA-1\n"
        "  claim: An existing canonical fact must retain its exact serialized bytes.\n"
    ).encode()
    sandbox["store"].write_bytes(original)

    seed_sal_candidates.seed("ora", "TC-TEST")

    updated = sandbox["store"].read_bytes()
    assert updated.startswith(original)
    assert len(yaml.safe_load(updated)["facts"]) == 2


def test_failed_combined_merge_restores_existing_store_bytes(
    sandbox,
    monkeypatch,
) -> None:
    _write_inputs(sandbox)
    sandbox["store"].parent.mkdir(parents=True)
    original = (
        "format_id: ora\n"
        "display_name: OpenRaster\n"
        "schema_version: '1.0'\n"
        "canonical: true\n"
        "facts:\n"
        "- fact_id: SAL-ORA-00001\n"
        "  qname: FACT-ORA-1\n"
        "  claim: An existing canonical fact survives a failed derived merge.\n"
    ).encode()
    sandbox["store"].write_bytes(original)
    monkeypatch.setattr(
        seed_sal_candidates.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=1,
            stderr="unrelated derived-cache conflict",
        ),
    )

    with pytest.raises(RuntimeError, match="merge_sal_facts failed"):
        seed_sal_candidates.seed("ora", "TC-TEST")

    assert sandbox["store"].read_bytes() == original


def test_merge_is_scoped_to_selected_format(sandbox, monkeypatch) -> None:
    _write_inputs(sandbox)
    commands: list[list[str]] = []

    def capture_run(command, **kwargs):
        commands.append(command)
        return SimpleNamespace(returncode=0, stderr="")

    monkeypatch.setattr(seed_sal_candidates.subprocess, "run", capture_run)

    seed_sal_candidates.seed("ora", "TC-TEST")

    assert commands == [
        [
            seed_sal_candidates.sys.executable,
            str(seed_sal_candidates.MERGE),
            "--formats",
            "ora",
        ]
    ]


def test_failed_merge_restores_derived_cache_and_alias_bytes(
    sandbox,
    monkeypatch,
    tmp_path: Path,
) -> None:
    _write_inputs(sandbox)
    combined = tmp_path / ".local" / "spec-cache" / "sal-facts-latest.json"
    aliases = tmp_path / "shared" / "sal-fact-id-aliases.json"
    combined.parent.mkdir(parents=True)
    aliases.parent.mkdir(parents=True, exist_ok=True)
    original_combined = b'{"state":"last-good"}\n'
    original_aliases = b'{"aliases":{},"total_aliases":0}\n'
    combined.write_bytes(original_combined)
    aliases.write_bytes(original_aliases)
    monkeypatch.setattr(seed_sal_candidates, "COMBINED_CACHE", combined, raising=False)
    monkeypatch.setattr(seed_sal_candidates, "ALIASES_PATH", aliases, raising=False)

    def failing_merge(*args, **kwargs):
        combined.write_bytes(b'{"state":"partially-written"}\n')
        aliases.write_bytes(b'{"aliases":{"FACT-ORA-1":"wrong"}}\n')
        return SimpleNamespace(returncode=1, stderr="merge failed after writes")

    monkeypatch.setattr(seed_sal_candidates.subprocess, "run", failing_merge)

    with pytest.raises(RuntimeError, match="merge_sal_facts failed"):
        seed_sal_candidates.seed("ora", "TC-TEST")

    assert combined.read_bytes() == original_combined
    assert aliases.read_bytes() == original_aliases


def test_existing_empty_store_is_extended_without_reformatting_metadata(
    sandbox,
) -> None:
    _write_inputs(sandbox)
    sandbox["store"].parent.mkdir(parents=True)
    metadata = (
        "format_id: ora\n"
        "display_name: OpenRaster\n"
        "schema_version: '1.0'\n"
        "canonical: true\n"
        "note: 'Preserve  this exact metadata.'\n"
    ).encode()
    sandbox["store"].write_bytes(metadata + b"facts: []\n")

    seed_sal_candidates.seed("ora", "TC-TEST")

    updated = sandbox["store"].read_bytes()
    assert updated.startswith(metadata + b"facts:\n")
    assert len(yaml.safe_load(updated)["facts"]) == 1


def test_selected_candidate_second_run_is_byte_idempotent(sandbox) -> None:
    _write_inputs(sandbox)
    queue = yaml.safe_load(sandbox["queue"].read_text(encoding="utf-8"))
    queue["candidates"][0]["candidate_id"] = "ORA-CAND-SELECTED"
    sandbox["queue"].write_text(
        yaml.safe_dump(queue, sort_keys=False),
        encoding="utf-8",
    )

    seed_sal_candidates.seed(
        "ora",
        "TC-TEST",
        candidate_id="ORA-CAND-SELECTED",
    )
    first = sandbox["store"].read_bytes()
    result = seed_sal_candidates.seed(
        "ora",
        "TC-TEST",
        candidate_id="ORA-CAND-SELECTED",
    )

    assert result == {"seeded": 0, "skipped": 1, "total_facts": 1}
    assert sandbox["store"].read_bytes() == first
