"""Deterministic filesystem and serialization primitives for FF6 compilation."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

import yaml


class UniverseError(ValueError):
    """The capability universe is incomplete, contradictory, or drifting."""


@dataclass(frozen=True)
class UniverseCompilation:
    """Immutable in-memory result of one capability-universe compilation."""

    outputs: Mapping[str, bytes]
    manifest: Mapping[str, Any]


def canonical_json(value: Any) -> bytes:
    """Serialize a value without time, path, identity, or ordering noise."""

    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def sha256(data: bytes) -> str:
    """Return a lowercase SHA-256 digest."""

    return hashlib.sha256(data).hexdigest()


def yaml_bytes(value: Any) -> bytes:
    """Serialize canonical repository YAML using stable ordering supplied by callers."""

    return yaml.safe_dump(
        value,
        sort_keys=False,
        allow_unicode=True,
        width=1000,
        default_flow_style=False,
    ).replace("\r\n", "\n").encode("utf-8")


def safe_path(root: Path, relative: Path) -> Path:
    """Resolve a repository-relative path and reject traversal or absolute paths."""

    if relative.is_absolute():
        raise UniverseError(f"absolute path is forbidden: {relative}")
    resolved_root = root.resolve()
    resolved = (resolved_root / relative).resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise UniverseError(f"path escapes repository root: {relative}") from exc
    return resolved


def load_yaml(root: Path, relative: Path) -> tuple[dict[str, Any], bytes]:
    """Load a required YAML mapping and retain its exact source bytes."""

    path = safe_path(root, relative)
    if not path.is_file():
        raise UniverseError(f"required input is missing: {relative.as_posix()}")
    raw = path.read_bytes()
    value = yaml.safe_load(raw) or {}
    if not isinstance(value, dict):
        raise UniverseError(f"expected YAML mapping: {relative.as_posix()}")
    return value, raw


def add_input_digest(
    root: Path, relative: Path, input_digests: dict[str, str]
) -> dict[str, str]:
    """Bind one required repository input into the compilation closure."""

    path = safe_path(root, relative)
    if not path.is_file():
        raise UniverseError(f"required input is missing: {relative.as_posix()}")
    digest = sha256(path.read_bytes())
    key = relative.as_posix()
    input_digests[key] = digest
    return {"path": key, "sha256": digest}


def write_outputs(output_dir: Path, outputs: Mapping[str, bytes]) -> None:
    """Atomically replace every compiled output without deleting unrelated files."""

    root = output_dir.resolve()
    root.mkdir(parents=True, exist_ok=True)
    for relative, data in sorted(outputs.items()):
        target = safe_path(root, Path(relative))
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name(f".{target.name}.tmp")
        temporary.write_bytes(data)
        os.replace(temporary, target)


def check_outputs(output_dir: Path, outputs: Mapping[str, bytes]) -> None:
    """Fail if any expected output is missing or byte-different; never write."""

    root = output_dir.resolve()
    drift: list[str] = []
    for relative, expected in sorted(outputs.items()):
        target = safe_path(root, Path(relative))
        if not target.is_file() or target.read_bytes() != expected:
            drift.append(relative)
    if drift:
        raise UniverseError(f"output drift: {', '.join(drift)}")


def validate_outputs(schema_path: Path, outputs: Mapping[str, bytes]) -> None:
    """Validate every compiled document against one versioned JSON Schema."""

    import jsonschema

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    validator = jsonschema.Draft202012Validator(schema)
    failures: list[str] = []
    for relative, data in sorted(outputs.items()):
        if relative.endswith(".json"):
            document = json.loads(data)
        else:
            document = yaml.safe_load(data)
        errors = sorted(validator.iter_errors(document), key=lambda error: list(error.path))
        for error in errors[:5]:
            location = "/".join(str(item) for item in error.absolute_path) or "<root>"
            failures.append(f"{relative}:{location}: {error.message}")
    if failures:
        raise UniverseError("schema validation failed: " + " | ".join(failures))


def verify_idempotency(
    outputs_factory: Callable[[], UniverseCompilation],
) -> str:
    """Compile into three clean directories and byte-compare every output."""

    snapshots: list[dict[str, bytes]] = []
    with tempfile.TemporaryDirectory(prefix="ff6-capability-universe-") as directory:
        root = Path(directory)
        for index in range(3):
            result = outputs_factory()
            target = root / f"run-{index + 1}"
            write_outputs(target, result.outputs)
            snapshots.append(
                {
                    path.relative_to(target).as_posix(): path.read_bytes()
                    for path in sorted(target.rglob("*"))
                    if path.is_file()
                }
            )
    if not (snapshots[0] == snapshots[1] == snapshots[2]):
        raise UniverseError("three-run output mismatch")
    return sha256(
        canonical_json({key: sha256(value) for key, value in snapshots[0].items()})
    )
