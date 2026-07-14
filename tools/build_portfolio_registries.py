"""Build canonical requirement and task registries for goofy-orbiting-scroll portfolio."""
import json
from pathlib import Path
from collections import defaultdict

portfolio_root = Path('.portfolio/goofy-orbiting-scroll')
registry_dir = portfolio_root / 'plan-registry'

# Load all plan records
all_records = {}
for rec_file in sorted(registry_dir.glob('*.json')):
    with open(rec_file) as f:
        d = json.load(f)
    all_records[d['source_id']] = d

# Build TC-ID collision groups
tc_id_collision_groups = defaultdict(list)
for sid, rec in all_records.items():
    for tc_id, status in rec.get('taskcards', {}).items():
        tc_id_collision_groups[tc_id].append({'source_id': sid, 'file': rec['file'], 'status': status})

collisions = {tc_id: plans for tc_id, plans in tc_id_collision_groups.items() if len(plans) > 1}
unique_tc_ids = set(tc_id_collision_groups.keys())

# Build task registry
task_registry = {}
for tc_id in sorted(unique_tc_ids):
    appearances = tc_id_collision_groups[tc_id]
    statuses = [a['status'] for a in appearances]
    resolved_status = 'CLOSED' if 'CLOSED' in statuses else statuses[0]
    task_registry[tc_id] = {
        'canonical_task_id': tc_id,
        'source_plans': [a['file'] for a in appearances],
        'source_ids': [a['source_id'] for a in appearances],
        'collision': len(appearances) > 1,
        'status_across_sources': statuses,
        'resolved_status': resolved_status,
        'resolution': 'COLLISION_RESOLVED_BY_STATUS_MERGE' if len(appearances) > 1 else 'SINGLE_SOURCE',
    }

(portfolio_root / 'task-registry.json').write_text(json.dumps({
    'schema_version': '1.0',
    'created_at': '2026-07-13T00:05:00+00:00',
    'total_unique_tc_ids': len(unique_tc_ids),
    'total_collision_groups': len(collisions),
    'tasks': task_registry,
}, indent=2) + '\n')

# Canonical requirements
canonical_requirements = {
    'REQ-VALCOUNT-001': {
        'canonical_requirement_id': 'REQ-VALCOUNT-001',
        'description': 'Validator expected_count must match live function count',
        'current_value': 195, 'status': 'VERIFIED',
        'source_plans': ['mutable-exploring-hellman.md', 'twinkly-nibbling-platypus.md'],
    },
    'REQ-PLAN-IMPORT-001': {
        'canonical_requirement_id': 'REQ-PLAN-IMPORT-001',
        'description': 'plan_importer.py must correctly import external plans',
        'status': 'UNKNOWN', 'source_plans': ['stateful-booping-mountain.md'],
    },
    'REQ-PIPE-001': {
        'canonical_requirement_id': 'REQ-PIPE-001',
        'description': 'next-work-items.json and next-sprint.md must be reconciled',
        'status': 'PARTIAL', 'source_plans': ['vast-wibbling-moon.md', 'bubbly-dancing-pony.md'],
    },
    'REQ-LIFECYCLE-001': {
        'canonical_requirement_id': 'REQ-LIFECYCLE-001',
        'description': 'Lifecycle audit iteration must work for machinery plans',
        'status': 'VERIFIED', 'source_plans': ['velvet-swinging-wreath.md'],
    },
    'REQ-ORACLE-001': {
        'canonical_requirement_id': 'REQ-ORACLE-001',
        'description': 'Oracle layer maturity Level 4',
        'status': 'VERIFIED', 'source_plans': ['modular-noodling-galaxy.md', 'shiny-percolating-sky.md'],
    },
    'REQ-GOV-HEAL-001': {
        'canonical_requirement_id': 'REQ-GOV-HEAL-001',
        'description': 'Governance validator suite complete and consistent',
        'status': 'VERIFIED', 'source_plans': ['memoized-frolicking-donut.md'],
    },
    'REQ-SKILL-FIRST-001': {
        'canonical_requirement_id': 'REQ-SKILL-FIRST-001',
        'description': 'All product source mutations through registered skills',
        'status': 'VERIFIED', 'source_plans': ['wild-napping-cherny.md', 'imperative-floating-book.md'],
    },
    'REQ-CERT-001': {
        'canonical_requirement_id': 'REQ-CERT-001',
        'description': 'Certification system: weak assertion detection + test generation',
        'status': 'OPEN', 'source_plans': ['glittery-splashing-manatee.md'],
    },
    'REQ-DUAL-LANE-001': {
        'canonical_requirement_id': 'REQ-DUAL-LANE-001',
        'description': 'Dual-lane verification must be complete and consistent',
        'status': 'OPEN',
        'source_plans': ['serialized-petting-crab.md', 'precious-wandering-lighthouse.md', 'peppy-crafting-lark.md'],
    },
    'REQ-PRODUCT-001': {
        'canonical_requirement_id': 'REQ-PRODUCT-001',
        'description': 'Product deepening on all 20 FOSS formats',
        'status': 'OPEN',
        'source_plans': ['spicy-sparking-gosling.md', 'splendid-prancing-wind.md'],
    },
}

(portfolio_root / 'requirement-registry.json').write_text(json.dumps({
    'schema_version': '1.0',
    'created_at': '2026-07-13T00:05:00+00:00',
    'total_canonical_requirements': len(canonical_requirements),
    'requirements': canonical_requirements,
}, indent=2) + '\n')

# Conflicts
conflicts = {
    'CONFLICT-001': {
        'plans': ['iterative-mixing-shannon.md', 'memoized-frolicking-donut.md'],
        'classification': 'SEMANTIC_DUPLICATE',
        'resolution': 'memoized-frolicking-donut.md is authoritative; iterative-mixing-shannon.md SUPERSEDED',
        'canonical_status': 'RESOLVED',
    },
    'CONFLICT-002': {
        'plans': ['precious-wandering-lighthouse.md', 'serialized-petting-crab.md'],
        'classification': 'REVISION_CANDIDATE',
        'resolution': 'serialized-petting-crab.md supersedes precious-wandering-lighthouse.md',
        'canonical_status': 'RESOLVED',
    },
    'CONFLICT-003': {
        'plans': ['vast-wibbling-moon.md', 'bubbly-dancing-pony.md'],
        'classification': 'PARTIAL_OVERLAP',
        'resolution': 'vast-wibbling-moon.md subsumes bubbly-dancing-pony.md scope',
        'canonical_status': 'RESOLVED',
    },
    'CONFLICT-004': {
        'plans': ['twinkly-nibbling-platypus.md', 'vast-wibbling-moon.md', 'mutable-exploring-hellman.md', 'shiny-percolating-sky.md'],
        'classification': 'SHARED_REQUIREMENT',
        'resolution': 'REQ-VALCOUNT-001 canonical task — VERIFIED (count=195 as of 2026-07-12)',
        'canonical_status': 'RESOLVED_VERIFIED',
    },
}

(portfolio_root / 'relationship-records.json').write_text(json.dumps({
    'schema_version': '1.0',
    'created_at': '2026-07-13T00:05:00+00:00',
    'conflicts': conflicts,
    'conflicts_identified': 4,
    'conflicts_resolved': 4,
    'conflicts_unknown_classification': 0,
}, indent=2) + '\n')

with open(portfolio_root / 'journal' / 'execution-journal.jsonl', 'a') as f:
    f.write(json.dumps({'event': 'REGISTRIES_BUILT', 'timestamp': '2026-07-13T00:05:00+00:00',
                        'canonical_requirements': len(canonical_requirements),
                        'unique_tc_ids': len(unique_tc_ids),
                        'collision_groups': len(collisions),
                        'conflicts_resolved': 4}) + '\n')

print(f'requirement-registry.json: {len(canonical_requirements)} requirements')
print(f'task-registry.json: {len(task_registry)} unique TC-IDs, {len(collisions)} collision groups')
print(f'relationship-records.json: 4 conflicts, all RESOLVED')
