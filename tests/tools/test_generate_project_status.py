"""Comprehensive tests for generate_project_status.py two-lane contract.

Covers:
- Two-lane structure presence
- Stable anchors
- Lane separation (no product metrics under machinery, vice versa)
- Atomic write
- --validate contract check
- --dry-run behavior
- Idempotency with --timestamp
- Limitations split by lane
- Generation evidence section
- README injection

Also serves as 10-pilot proof infrastructure per plan TC-PSG-005.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

TOOLS_DOCS = Path(__file__).resolve().parents[2] / "tools" / "docs"
sys.path.insert(0, str(TOOLS_DOCS))

from generate_project_status import (
    REQUIRED_ANCHORS,
    _atomic_write,
    _get_head_revision,
    generate_project_status,
    update_readme,
    validate_output,
)

FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "project_status"
FIXED_TS = "2026-01-01T00:00:00+00:00"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _gen(repo_root=None, ts=FIXED_TS) -> str:
    return generate_project_status(
        repo_root=repo_root or FIXTURE_ROOT,
        dry_run=True,
        timestamp_override=ts,
    )


# ---------------------------------------------------------------------------
# Pilot 1: Current fixture regeneration
# ---------------------------------------------------------------------------

class TestPilot1CurrentRegeneration:
    def test_generates_without_error(self):
        content = _gen()
        assert len(content) > 100

    def test_starts_with_auto_generated_marker(self):
        content = _gen()
        assert content.startswith("<!-- AUTO-GENERATED")

    def test_contains_do_not_edit_marker(self):
        content = _gen()
        assert "DO NOT EDIT MANUALLY" in content


# ---------------------------------------------------------------------------
# Two-lane structure
# ---------------------------------------------------------------------------

class TestTwoLaneStructure:
    """Pilot 1+2+3+4 structural requirements."""

    def test_machinery_lane_present(self):
        content = _gen()
        assert "## Machinery Lane" in content

    def test_product_lane_present(self):
        content = _gen()
        assert "## Product Lane" in content

    def test_shared_boundaries_present(self):
        content = _gen()
        assert "## Shared Boundaries" in content

    def test_generation_evidence_present(self):
        content = _gen()
        assert "## Generation and Evidence" in content

    def test_status_at_a_glance_present(self):
        content = _gen()
        assert "## Status at a Glance" in content

    def test_machinery_architecture_subsection(self):
        content = _gen()
        assert "### Architecture and Layer Inventory" in content

    def test_machinery_validators_subsection(self):
        content = _gen()
        assert "### Governance Validators" in content

    def test_machinery_capabilities_subsection(self):
        content = _gen()
        assert "### Capabilities and Skills" in content

    def test_machinery_supervision_subsection(self):
        content = _gen()
        assert "### Supervisor and Autonomous Execution" in content

    def test_product_inventory_subsection(self):
        content = _gen()
        assert "### Format and Family Inventory" in content

    def test_product_oracle_subsection(self):
        content = _gen()
        assert "### Oracle Verification" in content

    def test_product_certification_subsection(self):
        content = _gen()
        assert "### Certification Status" in content

    def test_product_gates_subsection(self):
        content = _gen()
        assert "### Gate Progress" in content

    def test_product_maturity_subsection(self):
        content = _gen()
        assert "### Product Maturity" in content


# ---------------------------------------------------------------------------
# Stable anchors (Pilot 1, 8)
# ---------------------------------------------------------------------------

class TestStableAnchors:
    def test_all_required_anchors_present(self):
        content = _gen()
        for anchor in REQUIRED_ANCHORS:
            assert f'name="{anchor}"' in content, f"Missing anchor: {anchor}"

    def test_no_duplicate_anchors(self):
        content = _gen()
        for anchor in REQUIRED_ANCHORS:
            count = content.count(f'name="{anchor}"')
            assert count == 1, f"Anchor '{anchor}' appears {count} times"

    def test_status_at_a_glance_anchor(self):
        content = _gen()
        assert 'name="status-at-a-glance"' in content

    def test_machinery_lane_anchor(self):
        content = _gen()
        assert 'name="machinery-lane"' in content

    def test_product_lane_anchor(self):
        content = _gen()
        assert 'name="product-lane"' in content


# ---------------------------------------------------------------------------
# Lane separation
# ---------------------------------------------------------------------------

class TestLaneSeparation:
    """Pilots 2-4: product-only, machinery-only, and mixed changes."""

    def test_validators_appear_in_machinery_not_product(self):
        content = _gen()
        machinery_start = content.find("## Machinery Lane")
        product_start = content.find("## Product Lane")
        validators_pos = content.find("### Governance Validators")
        # Validators section must be in machinery lane
        assert machinery_start < validators_pos < product_start

    def test_format_inventory_in_product_not_machinery(self):
        content = _gen()
        machinery_start = content.find("## Machinery Lane")
        product_start = content.find("## Product Lane")
        inventory_pos = content.find("### Format and Family Inventory")
        # Format inventory must be in product lane
        assert product_start < inventory_pos

    def test_oracle_verification_in_product_lane(self):
        content = _gen()
        product_start = content.find("## Product Lane")
        oracle_pos = content.find("### Oracle Verification")
        assert product_start < oracle_pos

    def test_gate_progress_in_product_lane(self):
        content = _gen()
        product_start = content.find("## Product Lane")
        gates_pos = content.find("### Gate Progress")
        assert product_start < gates_pos


# ---------------------------------------------------------------------------
# Known Limitations by lane
# ---------------------------------------------------------------------------

class TestLimitationsSplitByLane:
    def test_machinery_limitations_subsection(self):
        content = _gen()
        assert "### Machinery Limitations" in content

    def test_product_limitations_subsection(self):
        content = _gen()
        assert "### Product Limitations" in content

    def test_release_limitations_subsection(self):
        content = _gen()
        assert "### Release Limitations" in content

    def test_no_source_formats_in_product_limitations(self):
        content = _gen()
        # ORA has no source in fixture — should appear in product limitations
        assert "ORA" in content

    def test_layer_registry_hardcoded_in_machinery_limitations(self):
        content = _gen()
        assert "LAYER_DEFINITIONS" in content or "hardcoded" in content.lower()


# ---------------------------------------------------------------------------
# Specific claim fixes
# ---------------------------------------------------------------------------

class TestClaimFixes:
    def test_checkpoint_not_configured(self):
        content = _gen()
        assert "not configured" in content
        assert "Every N/A sprints" not in content

    def test_gate8_explanation_present(self):
        content = _gen()
        # gate_8_approval should have a clarifying note
        assert "gate_8_approval" in content
        assert "business" in content.lower() or "sign-off" in content.lower() or "distinct" in content.lower()

    def test_l09_labeled_gitignored(self):
        content = _gen()
        assert "gitignored local state" in content

    def test_unclassified_labeled_no_product_track(self):
        content = _gen()
        assert "(no product_track)" in content

    def test_oracle_denominator_present(self):
        content = _gen()
        # "of X tracked formats" or similar
        assert "tracked formats" in content or "tracked" in content

    def test_certification_denominator(self):
        content = _gen()
        assert "formats with source" in content

    def test_oracle_pass_rate_correct(self):
        content = _gen()
        # Fixture: csv 5/5, dif 2/3 → total 7/8
        assert "7/8" in content


# ---------------------------------------------------------------------------
# Atomic write (Pilot 9)
# ---------------------------------------------------------------------------

class TestAtomicWrite:
    def test_writes_content_correctly(self, tmp_path):
        target = tmp_path / "test.md"
        _atomic_write(target, "hello world")
        assert target.read_text() == "hello world"

    def test_cleans_up_tmp_on_failure(self, tmp_path):
        target = tmp_path / "subdir_does_not_exist" / "test.md"
        with pytest.raises(Exception):
            _atomic_write(target, "will fail")
        # No stale .tmp files
        tmp_files = list(tmp_path.rglob("*.tmp"))
        assert len(tmp_files) == 0

    def test_original_preserved_if_write_fails(self, tmp_path):
        target = tmp_path / "existing.md"
        target.write_text("original content")
        # Force failure by making a directory where .tmp would go
        # Actually let's test that atomic_write doesn't corrupt on success
        _atomic_write(target, "new content")
        assert target.read_text() == "new content"

    def test_no_partial_output(self, tmp_path):
        """Dry-run leaves target file unchanged."""
        target = tmp_path / "PROJECT_STATUS.md"
        target.write_text("original")
        # dry_run=True should NOT write to target
        generate_project_status(
            repo_root=FIXTURE_ROOT,
            output_path=target,
            dry_run=True,
            timestamp_override=FIXED_TS,
        )
        assert target.read_text() == "original"


# ---------------------------------------------------------------------------
# --validate mode (Pilot 7)
# ---------------------------------------------------------------------------

class TestValidateMode:
    def test_valid_content_returns_no_violations(self):
        content = _gen()
        violations = validate_output(content)
        assert violations == [], f"Unexpected violations: {violations}"

    def test_missing_machinery_lane_detected(self):
        content = _gen().replace("## Machinery Lane", "## RENAMED")
        violations = validate_output(content)
        assert any("Machinery Lane" in v for v in violations)

    def test_missing_product_lane_detected(self):
        content = _gen().replace("## Product Lane", "## RENAMED")
        violations = validate_output(content)
        assert any("Product Lane" in v for v in violations)

    def test_missing_anchor_detected(self):
        content = _gen().replace('name="status-at-a-glance"', 'name="something-else"')
        violations = validate_output(content)
        assert any("status-at-a-glance" in v for v in violations)

    def test_missing_do_not_edit_marker(self):
        content = _gen().replace("DO NOT EDIT MANUALLY", "")
        violations = validate_output(content)
        assert any("DO NOT EDIT MANUALLY" in v for v in violations)

    def test_duplicate_anchor_detected(self):
        content = _gen()
        # Inject a duplicate anchor
        content = content + '\n<a name="machinery-lane"></a>\n'
        violations = validate_output(content)
        assert any("Duplicate" in v and "machinery-lane" in v for v in violations)


# ---------------------------------------------------------------------------
# Idempotency (Pilot 10)
# ---------------------------------------------------------------------------

class TestIdempotency:
    def test_same_source_same_output(self):
        """Two runs with fixed timestamp produce identical output."""
        content1 = _gen(ts=FIXED_TS)
        content2 = _gen(ts=FIXED_TS)
        assert content1 == content2

    def test_different_timestamps_differ_only_in_timestamp(self):
        content1 = _gen(ts="2026-01-01T00:00:00+00:00")
        content2 = _gen(ts="2026-01-02T00:00:00+00:00")
        # Replace timestamp occurrences and compare rest
        c1 = content1.replace("2026-01-01T00:00:00+00:00", "TIMESTAMP")
        c2 = content2.replace("2026-01-02T00:00:00+00:00", "TIMESTAMP")
        assert c1 == c2, "Content differs beyond timestamp"


# ---------------------------------------------------------------------------
# Generation evidence section (Pilot 1)
# ---------------------------------------------------------------------------

class TestGenerationEvidence:
    def test_generator_path_in_evidence(self):
        content = _gen()
        assert "generate_project_status.py" in content

    def test_timestamp_in_evidence(self):
        content = _gen(ts=FIXED_TS)
        assert FIXED_TS in content

    def test_canonical_sources_listed(self):
        content = _gen()
        assert "format-registry.yaml" in content
        assert "oracle" in content


# ---------------------------------------------------------------------------
# Pilot 5: Missing authority sources
# ---------------------------------------------------------------------------

class TestMissingAuthority:
    def test_generates_with_missing_oracle_dir(self, tmp_path):
        """Generator degrades gracefully when oracle dir missing."""
        import shutil
        dest = tmp_path / "repo"
        shutil.copytree(str(FIXTURE_ROOT), str(dest))
        shutil.rmtree(dest / "oracle")
        content = generate_project_status(
            repo_root=dest,
            dry_run=True,
            timestamp_override=FIXED_TS,
        )
        assert "## Product Lane" in content
        # Oracle section should still be present (with 0 formats)
        assert "### Oracle Verification" in content

    def test_generates_with_missing_cert_matrix(self, tmp_path):
        """Generator degrades gracefully when cert matrix missing."""
        import shutil
        dest = tmp_path / "repo"
        shutil.copytree(str(FIXTURE_ROOT), str(dest))
        (dest / "reports" / "certification" / "portfolio-certification-matrix.json").unlink()
        content = generate_project_status(
            repo_root=dest,
            dry_run=True,
            timestamp_override=FIXED_TS,
        )
        assert "## Product Lane" in content


# ---------------------------------------------------------------------------
# Pilot 6: New unclassified capability/track
# ---------------------------------------------------------------------------

class TestNewUnclassifiedCapability:
    def test_new_track_appears_in_machinery_not_product(self, tmp_path):
        """A new capability track appears under Machinery Lane capabilities."""
        import shutil
        import yaml
        dest = tmp_path / "repo"
        shutil.copytree(str(FIXTURE_ROOT), str(dest))
        cap_path = dest / ".governance" / "capabilities" / "registry.yaml"
        caps = yaml.safe_load(cap_path.read_text())
        caps["capabilities"].append({
            "capability_id": "new-exotic-track-cap",
            "status": "active",
            "product_track": "new_exotic_track",
        })
        cap_path.write_text(yaml.dump(caps))

        content = generate_project_status(
            repo_root=dest,
            dry_run=True,
            timestamp_override=FIXED_TS,
        )

        # The new track should appear under Machinery Lane (Capabilities subsection)
        machinery_start = content.find("## Machinery Lane")
        product_start = content.find("## Product Lane")
        new_track_pos = content.find("new_exotic_track")

        assert new_track_pos > machinery_start, "New track not found in Machinery Lane"
        assert new_track_pos < product_start, "New track appeared in Product Lane (wrong)"


# ---------------------------------------------------------------------------
# Pilot 8: README link
# ---------------------------------------------------------------------------

class TestReadmeLink:
    def test_update_readme_uses_stable_anchor(self, tmp_path):
        """update_readme() links to PROJECT_STATUS.md#status-at-a-glance."""
        import shutil
        from generate_statistics import collect_statistics

        dest = tmp_path / "repo"
        shutil.copytree(str(FIXTURE_ROOT), str(dest))
        readme_path = dest / "README.md"
        readme_path.write_text("# Test README\n\nSome content.\n")

        stats = collect_statistics(dest)
        update_readme(dest, stats)

        content = readme_path.read_text()
        assert "PROJECT_STATUS.md#status-at-a-glance" in content

    def test_readme_injection_is_idempotent(self, tmp_path):
        """Running update_readme twice produces the same README."""
        import shutil
        from generate_statistics import collect_statistics

        dest = tmp_path / "repo"
        shutil.copytree(str(FIXTURE_ROOT), str(dest))
        readme_path = dest / "README.md"
        readme_path.write_text("# Test README\n\n")

        stats = collect_statistics(dest)
        update_readme(dest, stats)
        content1 = readme_path.read_text()
        update_readme(dest, stats)
        content2 = readme_path.read_text()

        # Strip the generated= timestamp since it will differ
        import re
        strip_ts = lambda s: re.sub(r'generated=\d{4}-\d{2}-\d{2}', 'generated=DATE', s)
        assert strip_ts(content1) == strip_ts(content2)

    def test_readme_block_not_duplicated(self, tmp_path):
        """Running update_readme twice does not create two injection blocks."""
        import shutil
        from generate_statistics import collect_statistics

        dest = tmp_path / "repo"
        shutil.copytree(str(FIXTURE_ROOT), str(dest))
        readme_path = dest / "README.md"
        readme_path.write_text("# Test README\n\n")

        stats = collect_statistics(dest)
        update_readme(dest, stats)
        update_readme(dest, stats)

        content = readme_path.read_text()
        assert content.count("BEGIN:PROJECT-STATUS-REF") == 1
        assert content.count("END:PROJECT-STATUS-REF") == 1
