"""Crash-resumable controller for the six Python production libraries.

The controller advances only evidence-safe machinery states.  Implementation
and verification states are entered by recording digest-bound task results;
there is no conversational approval or mutable promotion override.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import tempfile
import tomllib
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
PRODUCT_PRIORITY = {
    "_machinery": -2,
    "_core": -1,
    "safetensors": 0,
    "ipynb": 1,
    "nrrd": 2,
    "openraster": 3,
    "xliff": 4,
    "ubl": 5,
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
SAL_STATUS_SCHEMA_GAP_ID = "GAP-SAL-SCHEMA-VERIFIED-WITH-NOTE"
TRANSIENT_TREE_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".pyright",
    ".ruff_cache",
    "__pycache__",
    "build",
    "dist",
}


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


def source_creation_authorization(target: ProductTarget) -> dict[str, Any]:
    """Read the live Gate 9 source-creation decision from the registry.

    Persisted controller state is never authoritative for this decision. A
    status label alone is insufficient: implementation authorization, a
    passed Gate 9 status, and an approval identity/date must all be present.
    """

    registry_path = REPO_ROOT / "registry" / "format-registry.yaml"
    document = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
    records = [
        item
        for item in document.get("formats", [])
        if isinstance(item, dict)
        and str(item.get("format_id", "")) == target.contract_format_id
    ]
    if len(records) != 1:
        return {
            "authorized": False,
            "reason": (
                "canonical registry must contain exactly one format record for "
                f"{target.contract_format_id!r}; found {len(records)}"
            ),
            "registry_sha256": sha256_path(registry_path),
        }
    record = records[0]
    gates = record.get("gates", {})
    gate_9 = gates.get("gate_9", {}) if isinstance(gates, dict) else {}
    status = str(gate_9.get("status", "")).strip().lower()
    approved_by = gate_9.get("approved_by")
    approved_date = gate_9.get("approved_date")
    implementation_authorized = record.get("implementation_authorized") is True
    status_passed = status.startswith("pass") or status.startswith("approved")
    authorized = bool(
        implementation_authorized and status_passed and approved_by and approved_date
    )
    missing: list[str] = []
    if not implementation_authorized:
        missing.append("implementation_authorized=true")
    if not status_passed:
        missing.append("a passed Gate 9 status")
    if not approved_by:
        missing.append("Gate 9 approved_by")
    if not approved_date:
        missing.append("Gate 9 approved_date")
    return {
        "authorized": authorized,
        "reason": (
            "source creation authorized"
            if authorized
            else "source creation requires " + ", ".join(missing)
        ),
        "registry_sha256": sha256_path(registry_path),
        "gate_9_status": status,
        "approved_by": approved_by,
        "approved_date": str(approved_date) if approved_date else None,
        "implementation_authorized": implementation_authorized,
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
        files = (
            [root]
            if root.is_file()
            else sorted(
                path
                for path in root.rglob("*")
                if path.is_file()
                and not any(
                    part in TRANSIENT_TREE_PARTS or part.endswith(".egg-info")
                    for part in path.relative_to(root).parts
                )
            )
        )
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
            PRODUCT_PRIORITY.get(self.format_id, 99),
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


@dataclass(frozen=True)
class ExecutedProof:
    proof_id: str
    format_id: str
    obligation_id: str
    polarity: str
    contract_digest: str
    source_paths: tuple[str, ...]
    source_digest: str
    test_paths: tuple[str, ...]
    test_digest: str
    fixture_paths: tuple[str, ...]
    fixture_digest: str
    dependency_paths: tuple[str, ...]
    dependency_digest: str
    environment_digest: str
    command: tuple[str, ...]
    exit_code: int
    stdout_sha256: str
    stderr_sha256: str
    executed: bool = True


class ProductionProgram:
    def __init__(self, state_dir: Path):
        # Absolute paths are required for reliable atomic replacement on
        # Windows/OneDrive-backed workspaces.
        self.state_dir = state_dir.resolve()
        self.state_path = self.state_dir / "state.json"
        self.journal_path = self.state_dir / "journal.jsonl"
        self.gaps_path = self.state_dir / "current-gaps.json"
        self.proofs_path = self.state_dir / "executed-proofs.json"
        self.graph_root = self.state_dir / "proof-graphs"
        self.formats = {format_id: FormatState(format_id) for format_id in FORMATS}
        self.gaps: dict[str, Gap] = {}
        self.proofs: dict[str, ExecutedProof] = {}
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
        if self.proofs_path.exists():
            document = json.loads(self.proofs_path.read_text(encoding="utf-8"))
            self.proofs = {
                item["proof_id"]: ExecutedProof(
                    **{
                        **item,
                        "source_paths": tuple(item["source_paths"]),
                        "test_paths": tuple(item["test_paths"]),
                        "fixture_paths": tuple(item["fixture_paths"]),
                        "dependency_paths": tuple(item["dependency_paths"]),
                        "command": tuple(item["command"]),
                    }
                )
                for item in document["proofs"]
            }

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
        self._atomic_json(
            self.proofs_path,
            {
                "schema": "format-factory/executed-proof@1",
                "proofs": [
                    asdict(proof)
                    for proof in sorted(self.proofs.values(), key=lambda item: item.proof_id)
                ],
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

    def reconcile_gap(self, gap: Gap, *, persist: bool = True) -> None:
        existing = self.gaps.get(gap.gap_id)
        if existing:
            gap.retry_count = existing.retry_count
        self.gaps[gap.gap_id] = gap
        if persist:
            self.persist()

    def next_gap(self) -> Gap | None:
        open_gaps = [
            gap
            for gap in self.gaps.values()
            if gap.state == "OPEN" and gap.blocking_status == "UNBLOCKED"
        ]
        return min(open_gaps, key=Gap.sort_key) if open_gaps else None

    def next_blocked_gap(self) -> Gap | None:
        """Expose dependencies without allowing one format to stall the queue."""

        blocked = [
            gap
            for gap in self.gaps.values()
            if gap.state == "OPEN" and gap.blocking_status != "UNBLOCKED"
        ]
        return min(blocked, key=Gap.sort_key) if blocked else None

    @staticmethod
    def _repo_inputs(values: list[str] | tuple[str, ...], *, label: str) -> list[Path]:
        root = REPO_ROOT.resolve()
        paths: list[Path] = []
        for value in values:
            candidate = Path(value)
            if not candidate.is_absolute():
                candidate = root / candidate
            candidate = candidate.resolve()
            try:
                candidate.relative_to(root)
            except ValueError as error:
                raise ValueError(f"{label} input escapes the repository: {value}") from error
            if not candidate.exists():
                raise ValueError(f"{label} input does not exist: {value}")
            paths.append(candidate)
        return sorted(set(paths))

    @staticmethod
    def _relative_paths(paths: list[Path]) -> tuple[str, ...]:
        return tuple(path.relative_to(REPO_ROOT.resolve()).as_posix() for path in paths)

    @staticmethod
    def _environment_digest() -> str:
        distributions = sorted(
            (
                str(distribution.metadata.get("Name", "")).lower().replace("_", "-"),
                distribution.version,
            )
            for distribution in importlib.metadata.distributions()
        )
        return hashlib.sha256(
            canonical_bytes(
                {
                    "python": platform.python_version(),
                    "implementation": platform.python_implementation(),
                    "os": platform.system(),
                    "architecture": platform.machine(),
                    "distributions": distributions,
                }
            )
        ).hexdigest()

    @staticmethod
    def _canonical_command(command: list[str]) -> tuple[str, ...]:
        canonical: list[str] = []
        root = REPO_ROOT.resolve()
        executable = Path(sys.executable).resolve()
        for index, value in enumerate(command):
            candidate = Path(value)
            if index == 0 and candidate.exists():
                resolved = candidate.resolve()
                if resolved == executable:
                    canonical.append(f"<python:{sha256_path(resolved)}>")
                    continue
                try:
                    canonical.append(resolved.relative_to(root).as_posix())
                except ValueError:
                    canonical.append(
                        f"<external:{resolved.name}:{sha256_path(resolved)}>"
                    )
                continue
            if candidate.is_absolute():
                resolved = candidate.resolve()
                try:
                    canonical.append(resolved.relative_to(root).as_posix())
                except ValueError as error:
                    raise ValueError(
                        f"command argument contains an external absolute path: {value}"
                    ) from error
            else:
                canonical.append(value)
        return tuple(canonical)

    def _dependency_inputs(self, target: ProductTarget) -> list[Path]:
        package_root = REPO_ROOT / "src" / "python" / target.source_package_id
        candidates = [REPO_ROOT / "pyproject.toml", package_root / "pyproject.toml"]
        for root in (REPO_ROOT, package_root):
            if not root.is_dir():
                continue
            candidates.extend(root.glob("*.lock"))
            candidates.extend(root.glob("requirements*.txt"))
        return sorted({path.resolve() for path in candidates if path.is_file()})

    @staticmethod
    def _package_chassis_issues(
        source_package_id: str, distribution_suffix: str
    ) -> list[str]:
        package_root = REPO_ROOT / "src" / "python" / source_package_id
        pyproject = package_root / "pyproject.toml"
        issues: list[str] = []
        if not package_root.is_dir():
            return [f"source package directory is missing: {package_root.relative_to(REPO_ROOT)}"]
        if not pyproject.is_file():
            return [f"package metadata is missing: {pyproject.relative_to(REPO_ROOT)}"]
        try:
            document = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError) as error:
            return [f"package metadata is not parseable TOML: {error}"]
        project = document.get("project", {})
        expected_name = f"format-factory-{distribution_suffix}"
        if project.get("name") != expected_name:
            issues.append(
                f"distribution name must be {expected_name!r}, got {project.get('name')!r}"
            )
        requires_python = str(project.get("requires-python", ""))
        if ">=3.11" not in requires_python or "3.9" in requires_python or "3.10" in requires_python:
            issues.append(
                "requires-python must establish the Python 3.11 production floor"
            )
        namespace_root = package_root / "src" / "format_factory"
        module_root = namespace_root / distribution_suffix
        if not (module_root / "__init__.py").is_file():
            issues.append(
                "PEP 420 package is missing "
                f"{module_root.relative_to(REPO_ROOT).as_posix()}/__init__.py"
            )
        if (namespace_root / "__init__.py").exists():
            issues.append("PEP 420 parent format_factory/__init__.py is prohibited")
        tests_root = REPO_ROOT / "tests" / "python" / source_package_id
        if not tests_root.is_dir():
            issues.append(
                f"package test root is missing: {tests_root.relative_to(REPO_ROOT)}"
            )
        return issues

    def _audit_chassis(self) -> list[dict[str, Any]]:
        observed: list[dict[str, Any]] = []
        targets = [
            ("_core", "core", "core"),
            *[
                (target.product_id, target.source_package_id, target.product_id)
                for target in TARGETS
            ],
        ]
        current_ids: set[str] = set()
        for product_id, source_package_id, distribution_suffix in targets:
            issues = self._package_chassis_issues(
                source_package_id, distribution_suffix
            )
            authorization: dict[str, Any] | None = None
            if product_id != "_core":
                authorization = source_creation_authorization(
                    TARGETS_BY_PRODUCT[product_id]
                )
                if not authorization["authorized"]:
                    issues.append(str(authorization["reason"]))
            identity = f"{product_id}:production-package-chassis"
            gap_id = (
                "GAP-"
                + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16].upper()
            )
            current_ids.add(gap_id)
            package_root = REPO_ROOT / "src" / "python" / source_package_id
            evidence_digest = tree_digest(
                [
                    package_root,
                    REPO_ROOT / "tests" / "python" / source_package_id,
                ]
            )
            if issues:
                source_blocked = bool(
                    authorization is not None and not authorization["authorized"]
                )
                gap = Gap(
                    gap_id=gap_id,
                    format_id=product_id,
                    obligation_id="PRODUCTION_PACKAGE_CHASSIS",
                    category="referential_integrity",
                    severity="HIGH",
                    root_cause="; ".join(issues),
                    evidence_digest=evidence_digest,
                    owning_task=(
                        f"AUTO-{product_id.upper()}-GATE9-READINESS"
                        if source_blocked
                        else f"AUTO-{product_id.upper()}-PACKAGE-CHASSIS"
                    ),
                    blocking_status=(
                        "BLOCKED_DEPENDENCY" if source_blocked else "UNBLOCKED"
                    ),
                )
                self.reconcile_gap(gap, persist=False)
                observed.append(asdict(gap))
            elif existing := self.gaps.get(gap_id):
                existing.state = "RESOLVED"
                existing.evidence_digest = evidence_digest
        for gap in self.gaps.values():
            if (
                gap.obligation_id == "PRODUCTION_PACKAGE_CHASSIS"
                and gap.gap_id not in current_ids
            ):
                gap.state = "RESOLVED"
        self.persist()
        return observed

    def execute_proof(
        self,
        format_id: str,
        obligation_id: str,
        *,
        polarity: str,
        test_paths: list[str],
        fixture_paths: list[str],
        command: list[str],
    ) -> dict[str, Any]:
        """Execute one digest-bound proof command and persist only a live PASS."""

        from tools.format_contract.product_contract import load_and_compile

        target = self.target(format_id)
        contract_path = (
            REPO_ROOT
            / "shared"
            / "format-contracts"
            / f"{target.contract_format_id}.yaml"
        )
        compiled = load_and_compile(contract_path)
        obligations = {
            item["obligation_id"]: item
            for item in compiled.obligations
            if item["level"] == "MUST"
        }
        obligation = obligations.get(obligation_id)
        if obligation is None:
            raise ValueError(
                f"proof obligation is unknown or non-mandatory: {obligation_id}"
            )
        required_polarity = (
            "negative" if obligation["kind"] == "rejection" else "positive"
        )
        if polarity != required_polarity:
            raise ValueError(
                f"{obligation_id} requires {required_polarity} proof, got {polarity}"
            )
        if not command:
            raise ValueError("proof command is empty")
        if not test_paths:
            raise ValueError("at least one test input is required")

        source_root = REPO_ROOT / "src" / "python" / target.source_package_id
        source_inputs = self._repo_inputs(
            [source_root.as_posix()], label="source"
        )
        tests = self._repo_inputs(test_paths, label="test")
        tests_root = (REPO_ROOT / "tests").resolve()
        for path in tests:
            try:
                path.relative_to(tests_root)
            except ValueError as error:
                raise ValueError(
                    f"test input must be under tests/: {path.relative_to(REPO_ROOT)}"
                ) from error
        fixtures = self._repo_inputs(fixture_paths, label="fixture")
        dependencies = self._dependency_inputs(target)
        before = {
            "source": tree_digest(source_inputs),
            "tests": tree_digest(tests),
            "fixtures": tree_digest(fixtures),
            "dependencies": tree_digest(dependencies),
        }
        environment_digest = self._environment_digest()
        run_environment = {
            **os.environ,
            "PYTHONHASHSEED": "0",
            "SOURCE_DATE_EPOCH": "0",
            "TZ": "UTC",
        }
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            env=run_environment,
            capture_output=True,
            check=False,
        )
        after = {
            "source": tree_digest(source_inputs),
            "tests": tree_digest(tests),
            "fixtures": tree_digest(fixtures),
            "dependencies": tree_digest(dependencies),
        }
        if before != after:
            raise ValueError("proof inputs changed during execution")
        if result.returncode != 0:
            raise RuntimeError(
                f"proof command failed with exit code {result.returncode}; result not recorded"
            )

        material = {
            "format_id": format_id,
            "obligation_id": obligation_id,
            "polarity": polarity,
            "contract_digest": compiled.digest,
            "source_paths": self._relative_paths(source_inputs),
            "source_digest": before["source"],
            "test_paths": self._relative_paths(tests),
            "test_digest": before["tests"],
            "fixture_paths": self._relative_paths(fixtures),
            "fixture_digest": before["fixtures"],
            "dependency_paths": self._relative_paths(dependencies),
            "dependency_digest": before["dependencies"],
            "environment_digest": environment_digest,
            "command": self._canonical_command(command),
            "exit_code": result.returncode,
            "stdout_sha256": hashlib.sha256(result.stdout).hexdigest(),
            "stderr_sha256": hashlib.sha256(result.stderr).hexdigest(),
            "executed": True,
        }
        proof_id = "PROOF-" + hashlib.sha256(canonical_bytes(material)).hexdigest().upper()
        proof = ExecutedProof(
            proof_id=proof_id,
            format_id=format_id,
            obligation_id=obligation_id,
            polarity=polarity,
            contract_digest=compiled.digest,
            source_paths=self._relative_paths(source_inputs),
            source_digest=before["source"],
            test_paths=self._relative_paths(tests),
            test_digest=before["tests"],
            fixture_paths=self._relative_paths(fixtures),
            fixture_digest=before["fixtures"],
            dependency_paths=self._relative_paths(dependencies),
            dependency_digest=before["dependencies"],
            environment_digest=environment_digest,
            command=self._canonical_command(command),
            exit_code=result.returncode,
            stdout_sha256=hashlib.sha256(result.stdout).hexdigest(),
            stderr_sha256=hashlib.sha256(result.stderr).hexdigest(),
            executed=True,
        )
        self.proofs[proof_id] = proof
        self.persist()
        self.journal(
            {
                "event": "EXECUTED_PROOF_RECORDED",
                "format_id": format_id,
                "obligation_id": obligation_id,
                "proof_id": proof_id,
            }
        )
        return asdict(proof)

    def _build_product_graph(
        self, format_id: str, compiled: Any
    ) -> tuple[Any, dict[str, str], set[str]]:
        from tools.requirements_authority.production_graph import ProductionProofGraph

        graph = ProductionProofGraph()
        current: dict[str, str] = {}
        authority_nodes = []
        for authority in compiled.authorities:
            identity = str(authority["source_id"])
            input_key = f"authority:{format_id}:{identity}"
            is_normative = authority.get("authority_class") == "AUTHORITATIVE"
            digest = str(
                authority.get("content_hash")
                or hashlib.sha256(canonical_bytes(authority)).hexdigest()
            )
            current[input_key] = digest
            authority_nodes.append(
                graph.add_content_node(
                    "AuthorityArtifact" if is_normative else "ProductRequirement",
                    identity,
                    {
                        "format_id": format_id,
                        "acquired": authority["acquired"] if is_normative else True,
                        "authority_class": authority.get("authority_class"),
                        "content_hash": digest,
                    },
                    input_digests={input_key: digest},
                )
            )

        contract_key = f"contract:{format_id}"
        current[contract_key] = compiled.digest
        obligation_nodes = {}
        for obligation in compiled.obligations:
            node = graph.add_content_node(
                "NormativeObligation",
                obligation["obligation_id"],
                {
                    "format_id": format_id,
                    "level": obligation["level"],
                    "kind": obligation["kind"],
                    "capability_id": obligation["capability_id"],
                    "source_field": obligation["source_field"],
                },
                input_digests={contract_key: compiled.digest},
            )
            graph.add_dependencies(node, authority_nodes)
            obligation_nodes[obligation["obligation_id"]] = node

        target = self.target(format_id)
        source_root = REPO_ROOT / "src" / "python" / target.source_package_id
        source_node = None
        if source_root.is_dir():
            source_key = f"source:{format_id}"
            source_digest = tree_digest([source_root])
            current[source_key] = source_digest
            source_node = graph.add_content_node(
                "SourceSymbol",
                f"{target.source_package_id}:product-tree",
                {"format_id": format_id, "path": source_root.relative_to(REPO_ROOT).as_posix()},
                input_digests={source_key: source_digest},
            )

        stale_obligations: set[str] = set()
        for proof in sorted(self.proofs.values(), key=lambda item: item.proof_id):
            if proof.format_id != format_id:
                continue
            try:
                source_paths = self._repo_inputs(proof.source_paths, label="source")
                test_paths = self._repo_inputs(proof.test_paths, label="test")
                fixture_paths = self._repo_inputs(proof.fixture_paths, label="fixture")
                dependency_paths = self._repo_inputs(
                    proof.dependency_paths, label="dependency"
                )
            except ValueError:
                stale_obligations.add(proof.obligation_id)
                continue
            live = {
                "contract": compiled.digest,
                "source": tree_digest(source_paths),
                "tests": tree_digest(test_paths),
                "fixtures": tree_digest(fixture_paths),
                "dependencies": tree_digest(dependency_paths),
                "environment": self._environment_digest(),
            }
            recorded = {
                "contract": proof.contract_digest,
                "source": proof.source_digest,
                "tests": proof.test_digest,
                "fixtures": proof.fixture_digest,
                "dependencies": proof.dependency_digest,
                "environment": proof.environment_digest,
            }
            if live != recorded:
                stale_obligations.add(proof.obligation_id)
                continue
            obligation_node = obligation_nodes.get(proof.obligation_id)
            if obligation_node is None:
                stale_obligations.add(proof.obligation_id)
                continue
            input_digests = {
                f"proof:{proof.proof_id}:{key}": value
                for key, value in sorted(recorded.items())
            }
            current.update(input_digests)
            result_node = graph.add_content_node(
                "ExecutedTestResult",
                proof.proof_id,
                {
                    "format_id": format_id,
                    "outcome": "PASS",
                    "executed": proof.executed,
                    "polarity": proof.polarity,
                    "command": proof.command,
                    "exit_code": proof.exit_code,
                    "stdout_sha256": proof.stdout_sha256,
                    "stderr_sha256": proof.stderr_sha256,
                },
                input_digests=input_digests,
            )
            graph.add_dependency(
                result_node, obligation_node, edge_type="verified_by"
            )
            if source_node is not None:
                graph.add_dependency(result_node, source_node)
        return graph, current, stale_obligations

    @staticmethod
    def _obligation_gap_category(obligation: dict[str, Any]) -> str:
        source_field = obligation["source_field"]
        if source_field in {"security_requirements", "error_behavior"}:
            return "security"
        if source_field == "preservation_rules":
            return "data_loss"
        return "mandatory_read_write"

    def audit_implementation(self, format_id: str) -> dict[str, Any]:
        """Rebuild current proof and materialize every unproved MUST obligation."""

        from tools.format_contract.product_contract import load_and_compile
        from tools.requirements_authority.production_graph import PromotionDecision

        target = self.target(format_id)
        contract_path = (
            REPO_ROOT
            / "shared"
            / "format-contracts"
            / f"{target.contract_format_id}.yaml"
        )
        compiled = load_and_compile(contract_path)
        graph, current, stale_obligations = self._build_product_graph(
            format_id, compiled
        )
        decision = graph.compute_promotion(
            format_id, current_identity_digests=current
        )
        unmet = set(decision.unmet_obligations)
        stale_unmet = sorted(stale_obligations & unmet)
        if stale_unmet:
            decision = PromotionDecision(
                format_id=format_id,
                state="INVALIDATED",
                unmet_obligations=decision.unmet_obligations,
                invalidated_nodes=tuple(stale_unmet),
                reasons=("one or more previously executed proof inputs changed",),
            )

        graph_dir = self.graph_root / format_id
        graph.store.save_nodes(graph_dir / "nodes.jsonl")
        graph.store.save_edges(graph_dir / "edges.jsonl")
        graph_digest = graph.graph_digest()
        self.formats[format_id].proof_digest = graph_digest
        current_ids: set[str] = set()
        obligations = {
            item["obligation_id"]: item
            for item in compiled.obligations
            if item["level"] == "MUST"
        }
        source_exists = (
            REPO_ROOT / "src" / "python" / target.source_package_id
        ).is_dir()
        for obligation_id in sorted(unmet):
            obligation = obligations[obligation_id]
            identity = f"{format_id}:implementation:{obligation_id}"
            gap_id = (
                "GAP-"
                + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16].upper()
            )
            current_ids.add(gap_id)
            stale = obligation_id in stale_obligations
            if not source_exists:
                root_cause = (
                    "production source package is absent; executed behavior proof "
                    "cannot be produced"
                )
            elif stale:
                root_cause = (
                    "previous executed proof was invalidated by a changed or deleted "
                    "contract, source, test, fixture, dependency, or environment input"
                )
            else:
                required_polarity = (
                    "negative" if obligation["kind"] == "rejection" else "positive"
                )
                root_cause = (
                    "mandatory obligation has no live digest-bound executed "
                    f"{required_polarity} result"
                )
            gap = Gap(
                gap_id=gap_id,
                format_id=format_id,
                obligation_id=obligation_id,
                category=self._obligation_gap_category(obligation),
                severity="HIGH",
                root_cause=root_cause,
                evidence_digest=graph_digest,
                owning_task=(
                    f"AUTO-{format_id.upper()}-IMPLEMENT-"
                    f"{obligation['capability_id']}"
                ),
                invalidation_reason=(
                    "proof_input_changed" if stale else ""
                ),
            )
            self.reconcile_gap(gap, persist=False)
        prefix = f"AUTO-{format_id.upper()}-IMPLEMENT-"
        for gap in self.gaps.values():
            if gap.owning_task.startswith(prefix) and gap.gap_id not in current_ids:
                gap.state = "RESOLVED"
                gap.evidence_digest = graph_digest
        self.persist()

        evidence = {
            "format_id": format_id,
            "contract_digest": compiled.digest,
            "graph_digest": graph_digest,
            "promotion": asdict(decision),
            "mandatory_obligation_count": len(obligations),
            "unmet_obligation_count": len(unmet),
            "stale_proof_obligations": stale_unmet,
        }
        if self.formats[format_id].state == "CONTRACT":
            self.transition(format_id, "IMPLEMENT", evidence=evidence)
        return evidence

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
        observed.extend(self.audit_sal_status_policy())
        self.persist()
        return sorted(observed, key=lambda item: item["gap_id"])

    def audit_sal_status_policy(self) -> list[dict[str, Any]]:
        """Recompute schema drift and non-promoting mandatory fact gaps."""

        from tools.spec.sal_proof import (
            canonical_json_bytes,
            fact_proof_closure,
            sha256_bytes,
            validate_fact_promotion,
        )
        from tools.spec.sal_status import PROMOTING, load_status_policy

        schema_path = (
            REPO_ROOT / "schemas" / "sal-facts" / "sal-facts-schema.json"
        )
        store_dir = REPO_ROOT / "shared" / "sal-facts"
        evidence_digest = tree_digest([schema_path, store_dir])
        observed_statuses: set[str] = set()
        for path in sorted(store_dir.glob("*.yaml")):
            document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            observed_statuses.update(
                str(fact["verification_status"])
                for fact in document.get("facts", [])
                if fact.get("verification_status")
            )

        policy_error = ""
        try:
            policy = load_status_policy(schema_path)
            unknown = sorted(observed_statuses - set(policy))
            if unknown:
                policy_error = (
                    "canonical SAL stores use statuses absent from the schema: "
                    + ", ".join(unknown)
                )
        except (OSError, ValueError, json.JSONDecodeError) as error:
            policy = {}
            policy_error = str(error)

        observed: list[dict[str, Any]] = []
        if policy_error:
            gap = Gap(
                gap_id=SAL_STATUS_SCHEMA_GAP_ID,
                format_id="_machinery",
                obligation_id="SAL_SCHEMA_STATUS_ENUM",
                category="referential_integrity",
                severity="HIGH",
                root_cause=policy_error,
                evidence_digest=evidence_digest,
                owning_task="AUTO-SAL-SCHEMA-ENUM-REPAIR",
            )
            self.reconcile_gap(gap)
            observed.append(asdict(gap))
            return observed

        if existing := self.gaps.get(SAL_STATUS_SCHEMA_GAP_ID):
            existing.state = "RESOLVED"
            existing.evidence_digest = evidence_digest

        for target in TARGETS:
            contract_path = (
                REPO_ROOT
                / "shared"
                / "format-contracts"
                / f"{target.contract_format_id}.yaml"
            )
            store_path = store_dir / f"{target.contract_format_id}.yaml"
            if not contract_path.is_file() or not store_path.is_file():
                continue
            contract = yaml.safe_load(contract_path.read_text(encoding="utf-8")) or {}
            store = yaml.safe_load(store_path.read_text(encoding="utf-8")) or {}
            fact_by_id: dict[str, dict[str, Any]] = {}
            for fact in store.get("facts", []):
                for identity in (fact.get("fact_id"), fact.get("qname")):
                    if identity:
                        fact_by_id[str(identity)] = fact

            non_promoting: dict[str, int] = {}
            proof_failures: dict[str, int] = {}
            proof_closures: list[dict[str, Any]] = []
            referenced: set[str] = set()
            for capability in contract.get("capabilities", []):
                if str(capability.get("level", "")).upper() != "MUST":
                    continue
                referenced.update(
                    str(reference)
                    for reference in capability.get("provenance", [])
                    if str(reference).startswith("SAL-")
                )
            for reference in referenced:
                fact = fact_by_id.get(reference)
                status = (
                    str(fact.get("verification_status", "UNSPECIFIED"))
                    if fact is not None
                    else "UNSPECIFIED"
                )
                rule = policy.get(status)
                if rule is None or rule.promotion_class != PROMOTING:
                    non_promoting[status] = non_promoting.get(status, 0) + 1
                elif fact is not None:
                    proof_closures.append(fact_proof_closure(fact, REPO_ROOT))
                    valid, reason = validate_fact_promotion(fact, REPO_ROOT)
                    if not valid:
                        proof_failures[reason] = proof_failures.get(reason, 0) + 1

            identity = f"{target.product_id}:mandatory-fact-authority"
            gap_id = (
                "GAP-"
                + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16].upper()
            )
            if non_promoting or proof_failures:
                counts = ", ".join(
                    f"{status}={count}"
                    for status, count in sorted(non_promoting.items())
                )
                proof_counts = "; ".join(
                    f"{reason}={count}"
                    for reason, count in sorted(proof_failures.items())
                )
                details = ", ".join(filter(None, (counts, proof_counts)))
                gap = Gap(
                    gap_id=gap_id,
                    format_id=target.product_id,
                    obligation_id="MANDATORY_FACT_AUTHORITY",
                    category="authority",
                    severity="CRITICAL",
                    root_cause=(
                        "mandatory contract facts are referentially present but not "
                        "promotion-eligible under the canonical SAL policy and live "
                        f"proof closure: {details}"
                    ),
                    evidence_digest=sha256_bytes(
                        canonical_json_bytes(
                            {
                                "base": tree_digest(
                                    [schema_path, contract_path, store_path]
                                ),
                                "proof_closures": sorted(
                                    proof_closures,
                                    key=lambda item: item["fact_id"],
                                ),
                            }
                        )
                    ),
                    owning_task=(
                        f"AUTO-{target.product_id.upper()}-FACT-AUTHORITY"
                    ),
                )
                self.reconcile_gap(gap)
                observed.append(asdict(gap))
            elif existing := self.gaps.get(gap_id):
                existing.state = "RESOLVED"
                existing.evidence_digest = tree_digest(
                    [schema_path, contract_path, store_path]
                )
        return observed

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
        if self.formats[format_id].state == "SNAPSHOT":
            self.transition(format_id, "CONTRACT", evidence=evidence)
        else:
            self.persist()
        return evidence

    def bootstrap(self) -> dict[str, Any]:
        results: dict[str, Any] = {
            "target_registry": validate_target_registry(),
            "machinery": self.audit_machinery(),
            "package_chassis": self._audit_chassis(),
        }
        for format_id in FORMATS:
            state = self.formats[format_id].state
            if state == "DISCOVER":
                results[f"{format_id}:snapshot"] = self.discover(format_id)
            # CONTRACT is a materialized projection, not a terminal snapshot.
            # Recompile it on each bootstrap so repaired inputs resolve their
            # old gaps and changed inputs cannot retain stale readiness.
            contract = self.compile_contract(format_id)
            results[f"{format_id}:contract"] = contract
            if contract["ready"]:
                results[f"{format_id}:implementation"] = self.audit_implementation(
                    format_id
                )
        return results

    def status(self) -> dict[str, Any]:
        open_gaps = [gap for gap in self.gaps.values() if gap.state == "OPEN"]
        return {
            "formats": {key: asdict(value) for key, value in sorted(self.formats.items())},
            "next_gap": asdict(gap) if (gap := self.next_gap()) else None,
            "next_blocked_gap": (
                asdict(blocked) if (blocked := self.next_blocked_gap()) else None
            ),
            "open_gap_count": len(open_gaps),
            "blocked_gap_count": sum(
                gap.blocking_status != "UNBLOCKED" for gap in open_gaps
            ),
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
    parser.add_argument("command", choices=("bootstrap", "status", "next", "prove"))
    parser.add_argument("--format", dest="format_id", choices=FORMATS)
    parser.add_argument("--obligation")
    parser.add_argument("--polarity", choices=("positive", "negative"))
    parser.add_argument("--test", action="append", default=[])
    parser.add_argument("--fixture", action="append", default=[])
    parser.add_argument("--run", nargs=argparse.REMAINDER, default=[])
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
    elif args.command == "prove":
        if not all((args.format_id, args.obligation, args.polarity, args.run)):
            parser.error(
                "prove requires --format, --obligation, --polarity, --test, and --run"
            )
        proof = program.execute_proof(
            args.format_id,
            args.obligation,
            polarity=args.polarity,
            test_paths=args.test,
            fixture_paths=args.fixture,
            command=args.run,
        )
        payload = {
            "proof": proof,
            "implementation": program.audit_implementation(args.format_id),
            "status": program.status(),
        }
    else:
        payload = program.status()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
