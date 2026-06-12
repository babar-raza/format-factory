"""Tests for G3 AST Forbidden-Call Scanner.

Sprint: FF-LIBFORGE-GOVERNANCE-UNBLOCK-IMPLEMENTATION-001
Taskcard: LFI-5-C
Gate: G3 (post-LLM deterministic safety gate)
Execution-method: AGENT_GOVERNED_DIRECT_EXECUTION
Route-decision-id: RD-AST-SCANNER-IMPL-001
Idempotency-key: lfi-5-c-ast-forbidden-scanner-v1
Exception-classification: investigation_only
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT))

from tools.supervisor.ast_forbidden_scanner import (
    FORBIDDEN_BUILTINS,
    FORBIDDEN_ATTR_CALLS,
    Finding,
    ScanResult,
    ScanReport,
    Severity,
    scan_source,
    scan_file,
    scan_directory,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _tmp_py(content: str) -> str:
    """Write content to a temp .py file and return its path."""
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
        f.write(content)
        return f.name


# ---------------------------------------------------------------------------
# Constants sanity
# ---------------------------------------------------------------------------


class TestConstants:
    def test_forbidden_builtins_has_eval_exec(self):
        assert "eval" in FORBIDDEN_BUILTINS
        assert "exec" in FORBIDDEN_BUILTINS

    def test_forbidden_attr_calls_has_os_system(self):
        assert ("os", "system") in FORBIDDEN_ATTR_CALLS

    def test_forbidden_attr_calls_has_subprocess_variants(self):
        assert ("subprocess", "run") in FORBIDDEN_ATTR_CALLS
        assert ("subprocess", "Popen") in FORBIDDEN_ATTR_CALLS
        assert ("subprocess", "call") in FORBIDDEN_ATTR_CALLS
        assert ("subprocess", "check_call") in FORBIDDEN_ATTR_CALLS
        assert ("subprocess", "check_output") in FORBIDDEN_ATTR_CALLS


# ---------------------------------------------------------------------------
# scan_source — safe code
# ---------------------------------------------------------------------------


class TestScanSourceSafe:
    def test_empty_file_is_safe(self):
        result = scan_source("")
        assert result.safe is True
        assert result.findings == []
        assert result.parse_error is None

    def test_clean_python_is_safe(self):
        code = """
import os
import subprocess

def add(a, b):
    return a + b

x = add(1, 2)
print(x)
"""
        result = scan_source(code, "clean.py")
        assert result.safe is True

    def test_print_is_not_forbidden(self):
        result = scan_source("print('hello')", "print.py")
        assert result.safe is True

    def test_import_subprocess_alone_is_safe(self):
        result = scan_source("import subprocess\nx = subprocess\n", "import.py")
        assert result.safe is True


# ---------------------------------------------------------------------------
# scan_source — forbidden built-ins
# ---------------------------------------------------------------------------


class TestScanSourceEval:
    def test_eval_detected(self):
        result = scan_source("x = eval('1+1')\n", "evil.py")
        assert not result.safe
        assert len(result.findings) == 1
        assert result.findings[0].symbol == "eval"
        assert result.findings[0].line == 1

    def test_eval_in_function_detected(self):
        code = """
def bad():
    return eval(input())
"""
        result = scan_source(code, "bad.py")
        assert not result.safe
        assert any(f.symbol == "eval" for f in result.findings)

    def test_exec_detected(self):
        result = scan_source("exec('x=1')\n", "exec.py")
        assert not result.safe
        assert result.findings[0].symbol == "exec"

    def test_severity_is_critical(self):
        result = scan_source("eval('x')\n", "x.py")
        assert result.findings[0].severity == Severity.CRITICAL.value


# ---------------------------------------------------------------------------
# scan_source — forbidden attribute calls
# ---------------------------------------------------------------------------


class TestScanSourceOsSystem:
    def test_os_system_detected(self):
        code = "import os\nos.system('rm -rf /')\n"
        result = scan_source(code, "os_sys.py")
        assert not result.safe
        assert result.findings[0].symbol == "os.system"

    def test_os_system_line_number_correct(self):
        code = "import os\n\n\nos.system('whoami')\n"
        result = scan_source(code, "x.py")
        assert result.findings[0].line == 4


class TestScanSourceSubprocess:
    def test_subprocess_run_detected(self):
        code = "import subprocess\nsubprocess.run(['ls'])\n"
        result = scan_source(code, "sp.py")
        assert not result.safe
        assert result.findings[0].symbol == "subprocess.run"

    def test_subprocess_popen_detected(self):
        code = "import subprocess\np = subprocess.Popen(['cmd'])\n"
        result = scan_source(code, "sp.py")
        assert not result.safe
        assert result.findings[0].symbol == "subprocess.Popen"

    def test_subprocess_call_detected(self):
        code = "import subprocess\nsubprocess.call(['ls'])\n"
        result = scan_source(code)
        assert not result.safe
        assert result.findings[0].symbol == "subprocess.call"

    def test_subprocess_check_call_detected(self):
        code = "import subprocess\nsubprocess.check_call(['ls'])\n"
        result = scan_source(code)
        assert not result.safe
        assert result.findings[0].symbol == "subprocess.check_call"

    def test_subprocess_check_output_detected(self):
        code = "import subprocess\nout = subprocess.check_output(['ls'])\n"
        result = scan_source(code)
        assert not result.safe
        assert result.findings[0].symbol == "subprocess.check_output"


# ---------------------------------------------------------------------------
# Multiple findings in one file
# ---------------------------------------------------------------------------


class TestMultipleFindings:
    def test_multiple_forbidden_calls_all_detected(self):
        code = """
import os
import subprocess
eval('x')
exec('y')
os.system('ls')
subprocess.run(['ls'])
"""
        result = scan_source(code, "multi.py")
        symbols = {f.symbol for f in result.findings}
        assert "eval" in symbols
        assert "exec" in symbols
        assert "os.system" in symbols
        assert "subprocess.run" in symbols
        assert len(result.findings) == 4


# ---------------------------------------------------------------------------
# Alias detection — v2 hardening (LFI-6-A)
# ---------------------------------------------------------------------------


class TestAliasedModuleImports:
    """v2: aliased module imports are now detected. Finding.symbol is canonical."""

    def test_subprocess_alias_run_detected(self):
        code = "import subprocess as sp\nsp.run(['ls'])\n"
        result = scan_source(code, "alias.py")
        assert not result.safe
        assert result.findings[0].symbol == "subprocess.run"

    def test_subprocess_alias_popen_detected(self):
        code = "import subprocess as sp\np = sp.Popen(['cmd'])\n"
        result = scan_source(code, "alias.py")
        assert not result.safe
        assert result.findings[0].symbol == "subprocess.Popen"

    def test_subprocess_alias_check_output_detected(self):
        code = "import subprocess as sp\nout = sp.check_output(['ls'])\n"
        result = scan_source(code, "alias.py")
        assert not result.safe
        assert result.findings[0].symbol == "subprocess.check_output"

    def test_os_alias_system_detected(self):
        code = "import os as operating\noperating.system('whoami')\n"
        result = scan_source(code, "alias.py")
        assert not result.safe
        assert result.findings[0].symbol == "os.system"

    def test_canonical_symbol_used_not_alias(self):
        """Finding.symbol is always the canonical form, not the alias."""
        code = "import subprocess as sp\nsp.run(['x'])\n"
        result = scan_source(code, "x.py")
        assert result.findings[0].symbol == "subprocess.run"

    def test_safe_aliased_module_no_forbidden_call(self):
        """Aliased module with non-forbidden attribute is safe."""
        code = "import subprocess as sp\nsp.DEVNULL\n"
        result = scan_source(code, "safe.py")
        assert result.safe


class TestFromImports:
    """v2: from-import patterns are now detected."""

    def test_from_subprocess_import_run_detected(self):
        code = "from subprocess import run\nrun(['ls'])\n"
        result = scan_source(code, "fi.py")
        assert not result.safe
        assert result.findings[0].symbol == "subprocess.run"

    def test_from_subprocess_import_popen_detected(self):
        code = "from subprocess import Popen\np = Popen(['cmd'])\n"
        result = scan_source(code, "fi.py")
        assert not result.safe
        assert result.findings[0].symbol == "subprocess.Popen"

    def test_from_subprocess_import_run_as_alias_detected(self):
        """from subprocess import run as execute → execute() detected."""
        code = "from subprocess import run as execute\nexecute(['ls'])\n"
        result = scan_source(code, "fi.py")
        assert not result.safe
        assert result.findings[0].symbol == "subprocess.run"

    def test_from_subprocess_import_check_output_detected(self):
        code = "from subprocess import check_output\nout = check_output(['ls'])\n"
        result = scan_source(code, "fi.py")
        assert not result.safe
        assert result.findings[0].symbol == "subprocess.check_output"

    def test_from_safe_module_safe(self):
        """from os import path is safe — not a forbidden call."""
        code = "from os import path\npath.join('/a', 'b')\n"
        result = scan_source(code, "safe.py")
        assert result.safe


# ---------------------------------------------------------------------------
# Syntax error handling
# ---------------------------------------------------------------------------


class TestSyntaxError:
    def test_syntax_error_handled_safely(self):
        code = "def broken(\n    x\n# missing close paren\n"
        result = scan_source(code, "broken.py")
        assert result.parse_error is not None
        assert "SyntaxError" in result.parse_error
        assert result.findings == []
        assert result.safe is False

    def test_syntax_error_does_not_raise(self):
        """Scanner never raises on syntax errors."""
        code = "def (broken syntax here"
        result = scan_source(code)
        assert result.parse_error is not None


# ---------------------------------------------------------------------------
# scan_file
# ---------------------------------------------------------------------------


class TestScanFile:
    def test_safe_file_passes(self):
        path = _tmp_py("x = 1 + 2\nprint(x)\n")
        result = scan_file(path)
        assert result.safe is True

    def test_forbidden_file_detected(self):
        path = _tmp_py("import os\nos.system('cmd')\n")
        result = scan_file(path)
        assert not result.safe
        assert result.findings[0].symbol == "os.system"

    def test_missing_file_handled(self):
        result = scan_file("/nonexistent/path/file.py")
        assert result.scanned is False
        assert result.parse_error is not None
        assert "IOError" in result.parse_error


# ---------------------------------------------------------------------------
# scan_directory
# ---------------------------------------------------------------------------


class TestScanDirectory:
    def test_empty_directory_passes(self, tmp_path):
        report = scan_directory(tmp_path)
        assert report.verdict == "PASS"
        assert report.files_scanned == 0
        assert report.overall_safe is True

    def test_directory_with_safe_files_passes(self, tmp_path):
        (tmp_path / "a.py").write_text("x = 1\n")
        (tmp_path / "b.py").write_text("y = 2\n")
        report = scan_directory(tmp_path)
        assert report.verdict == "PASS"
        assert report.files_scanned == 2

    def test_directory_with_forbidden_file_fails(self, tmp_path):
        (tmp_path / "safe.py").write_text("x = 1\n")
        (tmp_path / "bad.py").write_text("eval('x')\n")
        report = scan_directory(tmp_path)
        assert report.verdict == "FAIL"
        assert report.files_with_findings == 1
        assert report.total_findings == 1

    def test_recursive_scan_finds_nested(self, tmp_path):
        subdir = tmp_path / "sub"
        subdir.mkdir()
        (subdir / "evil.py").write_text("exec('bad')\n")
        report = scan_directory(tmp_path, recursive=True)
        assert report.verdict == "FAIL"
        assert report.total_findings >= 1

    def test_non_recursive_misses_nested(self, tmp_path):
        subdir = tmp_path / "sub"
        subdir.mkdir()
        (subdir / "evil.py").write_text("exec('bad')\n")
        report = scan_directory(tmp_path, recursive=False)
        # No .py files in root, subdir is not scanned
        assert report.verdict == "PASS"
        assert report.files_scanned == 0


# ---------------------------------------------------------------------------
# JSON serialization
# ---------------------------------------------------------------------------


class TestJsonSerialization:
    def test_finding_is_json_serializable(self):
        f = Finding(file="x.py", line=1, col=0, symbol="eval",
                    severity=Severity.CRITICAL.value, description="Forbidden")
        parsed = json.loads(f.to_json())
        assert parsed["symbol"] == "eval"

    def test_scan_result_is_json_serializable(self):
        result = scan_source("eval('x')\n", "x.py")
        parsed = json.loads(result.to_json())
        assert parsed["safe"] is False
        assert len(parsed["findings"]) == 1

    def test_scan_report_is_json_serializable(self, tmp_path):
        (tmp_path / "a.py").write_text("eval('x')\n")
        report = scan_directory(tmp_path)
        parsed = json.loads(report.to_json())
        assert parsed["verdict"] == "FAIL"
        assert "results" in parsed

    def test_safe_report_json_correct(self, tmp_path):
        (tmp_path / "clean.py").write_text("x = 1\n")
        report = scan_directory(tmp_path)
        parsed = json.loads(report.to_json())
        assert parsed["verdict"] == "PASS"
        assert parsed["overall_safe"] is True
