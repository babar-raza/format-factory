"""Change 1 (plan investigate-and-plan-a-snuggly-grove): full-chain contract refresh.

run_contract_full_refresh must chain staleness/recompile -> reconciliation ->
gap-ledger refresh in a single Step 0a-fcl. Before this, the chain stopped after
staleness and the gap ledger stayed frozen.

The three pipeline modules are faked in sys.modules: the unit under test is the
orchestration (which formats get reconciled, which get gap-compiled, what
survives a failure), not the pipeline itself.
"""

from __future__ import annotations

import json
import sys
import types
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

# tools/supervisor/autonomous_cycle_extensions/ (a package) shadows
# autonomous_cycle_extensions.py, and re-exports the standalone module's public
# functions via importlib. This import is therefore the exact object
# autonomous_cycle.py's Step 0a-fcl calls — see the re-export test below.
from autonomous_cycle_extensions import run_contract_full_refresh  # noqa: E402

# The re-export skips underscore-prefixed names, so reach the private helper
# through the function's own module globals.
_reconciliation_is_stale = run_contract_full_refresh.__globals__["_reconciliation_is_stale"]

RECON_SUFFIX = "-reconciliation.json"


class _FakePipeline:
    """Records the calls the orchestrator makes into the contract pipeline."""

    def __init__(self, check_all_result: dict):
        self._check_all_result = check_all_result
        self.check_all_calls: list[dict] = []
        self.reconciled: list[str] = []
        self.gap_compiled: list[str] = []
        self.reconcile_failures: set[str] = set()
        self.gap_failures: set[str] = set()

    def check_all(self, *, refresh: bool = False) -> dict:
        self.check_all_calls.append({"refresh": refresh})
        return self._check_all_result

    def reconcile(self, format_id: str) -> dict:
        if format_id in self.reconcile_failures:
            raise RuntimeError(f"no compiled contract for {format_id}")
        self.reconciled.append(format_id)
        return {"format_id": format_id, "contract_input_digests": {"sal_facts_sha256": "new"}}

    def compile_gaps(self, format_id: str) -> dict:
        if format_id in self.gap_failures:
            raise RuntimeError(f"no reconciliation report: {format_id}")
        self.gap_compiled.append(format_id)
        return {"emitted": 1, "replaced_previous": 0, "ledger_total": 1}


@pytest.fixture
def fake_repo(tmp_path: Path) -> Path:
    """A repo root shaped just enough for the orchestrator's real guards."""
    fcl = tmp_path / "tools" / "format_contract"
    fcl.mkdir(parents=True)
    # run_contract_full_refresh returns early unless the checker module exists.
    (fcl / "staleness_checker.py").write_text("", encoding="utf-8")
    (tmp_path / "reports" / "format-contract-layer").mkdir(parents=True)
    (tmp_path / "shared" / "format-contracts").mkdir(parents=True)
    return tmp_path


def _install(monkeypatch: pytest.MonkeyPatch, pipeline: _FakePipeline,
             contracts: dict[str, dict] | None = None) -> None:
    """Put fake pipeline modules in sys.modules under their bare import names."""
    checker = types.ModuleType("staleness_checker")
    checker.check_all = pipeline.check_all
    reconciler = types.ModuleType("contract_reconciler")
    reconciler.reconcile = pipeline.reconcile
    gaps = types.ModuleType("gap_compiler")
    gaps.compile_gaps = pipeline.compile_gaps
    cio = types.ModuleType("canonical_io")
    cio.load_yaml = lambda path: (contracts or {}).get(Path(path).stem)

    for name, module in (
        ("staleness_checker", checker),
        ("contract_reconciler", reconciler),
        ("gap_compiler", gaps),
        ("canonical_io", cio),
    ):
        monkeypatch.setitem(sys.modules, name, module)
    monkeypatch.delitem(sys.modules, "contract_compiler", raising=False)


def test_refreshed_and_unreconciled_formats_flow_through_all_three_phases(
    fake_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Plan verification #1: qoi (refreshed) and csv (UNRECONCILED) must both be
    reconciled, then gap-compiled — in one invocation."""
    pipeline = _FakePipeline({
        "refreshed": ["qoi"],
        "tasks": [{"condition": "UNRECONCILED", "format_id": "csv"}],
    })
    _install(monkeypatch, pipeline)

    result = run_contract_full_refresh(fake_repo)

    assert pipeline.check_all_calls == [{"refresh": True}], "Phase 1 must recompile stale contracts"
    assert pipeline.reconciled == ["csv", "qoi"], "Phase 2 must reconcile refreshed + UNRECONCILED"
    assert pipeline.gap_compiled == ["csv", "qoi"], "Phase 3 must gap-compile both"
    assert result == {
        "refreshed": ["qoi"],
        "reconciled": ["csv", "qoi"],
        "gaps_updated": ["csv", "qoi"],
        "errors": [],
    }
    # Phase 2 writes the report reconcile() returns — Phase 3 reads it off disk.
    written = fake_repo / "reports" / "format-contract-layer" / f"qoi{RECON_SUFFIX}"
    assert json.loads(written.read_text(encoding="utf-8"))["format_id"] == "qoi"


def test_missing_refreshed_key_is_tolerated(fake_repo: Path,
                                            monkeypatch: pytest.MonkeyPatch) -> None:
    """check_all omits "refreshed" entirely when nothing was recompiled."""
    pipeline = _FakePipeline({"task_count": 0, "tasks": []})
    _install(monkeypatch, pipeline)

    result = run_contract_full_refresh(fake_repo)

    assert result["refreshed"] == []
    assert result["errors"] == []
    assert pipeline.reconciled == []


def test_stale_reconciliation_is_re_reconciled(fake_repo: Path,
                                               monkeypatch: pytest.MonkeyPatch) -> None:
    """A report whose contract_input_digests drifted from the contract must be
    re-reconciled even with no Phase 1 activity — the case check_all misses."""
    recon_dir = fake_repo / "reports" / "format-contract-layer"
    (recon_dir / f"toml{RECON_SUFFIX}").write_text(
        json.dumps({"contract_input_digests": {"sal_facts_sha256": "old"}}), encoding="utf-8")
    (recon_dir / f"tsv{RECON_SUFFIX}").write_text(
        json.dumps({"contract_input_digests": {"sal_facts_sha256": "current"}}), encoding="utf-8")

    pipeline = _FakePipeline({"tasks": []})
    _install(monkeypatch, pipeline, contracts={
        "toml": {"contract_metadata": {"input_digests": {"sal_facts_sha256": "new"}}},
        "tsv": {"contract_metadata": {"input_digests": {"sal_facts_sha256": "current"}}},
    })

    result = run_contract_full_refresh(fake_repo)

    assert result["reconciled"] == ["toml"], "only the drifted format re-reconciles"
    assert pipeline.gap_compiled == ["toml", "tsv"], "Phase 3 covers every report"


def test_per_format_failures_are_isolated_and_never_raise(
    fake_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pipeline = _FakePipeline({
        "refreshed": ["qoi", "abw"],
        "tasks": [{"condition": "UNRECONCILED", "format_id": "csv"}],
    })
    pipeline.reconcile_failures = {"abw"}
    pipeline.gap_failures = {"csv"}
    _install(monkeypatch, pipeline)

    result = run_contract_full_refresh(fake_repo)

    assert result["reconciled"] == ["csv", "qoi"], "abw's failure must not stop the others"
    assert result["gaps_updated"] == ["qoi"]
    assert len(result["errors"]) == 2
    assert any(e.startswith("phase2:reconcile:abw:") for e in result["errors"])
    assert any(e.startswith("phase3:compile_gaps:csv:") for e in result["errors"])


def test_phase1_failure_leaves_later_phases_running(fake_repo: Path,
                                                    monkeypatch: pytest.MonkeyPatch) -> None:
    recon_dir = fake_repo / "reports" / "format-contract-layer"
    (recon_dir / f"qoi{RECON_SUFFIX}").write_text("{}", encoding="utf-8")

    pipeline = _FakePipeline({})
    _install(monkeypatch, pipeline)
    boom = types.ModuleType("staleness_checker")

    def _explode(*, refresh: bool = False):
        raise RuntimeError("store unreadable")

    boom.check_all = _explode
    monkeypatch.setitem(sys.modules, "staleness_checker", boom)

    result = run_contract_full_refresh(fake_repo)

    assert result["errors"] and result["errors"][0].startswith("phase1:check_all:")
    assert result["gaps_updated"] == ["qoi"], "Phase 3 still refreshes existing reports"


def test_sys_path_is_not_left_polluted(fake_repo: Path,
                                       monkeypatch: pytest.MonkeyPatch) -> None:
    """tools/format_contract holds a quality_scorer.py that shadows the
    tools/supervisor one; the orchestrator must not leave it on sys.path.

    The pipeline modules also insert their own absolute path at import time, so
    this covers the entry the orchestrator never spelled itself: a filter keyed
    on its own path string would miss it and leak the shadow.
    """
    pipeline = _FakePipeline({"tasks": []})
    _install(monkeypatch, pipeline)
    smuggled = str(Path(__file__).parent / "some-other-format_contract-copy")

    def _check_all_that_inserts_its_own_path(*, refresh: bool = False) -> dict:
        sys.path.insert(0, smuggled)  # what contract_compiler et al. do on import
        return pipeline.check_all(refresh=refresh)

    checker = types.ModuleType("staleness_checker")
    checker.check_all = _check_all_that_inserts_its_own_path
    monkeypatch.setitem(sys.modules, "staleness_checker", checker)

    before = list(sys.path)
    run_contract_full_refresh(fake_repo)

    assert str(fake_repo / "tools" / "format_contract") not in sys.path
    assert smuggled not in sys.path, "a path inserted by the pipeline must not leak either"
    assert sys.path == before


def test_missing_pipeline_directory_is_a_no_op(tmp_path: Path) -> None:
    assert run_contract_full_refresh(tmp_path) == {
        "refreshed": [], "reconciled": [], "gaps_updated": [], "errors": [],
    }


def test_package_reexports_the_step_0a_fcl_entrypoints() -> None:
    """autonomous_cycle.py resolves autonomous_cycle_extensions to the package
    directory, not the .py file; the package re-exports the standalone module's
    functions. If that re-export ever drops these names, Step 0a-fcl dies inside
    autonomous_cycle.py's blanket try/except and the chain silently no-ops.
    """
    import autonomous_cycle_extensions as pkg

    assert hasattr(pkg, "__path__"), "the package is what production imports"
    assert callable(pkg.run_contract_full_refresh)
    assert callable(pkg.run_contract_healing_prepass), "back-compat alias must stay importable"


def test_healing_prepass_alias_runs_the_full_chain(fake_repo: Path,
                                                   monkeypatch: pytest.MonkeyPatch) -> None:
    """The old name keeps its int contract (repair-task count) while delegating."""
    import autonomous_cycle_extensions as pkg

    pipeline = _FakePipeline({"refreshed": ["qoi"], "tasks": []})
    _install(monkeypatch, pipeline)
    tasks_file = fake_repo / ".local" / "supervisor" / "contract-repair-tasks.json"
    tasks_file.parent.mkdir(parents=True)
    tasks_file.write_text(json.dumps({"task_count": 7}), encoding="utf-8")

    count = pkg.run_contract_healing_prepass(fake_repo)

    assert count == 7
    assert pipeline.reconciled == ["qoi"], "alias must reach Phase 2, not stop at staleness"
    assert pipeline.gap_compiled == ["qoi"]


@pytest.mark.parametrize("recon_body, contract_doc, expected", [
    ({"contract_input_digests": {"a": "1"}}, {"contract_metadata": {"input_digests": {"a": "1"}}}, False),
    ({"contract_input_digests": {"a": "1"}}, {"contract_metadata": {"input_digests": {"a": "2"}}}, True),
    ({"contract_input_digests": {"a": "1"}}, None, False),  # no contract -> not our call
    ({}, {"contract_metadata": {"input_digests": {"a": "1"}}}, True),  # unstamped report
])
def test_reconciliation_staleness_compares_digest_dicts(
    tmp_path: Path, recon_body: dict, contract_doc: dict | None, expected: bool
) -> None:
    recon = tmp_path / f"fmt{RECON_SUFFIX}"
    recon.write_text(json.dumps(recon_body), encoding="utf-8")
    assert _reconciliation_is_stale(recon, contract_doc) is expected


def test_reconciliation_staleness_never_raises_on_bad_json(tmp_path: Path) -> None:
    recon = tmp_path / f"fmt{RECON_SUFFIX}"
    recon.write_text("{not json", encoding="utf-8")
    assert _reconciliation_is_stale(recon, {"contract_metadata": {"input_digests": {}}}) is False
