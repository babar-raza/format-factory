"""Isolated mutation-testing lab.

`mutation_tester.py` mutates its target **in place** and restores it afterwards.
That is fine for a two-minute run in the foreground. It is not fine for a
whole-package campaign, which takes hours: the campaign would be rewriting files
in the live working tree the whole time, so any concurrent `git add` could stage
a mutated source file, and a crash or kill would leave one on disk.

This module copies the package and its tests into a throwaway directory and runs
the campaign there, so the live tree is never written to.

Getting the copy is the easy half. The hard half is that the editable install
binds ``format_factory.ipynb`` to an absolute path in the live tree through a
``sys.meta_path`` finder, which takes priority over ``sys.path``. A lab that
copied the files but still imported the originals would report kill rates for
source it never mutated -- every mutation would "survive" or, worse, the numbers
would look plausible and mean nothing. So the lab writes a ``conftest.py`` that
drops those finders, and then *proves* the redirection worked before running any
campaign: it breaks a function in the lab copy and requires the lab suite to
notice. If the lab is still importing the live tree, that check fails and the
campaign refuses to start.

Usage:
    python tools/certification/mutation_lab.py --package ipynb \
        --output reports/certification/ipynb/mutation-campaign
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MUTATION_TESTER = REPO_ROOT / "tools" / "certification" / "mutation_tester.py"

# The lab conftest runs before any test module imports format_factory, which is
# the only moment the editable finders can still be removed cleanly.
LAB_CONFTEST = '''"""Lab isolation -- redirect format_factory.{core,PACKAGE} to this tree.

Written by tools/certification/mutation_lab.py. The editable install registers
sys.meta_path finders pinned to absolute paths in the live working tree, and
meta_path beats sys.path, so removing them is the only way a copied tree gets
imported. tools/certification/mutation_lab.py proves this worked before running
a campaign -- see its `--verify-only` mode.
"""

import sys
from pathlib import Path

_LAB_ROOT = Path(__file__).resolve().parent
_REDIRECTED = ("ipynb", "core", "ora", "nrrd", "xliff", "safetensors", "ubl")


def _drop_editable_finders() -> list[str]:
    dropped = []
    keep = []
    for finder in sys.meta_path:
        module = getattr(type(finder), "__module__", "") or ""
        if module.startswith("__editable___format_factory_") and any(
            f"_format_factory_{name}_" in module for name in _REDIRECTED
        ):
            dropped.append(module)
            continue
        keep.append(finder)
    sys.meta_path[:] = keep
    return dropped


DROPPED_FINDERS = _drop_editable_finders()

for _candidate in sorted((_LAB_ROOT / "src" / "python").glob("*/src")):
    _path = str(_candidate)
    if _path not in sys.path:
        sys.path.insert(0, _path)
'''

LAB_PYTEST_INI = """[pytest]
testpaths = tests
addopts = -q --no-header
filterwarnings =
    ignore::DeprecationWarning
"""


def build_lab(package: str, lab_root: Path) -> Path:
    """Copy the package, format-factory-core and the test estate into `lab_root`."""
    if lab_root.exists():
        shutil.rmtree(lab_root)
    lab_root.mkdir(parents=True)

    def _ignore(_directory: str, names: list[str]) -> set[str]:
        return {
            name
            for name in names
            if name in {"__pycache__", "build", "dist", ".ruff_cache", ".mypy_cache"}
            or name.endswith(".egg-info")
        }

    for source_package in (package, "core"):
        source = REPO_ROOT / "src" / "python" / source_package
        if not source.is_dir():
            raise SystemExit(f"no such package source: {source}")
        shutil.copytree(source, lab_root / "src" / "python" / source_package, ignore=_ignore)

    tests_source = REPO_ROOT / "tests" / "python" / package
    if not tests_source.is_dir():
        raise SystemExit(f"no such test estate: {tests_source}")
    shutil.copytree(tests_source, lab_root / "tests" / "python" / package, ignore=_ignore)

    for conftest in (Path("tests/conftest.py"), Path("tests/python/conftest.py")):
        shutil.copy2(REPO_ROOT / conftest, lab_root / conftest)

    # Tests resolve corpora and registries relative to the repo root they are
    # copied into, so the lab needs those trees too or the suite fails before a
    # single mutation is applied.
    for resource in (
        Path("samples/by-format") / package,
        Path("shared/qname-registry"),
        Path("shared/format-contracts"),
        Path("oracle/formats") / package,
    ):
        source = REPO_ROOT / resource
        if source.is_dir():
            shutil.copytree(source, lab_root / resource, ignore=_ignore)

    (lab_root / "conftest.py").write_text(
        LAB_CONFTEST.replace("PACKAGE", package), encoding="utf-8"
    )
    (lab_root / "pytest.ini").write_text(LAB_PYTEST_INI, encoding="utf-8")
    return lab_root


def _pytest(
    lab_root: Path,
    target: str,
    deselect: tuple[str, ...] = (),
    timeout: int = 600,
) -> subprocess.CompletedProcess:
    command = [str(REPO_ROOT / ".venv" / "Scripts" / "pytest.exe"), target, "-x", "-q", "--tb=line"]
    for selector in deselect:
        command += ["--deselect", selector]
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(lab_root),
    )


def verify_isolation(package: str, lab_root: Path, deselect: tuple[str, ...] = ()) -> dict:
    """Prove the lab imports the *lab's* source, not the live tree.

    A campaign whose lab silently imported the originals would produce kill rates
    for source it never touched. This is the control that makes the campaign's
    numbers mean something, so a failure here is fatal rather than advisory.
    """
    lab_tests = lab_root / "tests" / "python" / package
    baseline = _pytest(lab_root, str(lab_tests), deselect)
    if baseline.returncode != 0:
        return {
            "isolated": False,
            "reason": "lab suite does not pass before any mutation is applied",
            "stdout_tail": baseline.stdout[-2000:],
        }

    # Break the lab copy in a way no correct suite can miss: make the package's
    # public loads() raise. If the live tree is being imported instead, the suite
    # keeps passing and the lab is not isolated.
    package_init = lab_root / "src" / "python" / package / "src" / "format_factory" / package / "__init__.py"
    live_init = REPO_ROOT / "src" / "python" / package / "src" / "format_factory" / package / "__init__.py"
    original_lab = package_init.read_text(encoding="utf-8")
    live_before = live_init.read_bytes()

    sabotage = original_lab + (
        "\n\n_MUTATION_LAB_ISOLATION_PROBE = True\n"
        "\n\ndef loads(*args, **kwargs):  # noqa: F811\n"
        "    raise RuntimeError('mutation lab isolation probe')\n"
    )
    package_init.write_text(sabotage, encoding="utf-8")
    try:
        sabotaged = _pytest(lab_root, str(lab_tests), deselect)
    finally:
        package_init.write_text(original_lab, encoding="utf-8")

    live_after = live_init.read_bytes()
    live_untouched = live_before == live_after

    return {
        "isolated": sabotaged.returncode != 0 and live_untouched,
        "lab_suite_passes_clean": True,
        "lab_suite_fails_when_lab_source_is_broken": sabotaged.returncode != 0,
        "live_tree_byte_identical_after_probe": live_untouched,
        "reason": (
            None
            if sabotaged.returncode != 0 and live_untouched
            else "lab did not observe its own broken source -- imports are resolving elsewhere"
        ),
    }


def campaign(
    package: str,
    lab_root: Path,
    output_dir: Path,
    max_mutations: int,
    module_timeout: int,
    deselect: tuple[str, ...] = (),
) -> dict:
    """Run mutation testing over every module of the package inside the lab."""
    source_root = lab_root / "src" / "python" / package / "src" / "format_factory" / package
    lab_tests = lab_root / "tests" / "python" / package
    modules = sorted(
        path
        for path in source_root.rglob("*.py")
        if "__pycache__" not in path.parts and path.stat().st_size > 0
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict] = []
    started = time.time()

    for index, module in enumerate(modules, start=1):
        relative = module.relative_to(source_root).as_posix()
        slug = relative.replace("/", "__").removesuffix(".py")
        per_module = output_dir / f"{slug}.json"
        print(f"[{index}/{len(modules)}] {relative}", flush=True)
        module_started = time.time()
        command = [
            sys.executable,
            str(MUTATION_TESTER),
            "--target",
            str(module),
            "--tests",
            str(lab_tests),
            "--output",
            str(per_module),
            "--max-mutations",
            str(max_mutations),
        ]
        for selector in deselect:
            command += ["--deselect", selector]
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=module_timeout,
                cwd=str(lab_root),
            )
            status = "ok" if completed.returncode == 0 else "tester_failed"
            detail = completed.stderr[-1000:] if completed.returncode else None
        except subprocess.TimeoutExpired:
            status = "timeout"
            detail = f"exceeded {module_timeout}s"

        entry: dict = {
            "module": relative,
            "status": status,
            "seconds": round(time.time() - module_started, 1),
        }
        if detail:
            entry["detail"] = detail
        if per_module.exists():
            payload = json.loads(per_module.read_text(encoding="utf-8"))
            entry.update(
                {
                    "total_mutations": payload.get("total_mutations"),
                    "killed": payload.get("killed"),
                    "survived": payload.get("survived"),
                    "errors": payload.get("errors"),
                    "kill_rate_pct": payload.get("kill_rate_pct"),
                    "verdict": payload.get("verdict"),
                    "survivors": payload.get("survivors", []),
                }
            )
        results.append(entry)
        print(f"    -> {status} in {entry['seconds']}s", flush=True)

    scored = [entry for entry in results if entry.get("total_mutations")]
    killed = sum(entry.get("killed", 0) for entry in scored)
    survived = sum(entry.get("survived", 0) for entry in scored)
    total = killed + survived
    return {
        "package": package,
        "modules_discovered": len(modules),
        "modules_scored": len(scored),
        "modules_timed_out": sum(1 for entry in results if entry["status"] == "timeout"),
        "modules_tester_failed": sum(1 for entry in results if entry["status"] == "tester_failed"),
        "mutations_tested": total,
        "killed": killed,
        "survived": survived,
        "kill_rate_pct": round(killed / total * 100, 1) if total else None,
        "wall_seconds": round(time.time() - started, 1),
        "modules": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", required=True, help="format package name, e.g. ipynb")
    parser.add_argument("--lab-root", help="where to build the lab (default: a temp dir)")
    parser.add_argument("--output", required=True, help="directory for per-module JSON results")
    parser.add_argument("--max-mutations", type=int, default=25)
    parser.add_argument("--module-timeout", type=int, default=1800)
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="build the lab and prove isolation, then stop without running a campaign",
    )
    parser.add_argument(
        "--reuse-lab",
        action="store_true",
        help="do not rebuild the lab if it already exists",
    )
    parser.add_argument(
        "--deselect",
        action="append",
        default=[],
        help=(
            "pytest --deselect selector for a test that fails on pristine source for "
            "environmental reasons (install residency, packaging layout) and so cannot "
            "kill a mutation. Repeatable. Never use it to silence a behavioural failure, "
            "and record every use in the gate document."
        ),
    )
    arguments = parser.parse_args()
    deselect = tuple(arguments.deselect)

    lab_root = (
        Path(arguments.lab_root).resolve()
        if arguments.lab_root
        else REPO_ROOT / ".local" / "mutation-lab" / arguments.package
    )
    output_dir = Path(arguments.output)
    if not output_dir.is_absolute():
        output_dir = REPO_ROOT / output_dir

    if not (arguments.reuse_lab and lab_root.exists()):
        print(f"building lab at {lab_root}", flush=True)
        build_lab(arguments.package, lab_root)

    print("verifying isolation", flush=True)
    isolation = verify_isolation(arguments.package, lab_root, deselect)
    isolation["deselected"] = list(deselect)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "isolation-control.json").write_text(
        json.dumps(isolation, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(isolation, indent=2), flush=True)
    if not isolation["isolated"]:
        print("ISOLATION NOT PROVEN -- refusing to run a campaign", file=sys.stderr)
        return 2
    if arguments.verify_only:
        return 0

    summary = campaign(
        arguments.package,
        lab_root,
        output_dir,
        arguments.max_mutations,
        arguments.module_timeout,
        deselect,
    )
    summary["deselected"] = list(deselect)
    summary["isolation_control"] = isolation
    (output_dir / "campaign-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({k: v for k, v in summary.items() if k != "modules"}, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
