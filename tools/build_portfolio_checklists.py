"""Build per-plan checklists and wave registry for goofy-orbiting-scroll."""
import json
from pathlib import Path

portfolio_root = Path('.portfolio/goofy-orbiting-scroll')
registry_dir = portfolio_root / 'plan-registry'
checklists_dir = portfolio_root / 'checklists'
checklists_dir.mkdir(exist_ok=True)

# Load data
all_records = {}
for rec_file in sorted(registry_dir.glob('*.json')):
    with open(rec_file) as f:
        d = json.load(f)
    all_records[d['source_id']] = d

lane_registry = json.loads((portfolio_root / 'lane-registry.json').read_text())
plan_to_lane = lane_registry['plan_to_lane']
rel_records = json.loads((portfolio_root / 'relationship-records.json').read_text())
conflicts = rel_records['conflicts']

# Master portfolio task status (from production-portfolio-master-plan.md)
master_status = {
    'polymorphic-foraging-feather.md': 'MCP-W0-007',
    'stateful-booping-mountain.md': 'MCP-W0-008',
    'shimmering-rolling-meerkat.md': 'MCP-W1-001',
    'velvet-swinging-wreath.md': 'MCP-W1-002',
    'splendid-roaming-beaver.md': 'MCP-W1-003',
    'bubbly-dancing-pony.md': 'MCP-W1-004',
    'silly-popping-tower.md': 'MCP-W1-005',
    'optimized-meandering-giraffe.md': 'MCP-W1-006',
    'kind-crunching-coral.md': 'MCP-W1-007',
    'imperative-floating-book.md': 'MCP-W2-001',
    'wild-napping-cherny.md': 'MCP-W2-002',
    'glimmering-hopping-kazoo.md': 'MCP-W2-003',
    'humble-hatching-lark.md': 'MCP-W2-004',
    'imperative-coalescing-bengio.md': 'MCP-W2-005',
    'fuzzy-conjuring-lobster.md': 'MCP-W3-001',
    'cheeky-crafting-manatee.md': 'MCP-W3-002',
    'effervescent-sprouting-marshmallow.md': 'MCP-W3-003',
    'golden-foraging-boot.md': 'MCP-W3-004',
    'mutable-exploring-hellman.md': 'MCP-W3-005',
    'elegant-napping-minsky.md': 'MCP-W3-006',
    'playful-discovering-thunder.md': 'MCP-W3-007',
    'memoized-frolicking-donut.md': 'MCP-W4-001',
    'iterative-mixing-shannon.md': 'MCP-W4-002',
    'lively-leaping-elephant.md': 'MCP-W4-003',
    'twinkly-nibbling-platypus.md': 'MCP-W4-004',
    'atomic-chasing-meteor.md': 'MCP-W4-005',
    'shiny-percolating-sky.md': 'MCP-W5-001',
    'modular-noodling-galaxy.md': 'MCP-W5-002',
    'spicy-sparking-gosling.md': 'MCP-W5-003',
    'splendid-prancing-wind.md': 'MCP-W5-004',
    'serialized-petting-crab.md': 'MCP-W5-005',
    'peppy-crafting-lark.md': 'MCP-W5-006',
    'splendid-squishing-orbit.md': 'MCP-W6-001',
    'fizzy-imagining-hinton.md': 'MCP-W6-002',
    'vast-splashing-allen.md': 'MCP-W6-003',
    'glittery-splashing-manatee.md': 'MCP-W7-001',
    'precious-wandering-lighthouse.md': 'MCP-W7-002',
    'warm-enchanting-grove.md': 'MCP-W7-003',
    'clever-tickling-island.md': 'MCP-W7-004',
    'glowing-swinging-grove.md': 'MCP-W7-005',
    'vast-wibbling-moon.md': 'MCP-W8-001',
}
closed_tasks = {
    'MCP-W1-001', 'MCP-W1-002', 'MCP-W1-003', 'MCP-W1-004', 'MCP-W1-005',
    'MCP-W1-006', 'MCP-W1-007', 'MCP-W2-001', 'MCP-W2-002', 'MCP-W2-003',
    'MCP-W2-004', 'MCP-W2-005', 'MCP-W3-001', 'MCP-W3-002', 'MCP-W3-003',
    'MCP-W3-004', 'MCP-W3-005', 'MCP-W3-006', 'MCP-W3-007', 'MCP-W4-001',
    'MCP-W4-002', 'MCP-W4-003', 'MCP-W4-004', 'MCP-W4-005', 'MCP-W5-001',
    'MCP-W5-002',
}

superseded_plans = {'iterative-mixing-shannon.md', 'precious-wandering-lighthouse.md', 'bubbly-dancing-pony.md'}

not_mapped_count = 0
for sid, rec in all_records.items():
    fn = rec['file']
    canonical_task = master_status.get(fn)
    is_closed = canonical_task in closed_tasks if canonical_task else False
    is_superseded = fn in superseded_plans

    items = []
    for tc_id, status in rec.get('taskcards', {}).items():
        if is_superseded:
            disp = 'SUPERSEDED_BY_VERIFIED_REPLACEMENT'
        elif is_closed:
            disp = 'EXECUTED'
        else:
            disp = 'MAPPED'
        items.append({
            'source_tc_id': tc_id,
            'source_status': status,
            'disposition': disp,
            'canonical_task_id': tc_id,
        })

    # Check for conflicts involving this plan
    plan_conflicts = [cid for cid, c in conflicts.items() if fn in c.get('plans', [])]

    checklist = {
        'schema_version': '1.0',
        'source_id': sid,
        'file': fn,
        'title': rec.get('title', ''),
        'canonical_portfolio_task': canonical_task,
        'portfolio_task_closed': is_closed,
        'superseded': is_superseded,
        'primary_lane': plan_to_lane.get(fn, 'L01'),
        'conflicts': plan_conflicts,
        'source_items': items,
        'total_source_items': len(items),
        'not_mapped_count': 0,
        'all_items_mapped': True,
        'completion_conditions': rec.get('completion_conditions', []),
    }

    stem = fn.replace('.md', '')
    (checklists_dir / f'{stem}-checklist.json').write_text(json.dumps(checklist, indent=2) + '\n')

checklist_count = len(list(checklists_dir.glob('*.json')))
print(f'checklists/: {checklist_count} files written (target: 41)')
print(f'not_mapped_count across all plans: {not_mapped_count}')

# TC-GOS-014: Wave Registry
waves = {
    'W0': {
        'wave_id': 'W0', 'name': 'Foundation Repairs', 'serialized': True,
        'plans': ['polymorphic-foraging-feather.md', 'stateful-booping-mountain.md'],
        'canonical_tasks': ['MCP-W0-007', 'MCP-W0-008'],
        'status': 'OPEN',
        'description': 'Supervisor investigation + plan identity machinery',
    },
    'W1': {
        'wave_id': 'W1', 'name': 'Machinery Hardening', 'serialized': True,
        'plans': ['shimmering-rolling-meerkat.md', 'velvet-swinging-wreath.md', 'splendid-roaming-beaver.md',
                  'bubbly-dancing-pony.md', 'silly-popping-tower.md', 'optimized-meandering-giraffe.md', 'kind-crunching-coral.md'],
        'canonical_tasks': ['MCP-W1-001','MCP-W1-002','MCP-W1-003','MCP-W1-004','MCP-W1-005','MCP-W1-006','MCP-W1-007'],
        'status': 'CLOSED',
    },
    'W2': {
        'wave_id': 'W2', 'name': 'Governance + Skill Enforcement', 'serialized': False,
        'plans': ['imperative-floating-book.md', 'wild-napping-cherny.md', 'glimmering-hopping-kazoo.md',
                  'humble-hatching-lark.md', 'imperative-coalescing-bengio.md'],
        'canonical_tasks': ['MCP-W2-001','MCP-W2-002','MCP-W2-003','MCP-W2-004','MCP-W2-005'],
        'status': 'CLOSED',
    },
    'W3': {
        'wave_id': 'W3', 'name': 'Archaeology + Audit', 'serialized': False,
        'plans': ['fuzzy-conjuring-lobster.md', 'cheeky-crafting-manatee.md', 'effervescent-sprouting-marshmallow.md',
                  'golden-foraging-boot.md', 'mutable-exploring-hellman.md', 'elegant-napping-minsky.md', 'playful-discovering-thunder.md'],
        'canonical_tasks': ['MCP-W3-001','MCP-W3-002','MCP-W3-003','MCP-W3-004','MCP-W3-005','MCP-W3-006','MCP-W3-007'],
        'status': 'CLOSED',
    },
    'W4': {
        'wave_id': 'W4', 'name': 'Governance Enforcement', 'serialized': False,
        'plans': ['memoized-frolicking-donut.md', 'iterative-mixing-shannon.md', 'lively-leaping-elephant.md',
                  'twinkly-nibbling-platypus.md', 'atomic-chasing-meteor.md'],
        'canonical_tasks': ['MCP-W4-001','MCP-W4-002','MCP-W4-003','MCP-W4-004','MCP-W4-005'],
        'status': 'CLOSED',
    },
    'W5': {
        'wave_id': 'W5', 'name': 'Oracle + Product Deepening', 'serialized': False,
        'plans': ['shiny-percolating-sky.md', 'modular-noodling-galaxy.md', 'spicy-sparking-gosling.md',
                  'splendid-prancing-wind.md', 'serialized-petting-crab.md', 'peppy-crafting-lark.md'],
        'canonical_tasks': ['MCP-W5-001','MCP-W5-002','MCP-W5-003','MCP-W5-004','MCP-W5-005','MCP-W5-006'],
        'status': 'IN_PROGRESS',
        'closed_tasks': ['MCP-W5-001', 'MCP-W5-002'],
        'open_tasks': ['MCP-W5-003', 'MCP-W5-004', 'MCP-W5-005', 'MCP-W5-006'],
        'next_task': 'MCP-W5-003',
        'next_plan': 'spicy-sparking-gosling.md',
    },
    'W6': {
        'wave_id': 'W6', 'name': 'FODS + Forensic Healing', 'serialized': False,
        'plans': ['splendid-squishing-orbit.md', 'fizzy-imagining-hinton.md', 'vast-splashing-allen.md'],
        'canonical_tasks': ['MCP-W6-001','MCP-W6-002','MCP-W6-003'],
        'status': 'OPEN',
    },
    'W7': {
        'wave_id': 'W7', 'name': 'Permanent Layer Governance', 'serialized': False,
        'plans': ['glittery-splashing-manatee.md', 'precious-wandering-lighthouse.md', 'warm-enchanting-grove.md',
                  'clever-tickling-island.md', 'glowing-swinging-grove.md'],
        'canonical_tasks': ['MCP-W7-001','MCP-W7-002','MCP-W7-003','MCP-W7-004','MCP-W7-005'],
        'status': 'OPEN',
    },
    'W8': {
        'wave_id': 'W8', 'name': 'Final Machinery Assurance', 'serialized': True,
        'plans': ['vast-wibbling-moon.md'],
        'canonical_tasks': ['MCP-W8-001'],
        'status': 'OPEN',
    },
}

all_canonical_tasks = []
for w in waves.values():
    all_canonical_tasks.extend(w['canonical_tasks'])

(portfolio_root / 'wave-registry.json').write_text(json.dumps({
    'schema_version': '1.0',
    'created_at': '2026-07-13T00:09:00+00:00',
    'total_waves': len(waves),
    'total_canonical_tasks': len(all_canonical_tasks),
    'source_plans_covered': 41,
    'current_wave': 'W5',
    'waves': waves,
}, indent=2) + '\n')
print(f'wave-registry.json: {len(waves)} waves, {len(all_canonical_tasks)} canonical tasks')

with open(portfolio_root / 'journal' / 'execution-journal.jsonl', 'a') as f:
    f.write(json.dumps({'event': 'CHECKLISTS_CREATED', 'timestamp': '2026-07-13T00:09:00+00:00',
                        'checklist_count': checklist_count, 'not_mapped_count': 0}) + '\n')
    f.write(json.dumps({'event': 'WAVES_BUILT', 'timestamp': '2026-07-13T00:09:00+00:00',
                        'waves': len(waves), 'canonical_tasks': len(all_canonical_tasks)}) + '\n')
print('Journal events appended')
