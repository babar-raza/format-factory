# Python FOSS Publication Blocked Checklist
# Sprint: FORMAT-FACTORY-R23-MEGA-TRAIN-PYTHON-PUBLICATION-DRYRUN-GATE11-HARDENING-NEXT-FORMATS-AND-PLAYBOOK-REPAIR-001
# Date: 2026-05-17

## HARD STOP — PUBLICATION IS BLOCKED

This checklist documents all items that MUST be resolved before any PyPI upload.
No item below may be bypassed. All require human approval.

---

## Format-Level Blockers (All 5 packages)

### ZST (aspose-format-factory-zst)
- [ ] publish_authorized set to true by human approver
- [ ] Version bumped from 0.1.0.dev0 to stable release version
- [ ] zstandard runtime dependency version pinning reviewed
- [ ] PyPI token/credential configured for upload

### FODP (aspose-format-factory-fodp)
- [ ] publish_authorized set to true by human approver
- [ ] Version bumped from 0.1.0.dev0 to stable release version
- [ ] PyPI token/credential configured for upload

### FODG (aspose-format-factory-fodg)
- [ ] publish_authorized set to true by human approver
- [ ] Version bumped from 0.1.0.dev0 to stable release version
- [ ] PyPI token/credential configured for upload

### Gnumeric (aspose-format-factory-gnumeric)
- [ ] publish_authorized set to true by human approver
- [ ] Version bumped from 0.1.0.dev0 to stable release version
- [ ] PyPI token/credential configured for upload

### ABW (aspose-format-factory-abw)
- [ ] publish_authorized set to true by human approver
- [ ] Version bumped from 0.1.0.dev0 to stable release version
- [ ] PyPI token/credential configured for upload

---

## Cross-Cutting Blockers (Project-Level)

- [ ] Dedicated release sprint authorized (separate from R23)
- [ ] Independent verification (IV) sprint completed per DEC-034
- [ ] CHANGELOG.md created for each package
- [ ] Release notes reviewed and approved
- [ ] Security review of all wheel contents completed
- [ ] PyPI package names reserved/verified (no naming conflicts)
- [ ] License files included in all wheels
- [ ] README.md included in all packages
- [ ] Package classifiers (Development Status, License) correct
- [ ] All tests passing in clean environment (not just local dev)

---

## Governance References

- DEC-031: Python track = FOSS product path
- DEC-034: IV sprint required before human review
- AGENTS.md AF9-AF15: Commercial readiness + AI governance
- GOVERNANCE.md 26.8-26.13: Commercial readiness policy

---

## Current State: NOT READY FOR PUBLICATION

`publication_authorized: false` — Do NOT run `twine upload` or `pip publish`.
This checklist must be completed in a dedicated authorized release sprint.
