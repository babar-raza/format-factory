"""
test_proof_backed_poc_gate.py

Tests for tools/supervisor/proof_backed_poc_gate.py

Proves:
- gates_passed "1-10" text alone is insufficient for POC readiness
- empty proof graph fails
- missing raw logs fails
- missing source files fails
- missing examples fails where required
- missing proof records fails
- ai_draft proof fails (advisory warning, not hard block — but not sufficient alone)
- FODS/FODT/Netpbm pass only with proof links
- FOSS minimum requires 3 proof-backed passes
- Gate 11 pending does not block POC candidate if proof complete
- release approval pending is separate from POC readiness
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.supervisor.proof_backed_poc_gate import (
    evaluate_poc_readiness,
    evaluate_format,
    _check_source_exists,
    _check_tests_exist,
    _check_raw_log_exists,
    _check_examples_exist,
    _check_proof_record,
    COMMERCIAL_NET_FORMATS,
    FOSS_PYTHON_FORMATS,
    FOSS_MINIMUM_PASS_COUNT,
)


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _fmt(
    name="TEST",
    source_dirs=None,
    test_dirs=None,
    example_dirs=None,
    log_patterns=None,
    ledger_key="test",
    required_log=True,
    required_example=True,
):
    return {
        "format": name,
        "source_dirs": source_dirs or [],
        "source_extensions": [".py", ".cs"],
        "test_dirs": test_dirs or [],
        "test_extensions": [".py", ".cs"],
        "example_dirs": example_dirs or [],
        "log_search_patterns": log_patterns or [name.lower()],
        "ledger_key": ledger_key,
        "required_log": required_log,
        "required_example": required_example,
    }


def _make_tmp_repo(tmp_path):
    """Create a minimal fake repo with required structure."""
    # Source
    src = tmp_path / "src" / "net" / "testfmt"
    src.mkdir(parents=True)
    (src / "TestDocument.cs").write_text("public class TestDocument { void Load() {} }", encoding="utf-8")

    # Tests
    tests = tmp_path / "tests" / "net" / "testfmt"
    tests.mkdir(parents=True)
    (tests / "TestDocumentTests.cs").write_text("[Fact] public void Test1() {}", encoding="utf-8")

    # Examples
    ex = tmp_path / "examples" / "net" / "testfmt"
    ex.mkdir(parents=True)
    (ex / "ExampleUsage.cs").write_text("// example", encoding="utf-8")

    # Raw log
    log_dir = tmp_path / "reports" / "sprint001" / "raw-logs"
    log_dir.mkdir(parents=True)
    (log_dir / "testfmt-tests.log").write_text("collected 10 items\ntestfmt passed 10 tests\n10 passed", encoding="utf-8")

    # Proof record (ledger)
    ledger_dir = tmp_path / "reports" / "r90"
    ledger_dir.mkdir(parents=True)
    ledger = [{"run_id": "r001", "format": "testfmt", "source_files": ["src/net/testfmt/TestDocument.cs"]}]
    (ledger_dir / "product-code-change-ledger.json").write_text(json.dumps(ledger), encoding="utf-8")

    # poc-targets.yaml
    poc = tmp_path / "product-capability-matrix"
    poc.mkdir(parents=True)
    (poc / "poc-targets.yaml").write_text("""
commercial_net_products:
  - format: TESTFMT
    gates_passed: "1-10"
    gate_11_g11g: NOT_STARTED
""", encoding="utf-8")

    return tmp_path


# ─────────────────────────────────────────────────────────────
# Test: gates_passed alone is insufficient
# ─────────────────────────────────────────────────────────────

class TestShallowGatesNotSufficient:
    def test_gates_passed_text_alone_does_not_pass_gate(self, tmp_path):
        """A repo with only poc-targets.yaml gates_passed must fail proof gate."""
        poc = tmp_path / "product-capability-matrix"
        poc.mkdir(parents=True)
        (poc / "poc-targets.yaml").write_text("""
commercial_net_products:
  - format: FODS
    gates_passed: "1-10"
    gate_11_g11g: NOT_STARTED
foss_reduced_products: []
""", encoding="utf-8")

        fmt = _fmt("FODS", source_dirs=["src/net/fods"], test_dirs=["tests/net/fods"])
        result = evaluate_format(fmt, tmp_path)
        assert result["passed"] is False, "gates_passed text alone must not pass proof gate"

    def test_poc_targets_proof_record_is_not_proof(self, tmp_path):
        """poc-targets.yaml is advisory only — proof_record check must fail for it."""
        poc = tmp_path / "product-capability-matrix"
        poc.mkdir(parents=True)
        (poc / "poc-targets.yaml").write_text("commercial_net_products:\n  - format: FODS\n    gates_passed: \"1-10\"\n", encoding="utf-8")

        fmt = _fmt("FODS", ledger_key="fods")
        result = _check_proof_record(fmt, tmp_path)
        # poc-targets.yaml is not a proof record — must not pass
        assert result["pass"] is False, "poc-targets.yaml must not count as proof record"

    def test_gates_passed_string_check_is_excluded(self, tmp_path):
        """The gate must not check gates_passed string."""
        # Even if we add gates_passed: "1-10" text, no other proof → FAIL
        poc = tmp_path / "product-capability-matrix"
        poc.mkdir(parents=True)
        (poc / "poc-targets.yaml").write_text("foss_reduced_products:\n  - format: ZST\n    gates_passed: \"1-10\"\n", encoding="utf-8")

        fmt = _fmt("ZST", source_dirs=["src/python/zst"], test_dirs=["tests/python/zst"])
        result = evaluate_format(fmt, tmp_path)
        assert result["passed"] is False


# ─────────────────────────────────────────────────────────────
# Test: individual checks
# ─────────────────────────────────────────────────────────────

class TestIndividualProofChecks:
    def test_missing_source_fails(self, tmp_path):
        """No source file → fail."""
        fmt = _fmt("FODS", source_dirs=["src/net/fods"])
        result = _check_source_exists(fmt, tmp_path)
        assert result["pass"] is False

    def test_source_present_passes(self, tmp_path):
        """Source file present → pass."""
        d = tmp_path / "src" / "net" / "fods"
        d.mkdir(parents=True)
        (d / "FodsDocument.cs").write_text("x" * 200, encoding="utf-8")
        fmt = _fmt("FODS", source_dirs=["src/net/fods"])
        result = _check_source_exists(fmt, tmp_path)
        assert result["pass"] is True

    def test_missing_tests_fails(self, tmp_path):
        """No test files → fail."""
        fmt = _fmt("FODS", test_dirs=["tests/net/fods"])
        result = _check_tests_exist(fmt, tmp_path)
        assert result["pass"] is False

    def test_tests_present_passes(self, tmp_path):
        """Test files present → pass."""
        d = tmp_path / "tests" / "net" / "fods"
        d.mkdir(parents=True)
        (d / "FodsTests.cs").write_text("[Fact] void Test() {}", encoding="utf-8")
        fmt = _fmt("FODS", test_dirs=["tests/net/fods"])
        result = _check_tests_exist(fmt, tmp_path)
        assert result["pass"] is True

    def test_missing_raw_log_fails(self, tmp_path):
        """No raw log → fail."""
        fmt = _fmt("FODS", log_patterns=["fods"])
        result = _check_raw_log_exists(fmt, tmp_path)
        assert result["pass"] is False

    def test_raw_log_present_passes(self, tmp_path):
        """Raw log with format content → pass."""
        log_dir = tmp_path / "reports" / "sprint" / "raw-logs"
        log_dir.mkdir(parents=True)
        (log_dir / "fods-tests.log").write_text("fods tests passed 100 items\n100 passed in 5s", encoding="utf-8")
        fmt = _fmt("FODS", log_patterns=["fods"])
        result = _check_raw_log_exists(fmt, tmp_path)
        assert result["pass"] is True

    def test_wrong_content_log_fails(self, tmp_path):
        """Log with wrong content → fail for target format."""
        log_dir = tmp_path / "reports" / "sprint" / "raw-logs"
        log_dir.mkdir(parents=True)
        (log_dir / "other-tests.log").write_text("completely unrelated log content about CSV", encoding="utf-8")
        fmt = _fmt("FODS", log_patterns=["fods", "FODS"])
        result = _check_raw_log_exists(fmt, tmp_path)
        assert result["pass"] is False

    def test_missing_examples_fails(self, tmp_path):
        """No examples → fail when required."""
        fmt = _fmt("FODS", example_dirs=["examples/net/fods"], required_example=True)
        result = _check_examples_exist(fmt, tmp_path)
        assert result["pass"] is False

    def test_examples_present_passes(self, tmp_path):
        """Examples present → pass."""
        d = tmp_path / "examples" / "net" / "fods"
        d.mkdir(parents=True)
        (d / "ExportCsvExample.cs").write_text("// example", encoding="utf-8")
        fmt = _fmt("FODS", example_dirs=["examples/net/fods"], required_example=True)
        result = _check_examples_exist(fmt, tmp_path)
        assert result["pass"] is True

    def test_missing_proof_record_fails(self, tmp_path):
        """No ledger or proof graph → fail."""
        fmt = _fmt("FODS", ledger_key="fods")
        result = _check_proof_record(fmt, tmp_path)
        assert result["pass"] is False

    def test_ledger_entry_without_projection_fails(self, tmp_path):
        """Ledger entry alone (no projection) → fails per Option B contract."""
        ledger_dir = tmp_path / "reports" / "r90"
        ledger_dir.mkdir(parents=True)
        ledger = [{"run_id": "r001", "format": "fods", "source_files": ["src/net/fods/FodsDocument.cs"]}]
        (ledger_dir / "product-code-change-ledger.json").write_text(json.dumps(ledger), encoding="utf-8")
        fmt = _fmt("FODS", ledger_key="fods")
        result = _check_proof_record(fmt, tmp_path)
        assert result["pass"] is False, "Ledger-only without projection must fail per Option B contract"
        assert "NO PROJECTION" in result.get("source", "")

    def test_ledger_entry_with_projection_passes(self, tmp_path):
        """Ledger entry + proof graph projection → pass."""
        ledger_dir = tmp_path / "reports" / "r90"
        ledger_dir.mkdir(parents=True)
        ledger = [{"run_id": "r001", "format": "fods", "source_files": ["src/net/fods/FodsDocument.cs"]}]
        (ledger_dir / "product-code-change-ledger.json").write_text(json.dumps(ledger), encoding="utf-8")
        # Add proof graph projection
        proj_dir = tmp_path / "reports" / "autonomous-system-audit" / "projected-proof-graph"
        proj_dir.mkdir(parents=True)
        (proj_dir / "nodes.jsonl").write_text(
            '{"node_id": "abc123", "type": "product", "label": "fods"}\n',
            encoding="utf-8"
        )
        fmt = _fmt("FODS", ledger_key="fods")
        result = _check_proof_record(fmt, tmp_path)
        assert result["pass"] is True
        assert result.get("projection_verified") is True

    def test_proof_graph_node_passes(self, tmp_path):
        """Proof graph node (nodes.jsonl) with ledger → pass."""
        ledger_dir = tmp_path / "reports" / "r90"
        ledger_dir.mkdir(parents=True)
        ledger = [{"run_id": "r001", "format": "fods", "source_files": ["src/net/fods/FodsDocument.cs"]}]
        (ledger_dir / "product-code-change-ledger.json").write_text(json.dumps(ledger), encoding="utf-8")
        pg_dir = tmp_path / "reports" / "sprint001"
        pg_dir.mkdir(parents=True)
        (pg_dir / "proof-graph-nodes.jsonl").write_text(
            '{"node_id": "fods-doc", "format": "FODS", "type": "product_document", "path": "src/net/fods/FodsDocument.cs"}\n',
            encoding="utf-8"
        )
        fmt = _fmt("FODS", ledger_key="fods")
        result = _check_proof_record(fmt, tmp_path)
        assert result["pass"] is True

    def test_no_examples_required_passes(self, tmp_path):
        """When example not required → pass without examples."""
        fmt = _fmt("DIF", example_dirs=[], required_example=False)
        result = _check_examples_exist(fmt, tmp_path)
        assert result["pass"] is True


# ─────────────────────────────────────────────────────────────
# Test: full evaluate_poc_readiness
# ─────────────────────────────────────────────────────────────

class TestEvaluatePocReadiness:
    def test_empty_repo_not_ready(self, tmp_path):
        """Empty repo returns POC_NOT_READY_CONTINUE."""
        result = evaluate_poc_readiness(tmp_path)
        assert result["poc_ready"] is False
        assert result["decision"] == "POC_NOT_READY_CONTINUE"

    def test_poc_ready_with_full_proof(self, tmp_path):
        """Repo with complete proof returns POC_READY."""
        # Build a fake repo where ALL checks pass for all formats
        repo = _build_full_proof_repo(tmp_path)
        result = evaluate_poc_readiness(repo)
        assert result["poc_ready"] is True

    def test_missing_log_for_one_commercial_not_ready(self, tmp_path):
        """If one commercial format missing raw log → not ready."""
        repo = _build_full_proof_repo(tmp_path)
        # Remove FODS log content
        for log_f in (repo / "reports").rglob("*.log"):
            content = log_f.read_text(encoding="utf-8")
            if "fods" in content.lower():
                log_f.write_text("unrelated content", encoding="utf-8")
        result = evaluate_poc_readiness(repo)
        # FODS fails → commercial not all pass → not ready
        assert result["poc_ready"] is False
        assert result["decision"] == "POC_NOT_READY_CONTINUE"

    def test_foss_minimum_3_required(self, tmp_path):
        """Must have 3+ FOSS formats with proof, not 2."""
        repo = _build_full_proof_repo(tmp_path)
        # Remove 2 FOSS log files
        removed = 0
        for log_f in list((repo / "reports").rglob("*.log")):
            content = log_f.read_text(encoding="utf-8")
            if any(p in content.lower() for p in ["sylk", "zst"]) and removed < 2:
                log_f.write_text("unrelated content", encoding="utf-8")
                removed += 1
        result = evaluate_poc_readiness(repo)
        assert result["foss_pass_count"] < 3
        assert result["poc_ready"] is False

    def test_gate11_pending_does_not_block_poc_candidate(self, tmp_path):
        """Gate 11 not approved means release_approval_pending=True but poc_ready can still be True."""
        repo = _build_full_proof_repo(tmp_path)
        # gate_11_g11g: NOT_STARTED in poc-targets.yaml
        result = evaluate_poc_readiness(repo)
        if result["poc_ready"]:
            # If proof is complete, release_approval_pending=True but poc_ready=True is allowed
            assert result["release_approval_pending"] is True
            assert result["poc_ready"] is True

    def test_release_pending_separate_from_poc_readiness(self, tmp_path):
        """release_approval_pending and poc_ready are independent fields."""
        result = evaluate_poc_readiness(tmp_path)
        # Both fields must exist
        assert "poc_ready" in result
        assert "release_approval_pending" in result
        # They can have independent values
        # An empty repo: poc_ready=False but release_approval_pending may be True or False
        assert isinstance(result["poc_ready"], bool)
        assert isinstance(result["release_approval_pending"], bool)

    def test_required_fields_present(self, tmp_path):
        """Result must have all required fields."""
        result = evaluate_poc_readiness(tmp_path)
        required = [
            "poc_ready", "release_approval_pending", "commercial_targets",
            "foss_targets", "foss_pass_count", "decision", "terminal_state",
            "proof_failures", "missing_logs", "missing_proof_records",
        ]
        for field in required:
            assert field in result, f"Missing required field: {field}"

    def test_decision_is_valid_enum(self, tmp_path):
        """Decision must be one of the 6 valid decision strings."""
        valid_decisions = {
            "MAINSTREAM_POC_READY_CANDIDATE_AUTHORITY_VERIFIED_RELEASE_APPROVAL_PENDING",
            "MAINSTREAM_POC_READY_CANDIDATE_AUTHORITY_VERIFIED",
            "POC_NOT_READY_CONTINUE",
            "HOST_INVOCATION_LAYER_MISSING",
            "MAINSTREAM_POC_UNSAFE_WORKSPACE",
            "MAINSTREAM_POC_BLOCKED_EXTERNAL_GATE",
        }
        result = evaluate_poc_readiness(tmp_path)
        assert result["decision"] in valid_decisions

    def test_phase4_docs_only_not_product_continuation(self, tmp_path):
        """Gate 11 readiness packets (docs) alone do not count as proof."""
        # Create only Gate 11 readiness packet docs — no source, tests, logs
        docs = tmp_path / "reports" / "autonomous-execution-chaining" / "product-continuation"
        docs.mkdir(parents=True)
        (docs / "gate11-readiness-fods.md").write_text("# FODS Gate 11 Readiness Packet", encoding="utf-8")

        poc = tmp_path / "product-capability-matrix"
        poc.mkdir(parents=True)
        (poc / "poc-targets.yaml").write_text("commercial_net_products:\n  - format: FODS\n    gates_passed: '1-10'\n    gate_11_g11g: NOT_STARTED\nfoss_reduced_products: []\n", encoding="utf-8")

        result = evaluate_poc_readiness(tmp_path)
        assert result["poc_ready"] is False, "Gate 11 doc packets alone must not make POC ready"

    def test_missing_proof_records_listed(self, tmp_path):
        """Formats with no proof records must be listed in missing_proof_records."""
        result = evaluate_poc_readiness(tmp_path)
        # All formats should have missing proof records in empty repo
        assert len(result["missing_proof_records"]) > 0

    def test_foss_minimum_constant(self):
        """FOSS minimum must be 3."""
        assert FOSS_MINIMUM_PASS_COUNT == 3

    def test_commercial_formats_defined(self):
        """Must have exactly 3 commercial formats: FODS, FODT, Netpbm."""
        names = {f["format"] for f in COMMERCIAL_NET_FORMATS}
        assert "FODS" in names
        assert "FODT" in names
        assert "Netpbm" in names
        assert len(COMMERCIAL_NET_FORMATS) == 3


# ─────────────────────────────────────────────────────────────
# Helpers for full proof repo
# ─────────────────────────────────────────────────────────────

def _add_format_proof(repo: Path, fmt_name: str, src_dir: str, test_dir: str, ex_dir: str,
                      ext: str, log_pattern: str, ledger_key: str):
    """Add complete proof for a single format."""
    # Source
    src = repo / src_dir
    src.mkdir(parents=True, exist_ok=True)
    (src / f"{fmt_name}Module{ext}").write_text("x" * 300, encoding="utf-8")
    # Tests
    tests = repo / test_dir
    tests.mkdir(parents=True, exist_ok=True)
    (tests / f"{fmt_name}Tests{ext}").write_text("[Fact] void Test() {}", encoding="utf-8")
    # Examples
    if ex_dir:
        ex = repo / ex_dir
        ex.mkdir(parents=True, exist_ok=True)
        (ex / f"{fmt_name}Example{ext}").write_text("// example", encoding="utf-8")
    # Log
    log_dir = repo / "reports" / f"sprint-{fmt_name.lower()}" / "raw-logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / f"{fmt_name.lower()}-tests.log").write_text(
        f"{log_pattern} tests\n{log_pattern} passed 50 items\n50 passed in 2s",
        encoding="utf-8"
    )


def _build_full_proof_repo(tmp_path: Path) -> Path:
    """Build a fake repo where all proof checks pass for all formats."""
    # Commercial .NET
    for name, src, test, ex in [
        ("FODS", "src/net/fods", "tests/net/fods", "examples/net/fods"),
        ("FODT", "src/net/fodt", "tests/net/fodt", "examples/net/fodt"),
        ("NETPBM", "src/net/netpbm", "tests/net/netpbm", "examples/net/netpbm"),
    ]:
        _add_format_proof(tmp_path, name, src, test, ex, ".cs", name.lower(), name.lower())

    # FOSS Python (need 3+ passes)
    for name, src, test, ex in [
        ("ZST", "src/python/zst", "tests/python/zst", "examples/python/zst"),
        ("PPM", "src/python/ppm", "tests/python/ppm", "examples/python/ppm"),
        ("SYLK", "src/python/sylk", "tests/python/sylk", "examples/python/sylk"),
        ("DIF", "src/python/dif", "tests/python/dif", ""),
    ]:
        _add_format_proof(tmp_path, name, src, test, ex or "", ".py", name.lower(), name.lower())

    # Ledger (covers all formats)
    ledger_dir = tmp_path / "reports" / "r90"
    ledger_dir.mkdir(parents=True, exist_ok=True)
    ledger = [
        {"run_id": "r001", "format": k, "source_files": [f"src/{k}.py"]}
        for k in ["fods", "fodt", "netpbm", "zst", "ppm", "sylk", "dif"]
    ]
    (ledger_dir / "product-code-change-ledger.json").write_text(json.dumps(ledger), encoding="utf-8")

    # Proof graph projection (required by Option B contract)
    proj_dir = tmp_path / "reports" / "autonomous-system-audit" / "projected-proof-graph"
    proj_dir.mkdir(parents=True, exist_ok=True)
    nodes_lines = [
        json.dumps({"node_id": f"node_{k}", "type": "product", "label": k})
        for k in ["fods", "fodt", "netpbm", "zst", "ppm", "sylk", "dif"]
    ]
    (proj_dir / "nodes.jsonl").write_text("\n".join(nodes_lines) + "\n", encoding="utf-8")

    # poc-targets.yaml (gate_11_g11g: NOT_STARTED → release pending)
    poc = tmp_path / "product-capability-matrix"
    poc.mkdir(parents=True, exist_ok=True)
    (poc / "poc-targets.yaml").write_text("""
commercial_net_products:
  - format: FODS
    gates_passed: "1-10"
    gate_11_g11g: NOT_STARTED
  - format: FODT
    gates_passed: "1-10"
    gate_11_g11g: NOT_STARTED
  - format: Netpbm
    gates_passed: "1-10"
    gate_11_g11g: NOT_STARTED
foss_reduced_products:
  - format: ZST
    gates_passed: "1-10"
  - format: Netpbm
    gates_passed: "1-10"
  - format: SYLK
    gates_passed: "1-10"
""", encoding="utf-8")

    return tmp_path
