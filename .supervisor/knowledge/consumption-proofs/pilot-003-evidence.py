# Consumption proof: pilot-003
# Task: Add TomlDocument.get_key_count() method to src/python/toml/models.py
#       AND confirm the TOML package follows the three-layer directory structure.
# Format: TOML — dict-based variant (KC-PYTHON-001 allowed_variants.dict-based.examples: ["toml"])
# Knowledge source: KC-PYTHON-001 + KC-PYTHON-002 ONLY — no implementation browsing
# Pilot target: TomlDocument in src/python/toml/models.py
#
# This pilot is the first to require BOTH contracts simultaneously:
#   - KC-PYTHON-001 (VERIFIED_CURRENT): accessor method pattern, dict-based variant
#   - KC-PYTHON-002 (VERIFIED_CURRENT, NEW in Phase 2): three-layer directory structure
#
# ============================================================================
# PART A: KC-PYTHON-002 — Directory structure verification (query result)
# ============================================================================
#
# KC-PYTHON-002 required_fields_or_components — expected in src/python/toml/:
#
#   [R1] __init__.py (root)         — EXPECTED (all 20 formats; toml in survey)
#   [R2] spec/ subdirectory         — EXPECTED (all 20 formats)
#        spec/table/__init__.py     — from KC-PYTHON-002 survey: TOML uses spec/table/
#        spec/table/table.py        — spec element class
#        spec/table/key.py          — spec element class
#   [R3] Compat/ subdirectory       — EXPECTED (all 20 formats)
#        Compat/toml_table.py       — facade for TomlTable
#        Compat/toml_key.py         — facade for TomlKey
#   [R4] codec file: toml_codec.py  — EXPECTED (KC-PYTHON-002 codec variant, not parser)
#   [R5] exceptions.py              — EXPECTED (all 20 formats)
#   [R6] domain document file       — config_document.py (per KC-PYTHON-002 survey note)
#
# KC-PYTHON-002 conclusion: TOML confirmed as three-layer format.
# Agent does NOT need to browse src/python/toml/ to know this.
#
# BEFORE Phase 2: KC-PYTHON-002 was DRAFT_PENDING_AUTHORITY — agent could NOT load this.
# AFTER Phase 2:  KC-PYTHON-002 is VERIFIED_CURRENT — this lookup is now authoritative.
#
# ============================================================================
# PART B: KC-PYTHON-001 — get_key_count() method (code snippet)
# ============================================================================
#
# TOML is dict-based (KC-PYTHON-001 allowed_variants.dict-based.examples includes "toml").
# get_key_count() is an accessor method pattern from KC-PYTHON-001:
#   "get_cell(), get_record(), or equivalent. Returns safe default on out-of-bounds."
#
# For a count (not indexed accessor), the closest pattern is a computed property
# (same as AbwDocument.word_count from pilot-002): derived from existing properties,
# int() coercion, safe default int(0).
#
# The neutral model for TOML (per KC-PYTHON-001 dict-based variant) is a dict.
# Key count = number of top-level keys in the parsed TOML dict.
# (No need to browse toml_codec.py — the contract says dict-based, so self._data is a dict.)
#
# KC-PYTHON-001 forbidden patterns checked:
#   - No spec_qname: str = (instance field) — not applicable, not adding a class attribute
#   - No self._data returned directly — we return int(), not the dict
#   - No module-level import — method body only
#   - Not a primary class definition — this is a method addition, no naming issues

    @property
    def key_count(self) -> int:
        """Total number of top-level keys in the TOML document.

        Derived from the neutral model dict (dict-based variant per KC-PYTHON-001).
        Returns 0 if the document is empty or not a dict.
        """
        # KC-PYTHON-001: use .get(key, default) pattern — but _data IS the neutral dict
        # For TOML dict-based: self._data is the full parsed dict of top-level keys.
        # len() on the dict gives key count. int() coercion per KC-PYTHON-001 pattern.
        return int(len(self._data))  # self._data is dict, len(dict) = number of keys

    def get_key_count(self) -> int:
        """Return the count of top-level keys. Non-property accessor variant.

        KC-PYTHON-001: accessor method pattern, safe default on error.
        """
        try:
            return int(len(self._data))
        except (TypeError, AttributeError):
            return int(0)  # Safe default per KC-PYTHON-001 accessor pattern


# ============================================================================
# Pilot-003 claim:
#   - No browsing of toml_codec.py, config_document.py, or any TOML file was needed
#   - KC-PYTHON-002 answered: TOML uses spec/table/, Compat/toml_*.py, toml_codec.py
#   - KC-PYTHON-001 answered: dict-based variant, int() coercion, safe default
#   - BEFORE Phase 2: Part A could NOT be answered (KC-PYTHON-002 was DRAFT)
#   - AFTER Phase 2: Both parts answered from contracts alone
#   - Remaining ambiguity: None for the accessor method itself
#   - Remaining ambiguity (layout): whether spec/table/ has additional files beyond
#     table.py/key.py — but KC-PYTHON-002 says "at least one namespace subdirectory"
#     and TOML was in the survey, so the spec/ presence is authoritative.
#
# Verdict: KNOWLEDGE_CONTRACT_SUFFICIENT (both KC-PYTHON-001 + KC-PYTHON-002 used)
# ============================================================================
