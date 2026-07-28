"""governance_validators_converter_compat.py — V251: converter information-model gate.

Full-repo-state validator following the V242-V246 pattern
(governance_validators_package_integrity.py): the function IGNORES the `declaration`
argument's scope and performs an unconditional scan of every `*_to_*.py` converter
module under src/python/. `repo_root` defaults to the real repo root but may be
overridden by tests pointing at a synthetic tmp_path.

V251 (TC-PA-008): validate_converter_compatibility_registered

    Every converter module must carry an explicit information-model compatibility
    classification in registry/converter-compatibility-matrix.yaml. A converter with
    no entry FAILs and blocks: the gate's purpose is to force the "does this
    conversion mean anything?" question to be answered BEFORE the code is generated,
    which is precisely the question /add-dogfood-export never asked (TC-PA-004).

    Categories (declared per source->target pair, derived from format domains):
      COMPATIBLE   — source and target share an information model (tabular->tabular,
                     document->document, raster->raster). Round-trip is meaningful.
      PROJECTION   — different models with a defensible, documented mapping and
                     known loss (document->tabular extracts text into rows;
                     raster->tabular emits the pixel grid as numbers).
      INCOMPATIBLE — no semantic relationship. Any implementation must invent
                     structure that the source does not contain (text->bitmap
                     character-code-to-pixel hashing). WARNs pending TC-PA-015
                     disposition; these are the converters that should not exist.

    SCOPE LIMIT (stated rather than hidden): V251 gates the DECLARED information-model
    relationship of a format pair. It does NOT inspect converter bodies and cannot
    tell a faithful PROJECTION from a lazy one — a fodg->pbm converter that truly
    rasterises vector geometry and one that hashes characters into pixels are
    indistinguishable to this validator. V229 checks a converter exists and its test
    passes; nothing in the portfolio checks implementation semantics. That gap is
    real and remains open (TC-PA-016).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from governance_validators_contract import validator
from skill_gate_bridge import SkillGateUnavailable, converter_compat

# Matrix loading and pair classification are DELEGATED to the shared skill-gate checker
# (tools/governance/skill_gates/converter_compat.py) so that /add-dogfood-export's
# creation-time gate and V251's sprint-time gate can never disagree about whether a pair
# is allowed. See docs/governance/skill-gate-validator-seam.md. What stays here is V251's
# own concern, which the gate has no opinion about: enumerating what is ON DISK and
# checking that every module is accounted for. The gate answers "may I create this pair?";
# V251 answers "is every pair that exists classified?".
_MATRIX_REL = "registry/converter-compatibility-matrix.yaml"
_NON_FORMAT_DIRS = frozenset({"__pycache__", "build", "dist", ".pytest_cache"})


def _repo_root(repo_root: "Path | None") -> Path:
    return Path(repo_root) if repo_root else Path(__file__).resolve().parent.parent.parent


def discover_converters(src_python: Path, repo: Path) -> list[dict[str, str]]:
    """Every *_to_*.py module under src/python/, with its parsed source->target pair."""
    out: list[dict[str, str]] = []
    for p in sorted(src_python.rglob("*_to_*.py")):
        rel_parts = p.relative_to(src_python).parts
        if any(part in _NON_FORMAT_DIRS for part in rel_parts):
            continue
        stem = p.stem
        if "_to_" not in stem:
            continue
        source, target = stem.split("_to_", 1)
        out.append({
            "path": p.relative_to(repo).as_posix(),
            "package": p.parent.name,
            "source": source,
            "target": target,
            "pair": f"{source}->{target}",
        })
    return out


@validator(rule_id="V251", domain="structural")
def validate_converter_compatibility_registered(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V251: every *_to_*.py converter needs a compatibility-matrix entry.

    Unconditional full-repo scan; ``declaration`` is ignored by design.
    FAIL when a converter module has no registry entry (blocks: an unclassified
    converter is exactly the machinery gap TC-PA-008 closes). WARN when a
    registered converter is classified INCOMPATIBLE and still awaits TC-PA-015
    disposition. Fails CLOSED when the matrix is missing or unparseable.
    """
    repo = _repo_root(repo_root)
    src_python = repo / "src" / "python"
    name = "validate_converter_compatibility_registered"

    if not src_python.is_dir():
        return {"validator": name, "result": "PASS", "blocks_sprint": False, "items": [],
                "summary": "V251: no src/python/ directory found"}

    matrix_path = repo / _MATRIX_REL
    try:
        gate = converter_compat()
    except SkillGateUnavailable as exc:
        return {"validator": name, "result": "FAIL", "blocks_sprint": True,
                "items": [{"issue": "shared skill-gate checker unavailable", "error": str(exc)}],
                "summary": (f"V251: shared checker tools/governance/skill_gates/converter_compat.py "
                            f"could not be loaded ({exc}) — converter enforcement did NOT run "
                            "(fail-closed)")}

    # The shared loader owns matrix reading + schema errors (it raises MatrixError for
    # missing/unparseable/invalid), so the two sides cannot disagree about validity.
    try:
        matrix = gate.load_matrix(matrix_path)
    except gate.MatrixError as exc:
        return {"validator": name, "result": "FAIL", "blocks_sprint": True,
                "items": [{"issue": f"matrix unusable: {exc}", "path": _MATRIX_REL}],
                "summary": f"V251: {_MATRIX_REL} missing/unparseable/invalid — {exc} (fail-closed)"}

    entries: dict[str, dict] = {k: (v or {}) for k, v in (matrix.get("converters") or {}).items()}
    converters = discover_converters(src_python, repo)

    unregistered, incompatible, bad_category = [], [], []
    # Category vocabulary comes from the shared checker — if it ever grows a category,
    # V251 accepts it automatically instead of rejecting what the skill gate allows.
    valid = {gate.CLASS_COMPATIBLE, gate.CLASS_PROJECTION, gate.CLASS_INCOMPATIBLE}
    counts: dict[str, int] = {}
    for c in converters:
        entry = entries.get(c["path"])
        if entry is None:
            unregistered.append({**c, "issue": "converter has no information-model compatibility entry"})
            continue
        category = entry.get("category")
        counts[str(category)] = counts.get(str(category), 0) + 1
        if category not in valid:
            bad_category.append({**c, "category": category,
                                 "issue": f"category must be one of {sorted(valid)}"})
        elif category == "INCOMPATIBLE" and entry.get("disposition", "PENDING") == "PENDING":
            incompatible.append({**c, "category": category,
                                 "rationale": entry.get("rationale", ""),
                                 "issue": "INCOMPATIBLE converter awaiting TC-PA-015 disposition"})

    stale = sorted(set(entries) - {c["path"] for c in converters})

    items: list[dict[str, Any]] = unregistered + bad_category
    if items:
        result, blocks = "FAIL", True
        summary = (f"V251: {len(unregistered)} unregistered converter(s), "
                   f"{len(bad_category)} with an invalid category — an unclassified converter "
                   f"is an ungoverned one")
    elif incompatible or stale:
        result, blocks = "WARN", False
        summary = (f"V251: all {len(converters)} converter(s) classified "
                   f"({', '.join(f'{k}={v}' for k, v in sorted(counts.items()))}); "
                   f"{len(incompatible)} INCOMPATIBLE awaiting TC-PA-015 disposition"
                   + (f"; {len(stale)} stale matrix entry(ies) with no module on disk" if stale else ""))
    else:
        result, blocks = "PASS", False
        summary = (f"V251: all {len(converters)} converter(s) carry an information-model "
                   f"classification ({', '.join(f'{k}={v}' for k, v in sorted(counts.items()))})")

    return {"validator": name, "result": result, "blocks_sprint": blocks,
            "items": items + incompatible + [{"path": s, "issue": "stale matrix entry"} for s in stale],
            "summary": summary,
            "metrics": {"converters": len(converters), "registered": len(converters) - len(unregistered),
                        "unregistered": len(unregistered), "by_category": counts,
                        "incompatible_pending": len(incompatible), "stale_entries": len(stale)}}
