"""
format-factory: NDJSON (Newline-Delimited JSON) FOSS Python track.

Minimal FOSS implementation for .ndjson / .jsonl format support.
Spec: https://ndjson.org/ — royalty-free, public domain format.
Uses stdlib json only — no external dependencies.
Acquisition Gates 1-4 initiated.

FOSS track only — no commercial readiness implied.
"""

# Import all core codec functions and exception classes
from .ndjson_codec import *  # noqa: F401, F403

# Import spec-level domain module (Compat facade)
from .Compat.ndjson_record import NdjsonRecord  # noqa: F401

# Compute public API: all non-private names loaded so far
import sys as _sys
__all__ = [k for k in vars(_sys.modules[__name__]) if not k.startswith("_")]
del _sys

__version__ = "0.1.0.dev0"
__track__ = "python-foss"
__commercial_ready__ = False
__capability_level__ = "alpha-foss-preview"
