"""proof_capability_taskcard_wiring.py — TC-EXT-009-05 focused proof (<80 lines).

Proves a capability_compiler-compiled taskcard (shape written by
capability_queue_consumer.py to .local/capability-consumer/taskcards/*.json)
actually surfaces as a real candidate from autonomous_task_generator.py's
generate_task_candidates() — not just an annotation on a pre-existing goal.
Uses a synthetic taskcard in an isolated temp dir; touches no real repo files.

Usage: python tools/supervisor/proof_capability_taskcard_wiring.py
Exit: 0 PASS, 1 FAIL
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import autonomous_task_generator as atg  # noqa: E402

_FN = "fodp_proof_synthetic_capability_feature"
_TC = {
    "taskcard_id": "TC-PROOF-CAP-COMPILER-0001",
    "generated_by": "capability_compiler",
    "format_id": "FODP",
    "function_name": _FN,
    "expected_module": "src/python/fodp/fodp_codec.py",
    "expected_test_file": "tests/python/fodp/test_rXXX_fodp_proof_synthetic.py",
    "governance_requirements": {"spec_qnames": ["proof:synthetic"]},
    "source_gap_id": "GAP-PROOF-CAP-COMPILER-0001",
    "gap_ledger_ref": "GAP-PROOF-CAP-COMPILER-0001",
    "gap_priority": "P0",
    "status": "READY_TO_EXECUTE",
    "advisory_only": False,
}

def main() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        tc_dir = tmp / "taskcards"
        tc_dir.mkdir(parents=True, exist_ok=True)
        (tc_dir / f"{_TC['taskcard_id']}.json").write_text(json.dumps(_TC), encoding="utf-8")

        loaded = atg._load_compiled_taskcards(taskcards_dir=tc_dir)
        if not any(g.get("function_name") == _FN for g in loaded):
            print("FAIL: _load_compiled_taskcards() missed the synthetic taskcard")
            return 1
        print(f"PASS (1/2): _load_compiled_taskcards() returned {len(loaded)} goal(s)")

        original = atg._COMPILED_TASKCARDS_DIR
        atg._COMPILED_TASKCARDS_DIR = tc_dir
        out = tmp / "product-task-candidates-proof.json"
        try:
            candidates = atg.generate_task_candidates(output_path=out, max_candidates=200)
        finally:
            atg._COMPILED_TASKCARDS_DIR = original

        match = [c for c in candidates if c.get("function_name") == _FN]
        if not match:
            print("FAIL: synthetic taskcard absent from generate_task_candidates() output")
            return 1
        item = match[0]
        assert item.get("compiled_taskcard_id") == _TC["taskcard_id"]
        assert item.get("gap_ledger_ref") == _TC["gap_ledger_ref"]
        on_disk = json.loads(out.read_text(encoding="utf-8"))
        assert on_disk.get("compiled_taskcards_merged", 0) >= 1

        print(
            f"PASS (2/2): synthetic candidate '{_FN}' surfaced "
            f"(compiled_taskcard_id={item.get('compiled_taskcard_id')}, "
            f"gap_ledger_ref={item.get('gap_ledger_ref')}, "
            f"compiled_taskcards_merged={on_disk.get('compiled_taskcards_merged')})"
        )
        return 0


if __name__ == "__main__":
    sys.exit(main())
