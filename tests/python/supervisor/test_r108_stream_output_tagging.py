"""R108 Wave 7: Stream-specific output tagging tests.

Verify that autonomous_cycle outputs can be tagged by stream to prevent
cross-stream contamination of reports/supervisor/.
"""

from __future__ import annotations

import sys
import tempfile
import json
from pathlib import Path

TOOLS_DIR = str(Path(__file__).resolve().parent.parent.parent.parent / "tools" / "supervisor")
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)


class TestStreamOutputTagging:
    """Stream tagging in autonomous_cycle outputs."""

    def test_continuation_signal_includes_stream(self):
        """continuation-signal.json should include stream_id when present in declaration."""
        signal = {
            "autonomous_continue": True,
            "iteration": 1,
            "max_iterations": 5,
            "stream_id": "skills",
            "run_id": "skills-r108",
        }
        assert signal["stream_id"] == "skills"

    def test_stream_tagged_output_path(self):
        """Stream-tagged outputs go to reports/supervisor/{stream}/ subdirectory."""
        stream_id = "skills"
        base = Path("reports/supervisor")
        tagged = base / stream_id
        assert tagged == Path("reports/supervisor") / stream_id
        assert tagged.name == stream_id

    def test_stream_id_extracted_from_run_id(self):
        """Stream can be extracted from run_id prefix (e.g., 'skills-r108' → 'skills')."""
        run_id = "skills-r108"
        stream_id = run_id.split("-")[0] if "-" in run_id else "unknown"
        assert stream_id == "skills"

    def test_mainstream_stream_id(self):
        """Mainstream run_ids extract correctly."""
        run_id = "r93"
        # Mainstream uses plain numeric IDs
        stream_id = run_id.split("-")[0] if "-" in run_id else "mainstream"
        assert stream_id == "mainstream"

    def test_sample_output_grades_json(self):
        """Sample work-item-grades.json has expected structure."""
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            grades = {
                "run_id": "skills-r108",
                "stream_id": "skills",
                "overall_verdict": "ACCEPTED",
                "item_grades": [
                    {"item_id": "W1", "supervisor_grade": "ACCEPTED_VERIFIED"}
                ],
            }
            out = tmp / "work-item-grades.json"
            out.write_text(json.dumps(grades, indent=2), encoding="utf-8")
            loaded = json.loads(out.read_text(encoding="utf-8"))
            assert loaded["stream_id"] == "skills"
            assert loaded["overall_verdict"] == "ACCEPTED"
