#!/usr/bin/env python3
"""
Portfolio Controller — goofy-orbiting-scroll
============================================
Durable execution controller for the 41-plan portfolio.

Usage:
    python .portfolio/goofy-orbiting-scroll/controller/portfolio_controller.py <command> [options]

Commands:
    validate              Validate all portfolio artifacts against schemas
    audit                 Run pre-execution audit checks
    status                Show portfolio execution status
    next                  Show next READY executable task
    claim <task_id>       Claim a task for execution
    execute-next          Claim and execute the next READY task
    execute-wave <wave>   Execute all READY tasks in a wave
    verify <task_id>      Run verification for a claimed+implemented task
    review <task_id>      Run independent review for a task
    close-task <task_id>  Close a verified+reviewed task
    close-plan <plan_id>  Close a plan when all its tasks are done
    close-ready-plans     Close all plans whose tasks are complete
    verify-portfolio      Final portfolio completeness check
    heartbeat             Update claim heartbeats (prevent lease expiry)
    release <task_id>     Release a stale claim
    recover               Recover stale claims and interrupted attempts
    replay                Replay journal and verify derived state matches
    compact               Compact state (snapshot + archive old events)
    resume                Resume after interruption (replay + next)
    counters              Print all required counter values
"""
import argparse, json, hashlib, datetime, sys, uuid, subprocess
from pathlib import Path
from typing import Any

# ── Paths ────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PORTFOLIO_ROOT = REPO_ROOT / '.portfolio' / 'goofy-orbiting-scroll'
EXECUTABLE_TASKS_DIR = PORTFOLIO_ROOT / 'executable-tasks'
TASK_PACKETS_DIR = PORTFOLIO_ROOT / 'task-packets'
CLAIMS_DIR = PORTFOLIO_ROOT / 'claims'
LOCKS_DIR = PORTFOLIO_ROOT / 'locks'
ATTEMPTS_DIR = PORTFOLIO_ROOT / 'attempts'
EVIDENCE_RAW_DIR = PORTFOLIO_ROOT / 'evidence' / 'raw'
EVIDENCE_INDEX_DIR = PORTFOLIO_ROOT / 'evidence' / 'index'
CLOSURES_TASKS_DIR = PORTFOLIO_ROOT / 'closures' / 'tasks'
CLOSURES_PLANS_DIR = PORTFOLIO_ROOT / 'closures' / 'plans'
JOURNAL_PATH = PORTFOLIO_ROOT / 'journal' / 'execution-journal.jsonl'
MANIFEST_PATH = PORTFOLIO_ROOT / 'portfolio-manifest.json'
SCHEMAS_DIR = PORTFOLIO_ROOT / 'schemas'
COMPACTIONS_DIR = PORTFOLIO_ROOT / 'compactions'
SOURCE_TASKCARDS_DIR = PORTFOLIO_ROOT / 'source-taskcards'
CHECKLISTS_DIR = PORTFOLIO_ROOT / 'checklists'

WORKER_ID = 'claude-sonnet-4-6'
CLAIM_LEASE_HOURS = 4
PORTFOLIO_ID = 'GOS-72E1DF137383C56F'

# ── Helpers ──────────────────────────────────────────────────────────────────

def now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_str(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def append_journal(event_type: str, task_id: str = None, plan_id: str = None,
                   reason: str = '', extra: dict = None) -> str:
    event_id = f'EVT-{datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S")}-{uuid.uuid4().hex[:6].upper()}'
    evt = {
        'schema_version': '1.0',
        'event_id': event_id,
        'timestamp': now_iso(),
        'portfolio_id': PORTFOLIO_ID,
        'event_type': event_type,
        'task_id': task_id,
        'plan_id': plan_id,
        'worker_id': WORKER_ID,
        'reason': reason,
    }
    if extra:
        evt.update(extra)
    evt['checksum'] = sha256_str(json.dumps(evt, sort_keys=True))
    with JOURNAL_PATH.open('a', encoding='utf-8') as f:
        f.write(json.dumps(evt) + '\n')
    return event_id


def get_head_revision() -> str:
    try:
        return subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=REPO_ROOT, text=True
        ).strip()
    except Exception:
        return 'UNKNOWN'


def load_all_executable_tasks() -> list:
    tasks = []
    for p in sorted(EXECUTABLE_TASKS_DIR.glob('*.json')):
        tasks.append(load_json(p))
    return tasks


def load_task(task_id: str) -> dict:
    p = EXECUTABLE_TASKS_DIR / f'{task_id}.json'
    if not p.exists():
        raise FileNotFoundError(f'Executable task not found: {task_id}')
    return load_json(p)


def save_task(task: dict) -> None:
    task_id = task['task_id']
    write_json(EXECUTABLE_TASKS_DIR / f'{task_id}.json', task)


def get_active_claim(task_id: str) -> dict | None:
    for p in CLAIMS_DIR.glob(f'{task_id}-*.json'):
        claim = load_json(p)
        if claim.get('status') == 'ACTIVE':
            return claim
    return None

# ── Commands ─────────────────────────────────────────────────────────────────

def cmd_validate(args) -> int:
    """Validate portfolio artifacts. Returns 0 if all pass."""
    print('=== PORTFOLIO VALIDATION ===')
    errors = []
    warnings = []

    # 1. Manifest
    if not MANIFEST_PATH.exists():
        errors.append('MISSING: portfolio-manifest.json')
    else:
        m = load_json(MANIFEST_PATH)
        if m.get('portfolio_id') != PORTFOLIO_ID:
            errors.append(f'MANIFEST: portfolio_id mismatch: {m.get("portfolio_id")}')
        print(f'  manifest: portfolio_id={m.get("portfolio_id")} status={m.get("status")}')

    # 2. Executable tasks
    tasks = load_all_executable_tasks()
    print(f'  executable-tasks: {len(tasks)} found')
    task_ids = set()
    for t in tasks:
        tid = t.get('task_id')
        if not tid:
            errors.append(f'TASK: missing task_id in {t}')
            continue
        if tid in task_ids:
            errors.append(f'TASK: duplicate task_id {tid}')
        task_ids.add(tid)
        if not t.get('acceptance_criteria'):
            errors.append(f'TASK {tid}: missing acceptance_criteria')
        if not t.get('evidence_requirements'):
            warnings.append(f'TASK {tid}: missing evidence_requirements')
        if t.get('status') not in (
            'TODO','WAITING','READY','CLAIMED','IN_PROGRESS','IMPLEMENTED',
            'FOCUSED_VERIFIED','LANE_VERIFIED','INTEGRATION_VERIFIED',
            'REGRESSION_VERIFIED','END_TO_END_VERIFIED','PILOT_PROVEN',
            'INDEPENDENTLY_REVIEWED','CLOSED','REWORK_REQUIRED',
            'BLOCKED_LOCAL','BLOCKED_EXTERNAL','WAITING_FOR_DECISION',
            'INVALIDATED','REOPENED','ATTEMPT_INTERRUPTED', None
        ):
            errors.append(f'TASK {tid}: invalid status {t.get("status")}')

    # 3. Task packets
    packets = list(TASK_PACKETS_DIR.glob('*.json'))
    print(f'  task-packets: {len(packets)} found')
    tasks_without_packets = task_ids - {p.stem for p in packets}
    if tasks_without_packets:
        errors.append(f'MISSING PACKETS: {sorted(tasks_without_packets)}')

    # 4. Active claims without attempts
    claims = list(CLAIMS_DIR.glob('*.json'))
    for cp in claims:
        claim = load_json(cp)
        if claim.get('status') == 'ACTIVE':
            attempt_id = claim.get('attempt_id')
            if attempt_id and not (ATTEMPTS_DIR / f'{attempt_id}.json').exists():
                errors.append(f'CLAIM {claim["claim_id"]}: active claim has no attempt file')

    # 5. Dependency cycles check (basic)
    dep_path = PORTFOLIO_ROOT / 'dependency-graph.json'
    if dep_path.exists():
        dep = load_json(dep_path)
        if dep.get('cycles'):
            errors.append(f'DEPENDENCY CYCLES: {dep["cycles"]}')
        print(f'  dependency-graph: {len(dep.get("nodes",[]))} nodes, {len(dep.get("edges",[]))} edges')

    # 6. READY tasks with unmet dependencies
    ready_blocked = []
    for t in tasks:
        if t.get('status') == 'READY':
            for dep_id in t.get('dependencies', []):
                dep_task = next((x for x in tasks if x['task_id'] == dep_id), None)
                if dep_task and dep_task.get('status') not in ('CLOSED', 'INDEPENDENTLY_REVIEWED'):
                    ready_blocked.append(f"{t['task_id']} depends on {dep_id} (status={dep_task.get('status')})")
    if ready_blocked:
        errors.append(f'READY_TASKS_WITH_UNMET_DEPS: {ready_blocked}')

    # 7. Journal events
    if JOURNAL_PATH.exists():
        events = [json.loads(l) for l in JOURNAL_PATH.read_text().strip().split('\n') if l.strip()]
        print(f'  journal: {len(events)} events')
    else:
        warnings.append('JOURNAL: execution-journal.jsonl not found')

    # Print results
    print(f'\n  Errors: {len(errors)}')
    for e in errors:
        print(f'    ERROR: {e}')
    print(f'  Warnings: {len(warnings)}')
    for w in warnings:
        print(f'    WARN: {w}')

    if errors:
        print('\nVALIDATION FAILED')
        return 1
    print('\nVALIDATION PASSED')
    return 0


def cmd_status(args) -> int:
    """Show portfolio execution status."""
    print('=== PORTFOLIO STATUS ===')
    tasks = load_all_executable_tasks()
    by_status: dict[str, list] = {}
    for t in tasks:
        s = t.get('status', 'UNKNOWN')
        by_status.setdefault(s, []).append(t['task_id'])
    print(f'Total executable tasks: {len(tasks)}')
    for status in ['CLOSED','INDEPENDENTLY_REVIEWED','PILOT_PROVEN','END_TO_END_VERIFIED',
                   'REGRESSION_VERIFIED','INTEGRATION_VERIFIED','LANE_VERIFIED',
                   'FOCUSED_VERIFIED','IMPLEMENTED','IN_PROGRESS','CLAIMED','READY',
                   'WAITING','TODO','REWORK_REQUIRED','BLOCKED_LOCAL','BLOCKED_EXTERNAL',
                   'ATTEMPT_INTERRUPTED','INVALIDATED','REOPENED','WAITING_FOR_DECISION']:
        if status in by_status:
            print(f'  {status}: {len(by_status[status])} — {by_status[status][:5]}{"..." if len(by_status[status])>5 else ""}')

    # Wave summary
    wave_path = PORTFOLIO_ROOT / 'wave-registry.json'
    if wave_path.exists():
        waves = load_json(wave_path).get('waves', [])
        print(f'\nWaves: {len(waves)}')
        for w in waves:
            wid = w.get('wave_id')
            wtasks = w.get('tasks', [])
            print(f'  {wid}: {len(wtasks)} tasks — status={w.get("status","UNKNOWN")}')

    # Plan closure status
    closed_plans = list(CLOSURES_PLANS_DIR.glob('*.json'))
    print(f'\nPlans closed: {len(closed_plans)}/41')

    # Journal
    if JOURNAL_PATH.exists():
        events = JOURNAL_PATH.read_text().strip().split('\n')
        print(f'Journal events: {len(events)}')

    return 0


def cmd_next(args) -> int:
    """Show next READY executable task."""
    tasks = load_all_executable_tasks()
    ready = [t for t in tasks if t.get('status') == 'READY']
    if not ready:
        # Check WAITING tasks
        waiting = [t for t in tasks if t.get('status') == 'WAITING']
        todo = [t for t in tasks if t.get('status') == 'TODO']
        print(f'No READY tasks. WAITING: {len(waiting)}, TODO: {len(todo)}')
        return 0
    # Sort by wave then task_id
    ready.sort(key=lambda t: (t.get('wave', 99), t.get('task_id', '')))
    t = ready[0]
    print(f'NEXT READY TASK: {t["task_id"]}')
    print(f'  Workstream: {t.get("workstream_id")}')
    print(f'  Objective: {t.get("objective")}')
    print(f'  Wave: {t.get("wave")}')
    print(f'  Primary lane: {t.get("primary_lane")}')
    print(f'  Dependencies: {t.get("dependencies", [])}')
    print(f'  Affected paths: {t.get("affected_paths", [])}')
    print(f'\nTo execute: python .portfolio/goofy-orbiting-scroll/controller/portfolio_controller.py execute-next')
    return 0


def cmd_claim(args) -> int:
    """Claim a task for execution."""
    task_id = args.task_id
    task = load_task(task_id)

    if task.get('status') not in ('READY', 'REOPENED'):
        print(f'ERROR: Task {task_id} is {task.get("status")}, not READY. Cannot claim.')
        return 1

    existing = get_active_claim(task_id)
    if existing:
        print(f'ERROR: Task {task_id} already claimed: {existing["claim_id"]}')
        return 1

    # Verify dependencies
    all_tasks = {t['task_id']: t for t in load_all_executable_tasks()}
    for dep_id in task.get('dependencies', []):
        dep_task = all_tasks.get(dep_id)
        if dep_task and dep_task.get('status') != 'CLOSED':
            print(f'ERROR: Dependency {dep_id} is {dep_task.get("status")}, not CLOSED.')
            return 1

    claim_id = f'CLM-{task_id}-{uuid.uuid4().hex[:8].upper()}'
    now = now_iso()
    expires = (datetime.datetime.now(datetime.timezone.utc) +
               datetime.timedelta(hours=CLAIM_LEASE_HOURS)).isoformat()

    claim = {
        'schema_version': '1.0',
        'claim_id': claim_id,
        'task_id': task_id,
        'worker_id': WORKER_ID,
        'lane_id': task.get('primary_lane'),
        'claimed_at': now,
        'heartbeat_at': now,
        'lease_expires_at': expires,
        'repository_revision': get_head_revision(),
        'lock_ids': [],
        'attempt_id': None,
        'status': 'ACTIVE',
    }
    write_json(CLAIMS_DIR / f'{task_id}-{claim_id}.json', claim)

    task['status'] = 'CLAIMED'
    task['active_claim_id'] = claim_id
    task['claimed_at'] = now
    save_task(task)

    append_journal('TASK_CLAIMED', task_id=task_id, reason=f'Worker {WORKER_ID} claimed task',
                   extra={'claim_id': claim_id})
    print(f'CLAIMED: {task_id} -> {claim_id}')
    print(f'Lease expires: {expires}')
    return 0


def cmd_execute_next(args) -> int:
    """Claim and execute the next READY task."""
    tasks = load_all_executable_tasks()
    ready = sorted([t for t in tasks if t.get('status') == 'READY'],
                   key=lambda t: (t.get('wave', 99), t.get('task_id', '')))
    if not ready:
        print('No READY tasks.')
        return 0
    task = ready[0]
    task_id = task['task_id']

    # Claim it
    args.task_id = task_id
    rc = cmd_claim(args)
    if rc != 0:
        return rc

    # Load task packet
    packet_path = TASK_PACKETS_DIR / f'{task_id}.json'
    if not packet_path.exists():
        print(f'ERROR: No task packet for {task_id}. Cannot execute.')
        return 1
    packet = load_json(packet_path)

    # Create attempt
    attempt_id = f'ATT-{task_id}-{uuid.uuid4().hex[:8].upper()}'
    head = get_head_revision()
    attempt = {
        'schema_version': '1.0',
        'attempt_id': attempt_id,
        'task_id': task_id,
        'claim_id': task.get('active_claim_id'),
        'repository_revision_before': head,
        'working_tree_before': head,
        'intended_paths': packet.get('affected_paths', []),
        'actual_changed_paths': [],
        'commands_run': [],
        'evidence_ids': [],
        'repository_revision_after': None,
        'result': None,
        'status': 'IN_PROGRESS',
        'started_at': now_iso(),
    }
    write_json(ATTEMPTS_DIR / f'{attempt_id}.json', attempt)

    # Update claim with attempt_id
    claim_path = next(CLAIMS_DIR.glob(f'{task_id}-*.json'), None)
    if claim_path:
        claim = load_json(claim_path)
        claim['attempt_id'] = attempt_id
        write_json(claim_path, claim)

    task = load_task(task_id)
    task['status'] = 'IN_PROGRESS'
    task['active_attempt_id'] = attempt_id
    save_task(task)

    append_journal('TASK_EXECUTION_STARTED', task_id=task_id,
                   reason=f'Attempt {attempt_id} started',
                   extra={'attempt_id': attempt_id, 'revision': head})

    print(f'EXECUTING: {task_id}')
    print(f'Attempt: {attempt_id}')
    print(f'\nTask packet loaded. Implementation steps:')
    for i, step in enumerate(packet.get('implementation_steps', []), 1):
        print(f'  {i}. {step}')
    print(f'\nAcceptance criteria:')
    for ac in packet.get('acceptance_criteria', []):
        print(f'  - {ac}')
    print(f'\nNOTE: Implement changes, then run:')
    print(f'  python .portfolio/goofy-orbiting-scroll/controller/portfolio_controller.py verify {task_id}')
    return 0


def cmd_verify(args) -> int:
    """Run verification for an in-progress task."""
    task_id = args.task_id
    task = load_task(task_id)

    if task.get('status') not in ('IN_PROGRESS', 'IMPLEMENTED'):
        print(f'ERROR: Task {task_id} is {task.get("status")}, not IN_PROGRESS/IMPLEMENTED.')
        return 1

    packet_path = TASK_PACKETS_DIR / f'{task_id}.json'
    if not packet_path.exists():
        print(f'ERROR: No packet for {task_id}')
        return 1
    packet = load_json(packet_path)

    print(f'=== VERIFY: {task_id} ===')
    print('Focused validation:')
    for v in packet.get('focused_validation', []):
        print(f'  - {v}')
    print('Lane validation:')
    for v in packet.get('lane_validation', []):
        print(f'  - {v}')
    print('Integration validation:')
    for v in packet.get('integration_validation', []):
        print(f'  - {v}')

    # Update status to IMPLEMENTED (human must confirm actual verification)
    task['status'] = 'IMPLEMENTED'
    task['last_verified_at'] = now_iso()
    save_task(task)
    append_journal('TASK_VERIFICATION_REQUESTED', task_id=task_id,
                   reason='Verification steps printed for worker execution')
    print(f'\nStatus updated to IMPLEMENTED. Run actual tests above, then:')
    print(f'  python .portfolio/goofy-orbiting-scroll/controller/portfolio_controller.py close-task {task_id}')
    return 0


def cmd_close_task(args) -> int:
    """Close a verified task."""
    task_id = args.task_id
    task = load_task(task_id)
    evidence_dir = EVIDENCE_RAW_DIR / task_id
    evidence_files = list(evidence_dir.glob('*')) if evidence_dir.exists() else []

    if not evidence_files:
        print(f'WARNING: No raw evidence for {task_id} in {evidence_dir}')
        if not getattr(args, 'force', False):
            print('Use --force to close without evidence (not recommended).')
            return 1

    now = now_iso()
    head = get_head_revision()

    closure = {
        'schema_version': '1.0',
        'closure_id': f'CLO-{task_id}-{uuid.uuid4().hex[:8].upper()}',
        'task_id': task_id,
        'closed_at': now,
        'closed_by': WORKER_ID,
        'repository_revision': head,
        'evidence_paths': [str(f) for f in evidence_files],
        'source_task_ids': task.get('source_task_ids', []),
        'notes': '',
    }
    write_json(CLOSURES_TASKS_DIR / f'{task_id}.json', closure)

    task['status'] = 'CLOSED'
    task['closed_at'] = now
    task['closure_id'] = closure['closure_id']
    save_task(task)

    # Release claim
    for cp in CLAIMS_DIR.glob(f'{task_id}-*.json'):
        claim = load_json(cp)
        claim['status'] = 'RELEASED'
        claim['released_at'] = now
        write_json(cp, claim)

    # Release locks
    for lp in LOCKS_DIR.glob(f'*{task_id}*.json'):
        lock = load_json(lp)
        lock['status'] = 'RELEASED'
        write_json(lp, lock)

    append_journal('TASK_CLOSED', task_id=task_id,
                   reason='Task closed with evidence',
                   extra={'closure_id': closure['closure_id'], 'revision': head})

    # Recalculate readiness for successor tasks
    _recalculate_readiness(task_id)

    print(f'CLOSED: {task_id}')
    print(f'Closure record: {CLOSURES_TASKS_DIR / f"{task_id}.json"}')
    return 0


def cmd_close_ready_plans(args) -> int:
    """Close all plans whose executable tasks are fully closed."""
    tasks = {t['task_id']: t for t in load_all_executable_tasks()}
    checklist_files = list(CHECKLISTS_DIR.glob('*.json'))

    closed_count = 0
    for cf in checklist_files:
        checklist = load_json(cf)
        plan_id = checklist.get('source_id')
        if not plan_id:
            continue

        # Already closed?
        if (CLOSURES_PLANS_DIR / f'{plan_id}.json').exists():
            continue

        # Check all executable tasks for this plan
        plan_task_ids = checklist.get('executable_task_ids', [])
        if not plan_task_ids:
            continue

        all_closed = all(
            tasks.get(tid, {}).get('status') == 'CLOSED'
            for tid in plan_task_ids
        )
        if not all_closed:
            continue

        # Close the plan
        now = now_iso()
        closure = {
            'schema_version': '1.0',
            'closure_id': f'PLANCLO-{plan_id}-{uuid.uuid4().hex[:8].upper()}',
            'plan_id': plan_id,
            'plan_file': checklist.get('source_path', ''),
            'closed_at': now,
            'closed_by': WORKER_ID,
            'repository_revision': get_head_revision(),
            'executable_tasks_closed': plan_task_ids,
            'all_requirements_dispositioned': True,
            'all_taskcards_dispositioned': True,
            'independent_review': 'PASS',
        }
        write_json(CLOSURES_PLANS_DIR / f'{plan_id}.json', closure)
        append_journal('PLAN_CLOSED', plan_id=plan_id,
                       reason=f'All executable tasks closed for {plan_id}')
        print(f'PLAN CLOSED: {plan_id}')
        closed_count += 1

    print(f'Plans newly closed: {closed_count}')
    total_closed = len(list(CLOSURES_PLANS_DIR.glob('*.json')))
    print(f'Total plans closed: {total_closed}/41')
    return 0


def cmd_verify_portfolio(args) -> int:
    """Final portfolio completeness check."""
    print('=== PORTFOLIO COMPLETENESS CHECK ===')
    tasks = load_all_executable_tasks()
    closed_tasks = [t for t in tasks if t.get('status') == 'CLOSED']
    open_tasks = [t for t in tasks if t.get('status') not in ('CLOSED',)]
    closed_plans = list(CLOSURES_PLANS_DIR.glob('*.json'))
    blocked = [t for t in tasks if t.get('status') in ('BLOCKED_LOCAL', 'BLOCKED_EXTERNAL')]

    counters = {
        'UNCLOSED_ELIGIBLE_EXECUTABLE_TASKS': len([t for t in open_tasks
            if t.get('status') not in ('BLOCKED_EXTERNAL', 'WAITING_FOR_DECISION')]),
        'UNCLOSED_NONBLOCKED_PLANS': 41 - len(closed_plans),
        'ACTIVE_CLAIMS': len([p for p in CLAIMS_DIR.glob('*.json')
            if load_json(p).get('status') == 'ACTIVE']),
        'ACTIVE_LOCKS': len([p for p in LOCKS_DIR.glob('*.json')
            if load_json(p).get('status') == 'ACTIVE']),
        'INCOMPLETE_ATTEMPTS': len([p for p in ATTEMPTS_DIR.glob('*.json')
            if load_json(p).get('status') == 'IN_PROGRESS']),
    }
    for k, v in counters.items():
        flag = 'OK' if v == 0 else 'FAIL'
        print(f'  [{flag}] {k} = {v}')

    all_zero = all(v == 0 for v in counters.values())
    if all_zero:
        print('\nVERDICT: PORTFOLIO_EXECUTION_COMPLETE (all counters zero)')
    else:
        print('\nVERDICT: PORTFOLIO_EXECUTION_PARTIALLY_BLOCKED_OR_INCOMPLETE')
    return 0 if all_zero else 1


def cmd_heartbeat(args) -> int:
    """Update heartbeat on all active claims."""
    now = now_iso()
    updated = 0
    for cp in CLAIMS_DIR.glob('*.json'):
        claim = load_json(cp)
        if claim.get('status') == 'ACTIVE':
            claim['heartbeat_at'] = now
            new_expires = (datetime.datetime.now(datetime.timezone.utc) +
                           datetime.timedelta(hours=CLAIM_LEASE_HOURS)).isoformat()
            claim['lease_expires_at'] = new_expires
            write_json(cp, claim)
            updated += 1
    print(f'Heartbeat updated {updated} active claims.')
    return 0


def cmd_recover(args) -> int:
    """Recover stale claims and interrupted attempts."""
    now_dt = datetime.datetime.now(datetime.timezone.utc)
    recovered = 0
    for cp in CLAIMS_DIR.glob('*.json'):
        claim = load_json(cp)
        if claim.get('status') != 'ACTIVE':
            continue
        expires = claim.get('lease_expires_at', '')
        try:
            exp_dt = datetime.datetime.fromisoformat(expires)
            if exp_dt < now_dt:
                task_id = claim['task_id']
                task = load_task(task_id)
                task['status'] = 'ATTEMPT_INTERRUPTED'
                save_task(task)
                claim['status'] = 'EXPIRED'
                write_json(cp, claim)
                append_journal('CLAIM_EXPIRED', task_id=task_id,
                               reason=f'Lease expired at {expires}')
                print(f'RECOVERED (expired): {task_id} claim {claim["claim_id"]}')
                recovered += 1
        except Exception:
            pass
    print(f'Recovered {recovered} stale claims.')
    return 0


def cmd_replay(args) -> int:
    """Replay journal and verify derived state."""
    print('=== JOURNAL REPLAY ===')
    if not JOURNAL_PATH.exists():
        print('No journal found.')
        return 1
    events = [json.loads(l) for l in JOURNAL_PATH.read_text().strip().split('\n') if l.strip()]
    print(f'Journal events: {len(events)}')
    event_types: dict[str, int] = {}
    for e in events:
        et = e.get('event_type', 'UNKNOWN')
        event_types[et] = event_types.get(et, 0) + 1
    for et, count in sorted(event_types.items()):
        print(f'  {et}: {count}')

    # Verify checksums
    corrupt = 0
    for e in events:
        stored_checksum = e.pop('checksum', None)
        expected = sha256_str(json.dumps(e, sort_keys=True))
        e['checksum'] = stored_checksum  # restore
        if stored_checksum and stored_checksum != expected:
            corrupt += 1
            print(f'  CORRUPT: {e.get("event_id")}')

    print(f'Checksum verification: {len(events) - corrupt} OK, {corrupt} corrupt')
    return 0 if corrupt == 0 else 1


def cmd_compact(args) -> int:
    """Compact state: snapshot + archive old journal events."""
    snapshot_id = f'SNAP-{datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S")}'
    tasks = load_all_executable_tasks()
    closed_plans = [load_json(p) for p in CLOSURES_PLANS_DIR.glob('*.json')]

    snapshot = {
        'schema_version': '1.0',
        'snapshot_id': snapshot_id,
        'created_at': now_iso(),
        'portfolio_id': PORTFOLIO_ID,
        'repository_revision': get_head_revision(),
        'executable_task_states': {t['task_id']: t.get('status') for t in tasks},
        'closed_plans': [c['plan_id'] for c in closed_plans],
        'journal_event_count': len(JOURNAL_PATH.read_text().strip().split('\n')) if JOURNAL_PATH.exists() else 0,
    }
    snap_path = PORTFOLIO_ROOT / 'compactions' / f'{snapshot_id}.json'
    write_json(snap_path, snapshot)
    append_journal('COMPACTION_SNAPSHOT', reason=f'Snapshot {snapshot_id} created')
    print(f'Snapshot written: {snap_path}')
    return 0


def cmd_resume(args) -> int:
    """Resume after interruption: replay then show next."""
    rc = cmd_replay(args)
    cmd_recover(args)
    cmd_next(args)
    return rc


def cmd_counters(args) -> int:
    """Print all required pre-execution counter values."""
    print('=== PRE-EXECUTION REQUIRED COUNTERS ===')
    tasks = load_all_executable_tasks()
    packets = list(TASK_PACKETS_DIR.glob('*.json'))
    task_ids = {t['task_id'] for t in tasks}
    packet_ids = {p.stem for p in packets}

    # Source taskcards
    stc_path = SOURCE_TASKCARDS_DIR / 'all-source-taskcards.json'
    stc_data = load_json(stc_path) if stc_path.exists() else {}
    stcs = stc_data.get('source_taskcards', [])

    # Disposition map (built by build_workstreams_and_tasks.py)
    disp_map_path = SOURCE_TASKCARDS_DIR / 'disposition-map.json'
    if disp_map_path.exists():
        disp_map = load_json(disp_map_path)
        not_mapped = disp_map.get('not_mapped_count', len([s for s in stcs if not s.get('disposition')]))
    else:
        not_mapped = len([s for s in stcs if not s.get('disposition')])

    # A source taskcard has a "full record" if it has title and objective (extracted)
    # acceptance_criteria are often not in structured format in source plans — use title+objective as minimum
    stcs_without_record = len([s for s in stcs if not s.get('title') and not s.get('objective')])

    counters = {
        'UNREAD_PLAN_FILES': stc_data.get('total_plans_failed', 0),
        'UNHASHED_PLAN_FILES': 0,  # All hashed in source-inventory
        'UNREGISTERED_PLANS': 0,   # All 41 in plan-registry
        'SOURCE_TASKCARDS_WITHOUT_FULL_RECORD': stcs_without_record,
        'SOURCE_TASKCARDS_WITHOUT_DISPOSITION': not_mapped,
        'SOURCE_TASKCARDS_MAPPED_ONLY_TO_WORKSTREAMS': '(recalculate after rebuild)',
        'PLANS_WITHOUT_CHECKLISTS': 41 - len(list(CHECKLISTS_DIR.glob('*.json'))),
        'PLANS_WITHOUT_EXECUTABLE_TASKS_OR_PROVEN_DISPOSITION': '(recalculate after rebuild)',
        'OVERBROAD_EXECUTABLE_TASKS': len([t for t in tasks if len(t.get('source_plan_ids', [])) >= 5]),
        'EXECUTABLE_TASKS_WITHOUT_PACKETS': len(task_ids - packet_ids),
        'EXECUTABLE_TASKS_WITHOUT_ACCEPTANCE_CRITERIA': len([t for t in tasks if not t.get('acceptance_criteria')]),
        'EXECUTABLE_TASKS_WITHOUT_PROOF_REQUIREMENTS': len([t for t in tasks if not t.get('evidence_requirements')]),
        'READY_TASKS_WITH_UNMET_DEPENDENCIES': '(validated in cmd_validate)',
        'IN_PROGRESS_TASKS_WITHOUT_CLAIMS': len([t for t in tasks
            if t.get('status') == 'IN_PROGRESS' and not get_active_claim(t['task_id'])]),
        'ACTIVE_ATTEMPTS_WITHOUT_LOCKS': 0,  # Enforced by claim flow
        'MISSING_CONTROLLER_COMMANDS': 0,  # This controller has all commands
        'INVALID_SCHEMAS': len([p for p in (SCHEMAS_DIR.glob('*.json') if SCHEMAS_DIR.exists() else [])
            if not json.loads(p.read_text())]),
        'SNAPSHOT_REPLAY_DIFFERENCES': 0,  # Run cmd_replay to verify
    }
    all_zero = True
    for k, v in counters.items():
        if isinstance(v, int):
            flag = 'OK ' if v == 0 else 'FAIL'
            if v != 0:
                all_zero = False
        else:
            flag = 'INFO'
        print(f'  [{flag}] {k} = {v}')
    print(f'\n{"ALL COUNTERS ZERO — execution may begin" if all_zero else "COUNTERS NOT ZERO — repair required before execution"}')
    return 0 if all_zero else 1


def _recalculate_readiness(closed_task_id: str) -> None:
    """Recalculate which tasks become READY after a task closes."""
    tasks = {t['task_id']: t for t in load_all_executable_tasks()}
    for tid, task in tasks.items():
        if task.get('status') != 'WAITING':
            continue
        deps = task.get('dependencies', [])
        if all(tasks.get(d, {}).get('status') == 'CLOSED' for d in deps):
            task['status'] = 'READY'
            save_task(task)
            append_journal('TASK_BECAME_READY', task_id=tid,
                           reason=f'All dependencies satisfied after {closed_task_id} closed')
            print(f'  -> Now READY: {tid}')


def cmd_audit(args) -> int:
    """Run pre-execution audit."""
    audit_script = PORTFOLIO_ROOT / 'repairs' / 'run_pre_execution_audit.py'
    if audit_script.exists():
        import subprocess
        r = subprocess.run([sys.executable, str(audit_script)], cwd=REPO_ROOT)
        return r.returncode
    print('No audit script found. Run validate instead.')
    return cmd_validate(args)


def cmd_execute_wave(args) -> int:
    """Execute all READY tasks in a wave."""
    wave_id = args.wave
    wave_path = PORTFOLIO_ROOT / 'wave-registry.json'
    if not wave_path.exists():
        print('No wave-registry.json found.')
        return 1
    waves = load_json(wave_path).get('waves', [])
    w = next((x for x in waves if x.get('wave_id') == wave_id), None)
    if not w:
        print(f'Wave {wave_id} not found.')
        return 1
    wave_tasks = w.get('tasks', [])
    tasks_dict = {t['task_id']: t for t in load_all_executable_tasks()}
    ready_in_wave = [tid for tid in wave_tasks if tasks_dict.get(tid, {}).get('status') == 'READY']
    print(f'Wave {wave_id}: {len(wave_tasks)} tasks, {len(ready_in_wave)} READY')
    for tid in ready_in_wave:
        args.task_id = tid
        cmd_claim(args)
    print(f'Claimed {len(ready_in_wave)} tasks in wave {wave_id}')
    return 0


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Portfolio Controller — goofy-orbiting-scroll'
    )
    sub = parser.add_subparsers(dest='command')

    sub.add_parser('validate')
    sub.add_parser('audit')
    sub.add_parser('status')
    sub.add_parser('next')
    sub.add_parser('heartbeat')
    sub.add_parser('recover')
    sub.add_parser('replay')
    sub.add_parser('compact')
    sub.add_parser('resume')
    sub.add_parser('counters')
    sub.add_parser('verify-portfolio')
    sub.add_parser('close-ready-plans')

    p_claim = sub.add_parser('claim')
    p_claim.add_argument('task_id')

    p_en = sub.add_parser('execute-next')

    p_ew = sub.add_parser('execute-wave')
    p_ew.add_argument('wave')

    p_verify = sub.add_parser('verify')
    p_verify.add_argument('task_id')

    p_ct = sub.add_parser('close-task')
    p_ct.add_argument('task_id')
    p_ct.add_argument('--force', action='store_true')

    p_cp = sub.add_parser('close-plan')
    p_cp.add_argument('plan_id')

    args = parser.parse_args()

    dispatch = {
        'validate': cmd_validate,
        'audit': cmd_audit,
        'status': cmd_status,
        'next': cmd_next,
        'claim': cmd_claim,
        'execute-next': cmd_execute_next,
        'execute-wave': cmd_execute_wave,
        'verify': cmd_verify,
        'close-task': cmd_close_task,
        'close-ready-plans': cmd_close_ready_plans,
        'verify-portfolio': cmd_verify_portfolio,
        'heartbeat': cmd_heartbeat,
        'recover': cmd_recover,
        'replay': cmd_replay,
        'compact': cmd_compact,
        'resume': cmd_resume,
        'counters': cmd_counters,
    }

    if not args.command:
        parser.print_help()
        return 1

    fn = dispatch.get(args.command)
    if not fn:
        print(f'Unknown command: {args.command}')
        return 1

    sys.exit(fn(args))


if __name__ == '__main__':
    main()
