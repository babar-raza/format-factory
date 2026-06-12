"""compose_verify_loop.py — Refdev-style Compose/Verify Loop

Implements a safe, deterministic compose → verify → retry loop for
Format Factory test/feature generation. Operates in synthetic temp workspace
mode by default — no real product source is mutated.

Pattern source: refdev compose → compile → verify → retry feedback loop.
Adapter seam: future LLM generation is isolated behind a disabled stub boundary.

Sprint: FF-LIBFORGE-BROAD-IMPLEMENTATION-001 (v1)
        FF-LIBFORGE-GUARDED-AUTONOMOUS-EXPANSION-001 (v2: queue-shape + G3 scan, LFI-6-C)
Taskcard: LFI-3-D01 (v1), LFI-6-C (v2)
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

_REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class VerifyResult:
    """Result of a single verification attempt."""
    attempt: int
    ok: bool
    test_command: str
    test_exit_code: int
    stdout: str
    stderr: str
    log_path: Optional[str] = None
    error: Optional[str] = None


@dataclass
class ComposeResult:
    """Aggregate result of a ComposeVerifyLoop.run() call."""
    ok: bool
    attempts: int
    max_attempts: int
    generated_file: Optional[str] = None
    changed_files: List[str] = field(default_factory=list)
    test_command: Optional[str] = None
    test_exit_code: Optional[int] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    log_path: Optional[str] = None
    rollback_required: bool = False
    error: Optional[str] = None
    verify_history: List[VerifyResult] = field(default_factory=list)
    freeze_gate_result: Optional[Dict[str, Any]] = None
    # Queue-shape tracking fields (v2, LFI-6-C)
    queue_item_id: Optional[str] = None
    taskcard_id: Optional[str] = None
    target_format: Optional[str] = None
    dry_run: bool = False
    g3_safe: bool = True
    g3_scan_result: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # Replace VerifyResult dicts with plain dicts
        d["verify_history"] = [asdict(v) for v in self.verify_history]
        return d

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


class LLMBackendStub:
    """Disabled LLM adapter boundary. Not used in this sprint.

    This class exists as the seam for future refdev-style LLM-assisted
    composition. To activate, replace with a real adapter that:
      1. Accepts ComposeRequest (template + context)
      2. Calls an approved LLM endpoint
      3. Returns generated code string
      4. Is always followed by a deterministic verification gate
    """

    enabled = False

    def compose(self, template: str, context: Dict[str, Any]) -> str:
        raise NotImplementedError(
            "LLM backend is disabled. Set enabled=True and provide a real adapter."
        )


class ComposeVerifyLoop:
    """Run a deterministic compose → verify → retry loop.

    In synthetic mode (default):
    - Generates a test file in a temp directory using FeatureFactory templates
    - Runs verification via pytest (or a custom verifier)
    - Captures failure output for retry feedback
    - Never mutates real product source
    - Supports max_attempts retries

    Future LLM mode:
    - Replace the compose step with LLMBackendStub.compose()
    - All other logic remains identical
    """

    DEFAULT_MAX_ATTEMPTS = 3

    def __init__(
        self,
        repo_root: Optional[str] = None,
        python_executable: Optional[str] = None,
        llm_backend: Optional[LLMBackendStub] = None,
        freeze_gate_format_id: Optional[str] = None,
        freeze_gate_kinds: Optional[List[str]] = None,
    ):
        self._repo = Path(repo_root) if repo_root else _REPO_ROOT
        self._python = python_executable or sys.executable
        self._llm = llm_backend or LLMBackendStub()
        # Optional post-verify freeze gate hook (disabled by default)
        self._freeze_gate_format_id = freeze_gate_format_id
        self._freeze_gate_kinds = freeze_gate_kinds

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(
        self,
        feature_name: str,
        template_content: str,
        verify_command: Optional[str] = None,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
        workspace: Optional[str] = None,
        log_dir: Optional[str] = None,
        queue_item_id: Optional[str] = None,
        taskcard_id: Optional[str] = None,
        target_format: Optional[str] = None,
        dry_run: bool = False,
    ) -> ComposeResult:
        """Run compose → verify → retry loop.

        Args:
            feature_name: Name for the generated artifact (used for file naming)
            template_content: Python code to write as the generated artifact
            verify_command: Command to verify the generated artifact; if None,
                uses python syntax check only
            max_attempts: Maximum number of verify-and-retry cycles
            workspace: Directory to write the generated file; if None, uses temp dir
            log_dir: Directory to write log files; if None, uses workspace
            queue_item_id: Optional queue item ID for tracking (queue-shape, LFI-6-C)
            taskcard_id: Optional taskcard ID for tracking (queue-shape, LFI-6-C)
            target_format: Optional format ID being targeted (queue-shape, LFI-6-C)
            dry_run: If True, run G3 scan and return without writing files (LFI-6-C)

        Returns:
            ComposeResult with outcome and history
        """
        # G3 scan on generated code BEFORE writing (always, even in dry_run)
        g3_result, g3_safe = self._run_g3_scan(template_content, feature_name)

        if not g3_safe:
            return ComposeResult(
                ok=False,
                attempts=0,
                max_attempts=max_attempts,
                error=f"G3 scan FAIL: forbidden call detected in generated code for {feature_name}",
                rollback_required=False,
                queue_item_id=queue_item_id,
                taskcard_id=taskcard_id,
                target_format=target_format,
                dry_run=dry_run,
                g3_safe=False,
                g3_scan_result=g3_result,
            )

        if dry_run:
            return ComposeResult(
                ok=True,
                attempts=0,
                max_attempts=max_attempts,
                error=None,
                rollback_required=False,
                queue_item_id=queue_item_id,
                taskcard_id=taskcard_id,
                target_format=target_format,
                dry_run=True,
                g3_safe=True,
                g3_scan_result=g3_result,
            )

        # Set up workspace
        _tmp = None
        if workspace is None:
            _tmp = tempfile.mkdtemp(prefix=f"compose_verify_{feature_name}_")
            ws = Path(_tmp)
        else:
            ws = Path(workspace)
            ws.mkdir(parents=True, exist_ok=True)

        log_d = Path(log_dir) if log_dir else ws

        generated_path = ws / f"{feature_name}_generated.py"
        changed_files = []
        verify_history: List[VerifyResult] = []

        # Write generated artifact
        generated_path.write_text(template_content, encoding="utf-8")
        changed_files.append(str(generated_path))

        last_result: Optional[VerifyResult] = None

        for attempt in range(1, max_attempts + 1):
            result = self._verify(
                attempt=attempt,
                generated_path=generated_path,
                verify_command=verify_command,
                log_dir=log_d,
            )
            verify_history.append(result)
            last_result = result

            if result.ok:
                break

            # Future: feed result.stderr into LLM for retry repair
            # For now, deterministic: if first attempt fails, we cannot repair
            if not self._llm.enabled:
                break  # No LLM — don't loop uselessly

        ok = last_result.ok if last_result else False
        rollback = not ok and len(changed_files) > 0

        # Optional post-verify freeze gate hook
        gate_result_dict: Optional[Dict[str, Any]] = None
        if ok and self._freeze_gate_format_id:
            gate_result_dict = self._run_freeze_gate_hook()

        return ComposeResult(
            ok=ok,
            attempts=len(verify_history),
            max_attempts=max_attempts,
            generated_file=str(generated_path),
            changed_files=changed_files,
            test_command=last_result.test_command if last_result else None,
            test_exit_code=last_result.test_exit_code if last_result else None,
            stdout=last_result.stdout if last_result else None,
            stderr=last_result.stderr if last_result else None,
            log_path=last_result.log_path if last_result else None,
            rollback_required=rollback,
            verify_history=verify_history,
            freeze_gate_result=gate_result_dict,
            queue_item_id=queue_item_id,
            taskcard_id=taskcard_id,
            target_format=target_format,
            dry_run=False,
            g3_safe=True,
            g3_scan_result=g3_result,
        )

    def _run_g3_scan(
        self, source_code: str, feature_name: str
    ) -> tuple[Optional[Dict[str, Any]], bool]:
        """Run G3 AST forbidden-call scan on generated code.

        G3 gate only blocks on actual forbidden call findings. Parse errors
        (syntax errors) are NOT treated as G3 failures — they will be caught by
        the py_compile verification step. This preserves separation of concerns:
        G3 = dangerous calls gate; py_compile = syntax validity gate.

        Returns:
            (scan_result_dict, g3_safe) where g3_safe=True unless forbidden calls found.
        """
        try:
            sys.path.insert(0, str(self._repo))
            from tools.supervisor.ast_forbidden_scanner import scan_source
            result = scan_source(source_code, filename=f"{feature_name}_generated.py")
            # G3 safe = no forbidden call findings (parse errors pass through to compile step)
            g3_safe = len(result.findings) == 0
            return result.to_dict(), g3_safe
        except ImportError:
            # G3 scanner not available — treat as safe with warning
            return {"warning": "G3 scanner unavailable — not enforced"}, True

    def _run_freeze_gate_hook(self) -> Dict[str, Any]:
        """Run FreezeGateRunner as optional post-verify gate.

        Disabled by default — activated by setting freeze_gate_format_id in __init__.
        Uses synthetic mode (no fixture_path) for safety.
        """
        try:
            from tools.supervisor.freeze_gate_runner import FreezeGateRunner
        except ImportError:
            # Try relative import from same package
            import sys as _sys
            _sys.path.insert(0, str(self._repo))
            from tools.supervisor.freeze_gate_runner import FreezeGateRunner

        runner = FreezeGateRunner(repo_root=str(self._repo))
        report = runner.run(
            format_id=self._freeze_gate_format_id,
            gate_kinds=self._freeze_gate_kinds,
            run_id="compose-verify-post-gate",
        )
        return report.to_dict()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _verify(
        self,
        attempt: int,
        generated_path: Path,
        verify_command: Optional[str],
        log_dir: Path,
    ) -> VerifyResult:
        log_path = log_dir / f"verify_attempt_{attempt}.log"

        if verify_command is None:
            # Default: Python syntax check
            cmd = [self._python, "-m", "py_compile", str(generated_path)]
            cmd_str = " ".join(str(c) for c in cmd)
        else:
            cmd_str = verify_command
            cmd = verify_command.split()

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
            )
            stdout = proc.stdout
            stderr = proc.stderr
            exit_code = proc.returncode
        except subprocess.TimeoutExpired:
            msg = f"Verification command timed out after 60s: {cmd_str}"
            log_path.write_text(msg, encoding="utf-8")
            return VerifyResult(
                attempt=attempt,
                ok=False,
                test_command=cmd_str,
                test_exit_code=-1,
                stdout="",
                stderr=msg,
                log_path=str(log_path),
                error="timeout",
            )
        except Exception as exc:
            msg = f"Verification command failed to run: {exc}"
            log_path.write_text(msg, encoding="utf-8")
            return VerifyResult(
                attempt=attempt,
                ok=False,
                test_command=cmd_str,
                test_exit_code=-1,
                stdout="",
                stderr=str(exc),
                log_path=str(log_path),
                error=str(exc),
            )

        log_path.write_text(
            f"=== attempt {attempt} ===\n"
            f"command: {cmd_str}\n"
            f"exit_code: {exit_code}\n"
            f"--- stdout ---\n{stdout}\n"
            f"--- stderr ---\n{stderr}\n",
            encoding="utf-8",
        )

        return VerifyResult(
            attempt=attempt,
            ok=(exit_code == 0),
            test_command=cmd_str,
            test_exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            log_path=str(log_path),
        )
