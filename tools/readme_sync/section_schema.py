"""README section schemas and heading matching."""

from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatchcase


@dataclass(frozen=True)
class SectionDef:
    heading: str
    section_id: str
    classification: str
    required: bool = False
    order: int = 0
    generator_name: str | None = None
    heading_aliases: list[str] = field(default_factory=list)


def _def(
    heading: str,
    section_id: str,
    classification: str,
    order: int,
    *,
    required: bool = False,
    generator_name: str | None = None,
    aliases: list[str] | None = None,
) -> SectionDef:
    return SectionDef(
        heading=heading,
        section_id=section_id,
        classification=classification,
        required=required,
        order=order,
        generator_name=generator_name,
        heading_aliases=aliases or [heading],
    )


PYTHON_FOSS_SECTIONS = [
    _def("Title", "title", "MAINTAINED", 0, aliases=["Title"]),
    _def("Installation", "installation", "GENERATED", 10, generator_name="installation"),
    _def("Quick Start", "quick_start", "MAINTAINED", 20, aliases=["Quick Start", "Getting Started", "Usage"]),
    _def("Public API", "public_api", "GENERATED", 30, generator_name="public_api"),
    _def("Features", "features", "MAINTAINED", 40, aliases=["Features", "Supported Features", "Capabilities"]),
    _def("Security Notes", "security_notes", "MAINTAINED", 50, aliases=["Security Notes", "Security"]),
    _def("Requirements Coverage", "requirements_coverage", "MAINTAINED", 60),
    _def("Package Info", "package_info", "GENERATED", 70, required=True, generator_name="package_info"),
    _def("Package Structure", "package_structure", "MAINTAINED", 80, aliases=["Package Structure", "Source Layout", "Folder Contents"]),
    _def("Running Tests", "running_tests", "MAINTAINED", 90, aliases=["Running Tests", "Tests"]),
    _def("License", "license", "GENERATED", 100, required=True, generator_name="license"),
]

DOTNET_COMMERCIAL_SECTIONS = [
    _def("Title", "title", "MAINTAINED", 0, aliases=["Title"]),
    _def("Status", "status", "MAINTAINED", 10, aliases=["Status", "Status: Gate 11*"]),
    _def("Scope", "scope", "MAINTAINED", 20),
    _def("DEC-033", "dec_033", "MAINTAINED", 30, aliases=["DEC-033*"]),
    _def("Current Implementation", "current_implementation", "MAINTAINED", 40, aliases=["Current Implementation*"]),
    _def("What Remains", "what_remains", "MAINTAINED", 50, aliases=["What Remains*"]),
    _def("Installation", "installation", "GENERATED", 60, generator_name="installation"),
    _def("Package Info", "package_info", "GENERATED", 70, required=True, generator_name="package_info"),
    _def("Commercial Licensing", "commercial_licensing", "MAINTAINED", 80),
    _def("References", "references", "MAINTAINED", 90),
    _def("License", "license", "GENERATED", 100, generator_name="license"),
]

DOTNET_MINIMAL_SECTIONS = [
    _def("Title", "title", "MAINTAINED", 0, aliases=["Title"]),
    _def("Classification", "classification", "MAINTAINED", 10),
    _def("Usage", "usage", "MAINTAINED", 20),
    _def("Gate Status", "gate_status", "MAINTAINED", 30),
    _def("Package Info", "package_info", "GENERATED", 40, required=True, generator_name="package_info"),
]

DOTNET_STANDARD_SECTIONS = [
    *PYTHON_FOSS_SECTIONS[:4],
    _def("Gate Status", "gate_status", "MAINTAINED", 35),
    *PYTHON_FOSS_SECTIONS[4:],
]


def get_schema_for_format(format_id: str, track: str) -> list[SectionDef]:
    fmt = format_id.lower()
    trk = track.lower()
    if trk == "dotnet" and fmt in {"html", "markdown", "txt"}:
        return DOTNET_MINIMAL_SECTIONS
    if trk == "dotnet" and fmt in {"fods", "fodt"}:
        return DOTNET_COMMERCIAL_SECTIONS
    if trk == "dotnet":
        return DOTNET_STANDARD_SECTIONS
    return PYTHON_FOSS_SECTIONS


def _normalize_heading(heading: str) -> str:
    value = heading.strip()
    while value.startswith("#"):
        value = value[1:].strip()
    return " ".join(value.split())


def match_heading(heading: str, schema: list[SectionDef]) -> SectionDef | None:
    if heading.lstrip().startswith("# ") and not heading.lstrip().startswith("## "):
        for item in schema:
            if item.section_id == "title":
                return item
    normalized = _normalize_heading(heading).casefold()
    for item in schema:
        candidates = [item.heading, *item.heading_aliases]
        for candidate in candidates:
            pattern = _normalize_heading(candidate).casefold()
            if fnmatchcase(normalized, pattern):
                return item
    return None
