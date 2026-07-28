"""Tests for V249/V250/V251 — portfolio audit Phase 1 prevention gates.

Plan: plans/.claude/primary-purpose-the-python-starry-cupcake.md
Taskcards: TC-PA-005 (V249), TC-PA-007 (V250), TC-PA-008 (V251)
Mission: PORTFOLIO-AUDIT-2026-07-16

These are full-repo-scan, declaration-ignoring validators modeled on V230/V242-V246.
Every fixture below builds a synthetic src/python/ tree under tmp_path and passes it as
repo_root, so none of these tests touch the real repository's src/python/ tree.

DISCRIMINATING POWER IS THE POINT OF THIS SUITE. All three validators PASS/WARN on the
real repo at their frozen baselines, so a green sweep proves nothing on its own. Each
validator therefore has an explicit "it FAILS on the thing it exists to catch" test:

  - test_v249_fails_on_new_file_not_in_baseline
  - test_v249_fails_on_file_exceeding_frozen_cap
  - test_v249_detects_aliased_syspath_that_naive_text_matching_misses  <- PA-F4 replay
  - test_v250_fails_on_new_stdlib_collision
  - test_v251_fails_on_unregistered_converter

PRE-FIX REPLAY FIXTURE (repo healing protocol): the aliased-sys.path test encodes the
exact evasion that a naive substring detector reports as clean. `import sys as _s;
_s.path.insert(...)` contains no "sys.path.insert" substring. It is a real pattern in
this repo (tools/supervisor/lifecycle_audit.py uses `import sys as _sys_cw`), so a text
detector is provably unsound. The test asserts both that V249 catches it AND that the
naive check it replaces does not.

FAIL-CLOSED IS ALSO TESTED. V149 (the zero-stub enforcer) returns PASS when its scanner
will not import — a fail-open enforcer is worse than no enforcer (PA-F3). V249/V251 must
never do that: test_v249_fails_closed_when_baseline_missing and
test_v251_fails_closed_when_matrix_missing pin that contract.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

_REPO = Path(__file__).resolve().parent.parent.parent
_SUPERVISOR = _REPO / "tools" / "supervisor"
if str(_SUPERVISOR) not in sys.path:
    sys.path.insert(0, str(_SUPERVISOR))

from governance_validators_converter_compat import (  # noqa: E402
    validate_converter_compatibility_registered,
)
from governance_validators_import_hygiene import (  # noqa: E402
    scan_syspath,
    validate_no_stdlib_namespace_collision,
    validate_no_syspath_mutation_in_product_source,
)

_DECL: dict = {"planned_work_items": [], "changed_files": []}


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _baseline(repo: Path, files: dict[str, dict]) -> None:
    _write(repo / "registry" / "governance" / "syspath-baseline.yaml",
           yaml.safe_dump({"schema_version": "1.0", "files": files}, sort_keys=False))


def _collision_baseline(repo: Path, known: dict) -> None:
    _write(repo / "registry" / "governance" / "namespace-collision-baseline.yaml",
           yaml.safe_dump({"schema_version": "1.0", "known_collisions": known}, sort_keys=False))


# ---------------------------------------------------------------------------
# V249 — validate_no_syspath_mutation_in_product_source
# ---------------------------------------------------------------------------

def test_v249_passes_when_no_syspath_anywhere(tmp_path: Path) -> None:
    _write(tmp_path / "src" / "python" / "fmt" / "codec.py", "import json\n\n\ndef load():\n    return {}\n")
    _baseline(tmp_path, {})
    r = validate_no_syspath_mutation_in_product_source(_DECL, tmp_path)
    assert r["result"] == "PASS"
    assert r["blocks_sprint"] is False


def test_v249_fails_on_new_file_not_in_baseline(tmp_path: Path) -> None:
    """The core prevention contract: NEW sys.path debt blocks the sprint."""
    _write(tmp_path / "src" / "python" / "fmt" / "conv.py",
           "import sys\nfrom pathlib import Path\nsys.path.insert(0, str(Path(__file__).parent))\n")
    _baseline(tmp_path, {})
    r = validate_no_syspath_mutation_in_product_source(_DECL, tmp_path)
    assert r["result"] == "FAIL"
    assert r["blocks_sprint"] is True
    assert any("src/python/fmt/conv.py" == i["path"] for i in r["items"])
    assert r["metrics"]["new_files"] == 1


def test_v249_fails_on_file_exceeding_frozen_cap(tmp_path: Path) -> None:
    """The ratchet: a baselined file may not GROW its sys.path count."""
    _write(tmp_path / "src" / "python" / "fmt" / "conv.py",
           "import sys\nsys.path.insert(0, 'a')\nsys.path.append('b')\n")
    _baseline(tmp_path, {"src/python/fmt/conv.py": {"occurrences": 1, "classification": "REDUNDANT"}})
    r = validate_no_syspath_mutation_in_product_source(_DECL, tmp_path)
    assert r["result"] == "FAIL"
    assert r["blocks_sprint"] is True
    item = next(i for i in r["items"] if i["path"] == "src/python/fmt/conv.py")
    assert item["occurrences"] == 2 and item["baseline_cap"] == 1


def test_v249_allows_file_at_exactly_its_cap(tmp_path: Path) -> None:
    _write(tmp_path / "src" / "python" / "fmt" / "conv.py", "import sys\nsys.path.insert(0, 'a')\n")
    _baseline(tmp_path, {"src/python/fmt/conv.py": {"occurrences": 1, "classification": "REDUNDANT"}})
    r = validate_no_syspath_mutation_in_product_source(_DECL, tmp_path)
    assert r["result"] == "PASS"
    assert r["blocks_sprint"] is False


def test_v249_warns_and_does_not_block_when_below_cap(tmp_path: Path) -> None:
    """Progress must not be punished, but a stale ratchet must be visible."""
    _write(tmp_path / "src" / "python" / "fmt" / "conv.py", "import json\n")
    _baseline(tmp_path, {"src/python/fmt/conv.py": {"occurrences": 2, "classification": "REDUNDANT"}})
    r = validate_no_syspath_mutation_in_product_source(_DECL, tmp_path)
    assert r["result"] == "WARN"
    assert r["blocks_sprint"] is False
    assert "stale" in r["summary"]


def test_v249_detects_aliased_syspath_that_naive_text_matching_misses(tmp_path: Path) -> None:
    """PA-F4 pre-fix replay: `import sys as _s` evades substring matching entirely.

    A naive detector greps for "sys.path.insert". The aliased form below contains no such
    substring, so the naive check reports CLEAN while the mutation is real. V249 resolves
    the alias via the AST and catches it. This is the fixture that would have caught the
    false-clean; it fails against a text-based implementation.
    """
    source = (
        "import sys as _s\n"
        "from pathlib import Path\n"
        "_s.path.insert(0, str(Path(__file__).parent))\n"
    )
    _write(tmp_path / "src" / "python" / "fmt" / "aliased.py", source)
    _baseline(tmp_path, {})

    # The naive detector this replaces: provably blind here.
    assert "sys.path.insert" not in source
    assert "sys.path.append" not in source

    r = validate_no_syspath_mutation_in_product_source(_DECL, tmp_path)
    assert r["result"] == "FAIL", "V249 must resolve `import sys as _s` aliases"
    assert r["blocks_sprint"] is True
    assert any(i["path"] == "src/python/fmt/aliased.py" for i in r["items"])


def test_v249_detects_from_sys_import_path_form(tmp_path: Path) -> None:
    """`from sys import path; path.insert(...)` is the other alias route."""
    _write(tmp_path / "src" / "python" / "fmt" / "fromimport.py",
           "from sys import path\npath.insert(0, 'x')\n")
    _baseline(tmp_path, {})
    r = validate_no_syspath_mutation_in_product_source(_DECL, tmp_path)
    assert r["result"] == "FAIL"
    assert any(i["path"] == "src/python/fmt/fromimport.py" for i in r["items"])


def test_v249_fails_closed_when_baseline_missing(tmp_path: Path) -> None:
    """Contrast V149 (PA-F3): an enforcer that cannot enforce must never report PASS."""
    _write(tmp_path / "src" / "python" / "fmt" / "conv.py", "import sys\nsys.path.insert(0, 'a')\n")
    r = validate_no_syspath_mutation_in_product_source(_DECL, tmp_path)
    assert r["result"] == "FAIL"
    assert r["blocks_sprint"] is True
    assert "fail-closed" in r["summary"]


def test_v249_classifies_load_bearing_vs_redundant(tmp_path: Path) -> None:
    """The csv-dependency distinction must be explicit and auditable, not a silent exemption."""
    _write(tmp_path / "src" / "python" / "fmt" / "loadbearing.py",
           "import sys\nsys.path.insert(0, 'r')\nfrom src.python.ff_csv.csv_writer import write_csv\n")
    _write(tmp_path / "src" / "python" / "fmt" / "redundant.py",
           "import sys\nsys.path.insert(0, 'r')\nfrom abw.abw_codec import load\n")
    live = scan_syspath(tmp_path / "src" / "python", tmp_path)
    assert live["src/python/fmt/loadbearing.py"]["classification"] == "LOAD_BEARING"
    assert live["src/python/fmt/redundant.py"]["classification"] == "REDUNDANT"


def test_v249_ignores_pycache_and_build(tmp_path: Path) -> None:
    _write(tmp_path / "src" / "python" / "fmt" / "__pycache__" / "x.py", "import sys\nsys.path.insert(0,'a')\n")
    _write(tmp_path / "src" / "python" / "fmt" / "build" / "y.py", "import sys\nsys.path.insert(0,'a')\n")
    _baseline(tmp_path, {})
    r = validate_no_syspath_mutation_in_product_source(_DECL, tmp_path)
    assert r["result"] == "PASS"


def test_v249_summary_never_claims_clean_while_debt_exists(tmp_path: Path) -> None:
    """Honesty contract: a frozen-baseline PASS must not read as 'no debt'."""
    _write(tmp_path / "src" / "python" / "fmt" / "conv.py", "import sys\nsys.path.insert(0, 'a')\n")
    _baseline(tmp_path, {"src/python/fmt/conv.py": {"occurrences": 1, "classification": "REDUNDANT"}})
    r = validate_no_syspath_mutation_in_product_source(_DECL, tmp_path)
    assert r["result"] == "PASS"
    assert "NOT clean" in r["summary"]


def test_v249_summary_says_clean_when_debt_is_actually_zero(tmp_path: Path) -> None:
    """Honesty contract, other direction (TC-PA-014 completion, 2026-07-20): once the
    ratchet is emitted at zero debt, the summary must say CLEAN, not the frozen-debt
    'NOT clean' wording that only applies when occurrences remain. Regression guard for
    the bug where the PASS-branch message was hardcoded to always claim frozen debt even
    when the live+baseline state was genuinely 0/0.
    """
    _write(tmp_path / "src" / "python" / "fmt" / "clean.py", "from other.mod import thing\n")
    _baseline(tmp_path, {})
    r = validate_no_syspath_mutation_in_product_source(_DECL, tmp_path)
    assert r["result"] == "PASS"
    assert "CLEAN" in r["summary"]
    assert "NOT clean" not in r["summary"]
    assert r["metrics"]["live_occurrences"] == 0


# ---------------------------------------------------------------------------
# V250 — validate_no_stdlib_namespace_collision
# ---------------------------------------------------------------------------

def test_v250_passes_with_no_collisions(tmp_path: Path) -> None:
    _write(tmp_path / "src" / "python" / "fodsx" / "__init__.py", "")
    _collision_baseline(tmp_path, {})
    r = validate_no_stdlib_namespace_collision(_DECL, tmp_path)
    assert r["result"] == "PASS"
    assert r["blocks_sprint"] is False


def test_v250_fails_on_new_stdlib_collision(tmp_path: Path) -> None:
    """A new package named after a stdlib module blocks the sprint."""
    _write(tmp_path / "src" / "python" / "json" / "__init__.py", "def dump_it():\n    pass\n")
    _collision_baseline(tmp_path, {})
    r = validate_no_stdlib_namespace_collision(_DECL, tmp_path)
    assert r["result"] == "FAIL"
    assert r["blocks_sprint"] is True
    entry = next(i for i in r["items"] if i["package"] == "json")
    assert entry["collides_with"] == "python_stdlib"


def test_v250_reports_both_failure_modes(tmp_path: Path) -> None:
    """PA-F2: unreachable-package AND process-wide-hijack are distinct modes; report both."""
    _write(tmp_path / "src" / "python" / "csv" / "__init__.py",
           "__all__ = ['write_csv']\n\n\ndef write_csv():\n    pass\n")
    _collision_baseline(tmp_path, {})
    r = validate_no_stdlib_namespace_collision(_DECL, tmp_path)
    entry = next(i for i in r["items"] if i["package"] == "csv")
    assert "MODE_1_UNREACHABLE" in entry["failure_modes"], "stdlib csv wins resolution"
    assert "MODE_2_HIJACK_RISK" in entry["failure_modes"], "our csv lacks reader/writer/DictReader"
    # The reported list is truncated for display; assert on a named stdlib symbol that the
    # synthetic package does not re-export, and that the stdlib surface was really measured.
    assert "DictReader" in entry["stdlib_api_not_reexported"]
    assert entry["stdlib_api_count"] > 10
    # Literal __all__ -> the count is trustworthy and IS published.
    assert entry["our_export_count"] == 1


def test_v250_does_not_publish_an_export_count_it_cannot_determine(tmp_path: Path) -> None:
    """The real csv computes __all__ at runtime (true size 119); the AST cannot know it.

    Publishing the static fallback would be a fabricated number. V250 must report None
    plus a note, and the MODE_2 verdict must survive without the count.
    """
    _write(tmp_path / "src" / "python" / "csv" / "__init__.py",
           "import sys as _sys\n"
           "__all__ = [k for k in vars(_sys.modules[__name__]) if not k.startswith('_')]\n")
    _collision_baseline(tmp_path, {})
    r = validate_no_stdlib_namespace_collision(_DECL, tmp_path)
    entry = next(i for i in r["items"] if i["package"] == "csv")
    assert entry["our_export_count"] is None
    assert "UNDETERMINABLE_STATICALLY" in entry["our_export_count_note"]
    assert "MODE_2_HIJACK_RISK" in entry["failure_modes"]


def test_v250_known_collision_warns_and_carries_migration_taskcard(tmp_path: Path) -> None:
    """Baselined debt WARNs — but only with a named owner and exit condition."""
    _write(tmp_path / "src" / "python" / "csv" / "__init__.py", "__all__ = []\n")
    _collision_baseline(tmp_path, {"csv": {"migration_taskcard": "TC-PA-013", "reason": "pre-existing"}})
    r = validate_no_stdlib_namespace_collision(_DECL, tmp_path)
    assert r["result"] == "WARN"
    assert r["blocks_sprint"] is False
    assert next(i for i in r["items"] if i["package"] == "csv")["migration_taskcard"] == "TC-PA-013"


def test_v250_warns_on_popular_pypi_collision_non_blocking(tmp_path: Path) -> None:
    """toml is not stdlib (tomllib is) — the collision is with the PyPI distribution (PA-F8).

    Policy fix 2026-07-20 (TC-PA-039 review): popular-PyPI collisions WARN, never FAIL/block
    — unlike a stdlib collision, this one is contingent on that specific distribution actually
    being installed alongside ours, which is not automatic or unconditional.
    """
    _write(tmp_path / "src" / "python" / "toml" / "__init__.py", "")
    _collision_baseline(tmp_path, {})
    r = validate_no_stdlib_namespace_collision(_DECL, tmp_path)
    assert r["result"] == "WARN"
    assert r["blocks_sprint"] is False
    assert next(i for i in r["items"] if i["package"] == "toml")["collides_with"] == "popular_pypi"


# ---------------------------------------------------------------------------
# V251 — validate_converter_compatibility_registered
# ---------------------------------------------------------------------------

def _matrix(repo: Path, converters: dict) -> None:
    _write(repo / "registry" / "converter-compatibility-matrix.yaml",
           yaml.safe_dump({"schema_version": "1.0", "converters": converters}, sort_keys=False))


def test_v251_fails_on_unregistered_converter(tmp_path: Path) -> None:
    """The gate: a converter nobody classified is a converter nobody justified."""
    _write(tmp_path / "src" / "python" / "toml" / "toml_to_ppm.py", "def toml_to_ppm():\n    pass\n")
    _matrix(tmp_path, {})
    r = validate_converter_compatibility_registered(_DECL, tmp_path)
    assert r["result"] == "FAIL"
    assert r["blocks_sprint"] is True
    assert any(i["path"] == "src/python/toml/toml_to_ppm.py" for i in r["items"])
    assert r["metrics"]["unregistered"] == 1


def test_v251_passes_when_all_registered(tmp_path: Path) -> None:
    _write(tmp_path / "src" / "python" / "csv" / "csv_to_tsv.py", "def csv_to_tsv():\n    pass\n")
    _matrix(tmp_path, {"src/python/csv/csv_to_tsv.py": {"pair": "csv->tsv", "category": "COMPATIBLE"}})
    r = validate_converter_compatibility_registered(_DECL, tmp_path)
    assert r["result"] == "PASS"
    assert r["blocks_sprint"] is False


def test_v251_warns_on_pending_incompatible(tmp_path: Path) -> None:
    _write(tmp_path / "src" / "python" / "fods" / "fods_to_pbm.py", "def fods_to_pbm():\n    pass\n")
    _matrix(tmp_path, {"src/python/fods/fods_to_pbm.py": {
        "pair": "fods->pbm", "category": "INCOMPATIBLE", "disposition": "PENDING"}})
    r = validate_converter_compatibility_registered(_DECL, tmp_path)
    assert r["result"] == "WARN"
    assert r["blocks_sprint"] is False
    assert r["metrics"]["incompatible_pending"] == 1


def test_v251_rejects_invalid_category(tmp_path: Path) -> None:
    _write(tmp_path / "src" / "python" / "csv" / "csv_to_tsv.py", "def csv_to_tsv():\n    pass\n")
    _matrix(tmp_path, {"src/python/csv/csv_to_tsv.py": {"pair": "csv->tsv", "category": "PROBABLY_FINE"}})
    r = validate_converter_compatibility_registered(_DECL, tmp_path)
    assert r["result"] == "FAIL"
    assert r["blocks_sprint"] is True


def test_v251_fails_closed_when_matrix_missing(tmp_path: Path) -> None:
    _write(tmp_path / "src" / "python" / "csv" / "csv_to_tsv.py", "def csv_to_tsv():\n    pass\n")
    r = validate_converter_compatibility_registered(_DECL, tmp_path)
    assert r["result"] == "FAIL"
    assert r["blocks_sprint"] is True
    assert "fail-closed" in r["summary"]


# ---------------------------------------------------------------------------
# V149 fail-open heal (PA-F3, TC-PA-004)
# ---------------------------------------------------------------------------

def test_v149_fails_closed_when_scanner_unavailable(tmp_path: Path, monkeypatch) -> None:
    """PA-F3 regression: the zero-stub enforcer must not report PASS when it did not run.

    V149 is in STRUCTURAL_GOV_BLOCKS — it is the gate certifying src/ is stub-free. Until
    2026-07-17 an ImportError on no_stub_scan returned PASS/blocks_sprint=False, silently
    converting "not checked" into "clean". This pins the fail-closed contract.

    TC-PA-029 (2026-07-17): V149 no longer imports the scanner via ``from no_stub_scan import``
    (which required a ``sys.path.insert`` — the aliased anti-pattern V249 bans). It now loads the
    scanner via importlib through the ``_load_no_stub_report`` seam, so unavailability is
    simulated by monkeypatching that seam to raise, NOT by poisoning
    ``sys.modules['no_stub_scan']`` (which the importlib load, using a distinct module name, no
    longer consults).
    """
    import governance_validators_ext4 as _ext4
    from governance_validators_ext4 import validate_source_stubs

    def _boom():
        raise ImportError("simulated: no_stub_scan unavailable")

    monkeypatch.setattr(_ext4, "_load_no_stub_report", _boom)

    product = validate_source_stubs(
        {"planned_work_items": [{"id": "X", "work_item_type": "PRODUCT_SOURCE"}]}, tmp_path)
    assert product["result"] == "FAIL"
    assert product["blocks_sprint"] is True
    assert "not a clean one" in product["summary"]

    # Nothing to certify -> visible but non-blocking. Still never PASS.
    empty = validate_source_stubs({"planned_work_items": []}, tmp_path)
    assert empty["result"] == "WARN"
    assert empty["blocks_sprint"] is False


# ---------------------------------------------------------------------------
# Real-repo baseline pins — these guard the frozen artifacts, not the source tree.
# ---------------------------------------------------------------------------

def test_real_repo_syspath_baseline_matches_live_scan() -> None:
    """The frozen ratchet must describe reality, or V249's verdict is meaningless."""
    baseline = yaml.safe_load((_REPO / "registry" / "governance" / "syspath-baseline.yaml").read_text(encoding="utf-8"))
    live = scan_syspath(_REPO / "src" / "python", _REPO)
    live_files = {k: v for k, v in live.items() if v["classification"] != "PARSE_ERROR"}
    assert set(live_files) == set(baseline["files"]), "baseline drifted from the real tree"
    assert sum(v["occurrences"] for v in live_files.values()) == baseline["totals"]["occurrences"]


def test_real_repo_every_converter_is_classified() -> None:
    """V251's real-repo contract: 0 unregistered converters."""
    r = validate_converter_compatibility_registered(_DECL, _REPO)
    assert r["metrics"]["unregistered"] == 0
    assert r["result"] in ("PASS", "WARN")
    assert r["blocks_sprint"] is False
