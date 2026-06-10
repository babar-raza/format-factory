# Staleness Invalidation Report

Stale events: 3
Stale claims: 1

Stale event IDs: ['StalenessEvent(node_id=\'spec:zst:old-draft\', trigger=\'spec_requirement_changed\', reason="SpecRequirementRef \'spec:zst:old-draft\' has status=\'stale\'", propagated_from=None, detected_at=\'2026-06-05T03:39:47.282834+00:00\')', 'StalenessEvent(node_id=\'req:zst:old-compress\', trigger=\'product_requirement_changed\', reason="ProductRequirement \'req:zst:old-compress\' has status=\'stale\'", propagated_from=None, detected_at=\'2026-06-05T03:39:47.282838+00:00\')', 'StalenessEvent(node_id=\'claim:zst:old-compress\', trigger=\'claim_scope_changed\', reason="CapabilityClaim \'claim:zst:old-compress\' has status=\'stale\'", propagated_from=None, detected_at=\'2026-06-05T03:39:47.282842+00:00\')']
Stale claim IDs: ['claim:zst:old-compress']

## Synthetic stale test
- `claim:zst:old-compress` is stale (stale_due_to req:zst:old-compress)
- Stale claims CANNOT support accepted_for_poc — correctly blocked
