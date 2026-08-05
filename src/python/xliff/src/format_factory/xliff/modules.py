"""XLIFF-MODULE-001 -- programmatic coverage declaration for optional modules.

"The XLIFF 2.1 standard package defines the Translation Candidates, Glossary,
Format Style, Metadata, Resource Data, Size and Length Restriction, Validation,
and ITS modules in their own namespaces." Every one of the eight is either
fully modeled or explicitly preservation-only here -- there is no third,
silent state where a module is simply absent from this manifest.

None of the eight has a typed accessor in ``model/document.py`` today: no
``Match``, ``GlossEntry``, ``MetaGroup``, or similar structured class exists.
Every one is therefore ``PRESERVATION_ONLY`` -- its content survives a
load/dump cycle as an opaque ``ExtensionNode`` (see ``model/document.py``),
verbatim, but is not exposed as queryable structure. Reporting any of them as
``MODELED`` before that accessor exists would be exactly the silent
overclaim GAP-022 was written to catch.

Resource Data is a deliberate exception within preservation-only: the
contract's SAL fact (SAL-XLIFF-00021 through -00026 give the other six modules
their namespace explicitly; the Resource Data fact does not) does not state its
namespace URI, so ``namespace`` is ``None`` and ``namespace_confirmed`` is
``False`` rather than asserting a value no verified fact backs. Its content
still round-trips: preservation here does not depend on knowing the exact
namespace, only on the element being unrecognized by the core reader.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ModuleCoverage(Enum):
    """"Every optional module of the target version is either fully modeled
    or explicitly preservation-only in the capability manifest - silent
    module downgrade is forbidden.\""""

    MODELED = "modeled"
    PRESERVATION_ONLY = "preservation_only"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True, slots=True)
class ModuleInfo:
    """One entry in the module coverage manifest."""

    name: str
    namespace: str | None
    coverage: ModuleCoverage
    namespace_confirmed: bool = True
    note: str = ""


STANDARD_MODULES: tuple[ModuleInfo, ...] = (
    ModuleInfo(
        name="Translation Candidates",
        namespace="urn:oasis:names:tc:xliff:matches:2.0",
        coverage=ModuleCoverage.PRESERVATION_ONLY,
    ),
    ModuleInfo(
        name="Glossary",
        namespace="urn:oasis:names:tc:xliff:glossary:2.0",
        coverage=ModuleCoverage.PRESERVATION_ONLY,
    ),
    ModuleInfo(
        name="Format Style",
        namespace="urn:oasis:names:tc:xliff:fs:2.0",
        coverage=ModuleCoverage.PRESERVATION_ONLY,
    ),
    ModuleInfo(
        name="Metadata",
        namespace="urn:oasis:names:tc:xliff:metadata:2.0",
        coverage=ModuleCoverage.PRESERVATION_ONLY,
    ),
    ModuleInfo(
        name="Resource Data",
        namespace=None,
        coverage=ModuleCoverage.PRESERVATION_ONLY,
        namespace_confirmed=False,
        note=(
            "No SAL fact states this module's namespace URI explicitly, unlike "
            "the other seven. Content still preserves losslessly: the reader "
            "captures any element it does not recognize as an ExtensionNode "
            "regardless of namespace, so preservation does not depend on this "
            "field being populated."
        ),
    ),
    ModuleInfo(
        name="Size and Length Restriction",
        namespace="urn:oasis:names:tc:xliff:sizerestriction:2.0",
        coverage=ModuleCoverage.PRESERVATION_ONLY,
    ),
    ModuleInfo(
        name="Validation",
        namespace="urn:oasis:names:tc:xliff:validation:2.0",
        coverage=ModuleCoverage.PRESERVATION_ONLY,
    ),
    ModuleInfo(
        name="ITS",
        namespace="http://www.w3.org/2005/11/its",
        coverage=ModuleCoverage.PRESERVATION_ONLY,
        note=(
            "Core ITS content uses the W3C ITS namespace directly; the XLIFF "
            "2.1 mapping additionally uses urn:oasis:names:tc:xliff:itsm:2.1 "
            "for domain/language attributes on core elements. Both preserve "
            "losslessly: elements via ExtensionNode, attributes via each "
            "container's unrecognized-attribute passthrough."
        ),
    ),
)


def module_coverage_manifest() -> dict[str, ModuleInfo]:
    """Programmatic per-module coverage, keyed by module name.

    "A developer inspects module coverage programmatically before relying on
    module data" -- this is that inspection point.
    """
    return {module.name: module for module in STANDARD_MODULES}


def is_production_complete() -> bool:
    """"production-complete status requires all modules modeled." """
    return all(module.coverage is ModuleCoverage.MODELED for module in STANDARD_MODULES)


__all__ = [
    "STANDARD_MODULES",
    "ModuleCoverage",
    "ModuleInfo",
    "is_production_complete",
    "module_coverage_manifest",
]
