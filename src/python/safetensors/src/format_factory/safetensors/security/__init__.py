"""Security policy for untrusted SafeTensors inputs."""

from .limits import SAFETENSORS_LIMITS, effective_limits

__all__ = ["SAFETENSORS_LIMITS", "effective_limits"]
