"""TC-GOV-007: Validate registry/governance-binding.yaml against actual file hashes."""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

REPO_ROOT = Path(__file__).resolve().parents[2]
BINDING_PATH = REPO_ROOT / "registry" / "governance-binding.yaml"

REQUIRED_KEYS = {"binding_id", "bound_at", "canonical_plan_location", "state_store", "governance_files"}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_yaml(path: Path) -> dict:
    if yaml is not None:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    # Minimal fallback: parse key: value lines only (no nested support needed for top-level check)
    raise RuntimeError("PyYAML not available — install it or use the full venv")


def main() -> int:
    errors: list[str] = []

    if not BINDING_PATH.exists():
        print(f"FAIL: {BINDING_PATH} does not exist")
        return 1

    try:
        binding = _load_yaml(BINDING_PATH)
    except Exception as e:
        print(f"FAIL: Could not parse governance-binding.yaml: {e}")
        return 1

    missing_keys = REQUIRED_KEYS - set(binding.keys())
    for k in sorted(missing_keys):
        errors.append(f"MISSING_KEY: {k}")

    gov_files = binding.get("governance_files", [])
    if not isinstance(gov_files, list) or len(gov_files) == 0:
        errors.append("EMPTY_OR_INVALID: governance_files")
    else:
        for entry in gov_files:
            p = REPO_ROOT / entry.get("path", "")
            expected_hash = entry.get("sha256", "")
            if not p.exists():
                errors.append(f"MISSING_FILE: {entry.get('path')}")
                continue
            actual_hash = _sha256(p)
            if actual_hash != expected_hash:
                errors.append(
                    f"HASH_MISMATCH: {entry.get('path')}\n"
                    f"    expected: {expected_hash}\n"
                    f"    actual:   {actual_hash}"
                )
            else:
                print(f"  [PASS] {entry.get('path')}")

    if errors:
        print("\nGovernance binding validation FAILED:")
        for e in errors:
            print(f"  ERROR: {e}")
        return 1

    print(f"\nGovernance binding validation: PASS ({len(gov_files)} file(s) verified)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
