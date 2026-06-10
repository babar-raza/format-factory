# Repair + Advancement Plan — Acceleration R106

## Repairs (from R105 deficiencies)
1. **Lane B:** Integrate package-identity + anti-skip into autonomous_cycle.py
2. **Lane C:** Add evidence-quality scoring to grade_declared_work.py (raw-proof instead of path-only)
3. **Lane D:** Regenerate fresh acceleration gaps for R106
4. **Lane G:** Actually build and validate a package pilot ZIP

## Advancements
1. **Lane E:** Expand anti-skip from 11→14 detectors (evidence_quality_score, declaration_completeness, test_count_regression)
2. **Lane F:** Add prompt diversity check and repair-lane enforcement to validate_prompt_quality.py
3. **Lane B:** Add post-grading quality gate in autonomous-cycle (anti-skip runs after grading)
