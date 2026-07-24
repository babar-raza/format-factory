"""governance_validators_package_proof.py — V226 (GAP-FORENSIC-001 heal)

V226: validate_package_install_proof_coverage
    FAIL (blocks) when the package-install-proof chain is broken anywhere:

    DRIFT     — a src/python/<fmt>/ package (has pyproject.toml) is missing from
                packaging/python/package-matrix.yaml or lacks an install_proof
                spec. This is the "next Python product" hook: onboarding a format
                without wiring its proof is a blocking failure, not a silent gap.
    MISSING   — a matrix format has no entry in the proof manifest
                (reports/package-install-proof/proof-manifest.json) or its
                verdict is not PASS.
    STALE     — the format's src/python/<fmt>/ content digest no longer matches
                the digest recorded at proof time. Proof of old source is not
                proof of current source; re-prove with
                `python tools/run_package_install_proof.py --format <fmt>`.

    Deliberately blocking on all three: WARN-only enforcement of proof artifacts
    is the exact failure mode that produced GAP-FORENSIC-001 (V138 precedent).
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

from governance_validators_contract import validator
from package_proof_common import PACKAGE_MATRIX_REL, PROOF_MANIFEST_REL, source_digest

_NAME = "validate_package_install_proof_coverage"
_REPROOF_HINT = "re-prove with: python tools/run_package_install_proof.py --format <fmt>"


def _result(result: str, summary: str, blocks: bool) -> dict:
    return {"validator": _NAME, "result": result, "summary": summary, "blocks_sprint": blocks}


@validator(rule_id="V226", domain="machinery")
def validate_package_install_proof_coverage(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V226: every Python format package must have a fresh, passing install proof."""
    repo = Path(repo_root) if repo_root else Path(__file__).resolve().parent.parent.parent

    matrix_path = repo / PACKAGE_MATRIX_REL
    if not matrix_path.exists():
        return _result("FAIL", f"V226: {PACKAGE_MATRIX_REL} missing — fleet undefined", True)
    try:
        packages = yaml.safe_load(matrix_path.read_text(encoding="utf-8"))["packages"]
    except Exception as exc:
        return _result("FAIL", f"V226: package-matrix.yaml unreadable: {exc}", True)

    matrix_ids = {p.get("format_id") for p in packages}
    no_spec = sorted(p.get("format_id") for p in packages if "install_proof" not in p)

    # DRIFT: every shipped-shaped source package must be in the matrix with a spec.
    # Compare against each entry's own module_path directory name, not format_id --
    # a package's format_id and its actual src/python/ directory name can legitimately
    # differ (e.g. csv's module lives at src/python/ff_csv/ to dodge stdlib `import csv`
    # shadowing; see GAP-FORENSIC-025). Falls back to format_id for any entry missing
    # module_path so a genuinely-undeclared package is still caught.
    matrix_dirs = {
        Path(p["module_path"]).name if p.get("module_path") else p.get("format_id")
        for p in packages
    }
    src_python = repo / "src" / "python"
    src_formats = sorted(
        d.name for d in src_python.iterdir()
        if d.is_dir() and (d / "pyproject.toml").exists()
    ) if src_python.exists() else []
    unmatrixed = sorted(set(src_formats) - matrix_dirs)
    if unmatrixed or no_spec:
        problems = []
        if unmatrixed:
            problems.append(f"src packages missing from matrix: {unmatrixed}")
        if no_spec:
            problems.append(f"matrix entries without install_proof spec: {no_spec}")
        return _result(
            "FAIL",
            "V226 DRIFT: " + "; ".join(problems) +
            " — add matrix entries with install_proof blocks (packaging/python/package-matrix.yaml)",
            True,
        )

    # MISSING: every matrix format needs a PASS entry in the proof manifest
    manifest_path = repo / PROOF_MANIFEST_REL
    if not manifest_path.exists():
        return _result(
            "FAIL",
            f"V226 MISSING: {PROOF_MANIFEST_REL} does not exist — no install proof has been "
            f"produced; run: python tools/run_package_install_proof.py",
            True,
        )
    try:
        proven = json.loads(manifest_path.read_text(encoding="utf-8")).get("formats", {})
    except Exception as exc:
        return _result("FAIL", f"V226: proof manifest unreadable: {exc}", True)

    # A known_failure waiver (install_proof.known_failure.gap_id in the matrix)
    # downgrades a recorded FAIL verdict to WARN — for defects that are tracked
    # in a gap register and cannot be fixed without a breaking product decision
    # (e.g. csv: stdlib shadows the wheel module). The proof must still RUN
    # (missing entries are never waivable) and staleness still applies.
    waivers = {
        p["format_id"]: p["install_proof"]["known_failure"]
        for p in packages
        if isinstance(p.get("install_proof", {}).get("known_failure"), dict)
        and p["install_proof"]["known_failure"].get("gap_id")
    }

    missing = sorted(f for f in matrix_ids if f not in proven)
    failing = sorted(
        f for f in matrix_ids
        if f in proven and proven[f].get("verdict") != "PASS" and f not in waivers
    )
    waived_failing = sorted(
        f for f in matrix_ids
        if f in proven and proven[f].get("verdict") != "PASS" and f in waivers
    )
    if missing or failing:
        problems = []
        if missing:
            problems.append(f"no proof entry: {missing}")
        if failing:
            problems.append(f"verdict != PASS: {failing}")
        return _result("FAIL", "V226 MISSING: " + "; ".join(problems) + f" — {_REPROOF_HINT}", True)

    # STALE: recorded digest must match current source content
    # Always use working-tree digests here — proof runner builds from working tree
    stale = sorted(
        fmt for fmt in matrix_ids
        if proven[fmt].get("source_digest") != source_digest(repo, fmt)
    )
    if stale:
        return _result(
            "FAIL",
            f"V226 STALE: source changed since proof for {stale} — proof of old source is "
            f"not proof of current source; {_REPROOF_HINT}",
            True,
        )

    if waived_failing:
        waived_desc = ", ".join(
            f"{f} (waived: {waivers[f]['gap_id']})" for f in waived_failing)
        return _result(
            "WARN",
            f"V226: {len(matrix_ids) - len(waived_failing)}/{len(matrix_ids)} packages have "
            f"fresh passing install proof; known failures under gap-register waiver: {waived_desc}",
            False,
        )
    return _result(
        "PASS",
        f"V226: all {len(matrix_ids)} Python format packages have fresh passing install proof",
        False,
    )
