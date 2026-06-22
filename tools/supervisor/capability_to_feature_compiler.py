# capability_to_feature_compiler.py — alias for capability_compiler.py
# Condition 3 fix: the expected filename is capability_to_feature_compiler.py
# The full implementation lives in capability_compiler.py (all phases 0-8).
from capability_compiler import *  # noqa: F401, F403
from capability_compiler import compile_gap  # explicit re-export for direct import
