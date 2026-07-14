"""Generate task packets for all 54 executable tasks.
Each packet is self-contained — a fresh worker needs only the packet + repo inspection.
"""
import json, hashlib, datetime
from pathlib import Path

ROOT = Path('.portfolio/goofy-orbiting-scroll')
PACKETS_DIR = ROOT / 'task-packets'
PACKETS_DIR.mkdir(exist_ok=True)
PORTFOLIO_ID = 'GOS-72E1DF137383C56F'
now = datetime.datetime.now(datetime.timezone.utc).isoformat()

tasks = []
for p in sorted((ROOT / 'executable-tasks').glob('*.json')):
    tasks.append(json.loads(p.read_text(encoding='utf-8')))

written = 0
for task in tasks:
    tid = task['task_id']
    # Build packet from task definition
    packet = {
        'schema_version': '1.0',
        'portfolio_id': PORTFOLIO_ID,
        'task_id': tid,
        'workstream_id': task['workstream_id'],
        'objective': task['objective'],
        'source_plan_ids': task['source_plan_ids'],
        'source_task_ids': task.get('source_task_ids', []),
        'source_anchors': task.get('source_anchors', []),
        'original_source_text_references': [],
        'repository_assessment': task.get('repository_assessment', 'NOT_STARTED'),
        'acceptance_criteria': task['acceptance_criteria'],
        'negative_acceptance_criteria': task.get('negative_acceptance_criteria', []),
        'prerequisites': task.get('prerequisites', []),
        'dependencies': task.get('dependencies', []),
        'affected_components': task.get('affected_components', []),
        'affected_paths': task.get('affected_paths', []),
        'allowed_mutation_scope': task.get('allowed_mutation_scope', task.get('affected_paths', [])),
        'forbidden_paths': task.get('forbidden_paths', []),
        'required_locks': task.get('affected_paths', []),
        'primary_lane': task.get('primary_lane', 'L01'),
        'integration_owner': task.get('integration_owner', 'claude-sonnet-4-6'),
        'implementation_steps': task.get('implementation_steps', []),
        'focused_validation': task.get('focused_verification', []),
        'lane_validation': task.get('lane_verification', []),
        'integration_validation': task.get('integration_verification', []),
        'regression_validation': task.get('regression_verification', []),
        'end_to_end_validation': task.get('end_to_end_verification', []),
        'pilot_validation': task.get('pilot_verification', []),
        'evidence_requirements': task.get('evidence_requirements', ['Implementation diff', 'Test output']),
        'rollback': task.get('rollback', 'git checkout -- .'),
        'cleanup': task.get('cleanup', ''),
        'invalidation_triggers': task.get('invalidation_triggers', []),
        'reopening_conditions': task.get('reopening_conditions', []),
        'expected_start_state': 'READY',
        'expected_terminal_state': 'CLOSED',
        'generated_at': now,
    }
    # Compute checksum (without the checksum field itself)
    chk = hashlib.sha256(json.dumps(packet, sort_keys=True).encode()).hexdigest()
    packet['packet_checksum'] = chk

    out = PACKETS_DIR / f'{tid}.json'
    out.write_text(json.dumps(packet, indent=2), encoding='utf-8')
    written += 1

print(f'Task packets written: {written}')
print(f'Location: {PACKETS_DIR}')
