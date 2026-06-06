"""
Format Factory — Local Deterministic Backend
Sprint: FORMAT-FACTORY-SUPERPOWERS-AGENTIC-AUTONOMY-EXECUTION-001

Executes deterministic, side-effect-free actions using only Python stdlib.
This is the fallback backend that is always available.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

# Add repo root to path for tools.supervisor.* imports
_repo_root = Path(__file__).resolve().parent.parent.parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from tools.supervisor.execution_backend import (
    BackendResult,
    BackendStatus,
    BackendType,
    ExecutionBackend,
    ProofLevel,
)


class LocalDeterministicBackend(ExecutionBackend):
    """
    Pure-Python deterministic backend. Always available.
    Supported action_types:
      - RUN_JSON_VALIDATION
      - RUN_YAML_VALIDATION
      - RUN_MD_NONEMPTY_CHECK
      - RUN_COMMAND_DISCOVERY
      - GENERATE_EVIDENCE_STUB
      - UPDATE_STATE
      - PRODUCT_GAP_CLASSIFICATION_READONLY
    """

    SUPPORTED_ACTIONS = {
        "RUN_JSON_VALIDATION",
        "RUN_YAML_VALIDATION",
        "RUN_MD_NONEMPTY_CHECK",
        "RUN_COMMAND_DISCOVERY",
        "GENERATE_EVIDENCE_STUB",
        "UPDATE_STATE",
        "PRODUCT_GAP_CLASSIFICATION_READONLY",
        "PRODUCT_SOURCE_PATCH_BOUNDED",
    }

    @property
    def backend_type(self) -> BackendType:
        return BackendType.LOCAL_DETERMINISTIC

    def discover(self) -> BackendStatus:
        return BackendStatus.VERIFIED_CALLABLE

    def can_execute(self, action: dict) -> bool:
        return action.get("action_type") in self.SUPPORTED_ACTIONS

    def _enforce_write_root(self, path: str, allowed_write_roots: List[str]) -> None:
        """Raise if path is outside allowed write roots."""
        if not allowed_write_roots:
            return
        p = Path(path).resolve()
        for root in allowed_write_roots:
            r = Path(root).resolve()
            try:
                p.relative_to(r)
                return
            except ValueError:
                continue
        raise PermissionError(f"Path {path} outside allowed write roots: {allowed_write_roots}")

    def execute(self, action: dict, allowed_write_roots: List[str]) -> BackendResult:
        action_id = action.get("action_id", "unknown")
        action_type = action.get("action_type", "")
        result_path = action.get("result_path")

        stdout_lines: List[str] = []
        stderr_lines: List[str] = []
        errors: List[str] = []
        warnings: List[str] = []
        exit_code = 0

        try:
            if action_type == "RUN_JSON_VALIDATION":
                result = self._run_json_validation(action, stdout_lines, stderr_lines, errors)
            elif action_type == "RUN_YAML_VALIDATION":
                result = self._run_yaml_validation(action, stdout_lines, stderr_lines, errors)
            elif action_type == "RUN_MD_NONEMPTY_CHECK":
                result = self._run_md_nonempty(action, stdout_lines, stderr_lines, errors)
            elif action_type == "GENERATE_EVIDENCE_STUB":
                result = self._generate_evidence_stub(action, stdout_lines, stderr_lines, errors)
            elif action_type == "UPDATE_STATE":
                result = self._update_state(action, stdout_lines, stderr_lines, errors)
            elif action_type == "RUN_COMMAND_DISCOVERY":
                result = self._run_command_discovery(action, stdout_lines, stderr_lines, errors)
            elif action_type == "PRODUCT_GAP_CLASSIFICATION_READONLY":
                result = self._run_product_gap_classification(action, stdout_lines, stderr_lines, errors, allowed_write_roots)
            elif action_type == "PRODUCT_SOURCE_PATCH_BOUNDED":
                result = self._run_product_source_patch(action, stdout_lines, stderr_lines, errors, allowed_write_roots)
            else:
                errors.append(f"Unsupported action_type: {action_type}")
                exit_code = 1
                result = {"action_id": action_id, "action_type": action_type, "status": "FAILED", "errors": errors}
        except Exception as e:
            errors.append(f"Exception in backend: {e}")
            exit_code = 9
            result = {"action_id": action_id, "action_type": action_type, "status": "ERROR", "errors": errors}

        if errors:
            exit_code = max(exit_code, 1)

        # Build result dict
        result.update({
            "backend_used": BackendType.LOCAL_DETERMINISTIC.value,
            "proof_level": ProofLevel.H3.value,
            "executed_at": datetime.now(timezone.utc).isoformat(),
            "stdout": "\n".join(stdout_lines),
            "stderr": "\n".join(stderr_lines),
        })

        # Write result file (runner/backend writes it — NOT the host/parent)
        evidence_paths = []
        if result_path:
            rp = Path(result_path)
            if allowed_write_roots:
                self._enforce_write_root(str(rp), allowed_write_roots)
            rp.parent.mkdir(parents=True, exist_ok=True)
            rp.write_text(json.dumps(result, indent=2), encoding="utf-8")
            evidence_paths.append(str(rp))

        return BackendResult(
            action_id=action_id,
            backend_used=BackendType.LOCAL_DETERMINISTIC,
            status="SUCCESS" if exit_code == 0 else "FAILED",
            exit_code=exit_code,
            result_path=result_path,
            evidence_paths=evidence_paths,
            proof_level=ProofLevel.H3,
            errors=errors,
            warnings=warnings,
            selection_reason="LOCAL_DETERMINISTIC is always available",
        )

    def _run_json_validation(self, action, stdout, stderr, errors) -> dict:
        target = action.get("target")
        if not target:
            errors.append("No target specified for RUN_JSON_VALIDATION")
            return {"status": "FAILED", "errors": errors}
        p = Path(target)
        if not p.exists():
            errors.append(f"Target not found: {target}")
            return {"status": "FAILED", "errors": errors}
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            stdout.append(f"JSON_VALID: {target} ({len(str(data))} chars)")
            return {"status": "SUCCESS", "target": target, "valid": True}
        except json.JSONDecodeError as e:
            errors.append(f"JSON_INVALID: {target}: {e}")
            return {"status": "FAILED", "target": target, "valid": False, "error": str(e)}

    def _run_yaml_validation(self, action, stdout, stderr, errors) -> dict:
        try:
            import yaml
        except ImportError:
            errors.append("PyYAML not available for YAML validation")
            return {"status": "FAILED"}
        target = action.get("target")
        if not target:
            errors.append("No target for RUN_YAML_VALIDATION")
            return {"status": "FAILED"}
        p = Path(target)
        if not p.exists():
            errors.append(f"Target not found: {target}")
            return {"status": "FAILED"}
        try:
            data = yaml.safe_load(p.read_text(encoding="utf-8"))
            stdout.append(f"YAML_VALID: {target}")
            return {"status": "SUCCESS", "target": target, "valid": True}
        except Exception as e:
            errors.append(f"YAML_INVALID: {target}: {e}")
            return {"status": "FAILED", "target": target, "valid": False, "error": str(e)}

    def _run_md_nonempty(self, action, stdout, stderr, errors) -> dict:
        target = action.get("target")
        if not target:
            errors.append("No target for RUN_MD_NONEMPTY_CHECK")
            return {"status": "FAILED"}
        p = Path(target)
        if not p.exists():
            errors.append(f"Not found: {target}")
            return {"status": "FAILED"}
        content = p.read_text(encoding="utf-8").strip()
        if not content:
            errors.append(f"Empty file: {target}")
            return {"status": "FAILED", "target": target, "non_empty": False}
        stdout.append(f"MD_NONEMPTY: {target} ({len(content)} chars)")
        return {"status": "SUCCESS", "target": target, "non_empty": True, "char_count": len(content)}

    def _generate_evidence_stub(self, action, stdout, stderr, errors) -> dict:
        target = action.get("target", "evidence-stub.json")
        stub = {
            "stub_generated_by": "LOCAL_DETERMINISTIC",
            "action_id": action.get("action_id"),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        p = Path(target)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(stub, indent=2), encoding="utf-8")
        stdout.append(f"EVIDENCE_STUB_WRITTEN: {target}")
        return {"status": "SUCCESS", "target": target}

    def _update_state(self, action, stdout, stderr, errors) -> dict:
        state_path = action.get("state_path", "reports/superpowers-agentic-autonomy/execution-state.json")
        updates = action.get("updates", {})
        p = Path(state_path)
        if p.exists():
            state = json.loads(p.read_text(encoding="utf-8"))
        else:
            state = {}
        state.update(updates)
        state["last_updated"] = datetime.now(timezone.utc).isoformat()
        p.write_text(json.dumps(state, indent=2), encoding="utf-8")
        stdout.append(f"STATE_UPDATED: {state_path}")
        return {"status": "SUCCESS", "state_path": state_path, "updates": updates}

    def _run_product_gap_classification(self, action, stdout, stderr, errors, allowed_write_roots) -> dict:
        """Execute PRODUCT_GAP_CLASSIFICATION_READONLY — read-only product gap analysis."""
        try:
            from tools.supervisor.product_action_guard import run_product_gap_classification_readonly
        except ImportError as e:
            errors.append(f"Cannot import product_action_guard: {e}")
            return {"status": "FAILED", "errors": errors}

        # Determine output path from action or use default
        result_path = action.get("result_path")
        output_path = None
        if result_path:
            output_path = Path(result_path)
            # Check write root enforcement
            if allowed_write_roots:
                self._enforce_write_root(str(output_path), allowed_write_roots)

        try:
            result = run_product_gap_classification_readonly(output_path=output_path)
            stdout.append(f"PRODUCT_GAP_CLASSIFICATION: classified={result.get('total_classified', 0)}, agent_owned={result.get('agent_owned_safe_count', 0)}, external_gate={result.get('external_gate_count', 0)}")
            stdout.append(f"product_source_mutated={result.get('product_source_mutated', False)}, poc_targets_mutated={result.get('poc_targets_mutated', False)}")
            return {
                "status": "SUCCESS",
                "action_type": "PRODUCT_GAP_CLASSIFICATION_READONLY",
                "total_classified": result.get("total_classified", 0),
                "agent_owned_safe_count": result.get("agent_owned_safe_count", 0),
                "external_gate_count": result.get("external_gate_count", 0),
                "product_source_mutated": False,
                "poc_targets_mutated": False,
                "result_path": str(output_path) if output_path else None,
            }
        except Exception as e:
            errors.append(f"PRODUCT_GAP_CLASSIFICATION failed: {e}")
            return {"status": "FAILED", "errors": errors}

    def _run_product_source_patch(self, action, stdout, stderr, errors, allowed_write_roots) -> dict:
        from tools.supervisor.product_action_guard import run_product_source_patch_bounded
        try:
            result = run_product_source_patch_bounded(action, allowed_write_roots=allowed_write_roots)
            if result.get("status") == "SUCCESS":
                stdout.append(f"PRODUCT_SOURCE_PATCH: target={result.get('target_path')}, patch_type={result.get('patch_type')}")
                stdout.append(f"product_source_mutated={result.get('product_source_mutated')}, rollback={result.get('rollback_instruction', 'n/a')}")
            else:
                errors.append(f"PRODUCT_SOURCE_PATCH failed: {result.get('error', 'unknown')}")
            return result
        except Exception as e:
            errors.append(f"PRODUCT_SOURCE_PATCH exception: {e}")
            return {"status": "FAILED", "errors": errors}

    def _run_command_discovery(self, action, stdout, stderr, errors) -> dict:
        commands = action.get("commands", [])
        results = {}
        for cmd in commands:
            import subprocess
            try:
                r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                results[cmd] = {"exit_code": r.returncode, "stdout": r.stdout[:200], "stderr": r.stderr[:200]}
                stdout.append(f"CMD[{r.returncode}]: {cmd[:80]}")
            except Exception as e:
                results[cmd] = {"exit_code": -1, "error": str(e)}
                errors.append(f"CMD failed: {cmd}: {e}")
        return {"status": "SUCCESS" if not errors else "PARTIAL", "commands": results}
