"""spec_parity_validators.py — 4 semantic spec-parity validators.

Implements:
  1. AttributePropertyMapValidator — validates attribute→property mappings match SAL facts
  2. ContainmentGraphValidator — validates parent→child element relationships
  3. AliasCompatibilityValidator — validates facade→canonical name mappings
  4. SkillWiringValidator — validates skill references match registered skills

Each validator accepts (facts, capability_map) and returns a ValidatorResult.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ValidatorResult:
    """Result of a spec-parity validation."""
    passed: bool
    validator_name: str
    evidence: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)

    def summary(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        lines = [f"{self.validator_name}: {status}"]
        for e in self.evidence:
            lines.append(f"  [OK] {e}")
        for f in self.failures:
            lines.append(f"  [FAIL] {f}")
        return "\n".join(lines)


class AttributePropertyMapValidator:
    """Validates that capability map attributes reference SAL fact QNames."""

    def validate(
        self, facts: list[dict[str, Any]], capability_map: dict[str, Any]
    ) -> ValidatorResult:
        result = ValidatorResult(passed=True, validator_name="AttributePropertyMapValidator")

        fact_qnames = {f.get("qname", "") for f in facts}
        if not fact_qnames:
            result.passed = False
            result.failures.append("No SAL facts provided")
            return result

        attributes = capability_map.get("attributes", [])
        if not attributes:
            result.evidence.append("No attributes in capability map (vacuously valid)")
            return result

        for attr in attributes:
            ref = attr.get("spec_fact_ref", "")
            if ref and ref not in fact_qnames:
                result.passed = False
                result.failures.append(
                    f"Attribute '{attr.get('name', '?')}' references unknown fact '{ref}'"
                )
            elif ref:
                result.evidence.append(
                    f"Attribute '{attr.get('name', '?')}' → fact '{ref}' validated"
                )

        return result


class ContainmentGraphValidator:
    """Validates parent→child element relationships against SAL facts."""

    def validate(
        self, facts: list[dict[str, Any]], capability_map: dict[str, Any]
    ) -> ValidatorResult:
        result = ValidatorResult(passed=True, validator_name="ContainmentGraphValidator")

        fact_elements: set[str] = set()
        for f in facts:
            desc = f.get("description", "")
            qname = f.get("qname", "")
            if qname:
                fact_elements.add(qname)

        containment = capability_map.get("containment", [])
        if not containment:
            result.evidence.append("No containment rules in capability map (vacuously valid)")
            return result

        for rule in containment:
            parent = rule.get("parent", "")
            child = rule.get("child", "")
            parent_ref = rule.get("parent_fact_ref", "")
            child_ref = rule.get("child_fact_ref", "")

            if parent_ref and parent_ref not in fact_elements:
                result.passed = False
                result.failures.append(
                    f"Containment '{parent}→{child}': parent ref '{parent_ref}' not in facts"
                )
            elif parent_ref:
                result.evidence.append(f"Containment '{parent}→{child}': parent ref validated")

            if child_ref and child_ref not in fact_elements:
                result.passed = False
                result.failures.append(
                    f"Containment '{parent}→{child}': child ref '{child_ref}' not in facts"
                )
            elif child_ref:
                result.evidence.append(f"Containment '{parent}→{child}': child ref validated")

        return result


class AliasCompatibilityValidator:
    """Validates facade→canonical name mappings are consistent."""

    def validate(
        self, facts: list[dict[str, Any]], capability_map: dict[str, Any]
    ) -> ValidatorResult:
        result = ValidatorResult(passed=True, validator_name="AliasCompatibilityValidator")

        aliases = capability_map.get("aliases", [])
        if not aliases:
            result.evidence.append("No aliases in capability map (vacuously valid)")
            return result

        seen_facades: dict[str, str] = {}
        for alias in aliases:
            facade = alias.get("facade", "")
            canonical = alias.get("canonical", "")

            if not facade or not canonical:
                result.passed = False
                result.failures.append(
                    f"Alias missing facade or canonical: {alias}"
                )
                continue

            if facade in seen_facades and seen_facades[facade] != canonical:
                result.passed = False
                result.failures.append(
                    f"Facade '{facade}' maps to both '{seen_facades[facade]}' "
                    f"and '{canonical}'"
                )
            else:
                seen_facades[facade] = canonical
                result.evidence.append(f"Alias '{facade}' → '{canonical}' consistent")

        return result


class SkillWiringValidator:
    """Validates skill references match registered skills."""

    def validate(
        self, facts: list[dict[str, Any]], capability_map: dict[str, Any]
    ) -> ValidatorResult:
        result = ValidatorResult(passed=True, validator_name="SkillWiringValidator")

        registered = set(capability_map.get("registered_skills", []))
        if not registered:
            result.evidence.append("No registered skills provided (vacuously valid)")
            return result

        referenced = set(capability_map.get("skill_references", []))
        if not referenced:
            result.evidence.append("No skill references in capability map (vacuously valid)")
            return result

        missing = referenced - registered
        if missing:
            result.passed = False
            for s in sorted(missing):
                result.failures.append(f"Referenced skill '{s}' not in registered skills")

        matched = referenced & registered
        for s in sorted(matched):
            result.evidence.append(f"Skill '{s}' is registered and referenced")

        return result
