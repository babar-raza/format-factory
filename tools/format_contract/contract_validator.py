"""Format Contract validator — blocking checks for canonical contracts (L30).

Checks (each maps to a governance validator in V232-V241):
  schema            — JSON Schema validity                     (V232)
  provenance        — every provenance ID resolves             (V233)
  depth             — depth present + >= family floor          (V234)
  shallow_language  — no unexpanded generic phrases            (V235)
  duplicate_ids     — capability IDs unique + well-formed      (V236)
  test_gate         — MUST capabilities carry tests + gates    (V237)
  freshness         — input_digests match current stores       (V238)
  family_adequacy   — all pack domains present, budget kept    (family review)

Exit codes: 0 all pass · 1 any FAIL.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import stores
from canonical_io import load_yaml

SCHEMA_PATH = stores.REPO_ROOT / "schemas" / "format-contracts" / "format-contract.schema.json"

_REQ_LINE_KEYS = (
    "required_behavior", "preservation_rules", "validation_rules",
    "security_requirements", "performance_requirements", "error_behavior",
)


def _result(check: str, ok: bool, items: list) -> dict:
    return {"check": check, "result": "PASS" if ok else "FAIL", "items": items}


def check_schema(doc: dict) -> dict:
    import jsonschema
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    errors = [
        {"path": "/".join(str(p) for p in e.absolute_path), "message": e.message[:200]}
        for e in validator.iter_errors(doc)
    ]
    return _result("schema", not errors, errors[:25])


def check_provenance(doc: dict) -> dict:
    fmt = doc["contract_metadata"]["format_id"]
    bad = []
    for cap in doc.get("capabilities", []):
        for pid in cap.get("provenance", []):
            if not stores.resolve_provenance_id(pid, fmt):
                bad.append({"capability_id": cap["capability_id"], "unresolved": pid})
    return _result("provenance", not bad, bad)


def check_depth(doc: dict) -> dict:
    family = doc["contract_metadata"]["family"]
    try:
        floors = stores.load_family_pack(family).get("depth_floors", {})
    except stores.StoreError:
        floors = {}
    bad = []
    for cap in doc.get("capabilities", []):
        depth = cap.get("depth_required")
        if depth is None or not cap.get("depth_rationale"):
            bad.append({"capability_id": cap["capability_id"], "issue": "missing depth or rationale"})
            continue
        floor = floors.get(cap.get("category"))
        if floor is not None and cap.get("level") == "MUST" and depth < int(floor):
            bad.append({
                "capability_id": cap["capability_id"],
                "issue": f"depth {depth} below family floor {floor} for MUST {cap.get('category')}",
            })
    return _result("depth", not bad, bad)


def check_shallow_language(doc: dict) -> dict:
    policy = stores.load_quality_policy()
    phrases = [p.lower() for p in policy["shallow_phrases"]]
    min_len = int(policy.get("min_requirement_line_length", 15))
    bad = []
    for cap in doc.get("capabilities", []):
        for key in _REQ_LINE_KEYS:
            for line in cap.get(key, []):
                line_l = str(line).strip().lower()
                if len(line_l) < min_len:
                    bad.append({"capability_id": cap["capability_id"], "field": key,
                                "issue": f"line shorter than {min_len} chars", "line": line})
                    continue
                for phrase in phrases:
                    # Blocked when the line IS the phrase or barely expands it.
                    if line_l == phrase or (phrase in line_l and len(line_l) < len(phrase) + 20):
                        bad.append({"capability_id": cap["capability_id"], "field": key,
                                    "issue": f"unexpanded shallow phrase '{phrase}'", "line": line})
    return _result("shallow_language", not bad, bad)


def check_duplicate_ids(doc: dict) -> dict:
    pattern = re.compile(r"^[A-Z0-9]+-[A-Z]+-[0-9]{3}$")
    seen: set[str] = set()
    bad = []
    for cap in doc.get("capabilities", []):
        cid = cap.get("capability_id", "")
        if not pattern.match(cid):
            bad.append({"capability_id": cid, "issue": "malformed id"})
        if cid in seen:
            bad.append({"capability_id": cid, "issue": "duplicate id"})
        seen.add(cid)
    return _result("duplicate_ids", not bad, bad)


def check_test_gate(doc: dict) -> dict:
    bad = []
    for cap in doc.get("capabilities", []):
        if cap.get("level") != "MUST":
            continue
        if not cap.get("required_tests"):
            bad.append({"capability_id": cap["capability_id"], "issue": "MUST capability without tests"})
        if not cap.get("release_gates"):
            bad.append({"capability_id": cap["capability_id"], "issue": "MUST capability without release gates"})
    return _result("test_gate", not bad, bad)


def check_freshness(doc: dict) -> dict:
    meta = doc["contract_metadata"]
    current = stores.input_digests(meta["format_id"], meta["family"])
    recorded = meta.get("input_digests", {})
    stale = [
        {"digest": key, "recorded": recorded.get(key), "current": value}
        for key, value in current.items()
        if recorded.get(key) != value
    ]
    return _result("freshness", not stale, stale)


def check_family_adequacy(doc: dict) -> dict:
    family = doc["contract_metadata"]["family"]
    fmt_prefix = doc["capabilities"][0]["capability_id"].split("-")[0] if doc.get("capabilities") else ""
    bad = []
    try:
        pack = stores.load_family_pack(family)
    except stores.StoreError as exc:
        return _result("family_adequacy", False, [{"issue": str(exc)}])
    have = {c["capability_id"] for c in doc.get("capabilities", [])}
    for dom in pack.get("domains", []):
        expected = f"{fmt_prefix}-{dom['domain']}-001"
        if expected not in have:
            bad.append({"issue": f"family domain {dom['domain']} missing", "expected": expected})
    budget = pack.get("simplicity_budget") or stores.load_quality_policy()["simplicity_budgets"]["default"]
    if len(doc.get("capabilities", [])) > int(budget["max_capabilities"]):
        bad.append({"issue": f"capability count {len(doc['capabilities'])} exceeds "
                             f"simplicity budget {budget['max_capabilities']}"})
    max_lines = int(budget["max_requirement_lines_per_capability"])
    for cap in doc.get("capabilities", []):
        lines = sum(len(cap.get(k, [])) for k in _REQ_LINE_KEYS)
        if lines > max_lines:
            bad.append({"capability_id": cap["capability_id"],
                        "issue": f"{lines} requirement lines exceed budget {max_lines}"})
    return _result("family_adequacy", not bad, bad)


ALL_CHECKS = (
    check_schema, check_provenance, check_depth, check_shallow_language,
    check_duplicate_ids, check_test_gate, check_freshness, check_family_adequacy,
)


def validate_contract(doc: dict, skip: set[str] | None = None) -> dict:
    skip = skip or set()
    results = [fn(doc) for fn in ALL_CHECKS if fn.__name__.removeprefix("check_") not in skip]
    verdict = "PASS" if all(r["result"] == "PASS" for r in results) else "FAIL"
    return {"verdict": verdict, "checks": results}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format-id")
    parser.add_argument("--contract-path")
    parser.add_argument("--skip", default="", help="comma-separated check names to skip")
    args = parser.parse_args(argv)
    if not args.format_id and not args.contract_path:
        parser.error("--format-id or --contract-path required")
    path = Path(args.contract_path) if args.contract_path else stores.contract_path(args.format_id.lower())
    doc = load_yaml(path)
    if not doc:
        print(f"[fcl-validator] ERROR contract not found or empty: {path}", file=sys.stderr)
        return 1
    report = validate_contract(doc, {s for s in args.skip.split(",") if s})
    print(json.dumps(report, indent=2))
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
