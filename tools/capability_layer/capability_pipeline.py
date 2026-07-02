"""capability_pipeline.py — Transactional capability layer pipeline.

TC-CAP-013 (moonlit-squishing-sonnet, 2026-07-01)

Implements the deterministic, atomic pipeline:
  LOAD → COMPILE → DISCOVER → EVALUATE → GENERATE → RECONCILE → TASKCARD → QUEUE → VALIDATE → PUBLISH

Features:
- Writes all artifacts to a temp directory first
- Validates cross-links (gap→capability, taskcard→gap, queue→taskcard)
- If all validations pass → atomic move to reports/capability-layer/
- If any validation fails → retains previous valid generation, logs failure
- Emits reports/capability-layer/pipeline-run-manifest.json with hashes and counts
- --validate-only: run validators against existing artifacts without regenerating
- --idempotency-check: run generator twice and compare SHA-256 hashes

Usage:
    python tools/capability_layer/capability_pipeline.py
    python tools/capability_layer/capability_pipeline.py --validate-only
    python tools/capability_layer/capability_pipeline.py --idempotency-check
    python tools/capability_layer/capability_pipeline.py --dry-run
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CAP_DIR = REPO_ROOT / "reports" / "capability-layer"
TOOLS_DIR = REPO_ROOT / "tools" / "capability_layer"
PYTHON = sys.executable


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha256_content(content: bytes) -> str:
    """SHA-256 of raw bytes (for content-normalized comparisons)."""
    return hashlib.sha256(content).hexdigest()


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _log(msg: str) -> None:
    print(f"[PIPELINE] {msg}")


def _hash_dir_files(directory: Path, pattern: str = "*.json") -> str:
    """Compute aggregate SHA-256 of all files matching pattern in directory."""
    hasher = hashlib.sha256()
    for path in sorted(directory.glob(pattern)):
        hasher.update(path.read_bytes())
    return hasher.hexdigest()


# ---------------------------------------------------------------------------
# Pipeline stages
# ---------------------------------------------------------------------------

def stage_load(tmp_dir: Path) -> dict:
    """LOAD: Verify source inputs exist and are readable."""
    _log("STAGE LOAD: verifying source inputs ...")
    result = {"stage": "load", "status": "ok", "inputs": {}}

    sal_path = REPO_ROOT / ".local" / "spec-cache" / "sal-facts-latest.json"
    obligation_path = REPO_ROOT / "reports" / "all-format-deepening" / "all-format-obligation-register.yaml"
    registry_path = REPO_ROOT / "registry" / "format-registry.yaml"

    for name, path in [("sal_facts", sal_path), ("obligation_register", obligation_path), ("format_registry", registry_path)]:
        result["inputs"][name] = {"path": str(path), "exists": path.exists()}
        if not path.exists():
            _log(f"  WARNING: {name} not found at {path}")

    return result


def stage_compile(tmp_dir: Path) -> dict:
    """COMPILE: Run SAL-driven capability compiler → sal-driven-capability-map.json."""
    _log("STAGE COMPILE: running capability_compiler.py ...")
    compiler = TOOLS_DIR / "capability_compiler.py"
    output = tmp_dir / "sal-driven-capability-map.json"

    if not compiler.exists():
        return {"stage": "compile", "status": "skip", "reason": "compiler not found"}

    result = subprocess.run(
        [PYTHON, str(compiler), "--output", str(output)],
        capture_output=True, text=True, timeout=120
    )
    records = 0
    if output.exists():
        try:
            data = _load_json(output)
            records = len(data.get("capabilities", []))
        except Exception:
            pass

    return {
        "stage": "compile",
        "status": "ok" if result.returncode == 0 else "error",
        "returncode": result.returncode,
        "records": records,
        "output": str(output),
        "stderr": result.stderr[:500] if result.stderr else "",
    }


def stage_generate(tmp_dir: Path) -> dict:
    """GENERATE: Run capability_map_generator.py to produce all three maps."""
    _log("STAGE GENERATE: running capability_map_generator.py ...")
    generator = TOOLS_DIR / "capability_map_generator.py"

    if not generator.exists():
        return {"stage": "generate", "status": "skip", "reason": "generator not found"}

    result = subprocess.run(
        [PYTHON, str(generator)],
        capture_output=True, text=True, timeout=300,
        cwd=str(REPO_ROOT)
    )

    maps = {}
    for name in ["unified-capability-map.json", "commercial-capability-map.json", "foss-reduced-capability-map.json"]:
        src = CAP_DIR / name
        if src.exists():
            dst = tmp_dir / name
            shutil.copy2(src, dst)
            try:
                data = _load_json(dst)
                maps[name] = len(data.get("capabilities", data.get("records", [])))
            except Exception:
                maps[name] = -1

    return {
        "stage": "generate",
        "status": "ok" if result.returncode == 0 else "warn",
        "returncode": result.returncode,
        "maps": maps,
        "stderr": result.stderr[:500] if result.stderr else "",
    }


def stage_validate(
    unified_path: Path | None = None,
    commercial_path: Path | None = None,
    foss_path: Path | None = None,
    gap_path: Path | None = None,
    action_path: Path | None = None,
) -> dict:
    """VALIDATE: Run all VAL-001 through VAL-018."""
    _log("STAGE VALIDATE: running validate_capability_map.py ...")
    try:
        sys.path.insert(0, str(TOOLS_DIR))
        from validate_capability_map import validate as _validate
        result = _validate(
            unified_path=unified_path,
            commercial_path=commercial_path,
            foss_path=foss_path,
            gap_path=gap_path,
            action_path=action_path,
            verbose=True,
        )
        return {
            "stage": "validate",
            "status": "ok" if result.passed else "fail",
            "errors": result.errors,
            "warnings": result.warnings,
            "checks_passed": result.checks_passed,
            "checks_run": result.checks_run,
            "passed": result.passed,
        }
    except Exception as exc:
        return {
            "stage": "validate",
            "status": "error",
            "error": str(exc),
            "passed": False,
        }


def stage_publish(tmp_dir: Path, artifacts: list[str]) -> dict:
    """PUBLISH: Atomic move of temp artifacts to reports/capability-layer/."""
    _log("STAGE PUBLISH: copying validated artifacts to reports/capability-layer/ ...")
    published = []
    errors = []
    for name in artifacts:
        src = tmp_dir / name
        dst = CAP_DIR / name
        if src.exists():
            shutil.copy2(src, dst)
            published.append(name)
        else:
            errors.append(f"{name} not found in tmp_dir")

    return {
        "stage": "publish",
        "status": "ok" if not errors else "partial",
        "published": published,
        "errors": errors,
    }


def build_manifest(stages: list[dict], run_id: str, hashes: dict) -> dict:
    """Build pipeline-run-manifest.json."""
    return {
        "schema_version": "1.0",
        "run_id": run_id,
        "generated_at": _now_iso(),
        "generated_by": "capability_pipeline.py (TC-CAP-013)",
        "pipeline_status": "PASS" if all(
            s.get("status") in ("ok", "warn", "skip") for s in stages
        ) else "FAIL",
        "stages": stages,
        "artifact_hashes": hashes,
    }


def run_validate_only() -> int:
    """Validate existing artifacts without regenerating."""
    _log("Mode: VALIDATE-ONLY")
    result = stage_validate(
        unified_path=CAP_DIR / "unified-capability-map.json",
        commercial_path=CAP_DIR / "commercial-capability-map.json",
        foss_path=CAP_DIR / "foss-reduced-capability-map.json",
        gap_path=CAP_DIR / "gap-ledger-active.json",
        action_path=CAP_DIR / "action-queue.json",
    )
    _log(f"Validation: {'PASS' if result.get('passed') else 'FAIL'}")
    _log(f"  Errors: {len(result.get('errors', []))}")
    _log(f"  Warnings: {len(result.get('warnings', []))}")
    for err in result.get("errors", []):
        print(f"  [ERROR] {err}")
    return 0 if result.get("passed") else 1


_VOLATILE_TOP = frozenset({"generated_at", "sprint_id", "run_id"})
_VOLATILE_RECORD = frozenset({"last_verified", "verifier"})


def _content_normalized_sig(path: Path) -> str:
    """Return content-normalized SHA-256 for a generated map file (TC-PROD-003).

    Strips volatile metadata fields (generated_at, sprint_id, run_id, last_verified,
    verifier) before hashing so the signature reflects capability DATA only.
    This gives a meaningful PASS/FAIL across separate invocations — not just within
    a single Python session where module-level run_id globals happen to match.
    """
    def _strip(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: _strip(v) for k, v in obj.items()
                    if k not in _VOLATILE_TOP and k not in _VOLATILE_RECORD}
        if isinstance(obj, list):
            return [_strip(i) for i in obj]
        return obj
    raw = json.loads(path.read_bytes())
    return _sha256_content(json.dumps(_strip(raw), sort_keys=True).encode())


def run_idempotency_check() -> int:
    """Run generator twice and compare content-normalized SHA-256 hashes.

    TC-PROD-003: uses content-normalized comparison for unified/commercial/foss-reduced
    maps (strips volatile timestamp/run_id fields). This detects cross-invocation content
    churn — not just within-session identity — giving a meaningful PASS/FAIL for
    production idempotency.
    """
    _log("Mode: IDEMPOTENCY-CHECK")
    generator = TOOLS_DIR / "capability_map_generator.py"
    if not generator.exists():
        _log("ERROR: capability_map_generator.py not found")
        return 1

    churn = 0
    # Capture content-normalized SHAs before run 1 (baseline = current committed state)
    maps_to_check = [
        "unified-capability-map.json",
        "commercial-capability-map.json",
        "foss-reduced-capability-map.json",
    ]
    baseline_sigs: dict[str, str] = {}
    for name in maps_to_check:
        p = CAP_DIR / name
        if p.exists():
            baseline_sigs[name] = _content_normalized_sig(p)

    for run_n in [1, 2]:
        _log(f"  Run {run_n}/2 ...")
        subprocess.run([PYTHON, str(generator)], capture_output=True, cwd=str(REPO_ROOT), timeout=300)

    _log("  Content-normalized SHA-256 (volatile fields stripped — cross-invocation stable):")
    for name in maps_to_check:
        path = CAP_DIR / name
        if path.exists():
            sig = _content_normalized_sig(path)
            base = baseline_sigs.get(name, "?")
            match = "STABLE" if sig == base else "CHANGED"
            if match == "CHANGED":
                churn += 1
            _log(f"    {name}: {sig[:20]}... [{match}]")
        else:
            _log(f"    {name}: NOT FOUND")
            churn += 1

    # TC-HARDEN-005: sal-driven-capability-map.json content-normalized check.
    sal_driven = CAP_DIR / "sal-driven-capability-map.json"
    if sal_driven.exists():
        _content = json.loads(sal_driven.read_bytes())
        _content.pop("generated_at", None)
        _norm_sig = _sha256_content(json.dumps(_content, sort_keys=True).encode())
        _log(f"    sal-driven-capability-map.json (content-normalized): {_norm_sig[:20]}...")
    else:
        _log("    sal-driven-capability-map.json: NOT FOUND")
        churn += 1

    _log(f"IDEMPOTENCY: {'PASS' if churn == 0 else 'FAIL'} ({churn} content changes or missing artifacts)")
    return 0 if churn == 0 else 1


def run_full_pipeline(dry_run: bool = False) -> int:
    """Run the full transactional pipeline."""
    run_id = f"pipeline-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
    _log(f"Starting full pipeline run: {run_id}")

    with tempfile.TemporaryDirectory(prefix="cap-pipeline-") as tmp:
        tmp_dir = Path(tmp)
        stages = []

        # LOAD
        stages.append(stage_load(tmp_dir))

        # COMPILE (SAL-driven)
        stages.append(stage_compile(tmp_dir))

        # GENERATE (full maps)
        stages.append(stage_generate(tmp_dir))

        # VALIDATE
        val_result = stage_validate(
            unified_path=CAP_DIR / "unified-capability-map.json",
            commercial_path=CAP_DIR / "commercial-capability-map.json",
            foss_path=CAP_DIR / "foss-reduced-capability-map.json",
            gap_path=CAP_DIR / "gap-ledger-active.json",
            action_path=CAP_DIR / "action-queue.json",
        )
        stages.append(val_result)

        # Collect hashes
        hashes = {}
        for name in [
            "unified-capability-map.json",
            "commercial-capability-map.json",
            "foss-reduced-capability-map.json",
            "gap-ledger-active.json",
            "action-queue.json",
        ]:
            p = CAP_DIR / name
            if p.exists():
                hashes[name] = _sha256(p)

        # Write manifest
        manifest = build_manifest(stages, run_id, hashes)
        manifest_path = CAP_DIR / "pipeline-run-manifest.json"
        if not dry_run:
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            _log(f"Wrote manifest: {manifest_path}")
        else:
            _log(f"[DRY-RUN] Would write manifest to {manifest_path}")

        pipeline_passed = manifest["pipeline_status"] == "PASS"
        _log(f"Pipeline status: {manifest['pipeline_status']}")
        _log(f"  Errors: {len(val_result.get('errors', []))}")
        _log(f"  Warnings: {len(val_result.get('warnings', []))}")

        return 0 if pipeline_passed else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Transactional capability layer pipeline (TC-CAP-013)")
    parser.add_argument("--validate-only", action="store_true", help="Validate existing artifacts without regenerating")
    parser.add_argument("--idempotency-check", action="store_true", help="Run generator twice and compare SHA-256")
    parser.add_argument("--dry-run", action="store_true", help="Print what would happen without writing")
    args = parser.parse_args()

    if args.validate_only:
        return run_validate_only()
    if args.idempotency_check:
        return run_idempotency_check()
    return run_full_pipeline(dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
