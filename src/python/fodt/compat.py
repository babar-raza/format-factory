# src/python/fodt/compat.py — BOOTSTRAP PHASE
#
# CRITICAL BOOTSTRAP RULE:
# During bootstrap (spec/ stubs at status: seeded / architecture_only), this file
# MUST import from models.py ONLY. The spec/ stubs are architecture_only skeletons —
# they have no properties (.kind, .text, .spans etc.) and importing from them would
# silently break all existing FODT tests.
#
# This file switches to spec/ imports ONLY after:
#   1. spec/ stubs reach status: implemented (in shared/qname-registry/fodt.yaml)
#   2. tests/python/fodt/test_compat_bootstrap.py proves behavioral equivalence
#      (FodtParagraph from spec/ has same .kind, .text, .spans as from models.py)
#
# DO NOT import from .spec.* until both conditions above are met.

try:
    from .models import FodtDocument, FodtParagraph, FodtSpan
except ImportError:
    FodtDocument = None  # type: ignore[assignment]
    FodtParagraph = None  # type: ignore[assignment]
    FodtSpan = None  # type: ignore[assignment]

__all__ = ["FodtDocument", "FodtParagraph", "FodtSpan"]
