"""governance_validators_ext7.py — V225: SAL Store Reconciliation (GAP-FORENSIC-008)

V225: validate_sal_store_reconciliation
    Guards the committed SAL fact stores (shared/sal-facts/*.yaml) against the
    drift classes that produced GAP-FORENSIC-008:

    1. Store integrity — unique, well-formed fact_ids per store.
    2. Alias completeness — every store fact's legacy FACT-* id resolves in
       shared/sal-fact-id-aliases.json to its fact_id.
    3. Combined-DB drift — if .local/spec-cache/sal-facts-latest.json exists,
       every store fact must be present in it with an identical claim
       (remediation: python tools/spec/merge_sal_facts.py).
    4. Count reconciliation — sal_facts_count in
       registry/python-qname-architecture.json must equal the live store count.
    5. QName resolution — every spec_fact_ref in shared/qname-registry/{fmt}.yaml
       must resolve to a store fact_id (or via alias).
    6. Completeness gate (B2) — live store count / raw_spec_units (from
       reports/spec-to-code-forensic-audit/raw-spec-unit-register.yaml) must be
       >= 0.8 for ACCEPTED_VERIFIED formats. The numerator is always computed
       live from the store — never from a snapshot — so stale registers cannot
       mask under-seeding.
    7. Code bindings — facts carrying code_bindings entries are checked against
       product source via ast: the named module-level constant must equal the
       expected value (int or bytes). Proves spec-claim/constant agreement on
       every governance run; branch semantics remain the oracle's job.

    Severity: violations are FAIL except completeness shortfalls already
    tracked by an OPEN gap in forensic-gap-register.yaml (scope match at
    boundary B2), which report as WARN — known, tracked debt stays visible
    without alarm-fatigue; NEW regressions fail loudly. blocks_sprint stays
    False for the initial rollout.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

try:
    import yaml
    _HAS_YAML = True
except ImportError:  # pragma: no cover
    _HAS_YAML = False

from governance_validators_contract import validator

_COMPLETENESS_THRESHOLD = 0.8


def _load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _resolve_binding_value(source_path: Path, symbol: str):
    """Resolve a module-level constant via ast. Supports int, str, and bytes
    constants, plus bytes built from a list of int constants (bytes([...]))."""
    tree = ast.parse(source_path.read_text(encoding="utf-8", errors="replace"))
    for node in ast.iter_child_nodes(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == symbol:
                value = node.value
                if isinstance(value, ast.Constant) and isinstance(value.value, (int, str, bytes)):
                    return value.value
                if (
                    isinstance(value, ast.Call)
                    and isinstance(value.func, ast.Name)
                    and value.func.id == "bytes"
                    and len(value.args) == 1
                    and isinstance(value.args[0], ast.List)
                    and all(isinstance(e, ast.Constant) and isinstance(e.value, int)
                            for e in value.args[0].elts)
                ):
                    return bytes(e.value for e in value.args[0].elts)
                return None  # unsupported expression shape
    return None  # symbol not found


def _binding_matches(actual, expected: str) -> bool:
    if isinstance(actual, bool):  # bool is an int subclass; reject explicitly
        return False
    if isinstance(actual, int):
        try:
            return actual == int(expected, 0)
        except ValueError:
            return False
    if isinstance(actual, str):
        return actual == expected
    if isinstance(actual, bytes):
        try:
            return actual == bytes.fromhex(expected)
        except ValueError:
            return False
    return False


def _open_b2_gap_formats(root: Path) -> set[str]:
    """Formats covered by an OPEN B2 (spec->fact) gap in the forensic register."""
    register = root / "reports" / "spec-to-code-forensic-audit" / "forensic-gap-register.yaml"
    tracked: set[str] = set()
    if not register.exists():
        return tracked
    try:
        doc = _load_yaml(register) or {}
    except Exception:
        return tracked
    gaps = doc.get("gaps", doc if isinstance(doc, list) else [])
    if isinstance(gaps, dict):
        gaps = gaps.get("gaps", [])
    for gap in gaps or []:
        if not isinstance(gap, dict):
            continue
        if str(gap.get("status", "")).upper() != "OPEN":
            continue
        if "B2" not in str(gap.get("pipeline_boundary", "")):
            continue
        for fmt in gap.get("scope", []) or []:
            tracked.add(str(fmt).lower())
    return tracked


def _find_arch_entry(node, fmt: str):
    if isinstance(node, dict):
        candidate = node.get(fmt)
        if isinstance(candidate, dict) and "sal_facts_count" in candidate:
            return candidate
        for value in node.values():
            found = _find_arch_entry(value, fmt)
            if found is not None:
                return found
    return None


@validator(
    rule_id="V225",
    domain="governance",
    description="Committed SAL fact stores reconcile with aliases, combined DB, "
                "architecture counts, qname refs, completeness gate, and code bindings",
)
def validate_sal_store_reconciliation(
    declaration: dict,
    repo_root: "Path | None" = None,
) -> dict:
    root = Path(repo_root) if repo_root else Path(".")
    store_dir = root / "shared" / "sal-facts"

    if not _HAS_YAML or not store_dir.is_dir():
        return {
            "validator": "validate_sal_store_reconciliation",
            "result": "PASS",
            "blocks_sprint": False,
            "violations": [],
            "summary": "V225: no committed SAL stores (or yaml unavailable) — nothing to check",
        }

    failures: list[str] = []
    warns: list[str] = []

    aliases: dict[str, str] = {}
    aliases_loaded = False
    aliases_path = root / "shared" / "sal-fact-id-aliases.json"
    if aliases_path.exists():
        try:
            aliases = json.loads(aliases_path.read_text(encoding="utf-8")).get("aliases", {})
            aliases_loaded = True
        except Exception:
            failures.append("sal-fact-id-aliases.json unreadable")

    combined_facts_by_format: dict[str, dict[str, dict]] = {}
    combined_path = root / ".local" / "spec-cache" / "sal-facts-latest.json"
    combined_available = combined_path.exists()
    if combined_available:
        try:
            combined = json.loads(combined_path.read_text(encoding="utf-8"))
            for entry in combined.get("results", []):
                combined_facts_by_format[entry.get("format_id", "")] = {
                    f.get("fact_id"): f for f in entry.get("spec_facts", []) if f.get("fact_id")
                }
        except Exception:
            failures.append("sal-facts-latest.json unreadable")
            combined_available = False

    arch = None
    arch_path = root / "registry" / "python-qname-architecture.json"
    if arch_path.exists():
        try:
            arch = json.loads(arch_path.read_text(encoding="utf-8"))
        except Exception:
            failures.append("python-qname-architecture.json unreadable")

    spec_units_by_format: dict[str, int] = {}
    register_path = root / "reports" / "spec-to-code-forensic-audit" / "raw-spec-unit-register.yaml"
    if register_path.exists():
        try:
            register = _load_yaml(register_path) or {}
            for entry in register.get("per_format", []):
                units = entry.get("raw_spec_units")
                if isinstance(units, int) and units > 0:
                    spec_units_by_format[str(entry.get("format_id", "")).lower()] = units
        except Exception:
            warns.append("raw-spec-unit-register.yaml unreadable — completeness gate skipped")

    tracked_b2_gaps = _open_b2_gap_formats(root)
    stores_checked = 0
    bindings_checked = 0

    for store_path in sorted(store_dir.glob("*.yaml")):
        fmt = store_path.stem.lower()
        try:
            store = _load_yaml(store_path) or {}
        except Exception as exc:
            failures.append(f"{fmt}: store unreadable ({exc})")
            continue
        facts = store.get("facts", [])
        stores_checked += 1

        # 1. Store integrity
        seen_ids: set[str] = set()
        for fact in facts:
            fid = fact.get("fact_id", "")
            if not fid or not fid.startswith("SAL-"):
                failures.append(f"{fmt}: fact missing well-formed fact_id: {str(fact.get('claim',''))[:60]}")
                continue
            if fid in seen_ids:
                failures.append(f"{fmt}: duplicate fact_id {fid}")
            seen_ids.add(fid)

            # 2. Alias completeness
            legacy = fact.get("qname")
            if legacy and aliases_loaded and aliases.get(legacy) != fid:
                failures.append(f"{fmt}: alias missing/mismatched for {legacy} (expected {fid})")

            # 3. Combined-DB drift
            if combined_available:
                db_fact = combined_facts_by_format.get(fmt, {}).get(fid)
                if db_fact is None:
                    failures.append(
                        f"{fmt}: {fid} absent from combined DB — run tools/spec/merge_sal_facts.py"
                    )
                elif db_fact.get("claim") != fact.get("claim"):
                    failures.append(f"{fmt}: {fid} claim diverges between store and combined DB")

            # 7. Code bindings
            for binding in fact.get("code_bindings", []) or []:
                bindings_checked += 1
                b_file = root / binding.get("file", "")
                symbol = binding.get("symbol", "")
                expected = str(binding.get("expected", ""))
                if not b_file.exists():
                    failures.append(f"{fmt}: {fid} binding file missing: {binding.get('file')}")
                    continue
                actual = _resolve_binding_value(b_file, symbol)
                if actual is None:
                    failures.append(f"{fmt}: {fid} binding symbol {symbol} not found/unsupported in {binding.get('file')}")
                elif not _binding_matches(actual, expected):
                    failures.append(
                        f"{fmt}: {fid} binding mismatch — {symbol} is {actual!r}, spec fact expects {expected}"
                    )

        # 4. Count reconciliation
        if arch is not None:
            entry = _find_arch_entry(arch, fmt)
            if entry is not None and entry.get("sal_facts_count") != len(facts):
                failures.append(
                    f"{fmt}: python-qname-architecture.json sal_facts_count={entry.get('sal_facts_count')} "
                    f"but store has {len(facts)}"
                )

        # 5. QName spec_fact_ref resolution
        qname_registry = root / "shared" / "qname-registry" / f"{fmt}.yaml"
        if qname_registry.exists():
            try:
                for qentry in _load_yaml(qname_registry) or []:
                    ref = qentry.get("spec_fact_ref")
                    if not ref:
                        continue
                    resolved = ref if ref.startswith("SAL-") else aliases.get(ref, ref)
                    if resolved not in seen_ids:
                        failures.append(
                            f"{fmt}: qname {qentry.get('qname')} spec_fact_ref {ref} does not resolve in store"
                        )
            except Exception as exc:
                failures.append(f"{fmt}: qname registry unreadable ({exc})")

        # 6. Completeness gate — live numerator, register denominator
        units = spec_units_by_format.get(fmt)
        if units:
            state = ""
            if arch is not None:
                entry = _find_arch_entry(arch, fmt)
                state = (entry or {}).get("state", "")
            if state == "ACCEPTED_VERIFIED":
                ratio = len(facts) / units
                if ratio < _COMPLETENESS_THRESHOLD:
                    msg = (f"{fmt}: spec_to_fact_ratio {ratio:.2f} "
                           f"({len(facts)}/{units}) below {_COMPLETENESS_THRESHOLD}")
                    if fmt in tracked_b2_gaps:
                        warns.append(msg + " [tracked by OPEN B2 gap]")
                    else:
                        failures.append(msg + " [UNTRACKED — register a gap or seed facts]")

    result = "FAIL" if failures else ("WARN" if warns else "PASS")
    violations = failures + warns
    return {
        "validator": "validate_sal_store_reconciliation",
        "result": result,
        "blocks_sprint": False,
        "violations": violations,
        "summary": (
            f"V225: {stores_checked} stores, {bindings_checked} code bindings — "
            + ("all reconciled" if result == "PASS"
               else f"{len(failures)} failure(s), {len(warns)} tracked warn(s)")
        ),
    }
