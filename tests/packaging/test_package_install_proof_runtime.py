"""Regression tests for native and dotted-namespace package install proof."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_module(name: str, relative_path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / relative_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def builder() -> ModuleType:
    return _load_module(
        "ff_build_local_packages",
        "packaging/python/build-local-packages.py",
    )


@pytest.fixture
def proof(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    monkeypatch.syspath_prepend(str(REPO_ROOT / "tools" / "supervisor"))
    return _load_module("ff_run_package_install_proof", "tools/run_package_install_proof.py")


def test_ipynb_matrix_uses_native_dotted_distribution() -> None:
    matrix = yaml.safe_load(
        (REPO_ROOT / "packaging/python/package-matrix.yaml").read_text(encoding="utf-8")
    )
    ipynb = next(pkg for pkg in matrix["packages"] if pkg["format_id"] == "ipynb")

    assert ipynb["build_mode"] == "native_pyproject"
    assert ipynb["module_import"] == "format_factory.ipynb"
    assert ipynb["python_version"] == ">=3.11"
    assert ipynb["install_proof"]["smoke_module"] == "format_factory.ipynb"
    assert ipynb["local_dependencies"] == [
        {
            "package_name": "format-factory-core",
            "source_path": "src/python/core",
        }
    ]


def test_specs_preserve_dotted_module_import(
    proof: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(proof, "WORK_DIR", tmp_path)
    packages = [
        {
            "format_id": "ipynb",
            "package_name": "format-factory-ipynb",
            "module_import": "format_factory.ipynb",
            "install_proof": {
                "smoke_module": "format_factory.ipynb",
                "smoke_callable": "load_ipynb",
                "expected": "dict",
                "smoke_sample": "samples/minimal.ipynb",
            },
        }
    ]

    specs_path = proof.write_specs_json(packages, ["ipynb"])
    specs = json.loads(specs_path.read_text(encoding="utf-8"))

    assert specs["ipynb"]["module_import"] == "format_factory.ipynb"


def test_deep_import_results_map_back_to_format_id(
    proof: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(proof, "WORK_DIR", tmp_path)

    def fake_run(command: list[str], **_: object) -> SimpleNamespace:
        Path(command[-1]).write_text(
            json.dumps(
                {
                    "format_factory.ipynb": {
                        "total": 4,
                        "failed": 0,
                        "failing_modules": {},
                    }
                }
            ),
            encoding="utf-8",
        )
        return SimpleNamespace(returncode=0, stderr="")

    monkeypatch.setattr(proof, "run", fake_run)
    result = proof.deep_import_scan(
        Path("python"),
        {"ipynb": "format_factory.ipynb"},
        "deep.json",
    )

    assert result == {
        "ipynb": {"total": 4, "failed": 0, "failing_modules": {}}
    }


def test_changed_input_closure_aborts_without_recording(proof: ModuleType) -> None:
    with pytest.raises(SystemExit, match="PROOF_INPUT_CHANGED_DURING_RUN.*ipynb"):
        proof.assert_input_closure_unchanged(
            {"ipynb": "before", "nrrd": "stable"},
            {"ipynb": "after", "nrrd": "stable"},
        )


def test_package_proof_id_is_canonical_and_rejects_timestamps(
    proof: ModuleType,
) -> None:
    first = {"format": "ipynb", "wheel_sha256": "abc", "verdict": "PASS"}
    reordered = {"verdict": "PASS", "wheel_sha256": "abc", "format": "ipynb"}

    assert proof.package_proof_id(first) == proof.package_proof_id(reordered)
    assert proof.package_proof_id(first) != proof.package_proof_id(
        {**first, "wheel_sha256": "changed"}
    )
    with pytest.raises(ValueError, match="non-deterministic"):
        proof.package_proof_id({**first, "proved_at": "now"})


def test_manifest_serialization_is_canonical(
    proof: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    path = tmp_path / "manifest.json"
    monkeypatch.setattr(proof, "MANIFEST_PATH", path)
    proof.write_canonical_manifest({"z": 1, "formats": {"b": {}, "a": {}}})
    first = path.read_bytes()
    proof.write_canonical_manifest({"formats": {"a": {}, "b": {}}, "z": 1})

    assert path.read_bytes() == first
    assert first.endswith(b"\n")


def test_package_transcript_includes_generic_skill_receipt(
    proof: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(proof, "REPORT_DIR", tmp_path)
    entry = {
        "proof_id": "PACKAGE-PROOF-ABC",
        "package_name": "format-factory-ipynb",
        "version": "1.0",
        "wheel_file": "ipynb.whl",
        "wheel_sha256": "abc",
        "source_digest": "source",
        "proof_input_digest": "inputs",
        "local_dependencies": [],
        "install_result": "PASS",
        "import_result": "PASS",
        "module_import": "format_factory.ipynb",
        "smoke_result": "PASS",
        "smoke_test": "format_factory.ipynb.load",
        "verdict": "PASS",
    }
    proof.write_transcripts(
        {"formats": {"ipynb": entry}},
        ["ipynb"],
        "2026-07-25T00:00:00+00:00",
    )
    transcript = json.loads(
        (tmp_path / "transcripts/package-install-proof-ipynb.json").read_text(
            encoding="utf-8"
        )
    )

    assert transcript["mode"] == "live"
    assert transcript["inputs"] == {
        "format_id": "ipynb",
        "package_name": "format-factory-ipynb",
    }
    assert transcript["result"] == "PASS"
    assert transcript["actual_files_changed"] == transcript["allowed_files"]


def test_native_build_builds_local_dependencies_first(
    builder: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, str, str | None]] = []

    def fake_native(
        source_path: str,
        expected_name: str,
        version_override: str | None = None,
    ) -> dict:
        calls.append((source_path, expected_name, version_override))
        return {
            "package_name": expected_name,
            "version": "1.0",
            "status": "built",
            "artifacts": [],
        }

    monkeypatch.setattr(builder, "_build_native_project", fake_native)
    result = builder.build_package(
        {
            "build_mode": "native_pyproject",
            "source_path": "src/python/ipynb",
            "package_name": "format-factory-ipynb",
            "module_import": "format_factory.ipynb",
            "local_dependencies": [
                {
                    "source_path": "src/python/core",
                    "package_name": "format-factory-core",
                }
            ],
        }
    )

    assert calls == [
        ("src/python/core", "format-factory-core", None),
        ("src/python/ipynb", "format-factory-ipynb", None),
    ]
    assert result["module"] == "format_factory.ipynb"
    assert result["local_dependencies"][0]["package_name"] == "format-factory-core"


def test_legacy_staging_excludes_transient_generated_files(
    builder: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "source"
    module_root = source_root / "example"
    module_root.mkdir(parents=True)
    (module_root / "codec.py").write_text("VALUE = 1\n", encoding="utf-8")
    cache = module_root / "__pycache__"
    cache.mkdir()
    (cache / "codec.pyc").write_bytes(b"transient")
    (module_root / "build").mkdir()
    (module_root / "build" / "generated.txt").write_text("transient", encoding="utf-8")
    template = tmp_path / "template.toml"
    template.write_text(
        '[project]\nname="{{PACKAGE_NAME}}"\nversion="{{VERSION}}"\n'
        'description="{{DESCRIPTION}}"\ndependencies={{DEPENDENCIES}}\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(builder, "SRC_PYTHON", source_root)
    monkeypatch.setattr(builder, "BUILD_DIR", tmp_path / "build-output")
    monkeypatch.setattr(builder, "TEMPLATE", template)

    def fake_build(source_dir: Path, package_name: str, version: str) -> dict:
        staged = source_dir / "src/python/example"
        assert (staged / "codec.py").is_file()
        assert not (staged / "__pycache__").exists()
        assert not (staged / "build").exists()
        return {
            "package_name": package_name,
            "version": version,
            "status": "built",
            "artifacts": [],
        }

    monkeypatch.setattr(builder, "_build_source", fake_build)
    result = builder.build_package(
        {
            "module_import": "example",
            "package_name": "format-factory-example",
            "dependencies": [],
        }
    )

    assert result["status"] == "built"


def test_native_build_rejects_matrix_project_name_contradiction(
    builder: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "native"
    source.mkdir()
    (source / "pyproject.toml").write_text(
        '[project]\nname = "actual-name"\nversion = "1.2.3"\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(builder, "REPO_ROOT", tmp_path)

    with pytest.raises(ValueError, match="does not match"):
        builder._build_native_project("native", "wrong-name")


def test_build_source_removes_stale_wheels_before_build(
    builder: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "source"
    source.mkdir()
    monkeypatch.setattr(builder, "BUILD_DIR", tmp_path / "builds")
    dist = builder.BUILD_DIR / "example" / "dist"
    dist.mkdir(parents=True)
    stale = dist / "example-0.0.1-py3-none-any.whl"
    stale.write_bytes(b"stale")
    build_environment: dict[str, str] = {}
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "999999999")

    def fake_build(*_args: object, **kwargs: object) -> SimpleNamespace:
        build_environment.update(kwargs["env"])  # type: ignore[arg-type]
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(
        builder.subprocess,
        "run",
        fake_build,
    )

    result = builder._build_source(source, "example", "1.0.0")

    assert result["status"] == "built"
    assert not stale.exists()
    assert build_environment["SOURCE_DATE_EPOCH"] == "315532800"
