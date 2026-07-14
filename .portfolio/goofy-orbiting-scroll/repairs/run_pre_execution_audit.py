"""Pre-execution audit for goofy-orbiting-scroll portfolio.
Inspects all existing reconcile-only artifacts and produces findings.
"""
import json, datetime
from pathlib import Path

root = Path('.portfolio/goofy-orbiting-scroll')
now = datetime.datetime.now(datetime.timezone.utc).isoformat()

# Load existing artifacts for audit
manifest = json.loads((root / 'portfolio-manifest.json').read_text())
inventory = json.loads((root / 'source-inventory.json').read_text())
req_reg = json.loads((root / 'requirement-registry.json').read_text())
task_reg = json.loads((root / 'task-registry.json').read_text())
prov = json.loads((root / 'provenance-map.json').read_text())
rel = json.loads((root / 'relationship-records.json').read_text())
dep = json.loads((root / 'dependency-graph.json').read_text())
wave = json.loads((root / 'wave-registry.json').read_text())
handoff = json.loads((root / 'execution-handoff.json').read_text())

# Count plan records
plan_records = list((root / 'plan-registry').glob('*.json'))
checklists = list((root / 'checklists').glob('*.json'))
journal_events = (root / 'journal/execution-journal.jsonl').read_text().strip().split('\n')

# Count source taskcards across all plan records
total_source_tcs = 0
plan_without_tasks = []
for p in sorted(plan_records):
    rec = json.loads(p.read_text())
    total_source_tcs += len(rec.get('source_taskcards', []))
    if not rec.get('canonical_task_ids'):
        plan_without_tasks.append(rec['source_id'])

tasks = task_reg.get('tasks', [])
canonical_task_count = len(tasks)
ratio = total_source_tcs / max(canonical_task_count, 1)
wave_data = wave.get('waves', [])
nodes = dep.get('nodes', [])
not_mapped_tasks = [m for m in prov.get('source_task_mappings', []) if m.get('disposition') == 'NOT_MAPPED']

findings = []

findings.append({
    'finding_id': 'F-001',
    'severity': 'CRITICAL',
    'category': 'OVER_CONSOLIDATION',
    'description': (
        f'{total_source_tcs} source taskcards compressed to {canonical_task_count} canonical tasks '
        f'(ratio {ratio:.1f}:1). RECONCILE_ONLY agent used plan-level grouping, not taskcard-level mapping.'
    ),
    'affected_artifact': 'task-registry.json',
    'repair_action': 'REBUILD_EXECUTABLE_TASKS_AT_TASKCARD_GRANULARITY'
})

for t in tasks:
    src_plans = t.get('source_plan_ids', [])
    if len(src_plans) >= 5:
        findings.append({
            'finding_id': f'F-002-{t["task_id"]}',
            'severity': 'CRITICAL',
            'category': 'OVERBROAD_CANONICAL_TASK',
            'description': (
                f'{t["task_id"]} maps {len(src_plans)} source plans: {src_plans}. '
                'A single executable task cannot cover this scope.'
            ),
            'affected_artifact': 'task-registry.json',
            'repair_action': 'SPLIT_INTO_ATOMIC_EXECUTABLE_TASKS'
        })

if plan_without_tasks:
    findings.append({
        'finding_id': 'F-003',
        'severity': 'HIGH',
        'category': 'UNMAPPED_PLANS',
        'description': f'{len(plan_without_tasks)} plans have no canonical_task_ids: {plan_without_tasks}',
        'affected_artifact': 'plan-registry/',
        'repair_action': 'MAP_ALL_PLANS_TO_EXECUTABLE_TASKS'
    })

w0 = next((w for w in wave_data if w.get('wave_id') == 'W0'), None)
if w0:
    findings.append({
        'finding_id': 'F-004',
        'severity': 'MEDIUM',
        'category': 'UNVERIFIED_READY_STATE',
        'description': (
            f'Wave 0 tasks {w0.get("tasks",[])} marked READY but repository implementation unverified. '
            'CT-001 requires actual validator count verification before claiming READY.'
        ),
        'affected_artifact': 'wave-registry.json',
        'repair_action': 'RECALCULATE_TASK_STATES_FROM_REPOSITORY_TRUTH'
    })

if not_mapped_tasks:
    findings.append({
        'finding_id': 'F-005',
        'severity': 'CRITICAL',
        'category': 'UNMAPPED_SOURCE_TASKCARDS',
        'description': f'{len(not_mapped_tasks)} source taskcards have disposition NOT_MAPPED. These cannot be closed.',
        'affected_artifact': 'provenance-map.json',
        'repair_action': 'ASSIGN_EXECUTABLE_TASK_TO_EVERY_SOURCE_TASKCARD'
    })

controller_file = root / 'controller' / 'portfolio_controller.py'
if not controller_file.exists():
    findings.append({
        'finding_id': 'F-006',
        'severity': 'CRITICAL',
        'category': 'MISSING_CONTROLLER',
        'description': 'No portfolio controller exists. execution-handoff.json lists ready tasks but has no execution mechanism.',
        'affected_artifact': 'controller/',
        'repair_action': 'BUILD_PORTFOLIO_CONTROLLER'
    })

if not list((root / 'schemas').glob('*.json')):
    findings.append({
        'finding_id': 'F-007',
        'severity': 'HIGH',
        'category': 'MISSING_SCHEMAS',
        'description': 'No JSON schemas exist. All state transitions are unvalidated.',
        'affected_artifact': 'schemas/',
        'repair_action': 'CREATE_JSON_SCHEMAS_FOR_ALL_ARTIFACT_TYPES'
    })

if not list((root / 'task-packets').glob('*.json')):
    findings.append({
        'finding_id': 'F-008',
        'severity': 'CRITICAL',
        'category': 'MISSING_TASK_PACKETS',
        'description': 'No task packets exist. A fresh worker cannot execute any task without loading all 41 plans.',
        'affected_artifact': 'task-packets/',
        'repair_action': 'GENERATE_ONE_TASK_PACKET_PER_EXECUTABLE_TASK'
    })

if nodes and all((n if isinstance(n, str) else n.get('node_id', '')).startswith('CT-') for n in nodes):
    findings.append({
        'finding_id': 'F-009',
        'severity': 'HIGH',
        'category': 'COARSE_DEPENDENCY_GRAPH',
        'description': (
            f'Dependency graph has {len(nodes)} nodes at canonical-task granularity. '
            'Must be rebuilt at executable-task granularity after task splitting.'
        ),
        'affected_artifact': 'dependency-graph.json',
        'repair_action': 'REBUILD_DEPENDENCY_GRAPH_AT_EXECUTABLE_TASK_GRANULARITY'
    })

findings.append({
    'finding_id': 'F-010',
    'severity': 'HIGH',
    'category': 'MISLEADING_HANDOFF_STATUS',
    'description': (
        'execution-handoff.json claims HANDOFF_READY / verdict=ACCEPT from RECONCILE_ONLY review. '
        'That review explicitly could not validate execution readiness.'
    ),
    'affected_artifact': 'execution-handoff.json',
    'repair_action': 'RESET_TO_REPAIR_IN_PROGRESS'
})

# Check for TERMINAL_CLOSED plans incorrectly mapped
terminal_plans = ['s036', 's039']
findings.append({
    'finding_id': 'F-011',
    'severity': 'MEDIUM',
    'category': 'TERMINAL_PLAN_DISPOSITION',
    'description': (
        f'Plans {terminal_plans} self-declare TERMINAL_CLOSED in source content. '
        'Their source taskcards must each have individual dispositions, not plan-level bulk closure.'
    ),
    'affected_artifact': 'provenance-map.json',
    'repair_action': 'VERIFY_INDIVIDUAL_TASKCARD_DISPOSITIONS_FOR_TERMINAL_PLANS'
})

findings.append({
    'finding_id': 'F-012',
    'severity': 'HIGH',
    'category': 'ZERO_TC_PLANS_SUPPLEMENTED_WITHOUT_VERIFICATION',
    'description': (
        'Plans s003, s005, s010, s012, s015, s030 had 0 taskcards extracted by regex and were '
        'supplemented with manually assumed TC IDs (e.g. TC-GOV-001..023 for s005). '
        'These assumed IDs must be verified against the actual plan files.'
    ),
    'affected_artifact': 'plan-registry/',
    'repair_action': 'VERIFY_SUPPLEMENTED_TASKCARD_IDS_AGAINST_SOURCE_PLANS'
})

findings.append({
    'finding_id': 'F-013',
    'severity': 'MEDIUM',
    'category': 'VALIDATOR_COUNT_CONFLICT_UNRESOLVED',
    'description': (
        'CONFLICT-004 (SHARED_REQUIREMENT REQ-VALCOUNT-001): MEMORY.md says 165 validators, '
        'governance_validator_runner.py has expected_count=167. CT-001 records this but no '
        'repository investigation was done to determine the ground truth.'
    ),
    'affected_artifact': 'task-registry.json / tools/supervisor/governance_validator_runner.py',
    'repair_action': 'INVESTIGATE_ACTUAL_VALIDATOR_COUNT_BEFORE_CREATING_FIX_TASK'
})

audit = {
    'schema_version': '1.0',
    'audit_type': 'PRE_EXECUTION_AUDIT',
    'audited_at': now,
    'auditor': 'claude-sonnet-4-6',
    'portfolio_id': manifest.get('portfolio_id'),
    'prior_mode': 'RECONCILE_ONLY',
    'current_mode': 'RECONCILE_REPAIR_AND_EXECUTE',
    'artifacts_inspected': {
        'portfolio_manifest': True,
        'source_inventory_entries': len(inventory.get('sources', [])),
        'plan_records': len(plan_records),
        'checklists': len(checklists),
        'canonical_requirements': len(req_reg.get('requirements', [])),
        'canonical_tasks': canonical_task_count,
        'provenance_source_task_mappings': len(prov.get('source_task_mappings', [])),
        'source_taskcards_in_plan_records': total_source_tcs,
        'relationship_records': len(rel.get('relationship_records', [])),
        'dependency_graph_nodes': len(nodes),
        'dependency_graph_edges': len(dep.get('edges', [])),
        'wave_count': len(wave_data),
        'journal_events': len(journal_events),
        'snapshots': len(list((root / 'snapshots').glob('*.json'))) if (root / 'snapshots').exists() else 0,
    },
    'finding_count': len(findings),
    'critical_findings': len([f for f in findings if f['severity'] == 'CRITICAL']),
    'high_findings': len([f for f in findings if f['severity'] == 'HIGH']),
    'medium_findings': len([f for f in findings if f['severity'] == 'MEDIUM']),
    'findings': findings,
    'required_repairs': [
        'SPLIT_26_CANONICAL_TASKS_INTO_ATOMIC_EXECUTABLE_TASKS',
        'MAP_ALL_SOURCE_TASKCARDS_TO_EXECUTABLE_TASKS',
        'VERIFY_SUPPLEMENTED_TASKCARD_IDS_AGAINST_SOURCE_PLANS',
        'BUILD_PORTFOLIO_CONTROLLER',
        'CREATE_JSON_SCHEMAS',
        'GENERATE_TASK_PACKETS',
        'REBUILD_DEPENDENCY_GRAPH_AT_EXECUTABLE_TASK_GRANULARITY',
        'RECALCULATE_TASK_STATES_FROM_REPOSITORY_TRUTH',
        'RESET_MISLEADING_HANDOFF_STATUS',
        'INVESTIGATE_VALIDATOR_COUNT_GROUND_TRUTH',
    ],
    'verdict': 'REQUIRES_FULL_REPAIR_BEFORE_EXECUTION',
}

out = root / 'repairs' / 'pre-execution-audit.json'
out.write_text(json.dumps(audit, indent=2))
print(f'Written: {out}')
print(f'Findings: {len(findings)} total — {audit["critical_findings"]} CRITICAL, {audit["high_findings"]} HIGH, {audit["medium_findings"]} MEDIUM')
print(f'Source TCs in plan records: {total_source_tcs}')
print(f'Plans without canonical_task_ids: {plan_without_tasks}')
print(f'NOT_MAPPED source taskcards: {len(not_mapped_tasks)}')
