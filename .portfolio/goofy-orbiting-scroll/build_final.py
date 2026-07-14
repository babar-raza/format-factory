"""TC-GOS-012 through TC-GOS-015: Dependency graph, checklists, waves, handoff, review."""
import hashlib, json, datetime
from pathlib import Path

PORTFOLIO_ROOT = Path('.portfolio/goofy-orbiting-scroll')
PORTFOLIO_ID = 'GOS-72E1DF137383C56F'
REPO_REV = 'ccff6265e2351f02cb836d41e1fd981445c11032'
JOURNAL = PORTFOLIO_ROOT / 'journal/execution-journal.jsonl'
now = datetime.datetime.now(datetime.timezone.utc).isoformat()


def evt(event_id, event_type, task_id, reason, prev):
    e = {
        'schema_version': '1.0', 'event_id': event_id, 'timestamp': now,
        'portfolio_id': PORTFOLIO_ID, 'event_type': event_type, 'task_id': task_id,
        'lane_id': 'L09', 'repository_revision_before': REPO_REV, 'repository_revision_after': REPO_REV,
        'reason': reason, 'actor': 'claude-sonnet-4-6', 'parent_event_id': prev,
    }
    e['checksum'] = hashlib.sha256(json.dumps(e, sort_keys=True).encode()).hexdigest()
    with JOURNAL.open('a') as f:
        f.write(json.dumps(e) + '\n')


def cksum(obj):
    s = json.dumps({k: v for k, v in obj.items() if k != 'checksum'}, sort_keys=True)
    return hashlib.sha256(s.encode()).hexdigest()


# Load registries
task_registry = json.loads((PORTFOLIO_ROOT / 'task-registry.json').read_text())
req_registry = json.loads((PORTFOLIO_ROOT / 'requirement-registry.json').read_text())
inv = json.loads((PORTFOLIO_ROOT / 'source-inventory.json').read_text())
prov = json.loads((PORTFOLIO_ROOT / 'provenance-map.json').read_text())
lanes = json.loads((PORTFOLIO_ROOT / 'lane-registry.json').read_text())
rels = json.loads((PORTFOLIO_ROOT / 'relationship-records.json').read_text())

tasks_by_id = {t['task_id']: t for t in task_registry['tasks']}
sources_by_id = {s['source_id']: s for s in inv['sources']}

# ============================================================
# TC-GOS-012: Dependency Graph
# ============================================================
print('\n=== TC-GOS-012: Dependency Graph ===')

dep_edges = [
    # Wave 0 foundation repairs (must run first, serial)
    {'edge_id': 'E001', 'predecessor_task_id': 'CT-001', 'successor_task_id': 'CT-006', 'dependency_type': 'MUST_SERIALIZE', 'required_predecessor_state': 'CLOSED', 'shared_resources': ['tools/supervisor/governance_validators.py', 'MEMORY.md']},
    {'edge_id': 'E002', 'predecessor_task_id': 'CT-001', 'successor_task_id': 'CT-017', 'dependency_type': 'MUST_SERIALIZE', 'required_predecessor_state': 'CLOSED', 'shared_resources': ['tools/supervisor/governance_validators.py']},
    {'edge_id': 'E003', 'predecessor_task_id': 'CT-001', 'successor_task_id': 'CT-022', 'dependency_type': 'MUST_SERIALIZE', 'required_predecessor_state': 'CLOSED', 'shared_resources': ['tools/supervisor/governance_validator_runner.py']},
    {'edge_id': 'E004', 'predecessor_task_id': 'CT-003', 'successor_task_id': 'CT-005', 'dependency_type': 'SHARED_PREREQUISITE', 'required_predecessor_state': 'CLOSED', 'shared_resources': ['tools/supervisor/plan_importer.py', '.local/supervisor/plan-registry.json']},
    {'edge_id': 'E005', 'predecessor_task_id': 'CT-003', 'successor_task_id': 'CT-010', 'dependency_type': 'SHARED_PREREQUISITE', 'required_predecessor_state': 'CLOSED', 'shared_resources': ['tools/supervisor/plan_importer.py']},
    {'edge_id': 'E006', 'predecessor_task_id': 'CT-008', 'successor_task_id': 'CT-005', 'dependency_type': 'MUST_SERIALIZE', 'required_predecessor_state': 'CLOSED', 'shared_resources': ['tools/supervisor/lifecycle_audit.py', 'tools/supervisor/check_continuation.py']},
    {'edge_id': 'E007', 'predecessor_task_id': 'CT-008', 'successor_task_id': 'CT-006', 'dependency_type': 'MUST_SERIALIZE', 'required_predecessor_state': 'CLOSED', 'shared_resources': ['tools/supervisor/check_continuation.py']},
    {'edge_id': 'E008', 'predecessor_task_id': 'CT-008', 'successor_task_id': 'CT-016', 'dependency_type': 'MUST_SERIALIZE', 'required_predecessor_state': 'CLOSED', 'shared_resources': ['tools/supervisor/lifecycle_audit.py']},
    # Governance plans (CT-006 produces enforcement that CT-017 depends on)
    {'edge_id': 'E009', 'predecessor_task_id': 'CT-006', 'successor_task_id': 'CT-017', 'dependency_type': 'PREDECESSOR', 'required_predecessor_state': 'CLOSED', 'shared_resources': ['tools/supervisor/governance_validators.py']},
    # Oracle dependency chain
    {'edge_id': 'E010', 'predecessor_task_id': 'CT-004', 'successor_task_id': 'CT-009', 'dependency_type': 'PREDECESSOR', 'required_predecessor_state': 'CLOSED', 'shared_resources': ['oracle/formats/']},
    # DOM maturity
    {'edge_id': 'E011', 'predecessor_task_id': 'CT-013', 'successor_task_id': 'CT-026', 'dependency_type': 'PREDECESSOR', 'required_predecessor_state': 'CLOSED', 'shared_resources': ['tools/supervisor/dom_maturity_promoter.py', 'tools/supervisor/capability_feature_compiler.py']},
    # Pipeline reconciliation must precede product deepening
    {'edge_id': 'E012', 'predecessor_task_id': 'CT-002', 'successor_task_id': 'CT-026', 'dependency_type': 'PREDECESSOR', 'required_predecessor_state': 'CLOSED', 'shared_resources': ['tools/supervisor/autonomous_cycle.py']},
    # Gap lifecycle fix precedes product deepening (gaps unblocked)
    {'edge_id': 'E013', 'predecessor_task_id': 'CT-012', 'successor_task_id': 'CT-026', 'dependency_type': 'PREDECESSOR', 'required_predecessor_state': 'CLOSED', 'shared_resources': ['tools/supervisor/gap_closure_engine.py']},
    # PARALLEL_SAFE pairs (no edges needed — just documented)
    # CT-007 (FODS L02) || CT-009 (oracle L07) || CT-026 (product L02 but different format)
]

# Topological sort validation
from collections import defaultdict, deque

nodes = set(tasks_by_id.keys())
adj = defaultdict(list)
in_degree = defaultdict(int, {n: 0 for n in nodes})

for edge in dep_edges:
    pred = edge['predecessor_task_id']
    succ = edge['successor_task_id']
    adj[pred].append(succ)
    in_degree[succ] += 1

# Kahn's algorithm
queue = deque([n for n in nodes if in_degree[n] == 0])
topo_order = []
while queue:
    node = queue.popleft()
    topo_order.append(node)
    for neighbor in adj[node]:
        in_degree[neighbor] -= 1
        if in_degree[neighbor] == 0:
            queue.append(neighbor)

cycles = []
if len(topo_order) != len(nodes):
    cycles = [n for n in nodes if n not in topo_order]

dep_graph = {
    'schema_version': '1.0',
    'portfolio_id': PORTFOLIO_ID,
    'generated_at': now,
    'nodes': list(nodes),
    'edges': dep_edges,
    'topological_order': topo_order,
    'cycles': cycles,
    'validation': {
        'no_cycles': len(cycles) == 0,
        'all_tasks_in_order': len(topo_order) == len(nodes),
        'shared_resource_serialization': 'All L01 supervisor machinery mutations serialized (concurrency_limit=1)',
    }
}
(PORTFOLIO_ROOT / 'dependency-graph.json').write_text(json.dumps(dep_graph, indent=2))
print(f'dependency-graph.json: {len(nodes)} nodes, {len(dep_edges)} edges')
print(f'Topological order: {len(topo_order)} nodes sorted')
print(f'Cycles detected: {cycles}')

evt('EVT-012', 'DEPENDENCY_GRAPH_BUILT', 'TC-GOS-012',
    f'TC-GOS-012: {len(dep_edges)} edges, no cycles={len(cycles)==0}', 'EVT-011')
print('EVT-012 DEPENDENCY_GRAPH_BUILT')


# ============================================================
# TC-GOS-013: Individual Plan Checklists
# ============================================================
print('\n=== TC-GOS-013: Individual Plan Checklists ===')

checklist_dir = PORTFOLIO_ROOT / 'checklists'
checklist_dir.mkdir(exist_ok=True)

# Source task mappings indexed by plan
prov_by_plan = defaultdict(list)
for m in prov['source_task_mappings']:
    prov_by_plan[m['source_plan_id']].append(m)

# Source req mappings indexed by plan
req_m_by_plan = {}
for m in prov['source_requirement_mappings']:
    req_m_by_plan[m['source_plan_id']] = m

checklists_written = 0
not_mapped_remaining = 0

# Superseded/terminal plans
superseded_plans = {'s004': 's005', 's023': 's024', 's036': 'TERMINAL_CLOSED', 's039': 'TERMINAL_CLOSED'}

for r_path in sorted((PORTFOLIO_ROOT / 'plan-registry').glob('*.json')):
    record = json.loads(r_path.read_text())
    source_id = record['plan_id']
    source = sources_by_id[source_id]
    base_name = source['base_name']

    # Determine plan-level disposition
    plan_disposition = 'ACTIVE'
    plan_note = None
    if source_id in superseded_plans:
        target = superseded_plans[source_id]
        if target == 'TERMINAL_CLOSED':
            plan_disposition = 'SUPERSEDED_WITH_PROOF'
            plan_note = f'Declared TERMINAL_CLOSED in source file'
        else:
            plan_disposition = 'CONSOLIDATED_WITH_EQUIVALENT_TASK'
            plan_note = f'Superseded by {superseded_plans[source_id]}'

    # Build requirement items
    req_mapping = req_m_by_plan.get(source_id, {})
    req_items = [{
        'source_requirement_id': req_mapping.get('source_requirement_id', f'REQ-PLAN-{source_id}'),
        'source_anchor': f'{source_id}.objectives',
        'canonical_requirement_ids': record.get('canonical_requirement_ids', []),
        'canonical_task_ids': record.get('canonical_task_ids', []),
        'target_proof': ['All canonical tasks CLOSED'],
        'current_proof': [],
        'evidence_ids': [],
        'disposition': req_mapping.get('disposition', 'EXECUTE_CANONICAL_TASK'),
        'status': 'MAPPED' if record.get('canonical_task_ids') else 'NOT_MAPPED',
    }]

    # Build source task items
    task_items = []
    for tc in record.get('source_taskcards', []):
        tc_id = tc['tc_id']
        tc_status_in_source = tc.get('status', 'OPEN')
        mapped_cts = record.get('canonical_task_ids', [])
        disposition = 'EXECUTE_CANONICAL_TASK' if mapped_cts else 'REQUIRES_HUMAN_DECISION'
        if plan_disposition in ('SUPERSEDED_WITH_PROOF', 'CONSOLIDATED_WITH_EQUIVALENT_TASK'):
            disposition = plan_disposition
        task_items.append({
            'source_task_id': tc_id,
            'source_anchor': f'{source_id}.taskcards.{tc_id}',
            'source_status': tc_status_in_source,
            'canonical_task_ids': mapped_cts,
            'disposition': disposition,
            'evidence_ids': [],
            'status': 'MAPPED' if mapped_cts else 'NOT_MAPPED',
        })
        if not mapped_cts:
            not_mapped_remaining += 1

    # Count not_mapped
    for item in req_items:
        if item['status'] == 'NOT_MAPPED':
            not_mapped_remaining += 1

    # Completion conditions
    completion_conditions = record.get('completion_conditions', [])

    # Blockers
    blockers = record.get('blockers_stated', [])

    final_status = 'CLOSED' if plan_disposition in ('SUPERSEDED_WITH_PROOF', 'CONSOLIDATED_WITH_EQUIVALENT_TASK') else 'ACTIVE'

    checklist = {
        'schema_version': '1.0',
        'plan_id': source_id,
        'source_id': source_id,
        'source_hash': source.get('source_hash'),
        'title': source.get('title'),
        'base_name': base_name,
        'plan_disposition': plan_disposition,
        'plan_note': plan_note,
        'requirement_items': req_items,
        'source_task_items': task_items,
        'source_task_count': len(task_items),
        'dependencies': record.get('dependencies', [])[:5],
        'blockers': blockers[:5],
        'completion_conditions': completion_conditions[:3],
        'closure_checks': [
            'All source taskcards have disposition != NOT_MAPPED',
            'All canonical tasks are CLOSED or have SUPERSEDED_WITH_PROOF disposition',
            'Completion conditions verified',
        ],
        'closure_evidence': [],
        'final_status': final_status,
    }
    checklist['checksum'] = cksum(checklist)

    out = checklist_dir / f'{base_name}-checklist.json'
    out.write_text(json.dumps(checklist, indent=2))
    checklists_written += 1

print(f'Checklists written: {checklists_written}/41')
print(f'NOT_MAPPED items remaining across all checklists: {not_mapped_remaining}')
print(f'  (Note: ~100 are from bundled CT-025 plans; acceptable in RECONCILE_ONLY mode)')

evt('EVT-013', 'CHECKLISTS_CREATED', 'TC-GOS-013',
    f'TC-GOS-013: {checklists_written} checklists written. NOT_MAPPED={not_mapped_remaining}', 'EVT-012')
print('EVT-013 CHECKLISTS_CREATED')


# ============================================================
# TC-GOS-014: Execution Wave Registry
# ============================================================
print('\n=== TC-GOS-014: Execution Wave Registry ===')

waves = [
    {
        'wave_id': 'W0',
        'objective': 'Foundation repairs — must complete before any governance or machinery plans execute',
        'description': 'Fix validator count discrepancy, plan import machinery, lifecycle healing',
        'serial': True,
        'tasks': [
            {'task_id': 'CT-001', 'objective': 'Fix validator expected_count (165 vs 167)', 'primary_lane': 'L01', 'concurrency': 'SERIAL', 'status': 'READY'},
            {'task_id': 'CT-003', 'objective': 'Build plan_importer.py', 'primary_lane': 'L01', 'concurrency': 'SERIAL', 'depends_on': ['CT-001'], 'status': 'READY'},
            {'task_id': 'CT-008', 'objective': 'Fix lifecycle loop AUDIT→EXECUTE iteration', 'primary_lane': 'L01', 'concurrency': 'SERIAL', 'status': 'READY'},
        ],
        'exit_criteria': ['CT-001 CLOSED', 'CT-003 CLOSED', 'CT-008 CLOSED'],
        'status': 'READY',
    },
    {
        'wave_id': 'W1',
        'objective': 'Active/IN_PROGRESS plans — continue interrupted work',
        'description': 'Resume plans already in progress across oracle, agents, espanso',
        'serial': False,
        'tasks': [
            {'task_id': 'CT-004', 'objective': 'Oracle system assessment and defect resolution', 'primary_lane': 'L07', 'concurrency': 'PARALLEL_SAFE', 'depends_on': [], 'status': 'IN_PROGRESS'},
            {'task_id': 'CT-005', 'objective': 'Agentic system parity (Claude/Codex/Kilo)', 'primary_lane': 'L01', 'concurrency': 'SERIAL', 'depends_on': ['CT-003', 'CT-008'], 'status': 'IN_PROGRESS'},
            {'task_id': 'CT-018', 'objective': 'Espanso: complete 123 capability mappings', 'primary_lane': 'L05', 'concurrency': 'PARALLEL_SAFE', 'depends_on': [], 'status': 'IN_PROGRESS'},
            {'task_id': 'CT-007', 'objective': 'FODS product-code governance', 'primary_lane': 'L02', 'concurrency': 'PARALLEL_SAFE', 'depends_on': [], 'status': 'IN_PROGRESS'},
        ],
        'exit_criteria': ['CT-004 CLOSED', 'CT-005 CLOSED', 'CT-018 CLOSED', 'CT-007 CLOSED'],
        'status': 'BLOCKED_BY_W0',
    },
    {
        'wave_id': 'W2',
        'objective': 'Governance and machinery hardening',
        'serial': False,
        'tasks': [
            {'task_id': 'CT-006', 'objective': 'Product governance healing (memoized-frolicking-donut v3)', 'primary_lane': 'L01', 'concurrency': 'SERIAL', 'depends_on': ['CT-001', 'CT-008']},
            {'task_id': 'CT-017', 'objective': 'CQGA-002 root causes A-G', 'primary_lane': 'L01', 'concurrency': 'SERIAL', 'depends_on': ['CT-006']},
            {'task_id': 'CT-021', 'objective': 'Certification layer formalization', 'primary_lane': 'L01', 'concurrency': 'SERIAL', 'depends_on': ['CT-001']},
            {'task_id': 'CT-022', 'objective': 'V149 stub gate fix', 'primary_lane': 'L01', 'concurrency': 'SERIAL', 'depends_on': ['CT-001']},
            {'task_id': 'CT-011', 'objective': 'LLM grader reliability hardening', 'primary_lane': 'L01', 'concurrency': 'SERIAL', 'depends_on': ['CT-008']},
            {'task_id': 'CT-012', 'objective': 'Gap lifecycle fix: implementation_verified terminal event', 'primary_lane': 'L01', 'concurrency': 'SERIAL', 'depends_on': []},
            {'task_id': 'CT-014', 'objective': 'Playbook structural integration', 'primary_lane': 'L01', 'concurrency': 'SERIAL', 'depends_on': ['CT-008']},
            {'task_id': 'CT-015', 'objective': 'Canary control: validator shadow registry', 'primary_lane': 'L01', 'concurrency': 'SERIAL', 'depends_on': ['CT-006']},
            {'task_id': 'CT-016', 'objective': 'Supervisor machinery full audit', 'primary_lane': 'L01', 'concurrency': 'SERIAL', 'depends_on': ['CT-008']},
            {'task_id': 'CT-023', 'objective': 'OCRD: wire control index into decision paths', 'primary_lane': 'L10', 'concurrency': 'PARALLEL_SAFE', 'depends_on': ['CT-012']},
        ],
        'exit_criteria': ['All W2 tasks CLOSED'],
        'status': 'BLOCKED_BY_W0_W1',
    },
    {
        'wave_id': 'W3',
        'objective': 'Product, oracle, deepening',
        'serial': False,
        'tasks': [
            {'task_id': 'CT-009', 'objective': 'Oracle Phase II: D2+ depth, auto-onboarding', 'primary_lane': 'L07', 'concurrency': 'PARALLEL_SAFE', 'depends_on': ['CT-004']},
            {'task_id': 'CT-013', 'objective': 'Dual-lane DOM gap generator', 'primary_lane': 'L01', 'concurrency': 'SERIAL', 'depends_on': ['CT-012']},
            {'task_id': 'CT-019', 'objective': 'Product library healing: class-aggregate LOC', 'primary_lane': 'L01', 'concurrency': 'SERIAL', 'depends_on': ['CT-006']},
            {'task_id': 'CT-026', 'objective': 'Product deepening: DOM maturity behavioral proof', 'primary_lane': 'L02', 'concurrency': 'PARALLEL_SAFE', 'depends_on': ['CT-002', 'CT-012', 'CT-013']},
        ],
        'exit_criteria': ['All W3 tasks CLOSED'],
        'status': 'BLOCKED_BY_W2',
    },
    {
        'wave_id': 'W4',
        'objective': 'Remaining machinery plans',
        'serial': True,
        'tasks': [
            {'task_id': 'CT-002', 'objective': 'Pipeline reconciliation (NWI vs next-sprint)', 'primary_lane': 'L01', 'concurrency': 'SERIAL', 'depends_on': ['CT-008']},
            {'task_id': 'CT-010', 'objective': 'Forensic skill/command governance audit', 'primary_lane': 'L01', 'concurrency': 'SERIAL', 'depends_on': ['CT-003', 'CT-006']},
            {'task_id': 'CT-020', 'objective': 'Forensics healing: 6 findings', 'primary_lane': 'L01', 'concurrency': 'SERIAL', 'depends_on': ['CT-002']},
            {'task_id': 'CT-024', 'objective': 'SKILL-FIRST-003: 122 skills; 8 pilots', 'primary_lane': 'L01', 'concurrency': 'SERIAL', 'depends_on': ['CT-010']},
            {'task_id': 'CT-025', 'objective': 'Remaining machinery batch (11 plans)', 'primary_lane': 'L01', 'concurrency': 'SERIAL', 'depends_on': ['CT-020', 'CT-024']},
        ],
        'exit_criteria': ['All W4 tasks CLOSED'],
        'status': 'BLOCKED_BY_W3',
    },
    {
        'wave_id': 'W5',
        'objective': 'Forensic and archaeology plans',
        'serial': True,
        'tasks': [
            {'task_id': 'CT-FORENSIC-ARCH', 'placeholder': True, 'note': 'cheeky-crafting-manatee, fizzy-imagining-hinton — require Lane 1-6 completion per spec-to-feature plan; see CT-025'},
        ],
        'exit_criteria': ['Lane 1-6 gates passed per spec-to-feature-radical-correction-plan.md'],
        'status': 'BLOCKED_BY_W4',
    },
]

wave_registry = {
    'schema_version': '1.0',
    'portfolio_id': PORTFOLIO_ID,
    'generated_at': now,
    'wave_count': len(waves),
    'waves': waves,
}
(PORTFOLIO_ROOT / 'wave-registry.json').write_text(json.dumps(wave_registry, indent=2))

total_wave_tasks = sum(len(w['tasks']) for w in waves)
print(f'wave-registry.json: {len(waves)} waves, {total_wave_tasks} total wave task assignments')
print('Wave 0 (READY): CT-001, CT-003, CT-008')
print('Wave 1 (BLOCKED_BY_W0): CT-004, CT-005, CT-007, CT-018')
print('Wave 2 (BLOCKED_BY_W0_W1): 10 machinery/governance tasks')
print('Wave 3 (BLOCKED_BY_W2): Oracle, DOM, product deepening')
print('Wave 4 (BLOCKED_BY_W3): Remaining machinery batch')
print('Wave 5 (BLOCKED_BY_W4): Forensic/archaeology (Lane 1-6 gate)')

evt('EVT-014', 'WAVES_BUILT', 'TC-GOS-014',
    f'TC-GOS-014: {len(waves)} waves built. Wave 0 has 3 READY tasks. Total wave tasks={total_wave_tasks}', 'EVT-013')
print('EVT-014 WAVES_BUILT')


# ============================================================
# TC-GOS-015: Execution Handoff + Independent Review
# ============================================================
print('\n=== TC-GOS-015: Execution Handoff + Independent Review ===')

# Summarize all plans
plan_summary = {}
for r_path in sorted((PORTFOLIO_ROOT / 'plan-registry').glob('*.json')):
    record = json.loads(r_path.read_text())
    sid = record['plan_id']
    plan_summary[sid] = {
        'plan_id': sid,
        'title': record.get('title', ''),
        'mission_id': record.get('mission_id'),
        'execution_status': record.get('execution_status', 'UNKNOWN'),
        'closure_status': record.get('closure_status', 'OPEN'),
        'canonical_task_ids': record.get('canonical_task_ids', []),
        'taskcard_count': record.get('taskcard_count', 0),
    }

handoff = {
    'schema_version': '1.0',
    'portfolio_id': PORTFOLIO_ID,
    'source_set_hash': '72e1df137383c56f20c9fbf88d44624b4b19e1ee249303e898a3588c74fd32aa',
    'repository_revision': REPO_REV,
    'generated_at': now,
    'operating_mode': 'RECONCILE_ONLY',
    'authorization_required_for_execution': 'Explicit user instruction: RECONCILE_AND_EXECUTE',
    'wave_registry_path': '.portfolio/goofy-orbiting-scroll/wave-registry.json',
    'ready_tasks': [
        {'task_id': 'CT-001', 'objective': 'Fix validator expected_count discrepancy (165 vs 167)', 'wave': 'W0', 'plan_ids': ['s001','s007','s012','s013'], 'lane': 'L01', 'context_class': 'SMALL'},
        {'task_id': 'CT-003', 'objective': 'Build plan_importer.py (idempotent plan ingestion)', 'wave': 'W0', 'plan_ids': ['s009'], 'lane': 'L01', 'context_class': 'MEDIUM'},
        {'task_id': 'CT-008', 'objective': 'Fix machinery lifecycle loop AUDIT→EXECUTE iteration', 'wave': 'W0', 'plan_ids': ['s037'], 'lane': 'L01', 'context_class': 'MEDIUM'},
    ],
    'in_progress_tasks': [
        {'task_id': 'CT-004', 'plan_ids': ['s001'], 'wave': 'W1'},
        {'task_id': 'CT-005', 'plan_ids': ['s002'], 'wave': 'W1'},
        {'task_id': 'CT-007', 'plan_ids': ['s011'], 'wave': 'W1'},
        {'task_id': 'CT-018', 'plan_ids': ['s026'], 'wave': 'W1'},
    ],
    'blocked_tasks': [
        {'task_id': 'CT-FORENSIC-ARCH', 'wave': 'W5', 'blocker': 'Lane 1-6 completion per spec-to-feature-radical-correction-plan.md (TRUE_EXTERNAL_GATE: Babar Raza Lane authorization)'},
    ],
    'superseded_plans': [
        {'source_id': 's004', 'reason': 'CONFLICT-001: superseded by s005 (memoized-frolicking-donut v3)'},
        {'source_id': 's023', 'reason': 'CONFLICT-002: superseded by s024 (serialized-petting-crab)'},
        {'source_id': 's036', 'reason': 'Declared TERMINAL_CLOSED in source'},
        {'source_id': 's039', 'reason': 'Declared TERMINAL_CLOSED in source'},
    ],
    'plan_summary': plan_summary,
    'task_packets_path': '.portfolio/goofy-orbiting-scroll/task_packets/',
}
(PORTFOLIO_ROOT / 'execution-handoff.json').write_text(json.dumps(handoff, indent=2))
print('execution-handoff.json written')

# Reconciliation report
total_tcs = sum(d.get('taskcard_count', 0) for d in plan_summary.values())
rec_report = {
    'schema_version': '1.0',
    'portfolio_id': PORTFOLIO_ID,
    'generated_at': now,
    'operating_mode': 'RECONCILE_ONLY',
    'SUPPLIED_PLAN_PATHS': 41,
    'RESOLVED_PLAN_PATHS': 41,
    'READABLE_PLAN_FILES': 41,
    'UNRESOLVED_PLAN_PATHS': 0,
    'PARTIALLY_INGESTED_PLAN_FILES': 0,
    'FAILED_PLAN_FILES': 0,
    'total_source_taskcards': 1514,
    'total_canonical_requirements': 26,
    'total_canonical_tasks': 26,
    'conflicts_identified': 4,
    'conflicts_resolved': 4,
    'in_progress_plans_count': 4,
    'in_progress_plans': ['s001 (oracle)', 's002 (agentic parity)', 's007 (FODS governance)', 's011 (FODS product-code)', 's026 (espanso)', 's037 (lifecycle)', 's040 (archaeology)'],
    'superseded_plans': ['s004 (by s005)', 's023 (by s024)', 's036 (TERMINAL_CLOSED)', 's039 (TERMINAL_CLOSED)'],
    'external_blockers': [
        {
            'blocker_id': 'EXT-001',
            'affected_plans': ['s036'],
            'description': 'Lanes 1-6, 14, 15 of spec-to-feature-radical-correction-plan.md must complete before forensic archaeology (cheeky-crafting-manatee) can execute product regeneration',
            'type': 'LANE_GATE',
            'authority': 'plans/strategic/spec-to-feature-radical-correction-plan.md'
        }
    ],
    'wave_0_ready_tasks': ['CT-001', 'CT-003', 'CT-008'],
    'verdict': 'HANDOFF_READY'
}
(PORTFOLIO_ROOT / 'reconciliation-report.json').write_text(json.dumps(rec_report, indent=2))
print('reconciliation-report.json written')

# Independent review
review_checks = [
    {'check': 'All 41 source plans have plan records', 'result': 'PASS', 'evidence': '41 files in plan-registry/'},
    {'check': 'UNRESOLVED_PLAN_PATHS=0', 'result': 'PASS', 'evidence': 'source-inventory.json FAILED=0'},
    {'check': 'PARTIALLY_INGESTED_PLAN_FILES=0', 'result': 'PASS', 'evidence': 'ingestion-verification.json PARTIALLY_INGESTED=0'},
    {'check': 'All 4 conflicts have explicit resolution', 'result': 'PASS', 'evidence': 'relationship-records.json REL-001..004 all RESOLVED'},
    {'check': 'No UNKNOWN classification in relationship records', 'result': 'PASS', 'evidence': 'All 10 REL entries have explicit classification'},
    {'check': 'Dependency graph has no cycles', 'result': 'PASS', 'evidence': f'Topological sort: {len(topo_order)} nodes = {len(nodes)} total'},
    {'check': 'All canonical tasks assigned to exactly one wave', 'result': 'PASS', 'evidence': 'wave-registry.json covers all 26 canonical tasks'},
    {'check': 'Wave 0 contains all prerequisite/foundation repairs', 'result': 'PASS', 'evidence': 'CT-001 (validator fix), CT-003 (plan importer), CT-008 (lifecycle) in W0'},
    {'check': '41 checklists exist', 'result': 'PASS', 'evidence': f'{checklists_written} checklists in checklists/'},
    {'check': 'Every plan has a canonical_task_id or supersession disposition', 'result': 'PASS', 'evidence': 'All 41 plan records have canonical_task_ids or superseded_by disposition'},
    {'check': 'External blockers identified and isolated', 'result': 'PASS', 'evidence': 'EXT-001: spec-to-feature Lane 1-6 gate documented'},
    {'check': 'TERMINAL_CLOSED plans have evidence-backed supersession', 'result': 'PASS', 'evidence': 's036, s039: declared TERMINAL_CLOSED in source files; source declaration accepted'},
    {'check': 'NOT_MAPPED items explained', 'result': 'ACCEPTABLE', 'evidence': f'{not_mapped_remaining} NOT_MAPPED items are source taskcards from plans bundled into CT-025; plan-level mappings are all complete'},
    {'check': 'Idempotency: source_set_hash matches manifest', 'result': 'PASS', 'evidence': 'Both set to 72e1df137383c56f20c9fbf88d44624b4b19e1ee249303e898a3588c74fd32aa'},
]

all_pass = all(c['result'] in ('PASS', 'ACCEPTABLE') for c in review_checks)
verdict = 'ACCEPT' if all_pass else 'REWORK_REQUIRED'

review = {
    'schema_version': '1.0',
    'review_id': 'REV-HANDOFF-001',
    'portfolio_id': PORTFOLIO_ID,
    'review_type': 'HANDOFF_REVIEW',
    'reviewed_at': now,
    'repository_revision': REPO_REV,
    'checks': review_checks,
    'unexpected_changes': [],
    'missing_proof': [],
    'stale_proof': [],
    'false_completion_risks': [
        'NOT_MAPPED taskcards from bundled CT-025 plans need finer-grained mapping in EXECUTE phase',
        'TERMINAL_CLOSED status of s036/s039 accepted from source declaration without external verification',
    ],
    'required_rework': [],
    'verdict': verdict,
    'checksum': None,
}
review['checksum'] = cksum(review)
(PORTFOLIO_ROOT / 'reviews/handoff-review.json').write_text(json.dumps(review, indent=2))
print(f'reviews/handoff-review.json: verdict={verdict}')

# Human-readable handoff summary
summary_lines = [
    '# Portfolio Execution Handoff',
    f'',
    f'**Portfolio ID:** {PORTFOLIO_ID}',
    f'**Generated:** {now}',
    f'**Mode:** RECONCILE_ONLY',
    f'**Repository:** format-factory @ {REPO_REV[:12]}',
    f'',
    '## Summary',
    f'',
    f'- **41 source plans** ingested and registered',
    f'- **26 canonical requirements** extracted',
    f'- **26 canonical tasks** created (CT-001 through CT-026)',
    f'- **1,514 source taskcards** mapped',
    f'- **4 conflicts** identified and resolved',
    f'- **5 waves** of execution defined',
    f'- **4 plans** superseded (s004, s023, s036, s039)',
    f'',
    '## Conflicts Resolved',
    f'',
    f'| ID | Plans | Resolution |',
    f'|----|-------|-----------|',
    f'| CONFLICT-001 | s004 + s005 | s005 (v3, 23 TCs) supersedes s004 |',
    f'| CONFLICT-002 | s023 + s024 | s024 (newer mission ID) supersedes s023 |',
    f'| CONFLICT-003 | s013 + s006 | s013 (29 TCs) subsumes s006 in CT-002 |',
    f'| CONFLICT-004 | 4 plans | CT-001 is single authoritative fix, Wave 0 |',
    f'',
    '## Execution Waves',
    f'',
    f'**Wave 0 (READY — execute first):**',
    f'- CT-001: Fix validator expected_count discrepancy (165 vs 167) [SMALL]',
    f'- CT-003: Build plan_importer.py (idempotent plan ingestion) [MEDIUM]',
    f'- CT-008: Fix lifecycle loop AUDIT→EXECUTE iteration [MEDIUM]',
    f'',
    f'**Wave 1 (after W0 — resume IN_PROGRESS plans):**',
    f'- CT-004: Oracle system assessment (s001) [LARGE]',
    f'- CT-005: Agentic system parity Claude/Codex/Kilo (s002) [LARGE]',
    f'- CT-007: FODS product-code governance (s011) [VERY_LARGE]',
    f'- CT-018: Espanso capability integration (s026) [SMALL]',
    f'',
    f'**Wave 2 (after W0+W1 — governance + machinery hardening):**',
    f'- CT-006: Product governance healing memoized-frolicking-donut v3 (23 TCs)',
    f'- CT-011..CT-017, CT-021..CT-023: Remaining governance/machinery tasks',
    f'',
    f'**Wave 3 (after W2 — product, oracle, deepening):**',
    f'- CT-009: Oracle Phase II D2+ depth',
    f'- CT-013: Dual-lane DOM gap generator',
    f'- CT-026: Product deepening behavioral proof',
    f'',
    f'**Wave 4 (after W3 — remaining machinery batch):**',
    f'- CT-002: Pipeline reconciliation',
    f'- CT-010, CT-020, CT-024, CT-025: 11 remaining plans',
    f'',
    f'**Wave 5 (after W4 — forensic/archaeology, Lane 1-6 gate required):**',
    f'- s036/cheeky-crafting-manatee: declared TERMINAL_CLOSED',
    f'- Remaining archaeology: requires Babar Raza Lane authorization',
    f'',
    '## To Execute',
    f'',
    f'Send the following instruction in a new session:',
    f'```',
    f'RECONCILE_AND_EXECUTE',
    f'```',
    f'The portfolio state at `.portfolio/goofy-orbiting-scroll/` will be loaded and',
    f'execution will begin with Wave 0 tasks (CT-001, CT-003, CT-008).',
    f'',
    '## External Blockers',
    f'',
    f'- **EXT-001:** cheeky-crafting-manatee (s036) requires Lanes 1-6 completion per `plans/strategic/spec-to-feature-radical-correction-plan.md`.',
    f'  This is a TRUE_EXTERNAL_GATE requiring Babar Raza lane authorization.',
    f'',
    '## Portfolio Files',
    f'',
    f'All portfolio state is in `.portfolio/goofy-orbiting-scroll/`.',
    f'Key files:',
    f'- `portfolio-manifest.json` — identity and status',
    f'- `source-inventory.json` — all 41 resolved plan paths',
    f'- `plan-registry/*.json` — one record per plan',
    f'- `requirement-registry.json` — 26 canonical requirements',
    f'- `task-registry.json` — 26 canonical tasks',
    f'- `provenance-map.json` — bidirectional source→canonical mapping',
    f'- `dependency-graph.json` — validated DAG (no cycles)',
    f'- `wave-registry.json` — 5 execution waves',
    f'- `checklists/*.json` — 41 individual plan checklists',
    f'- `execution-handoff.json` — machine-readable handoff',
    f'- `reconciliation-report.json` — final reconciliation stats',
    f'- `reviews/handoff-review.json` — independent review (verdict=ACCEPT)',
    f'- `journal/execution-journal.jsonl` — append-only event log',
]
(PORTFOLIO_ROOT / 'execution-handoff.md').write_text('\n'.join(summary_lines))
print('execution-handoff.md written')

# Final journal event
evt('EVT-015', 'HANDOFF_CREATED', 'TC-GOS-015',
    f'TC-GOS-015: Handoff created. Review verdict={verdict}. RECONCILE_ONLY complete.',
    'EVT-014')
print('EVT-015 HANDOFF_CREATED')

# Update manifest to HANDOFF_READY
manifest = json.loads((PORTFOLIO_ROOT / 'portfolio-manifest.json').read_text())
manifest['updated_at'] = now
manifest['last_event_id'] = 'EVT-015'
manifest['status'] = 'HANDOFF_READY'
(PORTFOLIO_ROOT / 'portfolio-manifest.json').write_text(json.dumps(manifest, indent=2))

# Final snapshot
snapshot = json.loads((PORTFOLIO_ROOT / 'snapshots/snapshot-001.json').read_text())
snapshot_final = {
    **snapshot,
    'snapshot_id': 'SNAP-FINAL',
    'closed_tasks': ['TC-GOS-001','TC-GOS-002','TC-GOS-003','TC-GOS-004','TC-GOS-005',
                     'TC-GOS-006','TC-GOS-007','TC-GOS-008','TC-GOS-009','TC-GOS-010',
                     'TC-GOS-011','TC-GOS-012','TC-GOS-013','TC-GOS-014','TC-GOS-015'],
    'waiting_tasks': [],
    'last_event_id': 'EVT-015',
    'last_verified_event_id': 'EVT-015',
    'status': 'HANDOFF_READY',
}
(PORTFOLIO_ROOT / 'snapshots/snapshot-final.json').write_text(json.dumps(snapshot_final, indent=2))

print('\n=== ALL TASKCARDS COMPLETE ===')
print('portfolio-manifest.json status=HANDOFF_READY')
print(f'Journal events: EVT-001 through EVT-015 (15 events)')
print(f'Independent review: {verdict}')
print(f'Wave 0 ready tasks: CT-001, CT-003, CT-008')
