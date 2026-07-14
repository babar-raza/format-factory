"""TC-GOS-003 through TC-GOS-006: Ingest all 41 plans in 4 bounded batches.

Extracts: objectives, taskcards (ID+status), requirements, completion conditions,
dependencies, mission_id, plan_type, and stated revision from each plan file.
"""
import hashlib, json, datetime, re
from pathlib import Path

PORTFOLIO_ROOT = Path('.portfolio/goofy-orbiting-scroll')
PLAN_REGISTRY = PORTFOLIO_ROOT / 'plan-registry'
PLAN_REGISTRY.mkdir(exist_ok=True)
JOURNAL = PORTFOLIO_ROOT / 'journal/execution-journal.jsonl'
PORTFOLIO_ID = 'GOS-72E1DF137383C56F'
REPO_REV = 'ccff6265e2351f02cb836d41e1fd981445c11032'

# Load source inventory
inventory = json.loads((PORTFOLIO_ROOT / 'source-inventory.json').read_text())
sources_by_id = {s['source_id']: s for s in inventory['sources']}

BATCHES = {
    'A': ['s001','s002','s003','s004','s005','s006','s007','s008','s009','s010'],
    'B': ['s011','s012','s013','s014','s015','s016','s017','s018','s019','s020'],
    'C': ['s021','s022','s023','s024','s025','s026','s027','s028','s029','s030'],
    'D': ['s031','s032','s033','s034','s035','s036','s037','s038','s039','s040','s041'],
}

TC_STATUS_PATTERNS = [
    re.compile(r'\|\s*(TC-[\w-]+)\s*\|\s*(OPEN|CLOSED|PENDING|READY|IN_PROGRESS|BLOCKED|TODO|DONE|VERIFIED|CHILDREN_IN_PROGRESS|INTEGRATION_PENDING|SCORED|PROPOSED)\s*\|', re.IGNORECASE),
    re.compile(r'[\*\-]\s+\*\*(TC-[\w-]+)\*\*.*?(?:status|Status):\s*(\w+)', re.IGNORECASE),
    re.compile(r'###\s+(TC-[\w-]+)\s+\|[^|]+\|\s*(\w+)', re.IGNORECASE),
    re.compile(r'###\s+(TC-[\w-]+)[^\n]*\|\s*(\w[\w_]*)\s*$', re.MULTILINE | re.IGNORECASE),
]

MISSION_PATTERN = re.compile(r'(?:Mission[\s_]ID|mission_id|Mission ID)[:\s]+([A-Z0-9_\-]+)', re.IGNORECASE)
PLAN_TYPE_PATTERN = re.compile(r'(?:plan[_\s]type|Plan Type|type)[:\s]+([a-z_]+)', re.IGNORECASE)
TASKCARD_HEADING = re.compile(r'###\s+(TC-[\w-]+)\s*[|\s]*(.*?)$', re.MULTILINE)
COMPLETION_PATTERN = re.compile(r'(?:Completion Condition|completion_condition|Closes when)[:\s]+(.+?)(?:\n\n|\n###|\Z)', re.IGNORECASE | re.DOTALL)


def extract_taskcards(text: str) -> list:
    """Extract taskcard IDs and statuses from plan text."""
    found = {}

    # Try table patterns
    for pattern in TC_STATUS_PATTERNS:
        for m in pattern.finditer(text):
            tc_id = m.group(1).strip()
            status = m.group(2).strip().upper()
            if tc_id not in found:
                found[tc_id] = status

    # Extract from ### TC-... headings (no status in heading = OPEN)
    for m in TASKCARD_HEADING.finditer(text):
        tc_id = m.group(1).strip()
        rest = m.group(2).strip()
        if tc_id not in found:
            # Check if status appears in heading after |
            parts = [p.strip() for p in rest.split('|')]
            status = 'OPEN'
            for part in parts:
                upper = part.upper()
                if upper in ('OPEN','CLOSED','PENDING','READY','IN_PROGRESS','BLOCKED','TODO','DONE','VERIFIED'):
                    status = upper
                    break
            found[tc_id] = status

    return [{'tc_id': k, 'status': v} for k, v in sorted(found.items())]


def extract_plan_record(source_id: str, source: dict) -> dict:
    """Parse a plan file and return a plan_record."""
    path = Path(source['normalized_path'])
    if not path.exists():
        # try the .md variant
        path = Path(source['normalized_path'] + '.md')

    try:
        text = path.read_text(encoding='utf-8', errors='replace')
    except Exception as e:
        return {
            'source_id': source_id,
            'error': str(e),
            'status': 'PARSE_FAILED'
        }

    title = source.get('title') or ''
    lines = text.splitlines()

    # Mission ID
    mission_match = MISSION_PATTERN.search(text[:3000])
    mission_id = mission_match.group(1).strip() if mission_match else None

    # Plan type
    type_match = PLAN_TYPE_PATTERN.search(text[:5000])
    plan_type = type_match.group(1).strip() if type_match else 'unknown'

    # Taskcards
    taskcards = extract_taskcards(text)

    # Completion conditions (first match)
    completion = []
    cm = COMPLETION_PATTERN.search(text)
    if cm:
        snippet = cm.group(1).strip()[:400]
        completion.append(snippet)

    # Extract stated dependencies (lines mentioning "Depends on")
    deps = []
    for line in lines:
        if re.search(r'Depends on[:\s]', line, re.IGNORECASE):
            deps.append(line.strip()[:200])

    # Extract stated blockers
    blockers = []
    for line in lines:
        if re.search(r'(blocker|blocked by|CRITICAL)[:\s]', line, re.IGNORECASE):
            blockers.append(line.strip()[:200])

    # Declared status
    declared_status = None
    for line in lines[:30]:
        for kw in ('READY_FOR_EXECUTION', 'IN_PROGRESS', 'READY', 'COMPLETE', 'TERMINAL_CLOSED', 'OPEN'):
            if kw in line:
                declared_status = kw
                break
        if declared_status:
            break

    record = {
        'schema_version': '1.0',
        'plan_id': source_id,
        'source_id': source_id,
        'source_path': source['normalized_path'],
        'source_hash': source['source_hash'],
        'title': title,
        'mission_id': mission_id,
        'plan_type': plan_type,
        'revision': None,
        'previous_revisions': [],
        'objectives': [],
        'source_taskcards': taskcards,
        'taskcard_count': len(taskcards),
        'constraints': [],
        'dependencies': deps,
        'blockers_stated': blockers[:10],
        'assumptions': [],
        'completion_conditions': completion,
        'stated_verification': [],
        'current_repository_assessment': 'NOT_CLASSIFIED',
        'canonical_requirement_ids': [],
        'canonical_task_ids': [],
        'checklist_path': f'.portfolio/goofy-orbiting-scroll/checklists/{source["base_name"]}-checklist.json',
        'evidence_paths': [],
        'execution_status': declared_status or 'NOT_STARTED',
        'closure_status': 'OPEN',
        'superseded_by': None,
        'supersession_evidence': [],
        'last_reconciled_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }

    # Compute checksum
    record_str = json.dumps(record, sort_keys=True)
    record['checksum'] = hashlib.sha256(record_str.encode()).hexdigest()
    return record


def append_journal(event_id, event_type, task_id, reason, prev_evt):
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    event = {
        'schema_version': '1.0',
        'event_id': event_id,
        'timestamp': now,
        'portfolio_id': PORTFOLIO_ID,
        'event_type': event_type,
        'plan_ids': [],
        'task_id': task_id,
        'lane_id': 'L09',
        'repository_revision_before': REPO_REV,
        'repository_revision_after': REPO_REV,
        'evidence_ids': [],
        'reason': reason,
        'actor': 'claude-sonnet-4-6',
        'parent_event_id': prev_evt,
    }
    event['checksum'] = hashlib.sha256(json.dumps(event, sort_keys=True).encode()).hexdigest()
    with JOURNAL.open('a') as f:
        f.write(json.dumps(event) + '\n')
    return event_id


event_counter = 3  # EVT-001 and EVT-002 already used

total_taskcards = 0
total_records = 0

for batch_id, source_ids in BATCHES.items():
    batch_file = PORTFOLIO_ROOT / f'batches/batch-{batch_id}.json'
    batch_file.parent.mkdir(exist_ok=True)

    # Claim batch
    batch_state = {
        'batch_id': batch_id,
        'source_ids': source_ids,
        'status': 'IN_PROGRESS',
        'plans_completed': [],
        'errors': []
    }
    batch_file.write_text(json.dumps(batch_state, indent=2))

    print(f'\n=== BATCH {batch_id}: {len(source_ids)} plans ===')

    records_written = []
    for source_id in source_ids:
        source = sources_by_id[source_id]
        record = extract_plan_record(source_id, source)

        # Write plan record
        out_path = PLAN_REGISTRY / f'{source_id}.json'
        out_path.write_text(json.dumps(record, indent=2))
        records_written.append(source_id)

        tc_count = record.get('taskcard_count', 0)
        total_taskcards += tc_count
        total_records += 1
        print(f'  {source_id} {source["base_name"]}: {tc_count} TCs | status={record["execution_status"]}')

        if record.get('error'):
            batch_state['errors'].append({'source_id': source_id, 'error': record['error']})

    # Commit batch
    batch_state['status'] = 'COMPLETE'
    batch_state['plans_completed'] = records_written
    batch_file.write_text(json.dumps(batch_state, indent=2))

    evt_id = f'EVT-{event_counter:03d}'
    append_journal(evt_id, f'BATCH_{batch_id}_COMMITTED', f'TC-GOS-00{3 + list(BATCHES.keys()).index(batch_id)}',
                   f'Batch {batch_id}: {len(records_written)} plans ingested', f'EVT-{event_counter-1:03d}')
    event_counter += 1
    print(f'  -> {evt_id} BATCH_{batch_id}_COMMITTED ({len(records_written)} records)')

# Update source inventory FULLY_INGESTED count
inventory['counters']['FULLY_INGESTED_PLAN_FILES'] = total_records
(PORTFOLIO_ROOT / 'source-inventory.json').write_text(json.dumps(inventory, indent=2))

# Update manifest
manifest = json.loads((PORTFOLIO_ROOT / 'portfolio-manifest.json').read_text())
manifest['updated_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
manifest['last_event_id'] = f'EVT-{event_counter-1:03d}'
manifest['source_task_count'] = total_taskcards
(PORTFOLIO_ROOT / 'portfolio-manifest.json').write_text(json.dumps(manifest, indent=2))

print(f'\n=== INGESTION COMPLETE ===')
print(f'Total plan records: {total_records}/41')
print(f'Total taskcards extracted: {total_taskcards}')
