"""Pluggable profile-specific validators.

UBL-PROFILE-001 (SAL-UBL-OBL-7D0855CD163E1EFD): "Expose version,
customization, and profile identifiers; allow profile-specific validators
to be registered; never claim profile conformance without the installed
ruleset passing."

validator.py's validate() checks the stable structural chassis only,
deliberately independent of any particular customization profile's
business rules -- EN 16931, PEPPOL BIS, and similar rulesets are numerous,
versioned, and not something this package can bundle for every
customization a caller might need. This module gives a caller a place to
register one.

Keyed by cbc:CustomizationID, not cbc:ProfileID: in real UBL deployments
(EN 16931 / PEPPOL BIS being the clearest example), CustomizationID is
what selects the Schematron/validation-artefact set a document must pass;
ProfileID identifies the business process (ordering, billing, ...) the
document participates in, not which ruleset applies to it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from format_factory.core import ValidationReport

from ..model import UblDocument

ProfileValidator = Callable[[UblDocument], ValidationReport]


@dataclass(frozen=True, slots=True)
class ProfileValidatorRegistry:
    """An immutable, caller-owned set of customization-ID-keyed validators.

    Frozen like every other model type in this package: `register()`
    returns a new registry rather than mutating this one, so a registry a
    caller has already shared or cached cannot be changed out from under
    them by an unrelated registration elsewhere.
    """

    _validators: "tuple[tuple[str, ProfileValidator], ...]" = ()

    def register(
        self, customization_id: str, validator: ProfileValidator
    ) -> "ProfileValidatorRegistry":
        """Return a new registry with `validator` registered for `customization_id`.

        Re-registering an already-registered ID replaces it in the
        returned registry.
        """
        if not customization_id:
            raise ValueError("customization_id must not be empty")
        remaining = tuple(
            (key, existing)
            for key, existing in self._validators
            if key != customization_id
        )
        return ProfileValidatorRegistry((*remaining, (customization_id, validator)))

    def installed_for(self, customization_id: str | None) -> ProfileValidator | None:
        """The validator registered for `customization_id`, or None."""
        if customization_id is None:
            return None
        for key, validator in self._validators:
            if key == customization_id:
                return validator
        return None

    def __len__(self) -> int:
        return len(self._validators)


def validate_profile(
    document: UblDocument, registry: ProfileValidatorRegistry
) -> ValidationReport | None:
    """Run the registered validator for `document`'s own customization ID.

    Returns None -- never an empty or passing ValidationReport -- when the
    document declares no customization ID, or when nothing is registered
    for the one it declares: "absent when not installed" per the
    obligation's own wording. A None result is not evidence of conformance;
    it means no profile-specific ruleset ran at all, so a caller must not
    read it as "passed."
    """
    validator = registry.installed_for(document.customization_id)
    if validator is None:
        return None
    return validator(document)


__all__ = ["ProfileValidator", "ProfileValidatorRegistry", "validate_profile"]
