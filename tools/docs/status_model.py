"""Normalized two-lane status model for PROJECT_STATUS.md.

Defines the data contract that separates MACHINERY lane (governance, supervisor,
architecture, skills) from PRODUCT lane (formats, oracle, certification, gates).

Every generated field belongs to exactly one lane. Cross-lane bleeding raises
a validation error before the document is written.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Lane constants
# ---------------------------------------------------------------------------

MACHINERY_FIELDS = frozenset({
    "validators",
    "capabilities_total",
    "capabilities_active",
    "capabilities_tracks",
    "skills",
    "skills_by_status",
    "commands",
    "sprint_count",
    "avg_quality",
    "evidence_runs",
    "supervisor_tools",
    "hard_prohibitions",
    "max_iterations",
    "checkpoint_interval",
    "agents",
    "architecture_layers",
})

PRODUCT_FIELDS = frozenset({
    "active_with_source",
    "total_in_registry",
    "family_count",
    "families",
    "python_files",
    "dotnet_files",
    "python_tests",
    "dotnet_tests",
    "formats_verified_oracle",
    "oracle_pass_rate",
    "oracle_total_cases",
    "certified",
    "certified_total",
    "format_inventory",
    "gates",
})

SHARED_FIELDS = frozenset({
    "doc_files",
    "sample_files",
    "python_examples",
    "dotnet_examples",
    "generation_timestamp",
    "head_revision",
    "generator_path",
    "source_map",
})

MACHINERY_SECTIONS = frozenset({
    "machinery-architecture",
    "machinery-validators",
    "machinery-capabilities",
    "machinery-supervision",
    "machinery-maturity",
    "machinery-limitations",
})

PRODUCT_SECTIONS = frozenset({
    "product-inventory",
    "product-implementations",
    "product-oracle",
    "product-certification",
    "product-gates",
    "product-maturity",
    "product-limitations",
})

REQUIRED_ANCHORS = [
    "status-at-a-glance",
    "machinery-lane",
    "product-lane",
    "shared-boundaries",
    "known-limitations",
    "generation-evidence",
]


# ---------------------------------------------------------------------------
# Classification helpers
# ---------------------------------------------------------------------------

def classify_section(name: str) -> str:
    """Return 'machinery', 'product', 'shared', or raise on 'AMBIGUOUS'."""
    n = name.lower().replace(" ", "-").replace("_", "-")
    if n in MACHINERY_SECTIONS:
        return "machinery"
    if n in PRODUCT_SECTIONS:
        return "product"
    if n in {"shared-boundaries", "status-at-a-glance", "generation-evidence", "known-limitations"}:
        return "shared"
    raise ValueError(
        f"Section '{name}' cannot be classified as machinery or product. "
        "Add it to MACHINERY_SECTIONS, PRODUCT_SECTIONS, or the shared set."
    )


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class MachineryStatus:
    """Machinery-lane status: governance, supervisor, architecture, skills."""
    validators: int = 0
    validator_modules: dict[str, int] = field(default_factory=dict)
    capabilities_total: int = 0
    capabilities_active: int = 0
    capabilities_tracks: dict[str, int] = field(default_factory=dict)
    skills: int = 0
    skills_by_status: dict[str, int] = field(default_factory=dict)
    commands: int = 0
    sprint_count: int = 0
    avg_quality: float = 0.0
    evidence_runs: int = 0
    evidence_runs_note: str = "session-local state (gitignored)"
    supervisor_tools: int = 0
    hard_prohibitions: list[str] = field(default_factory=list)
    max_iterations: int | None = None
    checkpoint_interval: str = "not configured"
    architecture_layers: list[dict] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)


@dataclass
class ProductStatus:
    """Product-lane status: formats, source, tests, oracle, certification, gates."""
    active_with_source: int = 0
    total_in_registry: int = 0
    family_count: int = 0
    families: dict[str, int] = field(default_factory=dict)
    python_files: int = 0
    dotnet_files: int = 0
    python_tests: int = 0
    dotnet_tests: int = 0
    formats_verified_oracle: int = 0
    oracle_pass_rate: str = "0/0"
    oracle_total_cases: int = 0
    certified: int = 0
    certified_total: int = 0
    format_inventory: list[dict] = field(default_factory=list)
    gates: list[dict] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)


@dataclass
class SharedStatus:
    """Shared facts that genuinely span both lanes."""
    doc_files: int = 0
    sample_files: int = 0
    python_examples: int = 0
    dotnet_examples: int = 0
    generation_timestamp: str = ""
    head_revision: str = "UNKNOWN"
    generator_path: str = "tools/docs/generate_project_status.py"
    source_map: list[str] = field(default_factory=list)


@dataclass
class ProjectStatusModel:
    """Complete two-lane project status model."""
    schema_version: str = "2.0"
    machinery: MachineryStatus = field(default_factory=MachineryStatus)
    products: ProductStatus = field(default_factory=ProductStatus)
    shared: SharedStatus = field(default_factory=SharedStatus)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

class StatusModelViolation(Exception):
    """Raised when the status model has lane violations or missing required fields."""


def validate_status_model(model: ProjectStatusModel) -> list[str]:
    """Validate the model for lane integrity and required fields.

    Returns a list of violation messages. Empty list = PASS.
    """
    violations: list[str] = []

    # Required machinery fields
    m = model.machinery
    if m.validators < 0:
        violations.append("MACHINERY: validators must be >= 0")
    if m.capabilities_active > m.capabilities_total:
        violations.append(
            f"MACHINERY: capabilities_active ({m.capabilities_active}) > "
            f"capabilities_total ({m.capabilities_total})"
        )
    if m.skills < 0:
        violations.append("MACHINERY: skills must be >= 0")

    # Required product fields
    p = model.products
    if p.active_with_source > p.total_in_registry:
        violations.append(
            f"PRODUCT: active_with_source ({p.active_with_source}) > "
            f"total_in_registry ({p.total_in_registry})"
        )
    if p.certified > p.certified_total and p.certified_total > 0:
        violations.append(
            f"PRODUCT: certified ({p.certified}) > certified_total ({p.certified_total})"
        )
    if p.formats_verified_oracle > p.active_with_source and p.active_with_source > 0:
        violations.append(
            f"PRODUCT: formats_verified_oracle ({p.formats_verified_oracle}) > "
            f"active_with_source ({p.active_with_source})"
        )

    # Lane integrity: product fields must not appear in machinery
    # (These are structural checks on the model fields, not rendered Markdown)
    # In this implementation the dataclasses enforce lane separation by structure.

    return violations


def collect_full_status(repo_root: Path) -> ProjectStatusModel:
    """Assemble all sub-collector results into the normalized two-lane model."""
    # Import sub-generators inline to avoid circular imports at module level
    import sys
    sys.path.insert(0, str(repo_root / "tools" / "docs"))

    from generate_statistics import collect_statistics
    from generate_product_inventory import collect_product_inventory
    from generate_architecture_inventory import collect_architecture_inventory
    from generate_agent_inventory import collect_agent_inventory

    stats = collect_statistics(repo_root)
    inventory = collect_product_inventory(repo_root)
    arch = collect_architecture_inventory(repo_root)
    agents = collect_agent_inventory(repo_root)

    # Get HEAD revision
    head = _get_head_revision(repo_root)

    # Machinery
    gov = stats.get("governance", {})
    inf = stats.get("infrastructure", {})
    policies = agents.get("policies", {})

    machinery = MachineryStatus(
        validators=gov.get("validators", 0),
        validator_modules={
            mod: len(names)
            for mod, names in arch.get("validators", {}).get("modules", {}).items()
        },
        capabilities_total=gov.get("capabilities_total", 0),
        capabilities_active=gov.get("capabilities_active", 0),
        capabilities_tracks=arch.get("capabilities", {}).get("tracks", {}),
        skills=gov.get("skills", 0),
        skills_by_status=arch.get("skills", {}).get("statuses", {}),
        commands=gov.get("commands", 0),
        sprint_count=inf.get("sprint_count", 0),
        avg_quality=inf.get("avg_quality", 0.0),
        evidence_runs=inf.get("evidence_runs", 0),
        supervisor_tools=agents.get("supervisor_tools", {}).get("total", 0),
        hard_prohibitions=policies.get("hard_prohibitions", []),
        max_iterations=policies.get("max_iterations"),
        checkpoint_interval=(
            "not configured"
            if not policies.get("checkpoint_interval")
            else str(policies["checkpoint_interval"])
        ),
        architecture_layers=arch.get("layers", []),
    )

    # Products
    fmt = stats.get("formats", {})
    src = stats.get("source", {})
    tst = stats.get("tests", {})
    orc = stats.get("oracle", {})
    cert = stats.get("certification", {})

    products = ProductStatus(
        active_with_source=fmt.get("active_with_source", 0),
        total_in_registry=fmt.get("total_in_registry", 0),
        family_count=fmt.get("family_count", 0),
        families=fmt.get("families", {}),
        python_files=src.get("python_files", 0),
        dotnet_files=src.get("dotnet_files", 0),
        python_tests=tst.get("python", 0),
        dotnet_tests=tst.get("dotnet", 0),
        formats_verified_oracle=orc.get("formats_verified", 0),
        oracle_pass_rate=orc.get("pass_rate", "0/0"),
        oracle_total_cases=orc.get("total_cases", 0),
        certified=cert.get("certified", 0),
        certified_total=cert.get("total", 0),
        format_inventory=inventory,
        gates=arch.get("gates", []),
    )

    # Shared
    shared = SharedStatus(
        doc_files=inf.get("doc_files", 0),
        sample_files=inf.get("sample_files", 0),
        python_examples=inf.get("python_examples", 0),
        dotnet_examples=inf.get("dotnet_examples", 0),
        head_revision=head,
        source_map=_build_source_map(repo_root),
    )

    model = ProjectStatusModel(machinery=machinery, products=products, shared=shared)
    return model


def _get_head_revision(repo_root: Path) -> str:
    """Return git HEAD revision or 'UNKNOWN' on failure."""
    try:
        import subprocess
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip()[:12]  # short SHA
    except Exception:
        pass
    return "UNKNOWN"


def _build_source_map(repo_root: Path) -> list[str]:
    """Return list of canonical source paths read by the generator."""
    sources = [
        "registry/format-registry.yaml",
        ".governance/capabilities/registry.yaml",
        ".supervisor/skill-registry.yaml",
        ".supervisor/policies.yaml",
        "oracle/formats/*/reports/oracle-run-summary.json",
        "reports/certification/portfolio-certification-matrix.json",
        "reports/supervisor/maturity-trend.json",
        "tools/supervisor/governance_validators*.py",
        "registry/gate-contract-registry.yaml",
        "src/python/**/*.py",
        "src/net/**/*.cs",
        "tests/**/*.py",
        "tests/**/*.cs",
        ".claude/commands/*.md",
        "samples/by-format/**/*",
        "docs/**/*.md",
        "examples/**/*",
        "AGENTS.md",
        ".claude/settings.json",
    ]
    return sources
