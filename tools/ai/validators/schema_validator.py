"""Schema validation wrapper for AI platform artifacts."""

from __future__ import annotations

from typing import Any, Type

from pydantic import BaseModel, ValidationError

from tools.ai.schemas.models import ValidationResult


def validate_schema(data: dict[str, Any], model_class: Type[BaseModel]) -> ValidationResult:
    """Validate data against a Pydantic model.

    Returns a ValidationResult with errors if validation fails.
    """
    try:
        model_class.model_validate(data)
        return ValidationResult(valid=True)
    except ValidationError as exc:
        errors = [str(e) for e in exc.errors()]
        return ValidationResult(valid=False, errors=errors)
