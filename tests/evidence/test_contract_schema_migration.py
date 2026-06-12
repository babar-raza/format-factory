"""
Lane B: Contract schema migration guard tests.

Proves that all evidence contracts use required_repo_files (not required_artifacts),
and that the validator correctly reads required_repo_files.

Sprint: FORMAT-FACTORY-R34-CLEAN-CLOSURE-AUTHORITY-PIPELINE-REPAIR-SWARM-001
"""
import pathlib
import yaml
import pytest

CONTRACTS_DIR = pathlib.Path(__file__).resolve().parents[2] / "tools" / "evidence" / "contracts"


def _load_all_contracts():
    """Load all YAML contracts from the contracts directory."""
    contracts = []
    for f in sorted(CONTRACTS_DIR.glob("*.yaml")):
        with open(f) as fh:
            data = yaml.safe_load(fh)
        if data:
            contracts.append((f.name, data))
    return contracts


ALL_CONTRACTS = _load_all_contracts()


class TestNoRequiredArtifactsKey:
    """No contract may use the defunct required_artifacts key."""

    @pytest.mark.parametrize("name,contract", ALL_CONTRACTS, ids=[c[0] for c in ALL_CONTRACTS])
    def test_no_required_artifacts_key(self, name, contract):
        assert "required_artifacts" not in contract, (
            f"{name} still uses 'required_artifacts' — must be 'required_repo_files'"
        )


class TestRequiredRepoFilesNonEmpty:
    """Sprint contracts that declare required_repo_files must have at least one entry.

    Template contracts (base-run, gate-approval, etc.) may have empty lists.
    """

    CONTRACTS_WITH_REPO_FILES = [
        (n, c) for n, c in ALL_CONTRACTS
        if "required_repo_files" in c and n not in {
            "base-run.yaml", "gate-approval.yaml", "gate-execution.yaml",
            "independent-verification.yaml", "spec-workbench.yaml",
        }
    ]

    @pytest.mark.parametrize(
        "name,contract",
        CONTRACTS_WITH_REPO_FILES,
        ids=[c[0] for c in CONTRACTS_WITH_REPO_FILES],
    )
    def test_required_repo_files_nonempty(self, name, contract):
        files = contract["required_repo_files"]
        assert isinstance(files, list), f"{name}: required_repo_files must be a list"
        assert len(files) > 0, f"{name}: required_repo_files is empty"


class TestMetadataFloorCompliance:
    """Sprint contracts (r2X+) with min_metadata_count must meet the RUN_CONTRACT_METADATA_FLOOR.

    Only checks contracts from R23+ onwards (when the floor was established).
    Template contracts (gate-approval, independent-verification, etc.) are excluded.
    Emergency blocker bundles are excluded.
    """

    RUN_CONTRACT_METADATA_FLOOR = 30

    # Only primary sprint contracts (not AI-only sub-sprints or repair sprints) are checked.
    # Known exceptions with documented low floors are excluded.
    KNOWN_LOW_FLOOR_CONTRACTS = {
        "r27-ai-platform-full-cycle.yaml",           # AI-only sub-sprint
        "r32-truth-matrix-gate-quality-and-drift-recovery.yaml",  # repair sub-sprint
        "r34-r33-scope-separation-repair.yaml",       # scope repair sub-sprint
    }

    CONTRACTS_WITH_MIN_META = [
        (n, c) for n, c in ALL_CONTRACTS
        if "min_metadata_count" in c
        and not c.get("emergency_blocker_bundle", False)
        and n.startswith(("r2", "r3"))
        and n not in {
            "r27-ai-platform-full-cycle.yaml",
            "r32-truth-matrix-gate-quality-and-drift-recovery.yaml",
            "r34-r33-scope-separation-repair.yaml",
        }
    ]

    @pytest.mark.parametrize(
        "name,contract",
        CONTRACTS_WITH_MIN_META,
        ids=[c[0] for c in CONTRACTS_WITH_MIN_META],
    )
    def test_metadata_floor(self, name, contract):
        min_meta = contract["min_metadata_count"]
        assert min_meta >= self.RUN_CONTRACT_METADATA_FLOOR, (
            f"{name}: min_metadata_count={min_meta} < floor={self.RUN_CONTRACT_METADATA_FLOOR}"
        )


class TestValidatorReadsCorrectKey:
    """Verify the validator source only reads required_repo_files, not required_artifacts."""

    def test_validator_uses_required_repo_files(self):
        validator = CONTRACTS_DIR.parent / "validate_evidence_bundle.py"
        assert validator.exists(), "Validator not found"
        source = validator.read_text()
        assert 'required_repo_files' in source, "Validator must reference required_repo_files"

    def test_validator_does_not_read_required_artifacts(self):
        validator = CONTRACTS_DIR.parent / "validate_evidence_bundle.py"
        source = validator.read_text()
        # The validator should not have a line like: contract.get("required_artifacts"
        import re
        matches = re.findall(r'contract\.get\(["\']required_artifacts', source)
        assert len(matches) == 0, (
            "Validator reads 'required_artifacts' — schema migration incomplete"
        )
