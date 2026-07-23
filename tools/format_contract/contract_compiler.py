"""Format Contract compiler — deterministic compile plane of L30.

Pure function of committed stores: SAL facts + research findings + family
pack + shared library contract + fact-category policy -> canonical contract
YAML at shared/format-contracts/{format_id}.yaml. Same inputs produce
byte-identical output (verified by --verify-idempotency; drift caught by
--check and validator freshness checks).

Refuses to compile below the family's fact-category coverage threshold:
thin inputs yield an honest BLOCKED_NEEDS_AUTHORITY registry state, never a
fabricated contract (root cause RC1, mission FCL-MACHINERY-2026-07-16).

Exit codes: 0 compiled/ok · 1 error · 2 blocked (readiness) · 3 --check diff.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import contract_registry
import stores
from canonical_io import canonical_dump, canonical_write

GENERATOR_VERSION = "fcl-compiler/1.0.0"


# ---------------------------------------------------------------------------
# Pass 1 — classification
# ---------------------------------------------------------------------------

def classify(format_id: str, need_pack: bool = False) -> dict:
    """Load committed inputs. The family pack is loaded only when needed so the
    readiness gate can issue an honest BLOCKED verdict for formats whose pack
    does not exist yet (readiness depends on facts + category policy only)."""
    family_map = stores.load_family_map()
    family = family_map.get(format_id)
    if not family:
        raise stores.StoreError(
            f"format '{format_id}' has no family mapping in format-family-map.yaml"
        )
    return {
        "format_id": format_id,
        "family": family,
        "pack": stores.load_family_pack(family) if need_pack else None,
        "registry_entry": stores.load_format_registry_entry(format_id),
        "sal": stores.load_sal_facts(format_id),
        "research": stores.load_research(format_id),
        "shared": stores.load_shared_contract(),
        "categories_policy": stores.load_fact_categories(),
    }


# ---------------------------------------------------------------------------
# Pass 2 — readiness gate (category coverage, not fact count)
# ---------------------------------------------------------------------------

def _fact_text(fact: dict) -> str:
    return " ".join(
        str(fact.get(k, "")) for k in ("claim", "element_qname", "section", "description")
    ).lower()


def readiness(ctx: dict) -> dict:
    policy = ctx["categories_policy"]
    family_rules = policy["families"].get(ctx["family"])
    if not family_rules:
        raise stores.StoreError(f"no fact-category rules for family {ctx['family']}")
    facts = ctx["sal"]["facts"]
    finding_domains = {
        str(f.get("capability_domain", "")).lower()
        for f in ctx["research"].get("findings", [])
    }
    report: dict = {"format_id": ctx["format_id"], "family": ctx["family"], "categories": {}}
    overrides = family_rules.get("min_facts_overrides", {})
    score = 0.0
    for cat_name in family_rules["required_categories"]:
        cat = policy["categories"][cat_name]
        keywords = [k.lower() for k in cat["match_keywords"]]
        matched = [
            f.get("fact_id") for f in facts
            if any(k in _fact_text(f) for k in keywords)
        ]
        min_facts = int(overrides.get(cat_name, cat.get("min_facts", 1)))
        covered = len(matched) >= min_facts
        # Reviewed research findings tagged with a category also cover it.
        if not covered and cat_name.lower() in finding_domains:
            covered = True
        weight = float(family_rules["weights"].get(cat_name, 0))
        if covered:
            score += weight
        report["categories"][cat_name] = {
            "matched_fact_ids": sorted(x for x in matched if x),
            "matched_count": len(matched),
            "min_facts": min_facts,
            "covered": covered,
            "weight": weight,
        }
    threshold = float(family_rules.get("threshold", policy.get("default_threshold", 0.7)))
    report["score"] = round(score, 4)
    report["threshold"] = threshold
    report["ready"] = score >= threshold
    report["missing_categories"] = sorted(
        name for name, c in report["categories"].items() if not c["covered"]
    )
    return report


# ---------------------------------------------------------------------------
# Pass 3 — capability derivation (facts/findings x pack rules)
# ---------------------------------------------------------------------------

def _norm_fmt(format_id: str) -> str:
    return format_id.upper().replace("_", "")


def _match_facts(facts: list[dict], keywords: list[str]) -> list[dict]:
    kws = [k.lower() for k in keywords]
    return [f for f in facts if any(k in _fact_text(f) for k in kws)]


def _findings_for_domain(findings: list[dict], domain: str) -> list[dict]:
    return sorted(
        (f for f in findings if str(f.get("capability_domain", "")).upper() == domain),
        key=lambda f: str(f.get("finding_id", "")),
    )


def derive_capabilities(ctx: dict) -> list[dict]:
    fmt = _norm_fmt(ctx["format_id"])
    pack = ctx["pack"]
    facts = ctx["sal"]["facts"]
    findings = ctx["research"].get("findings", [])
    floors = pack.get("depth_floors", {})
    caps: list[dict] = []

    for dom in pack.get("domains", []):
        domain = dom["domain"]
        matched = _match_facts(facts, dom.get("fact_keywords", []))
        dom_findings = _findings_for_domain(findings, domain)

        provenance = [item["id"] for item in dom.get("baseline_behavior", [])]
        provenance += sorted(f["fact_id"] for f in matched if f.get("fact_id"))
        provenance += [f["finding_id"] for f in dom_findings if f.get("finding_id")]

        behavior = [item["text"] for item in dom.get("baseline_behavior", [])]
        for finding in dom_findings:
            req = str(finding.get("requirement", "")).strip()
            if req:
                behavior.append(req)
        # Fact-derived normative rules live in their own field: their volume is
        # driven by the specification itself, so they are exempt from the
        # anti-overfit simplicity budget while staying fully traceable.
        normative = [
            f"({fact.get('section') or fact.get('authority') or 'spec'}) "
            f"{str(fact.get('claim', '')).strip()}"
            for fact in sorted(matched, key=lambda f: str(f.get("fact_id", "")))
        ]

        level = dom.get("level", "SHOULD")
        floor = int(floors.get(dom.get("category", ""), dom.get("min_depth", 2)))
        depth = max(int(dom.get("min_depth", floor)), floor)
        for finding in dom_findings:
            hint = finding.get("depth_hint")
            if isinstance(hint, int):
                depth = max(depth, min(hint, 8))

        tests = list(dom.get("required_tests", []))
        for finding in dom_findings:
            tests += [str(t) for t in finding.get("required_tests", [])]
        gates = list(dom.get("release_gates", []))
        for finding in dom_findings:
            gates += [str(g) for g in finding.get("release_gates", [])]

        cap: dict = {
            "capability_id": f"{fmt}-{domain}-001",
            "level": level,
            "category": dom.get("category", "advanced"),
            "title": dom["title"],
            "production_meaning": dom["production_meaning"],
            "developer_use_case": dom["developer_use_case"],
            "provenance": provenance,
            "required_behavior": behavior,
            "depth_required": depth,
            "depth_rationale": (
                f"{level} {dom.get('category')} capability: family depth floor "
                f"{floor}, finding hints applied; depth scale 0-8 per L30 schema."
            ),
            "required_tests": tests,
            "release_gates": gates,
        }
        if normative:
            cap["normative_rules"] = normative
        for key_src, key_dst in (
            ("required_model_objects", "required_model_objects"),
            ("required_operations", "required_operations"),
            ("required_invariants", "required_invariants"),
            ("preservation_rules", "preservation_rules"),
            ("validation_rules", "validation_rules"),
            ("security_requirements", "security_requirements"),
            ("performance_requirements", "performance_requirements"),
            ("error_behavior", "error_behavior"),
        ):
            merged = list(dom.get(key_src, []))
            for finding in dom_findings:
                merged += [str(x) for x in finding.get(key_src, [])]
            if merged:
                cap[key_dst] = merged
        caps.append(cap)

    caps += _shared_capabilities(ctx, fmt)
    caps.sort(key=lambda c: c["capability_id"])
    return caps


def _shared_capabilities(ctx: dict, fmt: str) -> list[dict]:
    shared = ctx["shared"]["groups"]
    applicable = ctx["pack"].get("shared_groups", [])
    caps = []
    spec = [
        ("lifecycle_io", f"{fmt}-LIFECYCLE-001", "lifecycle", "MUST", 4,
         "Baseline lifecycle I/O",
         "Load/save/bytes round-trip, version exposure, strict and tolerant read modes, first-class validation, deterministic serialization.",
         "A developer integrates the library with only lifecycle APIs and never needs format-internal knowledge for I/O plumbing."),
        ("preservation", f"{fmt}-PRESERVE-001", "preserve", "MUST", 4,
         "Baseline preservation duties",
         "Unknown constructs, absent-vs-default distinctions, and loss reporting are handled so round trips never silently drop data.",
         "A developer round-trips files containing constructs the library does not model and loses nothing silently."),
        ("security_limits", f"{fmt}-SEC-001", "security", "MUST", 5,
         "Baseline security posture",
         "Input limits, no implicit external effects, traversal protection, untrusted-payload discipline, and complexity-attack guards are enforced with diagnostics.",
         "A developer processes untrusted input with safe defaults and only opts into external effects explicitly."),
    ]
    for group_name, cap_id, category, level, depth, title, meaning, use_case in spec:
        if group_name not in applicable:
            continue
        items = shared.get(group_name, {}).get("items", [])
        if not items:
            continue
        caps.append({
            "capability_id": cap_id,
            "level": level,
            "category": category,
            "title": title,
            "production_meaning": meaning,
            "developer_use_case": use_case,
            "provenance": [item["id"] for item in items],
            "required_behavior": [item["text"] for item in items],
            "depth_required": depth,
            "depth_rationale": (
                f"Portfolio baseline ({group_name}) from shared-library-contract.yaml; "
                "depth reflects enforced-with-diagnostics expectation."
            ),
            "required_tests": [
                f"Each {group_name} baseline behavior has a focused positive test and, "
                "where refusable, a negative test proving refusal with diagnostics."
            ],
            "release_gates": [
                f"All {group_name} baseline behaviors demonstrably enforced or explicitly "
                "waived with recorded rationale."
            ],
        })
    return caps


# ---------------------------------------------------------------------------
# Pass 4 — document assembly
# ---------------------------------------------------------------------------

def assemble(ctx: dict, capabilities: list[dict]) -> dict:
    fmt_id = ctx["format_id"]
    fmt = _norm_fmt(fmt_id)
    pack = ctx["pack"]
    reg = ctx["registry_entry"]
    shared_store = ctx["shared"]
    identity = pack["identity_defaults"]
    research = ctx["research"]

    display_name = reg.get("display_name") or fmt_id.upper()
    spec_body = reg.get("spec_body") or "unspecified authority"
    spec_version = reg.get("spec_version") or "unversioned"

    description = identity["description_template"].format(
        display_name=display_name, spec_body=spec_body, spec_version=spec_version
    )

    research_sources = [
        dict(record)
        for record in sorted(
            research.get("source_records", []),
            key=lambda record: str(record.get("source_id", "")),
        )
    ]
    pinned_authorities = [
        record
        for record in research_sources
        if record.get("authority_class") == "AUTHORITATIVE"
        and record.get("acquisition_status") == "ACQUIRED"
        and record.get("content_hash")
    ]
    registry_source = {
        "source_id": f"SRC-{fmt}-001",
        "title": f"{spec_body} {spec_version}".strip(),
        "organization": spec_body,
        "version": str(spec_version),
        "canonical_url": reg.get("spec_url"),
        "authority_class": "AUTHORITATIVE",
        "acquisition_status": "URL_ONLY" if reg.get("spec_url") else "NEEDS_AUTHORITY",
    }
    # An acquired, digest-bound research authority supersedes the synthetic
    # registry URL record. Keeping both would make production readiness
    # impossible because the synthetic record is necessarily URL_ONLY.
    sources = (
        [
            record
            for record in research_sources
            if record.get("authority_class") != "AUTHORITATIVE"
            or (
                record.get("acquisition_status") == "ACQUIRED"
                and record.get("content_hash")
            )
        ]
        if pinned_authorities
        else [registry_source, *research_sources]
    )
    seen_source_ids: set[str] = set()
    sources = [
        source
        for source in sources
        if not (
            source.get("source_id") in seen_source_ids
            or seen_source_ids.add(str(source.get("source_id")))
        )
    ]

    shared_groups = shared_store["groups"]
    preserve_items = {i["id"]: i["text"] for i in shared_groups["preservation"]["items"]}
    sec_items = [i["text"] for i in shared_groups["security_limits"]["items"]]
    quality_items = [i["text"] for i in shared_groups["quality_proof"]["items"]]

    test_contract = list(quality_items)
    release_gates = []
    for cap in capabilities:
        test_contract += [t for t in cap.get("required_tests", []) if t not in test_contract]
        release_gates += [g for g in cap.get("release_gates", []) if g not in release_gates]
    release_gates.append(
        "Capability manifest published and independently verified against implementation and tests."
    )

    security_defaults = pack.get("security_defaults", {})
    doc = {
        "contract_metadata": {
            "schema_version": "1.0",
            "contract_id": f"FC-{fmt}-V1",
            "format_id": fmt_id,
            "format_canonical_name": display_name,
            "extensions": list(reg.get("extensions", []) or []),
            "family": ctx["family"],
            "target_spec_version": str(spec_version),
            "source_authority_status": "AUTHORITATIVE" if reg.get("spec_url") else "NEEDS_AUTHORITY",
            "generator_version": GENERATOR_VERSION,
            "lifecycle_status": "DRAFT",
            "confidence": "medium" if research.get("findings") else "low",
            "supersedes": None,
            "input_digests": stores.input_digests(fmt_id, ctx["family"]),
        },
        "format_identity": {
            "description": description,
            "data_model_type": identity["data_model_type"],
            "primary_use_cases": list(identity["primary_use_cases"]),
            "active_content_model": dict(identity["active_content_model"]),
        },
        "authoritative_sources": sources,
        "scope_policy": {
            "production_complete_target": pack["scope_defaults"]["production_complete_target"],
            "minimum_viable_support": pack["scope_defaults"]["minimum_viable_support"],
        },
        "capabilities": capabilities,
        "preservation_contract": {
            "structural_roundtrip": [preserve_items["POL-SLC-PRESERVE-02"]],
            "lexical_roundtrip": [preserve_items["POL-SLC-PRESERVE-04"]],
            "unknown_construct_policy": preserve_items["POL-SLC-PRESERVE-01"],
            "loss_reporting_policy": preserve_items["POL-SLC-PRESERVE-03"],
        },
        "validation_contract": {
            "layers": [dict(layer) for layer in pack.get("validation_layers", [])],
            "diagnostic_schema": {"fields": list(shared_store["diagnostic_schema_fields"])},
        },
        "security_contract": {
            "attack_surfaces": list(security_defaults.get("attack_surfaces", [])),
            "safe_defaults": list(security_defaults.get("safe_defaults", [])),
            "limits": sec_items,
        },
        "test_contract": test_contract,
        "release_gates": release_gates,
        "coverage_map": [
            {"capability_id": c["capability_id"], "provenance": list(c["provenance"])}
            for c in capabilities
        ],
    }

    api = _public_api_from_findings(research)
    if api:
        doc["public_api_contract"] = api
    return doc


def _public_api_from_findings(research: dict) -> dict | None:
    merged: dict[str, list[str]] = {}
    for finding in sorted(
        research.get("findings", []), key=lambda f: str(f.get("finding_id", ""))
    ):
        for key, values in (finding.get("api_expectations") or {}).items():
            bucket = merged.setdefault(key, [])
            for value in values:
                if value not in bucket:
                    bucket.append(str(value))
    return merged or None


# ---------------------------------------------------------------------------
# Orchestration + CLI
# ---------------------------------------------------------------------------

def compile_contract(format_id: str) -> tuple[dict, dict]:
    """Returns (readiness_report, contract_doc). Raises on hard errors."""
    ctx = classify(format_id)
    report = readiness(ctx)
    if not report["ready"]:
        return report, {}
    ctx["pack"] = stores.load_family_pack(ctx["family"])
    capabilities = derive_capabilities(ctx)
    return report, assemble(ctx, capabilities)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format-id", required=True)
    parser.add_argument("--check", action="store_true",
                        help="compile to memory and diff against committed contract")
    parser.add_argument("--verify-idempotency", action="store_true",
                        help="compile twice and byte-compare")
    parser.add_argument("--readiness-only", action="store_true",
                        help="print the readiness report and exit")
    args = parser.parse_args(argv)
    fmt = args.format_id.lower()

    try:
        if args.readiness_only:
            report, doc = readiness(classify(fmt)), {}
        else:
            report, doc = compile_contract(fmt)
    except stores.StoreError as exc:
        if "missing or empty" in str(exc):
            # No SAL store at all is the deepest readiness failure — an honest
            # BLOCKED state with a seeding task, never a bare error (RC1).
            contract_registry.update_entry(
                fmt,
                state="BLOCKED_NEEDS_AUTHORITY",
                readiness_score=0.0,
                missing_categories=["no_sal_fact_store"],
            )
            print(f"[fcl-compiler] BLOCKED_NEEDS_AUTHORITY {fmt}: no SAL fact store — "
                  f"route to /research-format-contract-sources + ingest-spec-sal seeding",
                  file=sys.stderr)
            return 2
        print(f"[fcl-compiler] ERROR {exc}", file=sys.stderr)
        return 1

    if args.readiness_only or not report["ready"]:
        print(canonical_dump(report))
        if not report["ready"]:
            contract_registry.update_entry(
                fmt,
                state="BLOCKED_NEEDS_AUTHORITY",
                readiness_score=report["score"],
                readiness_threshold=report["threshold"],
                missing_categories=report["missing_categories"],
            )
            print(f"[fcl-compiler] BLOCKED_NEEDS_AUTHORITY {fmt}: "
                  f"score {report['score']} < threshold {report['threshold']}; "
                  f"missing {report['missing_categories']}", file=sys.stderr)
            return 2
        return 0

    text = canonical_dump(doc)

    if args.verify_idempotency:
        _, doc2 = compile_contract(fmt)
        if canonical_dump(doc2) != text:
            print("[fcl-compiler] IDEMPOTENCY FAIL: two compilations differ", file=sys.stderr)
            return 1
        print(f"[fcl-compiler] idempotency OK for {fmt}")

    target = stores.contract_path(fmt)
    if args.check:
        current = target.read_text(encoding="utf-8").replace("\r\n", "\n") if target.is_file() else ""
        if current != text:
            print(f"[fcl-compiler] CHECK DIFF: committed {target} != recompiled output",
                  file=sys.stderr)
            return 3
        print(f"[fcl-compiler] check OK: {target} matches recompiled output")
        return 0

    canonical_write(target, doc)
    contract_registry.update_entry(
        fmt,
        state="COMPILED",
        contract_path=str(target.relative_to(stores.REPO_ROOT)).replace("\\", "/"),
        readiness_score=report["score"],
        readiness_threshold=report["threshold"],
        capability_count=len(doc["capabilities"]),
        generator_version=GENERATOR_VERSION,
        input_digests=doc["contract_metadata"]["input_digests"],
    )
    print(f"[fcl-compiler] compiled {fmt}: {len(doc['capabilities'])} capabilities -> {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
