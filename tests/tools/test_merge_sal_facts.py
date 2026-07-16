"""
Tests for tools/spec/merge_sal_facts.py union semantics.

GAP-FORENSIC-008 Phase 2 regression controls:
  - Union never drops facts that exist only in the combined DB
    (the FACT-QOI-003 loss scenario under the old replace semantics).
  - Claim conflicts are hard errors, never silent overwrites.
  - Reruns are no-ops (deterministic, idempotent).
  - --check mode reports drift without writing.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest
import yaml

_REPO = Path(__file__).resolve().parent.parent.parent
_MODULE_PATH = _REPO / "tools" / "spec" / "merge_sal_facts.py"

spec = importlib.util.spec_from_file_location("merge_sal_facts", _MODULE_PATH)
msf = importlib.util.module_from_spec(spec)
sys.modules["merge_sal_facts"] = msf
spec.loader.exec_module(msf)


def _fact(fact_id: str, qname: str, claim: str, **extra) -> dict:
    return {"fact_id": fact_id, "qname": qname, "claim": claim, **extra}


@pytest.fixture()
def sandbox(tmp_path, monkeypatch):
    """Redirect the module's repo paths into a temp sandbox."""
    spec_cache = tmp_path / ".local" / "spec-cache"
    store_dir = tmp_path / "shared" / "sal-facts"
    spec_cache.mkdir(parents=True)
    store_dir.mkdir(parents=True)

    combined = {
        "generated_at": "2026-01-01T00:00:00+00:00",
        "generator": "test",
        "formats_processed": 1,
        "spec_facts_total": 3,
        "workbench_verified_fact_total": 0,
        "results": [
            {
                "format_id": "qoi",
                "display_name": "QOI",
                "spec_body": "",
                "spec_version": "",
                "spec_url": "",
                "spec_facts": [
                    _fact("SAL-QOI-00001", "FACT-QOI-001", "QOI file header"),
                    _fact("SAL-QOI-00002", "FACT-QOI-002", "QOI encoded chunk"),
                    # Added directly to the combined DB by TC-SAL-CLOSE-13,
                    # absent from any per-format source file:
                    _fact("SAL-QOI-00003", "FACT-QOI-003", "QOI end marker"),
                ],
            }
        ],
    }
    combined_path = spec_cache / "sal-facts-latest.json"
    combined_path.write_text(json.dumps(combined, indent=2) + "\n", encoding="utf-8")

    aliases_path = tmp_path / "shared" / "sal-fact-id-aliases.json"
    aliases_path.write_text(json.dumps({
        "aliases": {
            "FACT-QOI-001": "SAL-QOI-00001",
            "FACT-QOI-002": "SAL-QOI-00002",
            "FACT-QOI-003": "SAL-QOI-00003",
        }
    }), encoding="utf-8")

    monkeypatch.setattr(msf, "_REPO", tmp_path)
    monkeypatch.setattr(msf, "_SPEC_CACHE", spec_cache)
    monkeypatch.setattr(msf, "_COMBINED", combined_path)
    monkeypatch.setattr(msf, "_STORE_DIR", store_dir)
    monkeypatch.setattr(msf, "_ALIASES_PATH", aliases_path)

    return {"root": tmp_path, "combined": combined_path, "store_dir": store_dir}


def _write_store(sandbox, facts: list[dict]) -> None:
    store = {"format_id": "qoi", "display_name": "QOI", "facts": facts}
    (sandbox["store_dir"] / "qoi.yaml").write_text(
        yaml.safe_dump(store, sort_keys=False), encoding="utf-8"
    )


def _read_combined_facts(sandbox) -> list[dict]:
    data = json.loads(sandbox["combined"].read_text(encoding="utf-8"))
    entry = next(e for e in data["results"] if e["format_id"] == "qoi")
    return entry["spec_facts"]


class TestUnionNeverDrops:
    def test_fact_qoi_003_loss_regression(self, sandbox):
        """Store lacks SAL-QOI-00003 (only in combined DB). Old replace
        semantics destroyed it; union must preserve it."""
        _write_store(sandbox, [
            _fact("SAL-QOI-00001", "FACT-QOI-001", "QOI file header"),
            _fact("SAL-QOI-00002", "FACT-QOI-002", "QOI encoded chunk"),
            _fact("SAL-QOI-00004", "FACT-QOI-004", "QOI_OP_RGB chunk"),
        ])
        summary = msf.merge_formats(formats=["qoi"])
        ids = {f["fact_id"] for f in _read_combined_facts(sandbox)}
        assert "SAL-QOI-00003" in ids, "union dropped a combined-only fact"
        assert "SAL-QOI-00004" in ids
        assert len(ids) == 4
        merged = summary["merged"][0]
        assert merged["added"] == 1

    def test_source_with_fewer_facts_never_downgrades(self, sandbox):
        _write_store(sandbox, [
            _fact("SAL-QOI-00001", "FACT-QOI-001", "QOI file header"),
        ])
        msf.merge_formats(formats=["qoi"])
        assert len(_read_combined_facts(sandbox)) == 3


class TestConflictDetection:
    def test_claim_conflict_is_hard_error(self, sandbox):
        _write_store(sandbox, [
            _fact("SAL-QOI-00001", "FACT-QOI-001", "A DIFFERENT header claim"),
        ])
        summary = msf.merge_formats(formats=["qoi"])
        assert summary["errors"], "claim conflict must surface as an error"
        assert "conflict" in summary["errors"][0]["reason"]
        # combined DB untouched on conflict
        facts = _read_combined_facts(sandbox)
        assert facts[0]["claim"] == "QOI file header"

    def test_identical_claim_is_not_conflict(self, sandbox):
        _write_store(sandbox, [
            _fact("SAL-QOI-00001", "FACT-QOI-001", "QOI file header",
                  section="1.0"),
        ])
        summary = msf.merge_formats(formats=["qoi"])
        assert not summary["errors"]
        facts = _read_combined_facts(sandbox)
        target = next(f for f in facts if f["fact_id"] == "SAL-QOI-00001")
        assert target["section"] == "1.0"  # supplementary field merged in


class TestIdempotency:
    def test_second_run_is_noop(self, sandbox):
        _write_store(sandbox, [
            _fact("SAL-QOI-00001", "FACT-QOI-001", "QOI file header"),
            _fact("SAL-QOI-00004", "FACT-QOI-004", "QOI_OP_RGB chunk"),
        ])
        msf.merge_formats(formats=["qoi"])
        first_bytes = sandbox["combined"].read_bytes()
        summary2 = msf.merge_formats(formats=["qoi"])
        second_bytes = sandbox["combined"].read_bytes()
        assert first_bytes == second_bytes, "rerun must be byte-identical"
        assert not summary2["merged"]
        assert any(s["reason"] == "already_in_sync" for s in summary2["skipped"])

    def test_facts_sorted_by_fact_id(self, sandbox):
        _write_store(sandbox, [
            _fact("SAL-QOI-00009", "FACT-QOI-009", "QOI_OP_RUN chunk"),
            _fact("SAL-QOI-00004", "FACT-QOI-004", "QOI_OP_RGB chunk"),
        ])
        msf.merge_formats(formats=["qoi"])
        ids = [f["fact_id"] for f in _read_combined_facts(sandbox)]
        assert ids == sorted(ids)


class TestCheckMode:
    def test_check_reports_drift_without_writing(self, sandbox):
        _write_store(sandbox, [
            _fact("SAL-QOI-00004", "FACT-QOI-004", "QOI_OP_RGB chunk"),
        ])
        before = sandbox["combined"].read_bytes()
        summary = msf.merge_formats(formats=["qoi"], check=True)
        after = sandbox["combined"].read_bytes()
        assert before == after, "--check must not write"
        assert summary["drift"]
        assert summary["drift"][0]["missing_in_combined"] == 1

    def test_check_clean_when_in_sync(self, sandbox):
        _write_store(sandbox, [
            _fact("SAL-QOI-00001", "FACT-QOI-001", "QOI file header"),
        ])
        summary = msf.merge_formats(formats=["qoi"], check=True)
        assert not summary["drift"]


class TestSpecFactsTotal:
    def test_header_total_recomputed(self, sandbox):
        _write_store(sandbox, [
            _fact("SAL-QOI-00004", "FACT-QOI-004", "QOI_OP_RGB chunk"),
        ])
        msf.merge_formats(formats=["qoi"])
        data = json.loads(sandbox["combined"].read_text(encoding="utf-8"))
        assert data["spec_facts_total"] == 4

    def test_legacy_fact_without_fact_id_resolved_via_alias(self, sandbox):
        _write_store(sandbox, [
            {"qname": "FACT-QOI-002", "claim": "QOI encoded chunk", "section": "3.0"},
        ])
        summary = msf.merge_formats(formats=["qoi"])
        assert not summary["errors"]
        facts = _read_combined_facts(sandbox)
        target = next(f for f in facts if f["fact_id"] == "SAL-QOI-00002")
        assert target["section"] == "3.0"
        assert len(facts) == 3  # matched existing, not duplicated


def _read_aliases(sandbox) -> dict:
    return json.loads(sandbox["root"].joinpath("shared", "sal-fact-id-aliases.json").read_text(encoding="utf-8"))


class TestAliasReconciliation:
    """GAP-FORENSIC-008 convergence round 2 (ISSUE-GWB-CONV2-001): the merge
    step itself must maintain alias completeness, since writer scripts
    (e.g. seed_sal_candidates.py) cannot be trusted to remember to."""

    def test_missing_alias_backfilled_on_merge(self, sandbox):
        _write_store(sandbox, [
            _fact("SAL-QOI-00001", "FACT-QOI-001", "QOI file header"),
            _fact("SAL-QOI-00099", "FACT-QOI-099", "a newly seeded fact with no alias yet"),
        ])
        summary = msf.merge_formats(formats=["qoi"])
        assert not summary["errors"]
        aliases = _read_aliases(sandbox)["aliases"]
        assert aliases.get("FACT-QOI-099") == "SAL-QOI-00099"
        assert summary["alias_additions"] == [{"format_id": "qoi", "added": 1}]

    def test_alias_conflict_is_hard_error_not_overwrite(self, sandbox):
        aliases_path = sandbox["root"] / "shared" / "sal-fact-id-aliases.json"
        doc = json.loads(aliases_path.read_text(encoding="utf-8"))
        doc["aliases"]["FACT-QOI-099"] = "SAL-QOI-00050"  # pre-existing, disagreeing mapping
        aliases_path.write_text(json.dumps(doc), encoding="utf-8")

        _write_store(sandbox, [
            _fact("SAL-QOI-00099", "FACT-QOI-099", "a fact whose qname collides with a different existing alias"),
        ])
        summary = msf.merge_formats(formats=["qoi"])
        assert summary["errors"], "alias conflict must be a hard error"
        assert "alias conflict" in summary["errors"][0]["reason"]
        # existing alias must be untouched
        assert _read_aliases(sandbox)["aliases"]["FACT-QOI-099"] == "SAL-QOI-00050"

    def test_check_mode_reports_alias_drift_without_writing(self, sandbox):
        _write_store(sandbox, [
            _fact("SAL-QOI-00099", "FACT-QOI-099", "a newly seeded fact with no alias yet"),
        ])
        before = _read_aliases(sandbox)
        summary = msf.merge_formats(formats=["qoi"], check=True)
        after = _read_aliases(sandbox)
        assert before == after, "--check must not write the alias file"
        assert summary["alias_drift"] == [{"format_id": "qoi", "missing_aliases": 1}]

    def test_total_aliases_recomputed(self, sandbox):
        _write_store(sandbox, [
            _fact("SAL-QOI-00099", "FACT-QOI-099", "a newly seeded fact with no alias yet"),
        ])
        before_count = len(_read_aliases(sandbox)["aliases"])
        msf.merge_formats(formats=["qoi"])
        after = _read_aliases(sandbox)
        assert after["total_aliases"] == before_count + 1
        assert after["total_aliases"] == len(after["aliases"])

    def test_second_run_reports_no_alias_additions(self, sandbox):
        _write_store(sandbox, [
            _fact("SAL-QOI-00099", "FACT-QOI-099", "a newly seeded fact with no alias yet"),
        ])
        msf.merge_formats(formats=["qoi"])
        summary2 = msf.merge_formats(formats=["qoi"])
        assert summary2["alias_additions"] == []


class TestStoreAutoDiscovery:
    def test_new_store_merged_without_explicit_formats(self, sandbox):
        """TC-GWB-H06: a committed store for a format NOT in the hardcoded
        candidate list must be picked up by a default (formats=None) run."""
        store = {"format_id": "newfmt", "display_name": "NEWFMT", "facts": [
            _fact("SAL-NEWFMT-00001", "FACT-NEWFMT-001", "newfmt magic header"),
        ]}
        (sandbox["store_dir"] / "newfmt.yaml").write_text(
            yaml.safe_dump(store, sort_keys=False), encoding="utf-8")
        summary = msf.merge_formats()  # no formats argument
        merged_ids = [m["format_id"] for m in summary["merged"]]
        assert "newfmt" in merged_ids, "auto-discovery missed a new committed store"
        data = json.loads(sandbox["combined"].read_text(encoding="utf-8"))
        entry = next(e for e in data["results"] if e["format_id"] == "newfmt")
        assert entry["spec_facts"][0]["fact_id"] == "SAL-NEWFMT-00001"

    def test_check_mode_detects_drift_in_new_store(self, sandbox):
        store = {"format_id": "newfmt", "facts": [
            _fact("SAL-NEWFMT-00001", "FACT-NEWFMT-001", "newfmt magic header"),
        ]}
        (sandbox["store_dir"] / "newfmt.yaml").write_text(
            yaml.safe_dump(store, sort_keys=False), encoding="utf-8")
        summary = msf.merge_formats(check=True)  # no formats argument
        assert any(d["format_id"] == "newfmt" for d in summary["drift"])


class TestFreshCheckoutBootstrap:
    def test_missing_combined_db_is_bootstrapped_from_stores(self, sandbox):
        """Fresh checkout: no .local/spec-cache/sal-facts-latest.json.
        The compile step must regenerate it from committed stores."""
        sandbox["combined"].unlink()
        _write_store(sandbox, [
            _fact("SAL-QOI-00001", "FACT-QOI-001", "QOI file header"),
            _fact("SAL-QOI-00004", "FACT-QOI-004", "QOI_OP_RGB chunk"),
        ])
        summary = msf.merge_formats(formats=["qoi"])
        assert not summary["errors"]
        assert sandbox["combined"].exists()
        facts = _read_combined_facts(sandbox)
        assert {f["fact_id"] for f in facts} == {"SAL-QOI-00001", "SAL-QOI-00004"}
        data = json.loads(sandbox["combined"].read_text(encoding="utf-8"))
        assert data["spec_facts_total"] == 2
