"""Canonical loaders for the skill / command / capability registries.

Single source of truth for *reading* the three governance registries. Every
Skills-First Control module loads through here so that schema assumptions and
fail-closed semantics live in exactly one place.

Fail-closed contract: a missing file, unparseable YAML, or a top-level shape
that is not the expected mapping raises RegistryError. Callers must NOT swallow
this into a clean pass — that is the whole point of the control layer.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]

SKILL_REGISTRY = REPO_ROOT / ".supervisor" / "skill-registry.yaml"
COMMAND_REGISTRY = REPO_ROOT / ".claude" / "commands" / "command-registry.yaml"
CAPABILITY_ROUTING = REPO_ROOT / ".supervisor" / "capability-routing-registry.yaml"
COMMANDS_DIR = REPO_ROOT / ".claude" / "commands"
POLICY_FILE = REPO_ROOT / "docs" / "governance" / "skill-only-policy.yaml"


class RegistryError(RuntimeError):
    """Raised when a governance registry is missing or structurally invalid."""


def _load_yaml_mapping(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RegistryError(f"registry not found: {path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:  # pragma: no cover - exercised via tests
        raise RegistryError(f"registry not parseable ({path.name}): {exc}") from exc
    if not isinstance(data, dict):
        raise RegistryError(
            f"registry top-level is {type(data).__name__}, expected mapping: {path}"
        )
    return data


def sha256_of(path: Path) -> str:
    """Content hash of a file; empty string if absent (callers decide severity)."""
    if not path.exists():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass
class Skill:
    skill_id: str
    status: str
    command: str
    command_file: str
    product_track: str = ""
    purpose: str = ""
    idempotency: str = ""
    mandatory_validations: list[str] = field(default_factory=list)
    required_handoff_fields: list[str] = field(default_factory=list)
    implementation_paths: list[str] = field(default_factory=list)
    test_paths: list[str] = field(default_factory=list)
    allowed_paths: list[str] = field(default_factory=list)
    supersedes: str = ""
    advisory_only: bool = False
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def is_active(self) -> bool:
        return self.status == "active"

    @property
    def command_name(self) -> str:
        """Normalized command slug (no leading slash)."""
        c = self.command or ""
        return c[1:] if c.startswith("/") else c


@dataclass
class Command:
    command_id: str
    skill_id: str
    file: str
    status: str = "active"
    skill_registry_ref: bool = False
    description: str = ""
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class Route:
    route_id: str
    current_status: str
    preferred_skill_ids: list[str] = field(default_factory=list)
    fallback_skill_ids: list[str] = field(default_factory=list)
    description: str = ""
    gap_id: str = ""
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def is_active(self) -> bool:
        return self.current_status == "ROUTE_ACTIVE"


def load_skills() -> list[Skill]:
    data = _load_yaml_mapping(SKILL_REGISTRY)
    raw_skills = data.get("skills")
    if not isinstance(raw_skills, list):
        raise RegistryError("skill-registry.yaml: 'skills' is not a list")
    out: list[Skill] = []
    for i, s in enumerate(raw_skills):
        if not isinstance(s, dict):
            raise RegistryError(f"skill-registry.yaml: skill[{i}] is not a mapping")
        sid = s.get("skill_id")
        if not sid:
            raise RegistryError(f"skill-registry.yaml: skill[{i}] missing skill_id")
        out.append(
            Skill(
                skill_id=sid,
                status=s.get("status", "unknown"),
                command=s.get("command", ""),
                command_file=s.get("command_file", ""),
                product_track=s.get("product_track", ""),
                purpose=s.get("purpose", ""),
                idempotency=s.get("idempotency", ""),
                mandatory_validations=list(s.get("mandatory_validations") or []),
                required_handoff_fields=list(s.get("required_handoff_fields") or []),
                implementation_paths=list(s.get("implementation_paths") or []),
                test_paths=list(s.get("test_paths") or []),
                allowed_paths=list(s.get("allowed_paths") or []),
                supersedes=s.get("supersedes", ""),
                advisory_only=bool(s.get("advisory_only", False)),
                raw=s,
            )
        )
    return out


def load_commands() -> list[Command]:
    data = _load_yaml_mapping(COMMAND_REGISTRY)
    raw_cmds = data.get("commands")
    if not isinstance(raw_cmds, list):
        raise RegistryError("command-registry.yaml: 'commands' is not a list")
    out: list[Command] = []
    for i, c in enumerate(raw_cmds):
        if not isinstance(c, dict):
            raise RegistryError(f"command-registry.yaml: command[{i}] is not a mapping")
        cid = c.get("command_id")
        if not cid:
            raise RegistryError(f"command-registry.yaml: command[{i}] missing command_id")
        out.append(
            Command(
                command_id=cid,
                skill_id=c.get("skill_id", ""),
                file=c.get("file", ""),
                status=c.get("status", "active"),
                skill_registry_ref=bool(c.get("skill_registry_ref", False)),
                description=c.get("description", ""),
                raw=c,
            )
        )
    return out


def load_routes() -> list[Route]:
    data = _load_yaml_mapping(CAPABILITY_ROUTING)
    raw_routes = data.get("routes")
    if not isinstance(raw_routes, list):
        raise RegistryError("capability-routing-registry.yaml: 'routes' is not a list")
    out: list[Route] = []
    for i, r in enumerate(raw_routes):
        if not isinstance(r, dict):
            raise RegistryError(f"capability-routing-registry.yaml: route[{i}] not a mapping")
        rid = r.get("route_id")
        if not rid:
            raise RegistryError(f"capability-routing-registry.yaml: route[{i}] missing route_id")
        out.append(
            Route(
                route_id=rid,
                current_status=r.get("current_status", "unknown"),
                preferred_skill_ids=list(r.get("preferred_skill_ids") or []),
                fallback_skill_ids=list(r.get("fallback_skill_ids") or []),
                description=r.get("description", ""),
                gap_id=r.get("gap_id", ""),
                raw=r,
            )
        )
    return out


def command_files_on_disk() -> list[str]:
    """Repo-relative paths of every command .md file (excludes the registry)."""
    if not COMMANDS_DIR.exists():
        raise RegistryError(f"commands dir not found: {COMMANDS_DIR}")
    out = []
    for p in sorted(COMMANDS_DIR.glob("*.md")):
        out.append(p.relative_to(REPO_ROOT).as_posix())
    return out


def load_policy() -> dict[str, Any]:
    return _load_yaml_mapping(POLICY_FILE)
