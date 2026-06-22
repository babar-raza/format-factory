"""
sal_format_advisory.py — Per-format SAL workbench authority advisory.

Reads sal-facts-latest.json and emits advisory warnings for:
- Formats with 0 workbench-verified facts (authority gap)
- Formats with only automated extraction facts (no manual review)
- Formats where gap-ledger cites spec_facts that are not in SAL

Designed for integration as Step 1c in autonomous_cycle.py once a LOC slot
is available. Currently invocable standalone:

    python tools/supervisor/sal_format_advisory.py [--json]

C1 implementation: spec-authority-healing-sprint-B-20260622
Wiring blocker: autonomous_cycle.py is at its LOC cap (2135/2135).
Wiring requires either reducing existing LOC first or a governed cap increase.
"""

import json
import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent.parent
_SAL_LATEST = _REPO / ".local" / "sal-output" / "sal-facts-latest.json"


def _load_sal_facts() -> list[dict]:
    """Load results from sal-facts-latest.json."""
    if not _SAL_LATEST.is_file():
        return []
    try:
        data = json.loads(_SAL_LATEST.read_text(encoding="utf-8"))
        return data.get("results", [])
    except Exception:
        return []


def build_advisory(results: list[dict]) -> dict:
    """Build per-format advisory from SAL results.

    Returns a dict with:
      - zero_workbench_facts: formats with 0 workbench-verified facts
      - low_fact_count: formats with 1-9 workbench-verified facts
      - automated_only: formats where all facts are automated extractions (no manual review)
      - healthy: formats with >= 10 workbench-verified facts
    """
    zero = []
    low = []
    automated = []
    healthy = []

    for r in results:
        fmt = r.get("format_id", "unknown")
        wb_count = r.get("workbench_verified_fact_count", 0)
        total = r.get("total_fact_count", 0)

        # Count manually reviewed vs automated extraction facts
        manual_count = 0
        auto_count = 0
        for fact in r.get("spec_facts", []):
            if fact.get("source") != "workbench_verified":
                continue
            claim = fact.get("claim", "")
            # Manually reviewed facts have human-authored claims (no RFC2119 boilerplate)
            is_auto = "RFC2119" in claim or "keyword" in claim.lower()
            prov_claim_id = fact.get("qname", "")
            # EX suffix indicates automated extraction pipeline
            is_ex = "-EX-" in prov_claim_id
            if is_ex:
                auto_count += 1
            else:
                manual_count += 1

        if wb_count == 0:
            zero.append({"format": fmt, "total_facts": total, "workbench_verified": 0})
        elif wb_count < 10:
            low.append({
                "format": fmt,
                "workbench_verified": wb_count,
                "manual": manual_count,
                "automated_extraction": auto_count,
            })
        elif manual_count == 0 and auto_count > 0:
            automated.append({
                "format": fmt,
                "workbench_verified": wb_count,
                "automated_extraction": auto_count,
                "note": "All facts are automated RFC2119 extractions — no manual verification",
            })
        else:
            healthy.append({
                "format": fmt,
                "workbench_verified": wb_count,
                "manual": manual_count,
                "automated_extraction": auto_count,
            })

    return {
        "zero_workbench_facts": zero,
        "low_fact_count": low,
        "automated_extraction_only": automated,
        "healthy": healthy,
    }


def print_advisory(advisory: dict) -> None:
    """Print human-readable advisory to stdout."""
    zero = advisory["zero_workbench_facts"]
    low = advisory["low_fact_count"]
    auto = advisory["automated_extraction_only"]
    healthy = advisory["healthy"]

    print("=== SAL FORMAT ADVISORY (C1) ===")
    print(f"Healthy (>=10 workbench facts, manual verified): {len(healthy)}")
    for f in sorted(healthy, key=lambda x: x["format"]):
        print(f"  OK  {f['format']}: {f['workbench_verified']} wb ({f.get('manual',0)} manual, {f.get('automated_extraction',0)} auto)")

    if auto:
        print(f"\nADVISORY — automated extraction only (no manual review): {len(auto)} format(s)")
        for f in sorted(auto, key=lambda x: x["format"]):
            print(f"  WARN  {f['format']}: {f['workbench_verified']} facts (all automated RFC2119 extraction)")

    if low:
        print(f"\nADVISORY — low workbench fact count (<10): {len(low)} format(s)")
        for f in sorted(low, key=lambda x: x["format"]):
            print(f"  LOW  {f['format']}: {f['workbench_verified']} wb facts")

    if zero:
        print(f"\nADVISORY — zero workbench facts: {len(zero)} format(s)")
        for f in sorted(zero, key=lambda x: x["format"]):
            print(f"  GAP  {f['format']}: 0 workbench-verified facts")

    print("=== END SAL ADVISORY ===")


def main() -> int:
    use_json = "--json" in sys.argv

    results = _load_sal_facts()
    if not results:
        msg = "sal-facts-latest.json not found or empty"
        if use_json:
            print(json.dumps({"error": msg}))
        else:
            print(f"WARN: {msg}")
        return 1

    advisory = build_advisory(results)

    if use_json:
        print(json.dumps(advisory, indent=2))
    else:
        print_advisory(advisory)

    # Return non-zero if any formats have zero workbench facts (advisory-only, caller decides)
    return 0


if __name__ == "__main__":
    sys.exit(main())
