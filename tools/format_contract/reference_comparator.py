"""Reference-oracle comparator (L30) — measurable quality comparison, not text
similarity.

Compares a generated contract against the hash-registered reference contract
(shared/format-contracts/policy/reference-oracle.yaml). The reference is a
comparison oracle ONLY: this module reads it exclusively for comparison,
verifies its SHA-256 first, and refuses on mismatch. Reference content is
never written anywhere.

Dimensions:
  domain_coverage    — reference capability domains addressed by the generated contract
  specificity_ratio  — mean requirement lines per capability vs the reference
  section_parity     — security/preservation/validation/tests/release-gate presence
Misses are emitted as machinery-repair findings (pack/policy/facts), never as
instructions to patch contract output.

Exit codes: 0 thresholds met · 1 error · 5 below thresholds (repair loop).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import stores
from canonical_io import digest_file, load_yaml

ORACLE_POLICY = stores.POLICY_DIR / "reference-oracle.yaml"
REPORTS_DIR = stores.REPO_ROOT / "reports" / "format-contract-layer"

_REF_KEYS = {"ubl": "UBL", "xliff": "XLIFF", "ipynb": "IPYNB", "mtlx": "MTLX", "nrrd": "NRRD"}


def _load_reference() -> tuple[dict, dict]:
    policy = load_yaml(ORACLE_POLICY)
    if not policy:
        raise stores.StoreError("reference-oracle.yaml missing")
    ref_path = stores.REPO_ROOT / policy["reference_path"]
    actual = digest_file(ref_path)
    if actual != policy["sha256_lf_normalized"]:
        raise stores.StoreError(
            f"reference oracle hash mismatch: expected {policy['sha256_lf_normalized']}, "
            f"got {actual} — re-register via policy revision before comparing"
        )
    return policy, load_yaml(ref_path)


def _domain_of(cap_id: str) -> str:
    parts = cap_id.split("-")
    return parts[1] if len(parts) >= 3 else cap_id


# Reference domains -> generated-domain synonyms (semantic, not lexical, coverage)
_DOMAIN_SYNONYMS = {
    "DOC": {"DOCTYPES", "MODEL"}, "CORE": {"EDIT", "MODEL"}, "AMOUNT": {"TYPES", "MODEL"},
    "CODELIST": {"CODELIST", "VALIDATE"}, "UPGRADE": {"UPGRADE", "VERSION"},
    "DIFF": {"DIFF", "QUERY"}, "ATTACH": {"ATTACH", "EXT", "PAYLOAD"},
    "SIGN": {"SIGN"}, "PROFILE": {"PROFILE", "VALIDATE"}, "REF": {"REF", "VALIDATE"},
    "CALC": {"CALC"}, "QUERY": {"QUERY", "MODEL"}, "EXT": {"EXT"},
    "TEXT": {"TEXT", "EDIT"}, "SEG": {"SEG"}, "STATE": {"STATE"}, "NOTE": {"NOTE"},
    "MODULE": {"MODULE"}, "ROLE": {"MERGE", "MODULE"}, "MERGE": {"MERGE"}, "QA": {"QA"},
    "ID": {"ID", "MODEL"}, "OUTPUT": {"OUTPUT"}, "META": {"META"}, "CLEAN": {"CLEAN", "EDIT"},
    "TRUST": {"TRUST"}, "SANITIZE": {"SANITIZE"}, "EXEC": {"EXEC"}, "EXPORT": {"EXPORT"},
    "INCLUDE": {"INCLUDE"}, "TYPE": {"TYPES"}, "NAME": {"NAME", "MODEL"},
    "GRAPH": {"GRAPH"}, "DEF": {"DEF"}, "LIB": {"LIB"}, "MAT": {"MAT"}, "LOOK": {"LOOK"},
    "VARIANT": {"VARIANT"}, "COLOR": {"COLOR"}, "UNIT": {"UNIT"},
    "TRANSFORM": {"TRANSFORM", "GRAPH"}, "SHADER": {"SHADER"}, "BAKE": {"SHADER"},
    "HEADER": {"HEADER", "PARSE"}, "DATA": {"PAYLOAD", "DATA"}, "ENC": {"ENC", "ENCODING"},
    "ENDIAN": {"SHAPE", "ENDIAN", "TYPES"}, "SHAPE": {"SHAPE"}, "SKIP": {"PAYLOAD", "HEADER"},
    "AXIS": {"SPACE", "AXIS", "SHAPE"}, "SPACE": {"SPACE"}, "ARRAY": {"ARRAY"},
    "LAZY": {"LAZY", "PERFORMANCE"}, "STATS": {"STATS", "ARRAY"}, "CONVERT": {"CONVERT", "TRANSFORM"},
    "SEC": {"SEC"}, "PARSE": {"PARSE"}, "MODEL": {"MODEL"}, "VALIDATE": {"VALIDATE"},
    "WRITE": {"WRITE"}, "INLINE": {"INLINE"},
}

_REQ_KEYS = ("required_behavior", "normative_rules", "preservation_rules",
             "validation_rules", "security_requirements", "performance_requirements",
             "error_behavior")


def compare(format_id: str) -> dict:
    policy, ref = _load_reference()
    ref_key = _REF_KEYS.get(format_id)
    if not ref_key:
        raise stores.StoreError(f"{format_id} is not covered by the reference oracle")
    ref_fmt = ref["formats"][ref_key]
    gen = load_yaml(stores.contract_path(format_id))
    if not gen:
        raise stores.StoreError(f"no generated contract for {format_id}")

    ref_caps = ref_fmt.get("required_capabilities", [])
    ref_domains = sorted({_domain_of(c["id"]) for c in ref_caps})
    gen_domains = {_domain_of(c["capability_id"]) for c in gen.get("capabilities", [])}

    covered, missed = [], []
    for dom in ref_domains:
        accepted = _DOMAIN_SYNONYMS.get(dom, {dom})
        (covered if accepted & gen_domains else missed).append(dom)
    domain_coverage = round(len(covered) / max(1, len(ref_domains)), 3)

    ref_lines = sum(len(c.get("requirements", [])) for c in ref_caps)
    ref_mean = ref_lines / max(1, len(ref_caps))
    gen_caps = gen.get("capabilities", [])
    gen_lines = sum(sum(len(c.get(k, [])) for k in _REQ_KEYS) for c in gen_caps)
    gen_mean = gen_lines / max(1, len(gen_caps))
    specificity_ratio = round(gen_mean / max(0.001, ref_mean), 3)

    section_parity = {
        "security": bool((gen.get("security_contract") or {}).get("attack_surfaces")),
        "preservation": bool(gen.get("preservation_contract")),
        "validation": bool((gen.get("validation_contract") or {}).get("layers")),
        "tests": len(gen.get("test_contract", [])) >= 3,
        "release_gates": len(gen.get("release_gates", [])) >= 3,
    }

    thresholds = policy["comparator_thresholds"]
    passes = (
        domain_coverage >= thresholds["domain_coverage_min"]
        and specificity_ratio >= thresholds["specificity_ratio_min"]
        and all(section_parity[s] for s in thresholds["section_parity_required"])
    )
    repair_findings = [
        {
            "kind": "machinery_repair",
            "target": "family pack / research findings / SAL facts",
            "missed_reference_domain": dom,
            "instruction": (
                f"Reference defines {ref_key}-{dom}-* capabilities not addressed by any "
                f"generated domain; add the domain to the family pack (generic) or seed "
                f"facts/findings covering it. NEVER patch the generated contract directly."
            ),
        }
        for dom in missed
    ]
    return {
        "format_id": format_id,
        "reference_sha256": policy["sha256_lf_normalized"],
        "reference_capability_count": len(ref_caps),
        "generated_capability_count": len(gen_caps),
        "domain_coverage": domain_coverage,
        "reference_domains": ref_domains,
        "covered_domains": covered,
        "missed_domains": missed,
        "specificity_ratio": specificity_ratio,
        "reference_mean_requirements_per_capability": round(ref_mean, 2),
        "generated_mean_requirement_lines_per_capability": round(gen_mean, 2),
        "section_parity": section_parity,
        "thresholds": thresholds,
        "verdict": "MEETS_REFERENCE_BAR" if passes else "BELOW_REFERENCE_BAR",
        "machinery_repair_findings": repair_findings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format-id", required=True)
    args = parser.parse_args(argv)
    fmt = args.format_id.lower()
    try:
        report = compare(fmt)
    except stores.StoreError as exc:
        print(f"[fcl-compare] ERROR {exc}", file=sys.stderr)
        return 1
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORTS_DIR / f"{fmt}-reference-comparison.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"[fcl-compare] {fmt}: {report['verdict']} (domains {report['domain_coverage']}, "
          f"specificity {report['specificity_ratio']}) -> {out}")
    return 0 if report["verdict"] == "MEETS_REFERENCE_BAR" else 5


if __name__ == "__main__":
    sys.exit(main())
