"""Crash-resumable controller for the six Python production libraries.

The controller advances only evidence-safe machinery states.  Implementation
and verification states are entered by recording digest-bound task results;
there is no conversational approval or mutable promotion override.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
STATES = (
    "DISCOVER",
    "SNAPSHOT",
    "CONTRACT",
    "IMPLEMENT",
    "VERIFY",
    "REPAIR",
    "CERTIFY",
    "EXTRACT",
    "RELEASE_PREP",
    "COMPLETE",
)
SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
GAP_PRIORITY = {
    "authority": 0,
    "referential_integrity": 0,
    "security": 1,
    "data_loss": 1,
    "mandatory_read_write": 2,
    "interoperability": 3,
    "packaging": 4,
    "installed_use": 4,
    "public_api": 5,
    "documentation": 5,
    "optional": 6,
    "analytics": 7,
}


@dataclass(frozen=True)
class ProductTarget:
    """Stable identities used by one independently publishable product.

    Repository format IDs are historical authorities and do not always match a
    distribution/import name.  Keeping these identities explicit prevents a
    package rename from silently changing contract lookup or persistent state.
    """

    product_id: str
    contract_format_id: str
    source_package_id: str


TARGETS = (
    ProductTarget("ipynb", "ipynb", "ipynb"),
    ProductTarget("openraster", "ora", "openraster"),
    ProductTarget("nrrd", "nrrd", "nrrd"),
    ProductTarget("xliff", "xliff", "xliff"),
    ProductTarget("safetensors", "safetensors", "safetensors"),
    ProductTarget("ubl", "ubl", "ubl"),
)
TARGETS_BY_PRODUCT = {target.product_id: target for target in TARGETS}
FORMATS = tuple(target.product_id for target in TARGETS)


def validate_target_registry() -> dict[str, Any]:
    """Fail closed when a target references a non-canonical format ID."""

    registry_path = REPO_ROOT / "registry" / "format-registry.yaml"
    document = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
    registered = {
        str(item.get("format_id", ""))
        for item in document.get("formats", [])
        if isinstance(item, dict)
    }
    referenced = {target.contract_format_id for target in TARGETS}
    missing = sorted(referenced - registered)
    if missing:
        raise ValueError(
            "production targets reference unregistered contract format IDs: "
            + ", ".join(missing)
        )
    return {
        "registry_sha256": sha256_path(registry_path),
        "contract_format_ids": sorted(referenced),
    }


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tree_digest(paths: list[Path]) -> str:
    entries = []
    for root in paths:
        if not root.exists():
            entries.append({"path": root.relative_to(REPO_ROOT).as_posix(), "missing": True})
            continue
        files = [root] if root.is_file() else sorted(p for p in root.rglob("*") if p.is_file())
        for path in files:
            entries.append(
                {
                    "path": path.relative_to(REPO_ROOT).as_posix(),
                    "sha256": sha256_path(path),
                }
            )
    return hashlib.sha256(canonical_bytes(entries)).hexdigest()


@dataclass
class Gap:
    gap_id: str
    format_id: str
    obligation_id: str
    category: str
    severity: str
    root_cause: str
    state: str = "OPEN"
    evidence_digest: str = ""
    retry_count: int = 0
    invalidation_reason: str = ""
    owning_task: str = ""
    blocking_status: str = "UNBLOCKED"

    def sort_key(self) -> tuple[Any, ...]:
        return (
            GAP_PRIORITY.get(self.category, 99),
            SEVERITY_ORDER.get(self.severity, 99),
            self.format_id,
            self.obligation_id,
            self.gap_id,
        )


@dataclass
class FormatState:
    format_id: str
    state: str = "DISCOVER"
    input_digest: str = ""
    contract_digest: str = ""
    proof_digest: str = ""
    last_verified_transition: str = ""
    retry_roots: dict[str, int] = field(default_factory=dict)


class ProductionProgram:
    def __init__(self, state_dir: Path):
        # Absolute paths are required for reliable atomic replacement on
        # Windows/OneDrive-backed workspaces.
        self.state_dir = state_dir.resolve()
        self.state_path = self.state_dir / "state.json"
        self.journal_path = self.state_dir / "journal.jsonl"
        self.gaps_path = self.state_dir / "current-gaps.json"
        self.formats = {format_id: FormatState(format_id) for format_id in FORMATS}
        self.gaps: dict[str, Gap] = {}
        self.load()

    @staticmethod
    def target(format_id: str) -> ProductTarget:
        try:
            return TARGETS_BY_PRODUCT[format_id]
        except KeyError as error:
            raise ValueError(f"unknown production product: {format_id}") from error

    def load(self) -> None:
        if self.state_path.exists():
            document = json.loads(self.state_path.read_text(encoding="utf-8"))
            self.formats = {
                key: FormatState(**value) for key, value in document["formats"].items()
            }
        if self.gaps_path.exists():
            document = json.loads(self.gaps_path.read_text(encoding="utf-8"))
            self.gaps = {item["gap_id"]: Gap(**item) for item in document["gaps"]}

    @staticmethod
    def _atomic_json(path: Path, value: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(canonical_bytes(value) + b"\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(tmp_name, path)
        except BaseException:
            try:
                os.unlink(tmp_name)
            except FileNotFoundError:
                pass
            raise

    def persist(self) -> None:
        self._atomic_json(
            self.state_path,
            {
                "schema": "format-factory/production-program-state@1",
                "formats": {
                    key: asdict(value) for key, value in sorted(self.formats.items())
                },
            },
        )
        self._atomic_json(
            self.gaps_path,
            {
                "schema": "format-factory/current-gap-projection@1",
                "gaps": [asdict(gap) for gap in sorted(self.gaps.values(), key=Gap.sort_key)],
            },
        )

    def journal(self, event: dict[str, Any]) -> None:
        self.journal_path.parent.mkdir(parents=True, exist_ok=True)
        record = {**event, "event_digest": hashlib.sha256(canonical_bytes(event)).hexdigest()}
        with self.journal_path.open("ab") as stream:
            stream.write(canonical_bytes(record) + b"\n")
            stream.flush()
            os.fsync(stream.fileno())

    def transition(
        self, format_id: str, state: str, *, evidence: dict[str, Any]
    ) -> None:
        if state not in STATES:
            raise ValueError(f"unknown state: {state}")
        current = self.formats[format_id]
        current_index = STATES.index(current.state)
        next_index = STATES.index(state)
        if next_index > current_index + 1 and state != "REPAIR":
            raise ValueError(f"unsafe transition {current.state} -> {state}")
        evidence_digest = hashlib.sha256(canonical_bytes(evidence)).hexdigest()
        event = {
            "format_id": format_id,
            "from": current.state,
            "to": state,
            "evidence_digest": evidence_digest,
        }
        self.journal(event)
        current.state = state
        current.last_verified_transition = evidence_digest
        self.persist()

    def reconcile_gap(self, gap: Gap) -> None:
        existing = self.gaps.get(gap.gap_id)
        if existing:
            gap.retry_count = existing.retry_count
        self.gaps[gap.gap_id] = gap
        self.persist()

    def next_gap(self) -> Gap | None:
        open_gaps = [gap for gap in self.gaps.values() if gap.state == "OPEN"]
        return min(open_gaps, key=Gap.sort_key) if open_gaps else None

    def audit_machinery(self) -> list[dict[str, Any]]:
        """Materialize current validator failures without scanning history."""
        sources = (
            (
                REPO_ROOT / ".supervisor" / "skill-contract-validation-results.yaml",
                "findings",
            ),
            (
                REPO_ROOT / ".supervisor" / "skill-command-registry-sync-report.yaml",
                "flags",
            ),
        )
        observed: list[dict[str, Any]] = []
        current_ids: set[str] = set()
        for path, finding_key in sources:
            if not path.exists():
                continue
            document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            records = document if isinstance(document, list) else [document]
            for record in records:
                findings = record.get(finding_key, []) if isinstance(record, dict) else []
                for finding in findings or []:
                    result = str(finding.get("result", ""))
                    if result not in {"FAIL", "BROKEN_POINTER"}:
                        continue
                    obligation = str(
                        record.get("skill_id")
                        or finding.get("item")
                        or finding.get("check")
                        or "MACHINERY"
                    )
                    identity = f"machinery:{path.name}:{obligation}:{finding.get('check', '')}"
                    gap_id = "GAP-" + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16].upper()
                    current_ids.add(gap_id)
                    detail = str(finding.get("detail", result))
                    evidence_digest = sha256_path(path)
                    gap = Gap(
                        gap_id=gap_id,
                        format_id="_machinery",
                        obligation_id=obligation,
                        category="referential_integrity",
                        severity="HIGH",
                        root_cause=detail,
                        evidence_digest=evidence_digest,
                        owning_task="AUTO-MACHINERY-INTEGRITY",
                    )
                    self.reconcile_gap(gap)
                    observed.append(asdict(gap))
        for gap in self.gaps.values():
            if (
                gap.owning_task == "AUTO-MACHINERY-INTEGRITY"
                and gap.gap_id not in current_ids
            ):
                gap.state = "RESOLVED"
        self.persist()
        return sorted(observed, key=lambda item: item["gap_id"])

    def discover(self, format_id: str) -> dict[str, Any]:
        target = self.target(format_id)
        paths = [
            REPO_ROOT / "src" / "python" / target.source_package_id,
            REPO_ROOT / "tests" / "python" / target.source_package_id,
            REPO_ROOT
            / "shared"
            / "format-contracts"
            / f"{target.contract_format_id}.yaml",
        ]
        digest = tree_digest(paths)
        self.formats[format_id].input_digest = digest
        evidence = {
            "format_id": format_id,
            "contract_format_id": target.contract_format_id,
            "source_package_id": target.source_package_id,
            "input_digest": digest,
            "paths": [path.relative_to(REPO_ROOT).as_posix() for path in paths],
        }
        self.transition(format_id, "SNAPSHOT", evidence=evidence)
        return evidence

    def compile_contract(self, format_id: str) -> dict[str, Any]:
        from tools.format_contract.product_contract import load_and_compile

        target = self.target(format_id)
        path = (
            REPO_ROOT
            / "shared"
            / "format-contracts"
            / f"{target.contract_format_id}.yaml"
        )
        compiled = load_and_compile(path)
        if compiled.format_id != target.contract_format_id:
            raise ValueError(
                "compiled contract identity mismatch: "
                f"expected {target.contract_format_id}, got {compiled.format_id}"
            )
        self.formats[format_id].contract_digest = compiled.digest
        current_ids: set[str] = set()
        for issue in compiled.issues:
            category = (
                "authority"
                if issue.code in {"AUTHORITY_NOT_PINNED", "CONTRACT_MISSING"}
                else "referential_integrity"
            )
            identity = f"{format_id}:{issue.code}:{issue.reference}"
            gap_id = "GAP-" + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16].upper()
            current_ids.add(gap_id)
            self.reconcile_gap(
                Gap(
                    gap_id=gap_id,
                    format_id=format_id,
                    obligation_id=issue.reference or "CONTRACT",
                    category=category,
                    severity=issue.severity,
                    root_cause=issue.message,
                    evidence_digest=compiled.digest,
                    owning_task=f"AUTO-{format_id.upper()}-CONTRACT",
                )
            )
        for gap in self.gaps.values():
            if (
                gap.format_id == format_id
                and gap.owning_task == f"AUTO-{format_id.upper()}-CONTRACT"
                and gap.gap_id not in current_ids
            ):
                gap.state = "RESOLVED"
        evidence = {
            "format_id": format_id,
            "contract_format_id": target.contract_format_id,
            "source_package_id": target.source_package_id,
            "contract_digest": compiled.digest,
            "ready": compiled.ready,
            "obligation_count": len(compiled.obligations),
            "issues": [asdict(issue) for issue in compiled.issues],
        }
        self.transition(format_id, "CONTRACT", evidence=evidence)
        return evidence

    def bootstrap(self) -> dict[str, Any]:
        results: dict[str, Any] = {
            "target_registry": validate_target_registry(),
            "machinery": self.audit_machinery(),
        }
        for format_id in FORMATS:
            state = self.formats[format_id].state
            if state == "DISCOVER":
                results[f"{format_id}:snapshot"] = self.discover(format_id)
                state = self.formats[format_id].state
            # CONTRACT is a materialized projection, not a terminal snapshot.
            # Recompile it on each bootstrap so repaired inputs resolve their
            # old gaps and changed inputs cannot retain stale readiness.
            if state in {"SNAPSHOT", "CONTRACT"}:
                results[f"{format_id}:contract"] = self.compile_contract(format_id)
        return results

    def status(self) -> dict[str, Any]:
        return {
            "formats": {key: asdict(value) for key, value in sorted(self.formats.items())},
            "next_gap": asdict(gap) if (gap := self.next_gap()) else None,
            "open_gap_count": sum(gap.state == "OPEN" for gap in self.gaps.values()),
        }


def _git_commit() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
    ).strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--state-dir",
        type=Path,
        default=REPO_ROOT / ".local" / "production-program",
    )
    parser.add_argument("command", choices=("bootstrap", "status", "next"))
    args = parser.parse_args(argv)
    program = ProductionProgram(args.state_dir)
    payload: Any
    if args.command == "bootstrap":
        payload = {
            "git_commit": _git_commit(),
            "results": program.bootstrap(),
            "status": program.status(),
        }
    elif args.command == "next":
        payload = asdict(gap) if (gap := program.next_gap()) else None
    else:
        payload = program.status()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
