# Consumption proof: pilot-002
# Task: Add AbwDocument.word_count property
# Format: ABW (AbiWord) — dict-based variant (per KC-PYTHON-001 allowed_variants)
# Knowledge source: KC-PYTHON-001 ONLY — no implementation browsing
# Pilot target: AbwDocument in src/python/abw/models.py
#
# KC-PYTHON-001 contract applied:
# - dict-based variant: self._data, defensive copy via list(), .get(key, default)
# - typed @property, return type coerced: int()
# - computed property (derived from existing properties) — same pattern as column_count in canonical example
# - no module-level imports from codec

    @property
    def word_count(self) -> int:
        """Total word count across all paragraphs.

        Derived from paragraphs property (defensive copy already applied there).
        Returns 0 if no paragraphs present.
        """
        # KC-PYTHON-001: use property (defensive copy) not self._data directly
        paragraphs = self.paragraphs  # list[str], defensive copy already applied
        if not paragraphs:
            return int(0)  # coerce to int, safe default
        return int(sum(len(p.split()) for p in paragraphs))  # coerce to int


# Pilot-002 claim:
#   - No browsing of abw_codec.py, word_document.py, or any other ABW file was needed
#   - KC-PYTHON-001 section "allowed_variants.dict-based.description" gave:
#       self._data, to_dict() pattern
#   - KC-PYTHON-001 canonical example (CsvDocument.column_count) gave:
#       derived property using existing @property methods, int() coercion
#   - Forbidden pattern check passed:
#       - no spec_qname: str = (instance field) -- using bare class attribute
#       - no self._data returned directly (using self.paragraphs which is defensive)
#       - no module-level relative import
#
# Verdict determination:
#   broad_search_required: False -- KC-PYTHON-001 sufficient for dict-based derived property
#   remaining_ambiguity: None -- pattern is explicit in contract and canonical example
