"""
EvidenceGraphImporter: read-only import of existing system state into candidate
proof graph records. Imports from poc-targets.yaml, format-registry.yaml,
supervisor reports, evidence declarations, and evidence manifests.

Import rules:
1. poc-targets status is NOT authority — imported as candidates only
2. Imported reports are candidates, not truth
3. Imported tests must link to a claim to count
4. Imported dogfood needs path + checksum + validation
5. Evidence packages must materialize files or mark declared_not_verified
"""
import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from .graph_store import GraphStore
from .models import GraphNode, GraphEdge


def _sha256_file(path: Path) -> Optional[str]:
    """Compute SHA-256 of a file, or return None if not readable."""
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9_]", "_", text.lower())


class ImportConflict:
    def __init__(self, source: str, node_id: str, message: str):
        self.source = source
        self.node_id = node_id
        self.message = message

    def __repr__(self) -> str:
        return f"ImportConflict({self.source!r}, {self.node_id!r}): {self.message}"


class ImportResult:
    def __init__(self):
        self.store = GraphStore()
        self.conflicts: List[ImportConflict] = []
        self.phase_logs: Dict[str, List[str]] = {}

    def log(self, phase: str, message: str) -> None:
        self.phase_logs.setdefault(phase, []).append(message)


class EvidenceGraphImporter:
    """
    Phase 0–1 importer: read-only inventory → candidate graph.
    All imported nodes are candidate status (not accepted/rejected).
    """

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.result = ImportResult()

    def import_all(self) -> ImportResult:
        """Run full Phase 0 (inventory) + Phase 1 (candidate graph) import."""
        self.result = ImportResult()
        self._phase0_inventory()
        self._import_poc_targets()
        self._import_format_registry()
        self._import_evidence_declarations()
        self._import_evidence_manifests()
        self._import_supervisor_reports()
        return self.result

    # ── Phase 0: read-only inventory ────────────────────────────────────────

    def _phase0_inventory(self) -> None:
        phase = "Phase0_Inventory"
        key_paths = [
            "product-capability-matrix/poc-targets.yaml",
            "registry/format-registry.yaml",
            "reports/supervisor/session-resume.md",
            ".local/evidences",
        ]
        for rel in key_paths:
            p = self.repo_root / rel
            if p.exists():
                self.result.log(phase, f"FOUND: {rel}")
            else:
                self.result.log(phase, f"MISSING: {rel}")

    # ── poc-targets.yaml: candidate PocTargetField nodes ────────────────────

    def _import_poc_targets(self) -> None:
        phase = "Import_PocTargets"
        path = self.repo_root / "product-capability-matrix" / "poc-targets.yaml"
        if not path.exists():
            self.result.log(phase, "poc-targets.yaml not found — skipping")
            return

        data = self._load_yaml(path)
        if not data:
            self.result.log(phase, "poc-targets.yaml empty or unparseable")
            return

        targets = data.get("targets", data.get("poc_targets", []))
        if isinstance(targets, dict):
            targets = [{"id": k, **v} for k, v in targets.items()]

        for target in targets:
            tid = target.get("id", target.get("format_id", "unknown"))
            node_id = f"ptf:{_slug(tid)}"
            node = GraphNode(
                node_id=node_id,
                node_type="PocTargetField",
                label=f"POC Target: {tid}",
                status="candidate",
                metadata={
                    "imported_from": "poc-targets.yaml",
                    "import_rule": "poc_targets_status_is_not_authority",
                    "original_status": str(target.get("status", "unknown")),
                    "target_id": tid,
                    "declared_not_verified": True,
                },
                created_at=_now_iso(),
            )
            self.result.store.add_node(node)
            self.result.log(phase, f"Imported PocTargetField: {node_id} (original status: {node.metadata['original_status']})")

    # ── format-registry.yaml: candidate SpecRequirementRef nodes ────────────

    def _import_format_registry(self) -> None:
        phase = "Import_FormatRegistry"
        path = self.repo_root / "registry" / "format-registry.yaml"
        if not path.exists():
            self.result.log(phase, "format-registry.yaml not found — skipping")
            return

        data = self._load_yaml(path)
        if not data:
            self.result.log(phase, "format-registry.yaml empty or unparseable")
            return

        formats = data.get("formats", data if isinstance(data, list) else [])
        count = 0
        for fmt in formats:
            if not isinstance(fmt, dict):
                continue
            fid = fmt.get("id", fmt.get("format_id", "unknown"))
            node_id = f"spec:{_slug(fid)}"
            node = GraphNode(
                node_id=node_id,
                node_type="SpecRequirementRef",
                label=f"Format Spec: {fid}",
                status="candidate",
                metadata={
                    "imported_from": "format-registry.yaml",
                    "format_id": fid,
                    "declared_not_verified": True,
                },
                created_at=_now_iso(),
            )
            self.result.store.add_node(node)
            count += 1

        self.result.log(phase, f"Imported {count} SpecRequirementRef nodes from format-registry.yaml")

    # ── Evidence declarations: candidate EvidencePackage + CapabilityClaim ──

    def _import_evidence_declarations(self) -> None:
        phase = "Import_EvidenceDeclarations"
        evidences_dir = self.repo_root / ".local" / "evidences"
        if not evidences_dir.exists():
            self.result.log(phase, ".local/evidences not found — skipping")
            return

        declaration_files = list(evidences_dir.glob("*/evidence-declaration.yaml"))
        for decl_path in sorted(declaration_files):
            run_id = decl_path.parent.name
            self._import_single_declaration(decl_path, run_id, phase)

    def _import_single_declaration(self, path: Path, run_id: str, phase: str) -> None:
        data = self._load_yaml(path)
        if not data:
            self.result.log(phase, f"SKIP {run_id}: unparseable declaration")
            return

        sprint_id = data.get("sprint_id", run_id)
        # Import as EvidencePackage candidate
        pkg_node_id = f"evpkg:{_slug(run_id)}"
        pkg_node = GraphNode(
            node_id=pkg_node_id,
            node_type="EvidencePackage",
            label=f"Evidence: {sprint_id}",
            status="candidate",
            metadata={
                "imported_from": str(path.relative_to(self.repo_root)),
                "sprint_id": sprint_id,
                "run_id": run_id,
                "import_rule": "evidence_packages_must_materialize_files_or_mark_declared_not_verified",
                "declared_not_verified": True,
                "worker_verdict": data.get("worker_self_verdict", "unknown"),
            },
            created_at=_now_iso(),
        )
        self.result.store.add_node(pkg_node)

        # Import taskcards as candidate UsageRecord nodes
        for tc in data.get("taskcards", []):
            tc_id = tc.get("id", "unknown")
            tc_node_id = f"usage:{_slug(run_id)}:{_slug(tc_id)}"
            tc_node = GraphNode(
                node_id=tc_node_id,
                node_type="UsageRecord",
                label=f"TC {tc_id} in {run_id}",
                status="candidate",
                metadata={
                    "taskcard_id": tc_id,
                    "taskcard_status": tc.get("status", "unknown"),
                    "output_files": tc.get("output_files", []),
                    "run_id": run_id,
                    "import_rule": "imported_tests_must_link_to_claim_to_count",
                    "declared_not_verified": True,
                },
                created_at=_now_iso(),
            )
            self.result.store.add_node(tc_node)
            # Edge: evidence package consumed_by this usage record
            edge = GraphEdge(
                edge_id=f"edge:evpkg:{_slug(run_id)}:consumed_by:{_slug(tc_id)}",
                edge_type="consumed_by",
                source_node_id=pkg_node_id,
                target_node_id=tc_node_id,
                metadata={"declared_not_verified": True},
            )
            self.result.store.add_edge(edge)

        self.result.log(phase, f"Imported EvidencePackage: {pkg_node_id} ({sprint_id})")

    # ── Evidence manifests: candidate artifact nodes ─────────────────────────

    def _import_evidence_manifests(self) -> None:
        phase = "Import_EvidenceManifests"
        evidences_dir = self.repo_root / ".local" / "evidences"
        if not evidences_dir.exists():
            return

        manifest_files = list(evidences_dir.glob("*/evidence-manifest.yaml"))
        for mf_path in sorted(manifest_files):
            run_id = mf_path.parent.name
            data = self._load_yaml(mf_path)
            if not data:
                continue

            for entry in data.get("output_files", []):
                rel_path = entry.get("path", "")
                if not rel_path:
                    continue
                abs_path = self.repo_root / rel_path
                exists = abs_path.exists()
                checksum = _sha256_file(abs_path) if exists else None

                file_type = entry.get("type", "unknown")
                node_type = self._file_type_to_node_type(file_type)
                node_id = f"artifact:{_slug(run_id)}:{_slug(rel_path.replace('/', '__'))}"

                node = GraphNode(
                    node_id=node_id,
                    node_type=node_type,
                    label=f"{file_type}: {rel_path}",
                    status="candidate",
                    metadata={
                        "imported_from": str(mf_path.relative_to(self.repo_root)),
                        "relative_path": rel_path,
                        "file_type": file_type,
                        "run_id": run_id,
                        "file_exists": exists,
                        "sha256": checksum,
                        "declared_not_verified": not exists,
                        "import_rule": "imported_dogfood_needs_path_checksum_validation",
                    },
                    created_at=_now_iso(),
                )
                self.result.store.add_node(node)

        self.result.log(phase, f"Processed {len(manifest_files)} manifest files")

    def _file_type_to_node_type(self, file_type: str) -> str:
        mapping = {
            "test": "TestArtifact",
            "test_result": "TestArtifact",
            "dogfood": "DogfoodArtifact",
            "example": "ExampleArtifact",
            "evidence": "EvidencePackage",
            "validation_result": "EvidencePackage",
        }
        return mapping.get(file_type, "EvidencePackage")

    # ── Supervisor reports: candidate StreamHandoff nodes ────────────────────

    def _import_supervisor_reports(self) -> None:
        phase = "Import_SupervisorReports"
        reports_dir = self.repo_root / "reports" / "supervisor"
        if not reports_dir.exists():
            self.result.log(phase, "reports/supervisor not found — skipping")
            return

        report_files = list(reports_dir.glob("*.md")) + list(reports_dir.glob("*.json"))
        count = 0
        for rf in sorted(report_files)[:20]:  # cap at 20 to avoid noise
            node_id = f"handoff:supervisor:{_slug(rf.stem)}"
            node = GraphNode(
                node_id=node_id,
                node_type="StreamHandoff",
                label=f"Supervisor report: {rf.name}",
                status="candidate",
                metadata={
                    "imported_from": str(rf.relative_to(self.repo_root)),
                    "declared_not_verified": True,
                    "import_rule": "imported_reports_are_candidates_not_truth",
                },
                created_at=_now_iso(),
            )
            self.result.store.add_node(node)
            count += 1

        self.result.log(phase, f"Imported {count} StreamHandoff candidates from supervisor reports")

    # ── YAML loading helper ──────────────────────────────────────────────────

    def _load_yaml(self, path: Path) -> Optional[Dict[str, Any]]:
        if not path.exists():
            return None
        try:
            if HAS_YAML:
                with open(path, encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            else:
                # Minimal JSON fallback (won't work for YAML, but keeps import from crashing)
                return {}
        except Exception:
            return None


def import_existing_state(repo_root: Path) -> ImportResult:
    """Convenience function: run full import and return result."""
    importer = EvidenceGraphImporter(repo_root)
    return importer.import_all()
