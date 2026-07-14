"""Tests for dom_maturity_promoter.py — TC-DL2-008 + TC-PCL-003-03 (behavioral proof runner)."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools" / "supervisor"))
from dom_maturity_promoter import check_promotion, promote, load_dom_proofs, run_proof, assess_dom_maturity


def _make_ledger(fmt="fods", maturity="D2", ceiling="D5"):
    entries = [{
        "product_id": f"{fmt.upper()}-PYTHON", "format": fmt, "runtime": "python",
        "dom_applicability": "FULL", "lane_a_maturity": "A1",
        "lane_b_maturity": maturity, "lane_b_ceiling": ceiling,
        "execution_mode": "AUTO", "lane_a_consecutive": 0,
        "lane_b_consecutive": 0, "lane_starvation_threshold": 3,
    }]
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8")
    yaml.dump(entries, tmp, default_flow_style=False)
    tmp.close()
    return Path(tmp.name)


class TestDomMaturityPromoter:

    def test_eligible_promotion_succeeds(self, tmp_path):
        """Eligible promotion succeeds and updates ledger (no proof files → AST path)."""
        lp = _make_ledger("fods", "D2", "D5")
        result = promote("fods", "D3", lp, repo_root=tmp_path)
        assert result["promoted"] is True
        assert result["new_level"] == "D3"
        # Verify ledger updated
        updated = yaml.safe_load(lp.read_text(encoding="utf-8"))
        assert updated[0]["lane_b_maturity"] == "D3"

    def test_ineligible_promotion_rejected(self):
        """Ineligible promotion (failed criteria) rejected."""
        lp = _make_ledger("fods", "D3", "D5")
        # D4 requires mutation API which FODS doesn't have
        result = check_promotion("fods", "D4", lp)
        assert result["eligible"] is False

    def test_idempotent_re_promotion(self, tmp_path):
        """Re-promoting an already-at-level format is a no-op."""
        lp = _make_ledger("fods", "D3", "D5")
        result = promote("fods", "D3", lp, repo_root=tmp_path)
        assert result["promoted"] is False
        assert result.get("reason") == "already_at_or_above_target"

    def test_cannot_promote_beyond_ceiling(self):
        """Cannot promote beyond ceiling."""
        lp = _make_ledger("fods", "D3", "D3")
        result = check_promotion("fods", "D4", lp)
        assert result["eligible"] is False
        assert result.get("reason") == "exceeds_ceiling"

    def test_dry_run_no_write(self, tmp_path):
        """Dry-run does not write ledger (no proof files → AST path)."""
        lp = _make_ledger("fods", "D2", "D5")
        result = promote("fods", "D3", lp, dry_run=True, repo_root=tmp_path)
        assert result["promoted"] is False
        assert result["dry_run"] is True
        # Ledger unchanged
        data = yaml.safe_load(lp.read_text(encoding="utf-8"))
        assert data[0]["lane_b_maturity"] == "D2"

    def test_missing_format_error(self):
        """Missing format returns error."""
        lp = _make_ledger("fods", "D2", "D5")
        result = check_promotion("nonexistent", "D3", lp)
        assert result["eligible"] is False
        assert "error" in result


# ── TC-PCL-003-03: Behavioral proof runner tests ──────────────────────────────

def _make_proof_dir(tmp_path: Path, fmt: str, proofs: dict) -> Path:
    proof_dir = tmp_path / ".supervisor" / "dom-proofs"
    proof_dir.mkdir(parents=True)
    (proof_dir / f"{fmt}.yaml").write_text(yaml.dump({"format": fmt, "proofs": proofs}))
    return tmp_path


def _make_ledger_in(tmp_path: Path, fmt: str = "fodt", maturity: str = "D1",
                    ceiling: str = "D5") -> Path:
    entries = [{"format": fmt, "runtime": "python", "dom_applicability": "FULL",
                "lane_b_maturity": maturity, "lane_b_ceiling": ceiling}]
    p = tmp_path / "ledger.yaml"
    p.write_text(yaml.dump(entries))
    return p


class TestBehavioralProofRunner:

    def test_no_proof_file_falls_back_to_ast(self, tmp_path):
        """No proof file → fallback=ast_scan."""
        result = assess_dom_maturity("fodt", repo_root=tmp_path)
        assert result["fallback"] == "ast_scan"
        assert result["computed_level"] is None

    def test_d1_pass_d2_fail_returns_d1(self, tmp_path):
        """D1 passes, D2 fails → computed_level=D1."""
        _make_proof_dir(tmp_path, "fodt", {
            "D1": {"test_command": "python -c \"exit(0)\""},
            "D2": {"test_command": "python -c \"exit(1)\""},
        })
        result = assess_dom_maturity("fodt", repo_root=tmp_path)
        assert result["computed_level"] == "D1"
        assert "D1" in result["passing_levels"]
        assert "D2" not in result["passing_levels"]

    def test_both_pass_returns_d2(self, tmp_path):
        """D1 and D2 both pass → computed_level=D2."""
        _make_proof_dir(tmp_path, "fodt", {
            "D1": {"test_command": "python -c \"exit(0)\""},
            "D2": {"test_command": "python -c \"exit(0)\""},
        })
        result = assess_dom_maturity("fodt", repo_root=tmp_path)
        assert result["computed_level"] == "D2"

    def test_promote_updates_ledger_when_proof_passes(self, tmp_path):
        """Behavioral proof at D2 → ledger updated for format at D1."""
        ledger = _make_ledger_in(tmp_path, "fodt", "D1", "D5")
        _make_proof_dir(tmp_path, "fodt", {
            "D1": {"test_command": "python -c \"exit(0)\""},
            "D2": {"test_command": "python -c \"exit(0)\""},
        })
        result = promote("fodt", "D2", ledger_path=ledger, repo_root=tmp_path)
        assert result["promoted"] is True
        assert result["new_level"] == "D2"
        updated = yaml.safe_load(ledger.read_text())
        assert updated[0]["lane_b_maturity"] == "D2"

    def test_no_auto_demote(self, tmp_path):
        """Format claimed D2 with proof returning D1 → ledger NOT lowered."""
        ledger = _make_ledger_in(tmp_path, "fodt", "D2", "D5")
        _make_proof_dir(tmp_path, "fodt", {
            "D1": {"test_command": "python -c \"exit(0)\""},
            "D2": {"test_command": "python -c \"exit(1)\""},
        })
        promote("fodt", "D2", ledger_path=ledger, repo_root=tmp_path)
        updated = yaml.safe_load(ledger.read_text())
        assert updated[0]["lane_b_maturity"] == "D2"
