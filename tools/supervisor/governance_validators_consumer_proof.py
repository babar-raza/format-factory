"""governance_validators_consumer_proof.py — V137-V138: Consumer proof integrity gates.

Added 2026-07-04 (TC-CPR-003, sparkling-waddling-narwhal plan).

V137 (TC-CPR-003a): validate_no_stale_installed_packages
    Detects format module directories in .venv/Lib/site-packages/ that coexist with
    source packages in src/python/. A module dir + matching source = stale copy situation.
    Stale copies defeat editable installs (site-packages dirs shadow PTH-based paths)
    and mean consumer proof runs against old code. This validator prevents regression
    back to the dual-identity problem that existed before 2026-07-04.
    blocks_sprint: True for PRODUCT_SOURCE items touching formats with stale dirs.

V138 (TC-CPR-003b): validate_consumer_proof_evidence_exists
    Checks that .local/evidences/consumer-proof-manifest.json exists and is populated.
    Consumer proof PASS claims require captured execution output, not just script existence.
    blocks_sprint: False (WARN-only — evidence capture is a best-effort closeout step).
"""

from __future__ import annotations
from governance_validators_contract import validator  # noqa: F401

import json
import hashlib
from pathlib import Path


# ---------------------------------------------------------------------------
# Result helper
# ---------------------------------------------------------------------------

def _result(vid: str, name: str, passed: bool, items: list, blocks: bool = False) -> dict:
    """Standard validator result shape."""
    result_label = "PASS" if passed else ("FAIL" if blocks else "WARN")
    return {
        "validator": name,
        "result": result_label,
        "blocks_sprint": (not passed) and blocks,
        "items": items,
        "summary": f"{vid}: {'OK' if passed else str(len(items)) + ' issue(s)'}",
    }


# ---------------------------------------------------------------------------
# V137: No stale installed package copies in site-packages
# ---------------------------------------------------------------------------

_FORMAT_NAMES = [
    "abw", "csv", "dif", "fodg", "fodp", "fods", "fodt", "gnumeric",
    "ndjson", "ods", "odt", "pbm", "pgm", "ppm", "qoi", "sylk",
    "toml", "tsv", "xcf", "zst",
]


def _find_venv_site_packages(repo_root: Path) -> Path | None:
    """Find the .venv/Lib/site-packages directory."""
    sp = repo_root / ".venv" / "Lib" / "site-packages"
    if sp.is_dir():
        return sp
    # Linux .venv layout
    for p in (repo_root / ".venv" / "lib").glob("python*/site-packages"):
        if p.is_dir():
            return p
    return None


@validator(rule_id="V_VALIDATE_NO_STALE_INSTALLED_PACKAGES", domain="consumer_proof")
def validate_no_stale_installed_packages(
    declaration: dict, repo_root: Path | None = None
) -> dict:
    """V137: Detect format module directories in site-packages that create stale-copy state.

    A module dir in site-packages that coexists with src/python/{fmt}/ is a stale copy.
    Stale copies shadow PTH-based editable installs, meaning consumer proof scripts run
    against old code instead of the current source.

    Checks:
    1. For each format: if site-packages/{fmt}/ exists AND src/python/{fmt}/ exists,
       report as a stale copy (regression).
    2. For each format that appears in declaration changed_files: if stale copy exists,
       that's a FAIL (sprint is adding/modifying code that consumers can't see).
    3. Also detects ghost files: files in site-packages/{fmt}/ not present in src/python/{fmt}/.
    """
    _root = repo_root or Path(".")
    sp = _find_venv_site_packages(_root)
    src_python = _root / "src" / "python"

    if sp is None:
        return _result("V137", "validate_no_stale_installed_packages",
                       passed=True, items=["SKIP: no site-packages found"])

    changed_formats: set[str] = set()
    for cf in declaration.get("changed_files", []):
        norm = str(cf).replace("\\", "/")
        if "src/python/" in norm:
            parts = norm.split("src/python/")
            if len(parts) > 1:
                fmt = parts[1].split("/")[0]
                if fmt in _FORMAT_NAMES:
                    changed_formats.add(fmt)

    issues = []
    blocking = False

    for fmt in _FORMAT_NAMES:
        sp_dir = sp / fmt
        src_dir = src_python / fmt
        if not sp_dir.is_dir() or not src_dir.is_dir():
            continue

        # Module dir coexists with source — stale copy regression
        sp_files = {f.name for f in sp_dir.glob("*.py")}
        src_files = {f.name for f in src_dir.glob("*.py")}

        ghost_files = sp_files - src_files
        stale_files = []
        for name in sp_files & src_files:
            sp_f = sp_dir / name
            src_f = src_dir / name
            try:
                sh = hashlib.md5(sp_f.read_bytes()).hexdigest()
                rh = hashlib.md5(src_f.read_bytes()).hexdigest()
                if sh != rh:
                    stale_files.append(name)
            except OSError:
                pass

        if ghost_files:
            issues.append(
                f"{fmt}: {len(ghost_files)} ghost file(s) in site-packages not in source: "
                f"{sorted(ghost_files)[:3]}"
            )
        if stale_files:
            msg = (
                f"{fmt}: {len(stale_files)} stale file(s) in site-packages differ from source "
                f"(editable install defeated): {stale_files[:3]}"
            )
            issues.append(msg)
            if fmt in changed_formats:
                blocking = True

    return _result(
        "V137",
        "validate_no_stale_installed_packages",
        passed=len(issues) == 0,
        items=issues,
        blocks=blocking,
    )


# ---------------------------------------------------------------------------
# V138: Consumer proof execution evidence must exist
# ---------------------------------------------------------------------------

@validator(rule_id="V_VALIDATE_CONSUMER_PROOF_EVIDENCE_EXISTS", domain="consumer_proof")
def validate_consumer_proof_evidence_exists(
    declaration: dict, repo_root: Path | None = None
) -> dict:
    """V138: Consumer proof evidence must be captured execution output, not just script files.

    Checks for the existence of .local/evidences/consumer-proof-manifest.json.
    If present, verifies it has entries for at least some of the 20 formats.

    blocks_sprint: False (WARN-only — evidence capture is a best-effort closeout step;
    consumer proof runner may not have been invoked yet).
    """
    _root = repo_root or Path(".")
    manifest = _root / ".local" / "evidences" / "consumer-proof-manifest.json"

    if not manifest.exists():
        return _result(
            "V138",
            "validate_consumer_proof_evidence_exists",
            passed=False,
            items=[
                "consumer-proof-manifest.json not found — run tools/consumer_proof_runner.py "
                "to capture dated consumer proof execution evidence"
            ],
            blocks=False,
        )

    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return _result(
            "V138",
            "validate_consumer_proof_evidence_exists",
            passed=False,
            items=[f"consumer-proof-manifest.json is malformed: {e}"],
            blocks=False,
        )

    entries = data if isinstance(data, dict) else {}
    passed_count = sum(1 for v in entries.values() if isinstance(v, dict) and v.get("pass"))
    total_count = len(entries)
    failed_formats = [fmt for fmt, v in entries.items() if isinstance(v, dict) and not v.get("pass")]

    issues = []
    if total_count == 0:
        issues.append("consumer-proof-manifest.json is empty — no formats verified")
    if failed_formats:
        issues.append(f"Consumer proof FAIL for formats: {failed_formats}")

    summary_note = f"{passed_count}/{total_count} formats have captured PASS evidence"
    items = issues if issues else [summary_note]

    return _result(
        "V138",
        "validate_consumer_proof_evidence_exists",
        passed=len(issues) == 0,
        items=items,
        blocks=False,
    )
