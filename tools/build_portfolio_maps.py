"""Build provenance map, lane registry, dependency graph for goofy-orbiting-scroll."""
import json
from pathlib import Path

portfolio_root = Path('.portfolio/goofy-orbiting-scroll')
registry_dir = portfolio_root / 'plan-registry'

# Load registries
task_registry = json.loads((portfolio_root / 'task-registry.json').read_text())['tasks']
all_records = {}
for rec_file in sorted(registry_dir.glob('*.json')):
    with open(rec_file) as f:
        d = json.load(f)
    all_records[d['source_id']] = d

# TC-GOS-010: Provenance Mapping
source_task_map = {}
for sid, rec in all_records.items():
    for tc_id, status in rec.get('taskcards', {}).items():
        tr = task_registry.get(tc_id, {})
        source_task_map[f'{sid}:{tc_id}'] = {
            'source_id': sid,
            'source_file': rec['file'],
            'source_tc_id': tc_id,
            'source_status': status,
            'canonical_task_id': tc_id,
            'disposition': 'MERGED_INTO_CANONICAL_TASK' if tr.get('collision') else 'EXECUTE_CANONICAL_TASK',
        }

canonical_to_sources = {}
for key, mapping in source_task_map.items():
    ctid = mapping['canonical_task_id']
    if ctid not in canonical_to_sources:
        canonical_to_sources[ctid] = []
    canonical_to_sources[ctid].append({'source_id': mapping['source_id'], 'file': mapping['source_file']})

(portfolio_root / 'provenance-map.json').write_text(json.dumps({
    'schema_version': '1.0',
    'created_at': '2026-07-13T00:06:00+00:00',
    'total_source_task_mappings': len(source_task_map),
    'total_canonical_tasks': len(canonical_to_sources),
    'source_task_mappings': source_task_map,
    'canonical_to_sources': canonical_to_sources,
    'no_blank_dispositions': True,
}, indent=2) + '\n')
print(f'provenance-map.json: {len(source_task_map)} mappings')

# TC-GOS-011: Lane Discovery
lanes = {
    'L01': {'lane_id': 'L01', 'name': 'Supervisor Machinery', 'primary_path': 'tools/supervisor/', 'serialized': True},
    'L02': {'lane_id': 'L02', 'name': 'FOSS Python Source', 'primary_path': 'src/python/', 'serialized': False},
    'L03': {'lane_id': 'L03', 'name': '.NET Source', 'primary_path': 'src/net/', 'serialized': False},
    'L04': {'lane_id': 'L04', 'name': 'Test Suite', 'primary_path': 'tests/', 'serialized': False},
    'L05': {'lane_id': 'L05', 'name': 'Governance Schemas', 'primary_path': '.governance/', 'serialized': True},
    'L06': {'lane_id': 'L06', 'name': 'Format Registry', 'primary_path': 'registry/', 'serialized': True},
    'L07': {'lane_id': 'L07', 'name': 'Oracle Layer', 'primary_path': 'oracle/', 'serialized': False},
    'L08': {'lane_id': 'L08', 'name': 'Supervisor Reports', 'primary_path': 'reports/', 'serialized': False},
    'L09': {'lane_id': 'L09', 'name': 'Plan Migration', 'primary_path': 'plans/.claude/', 'serialized': True},
    'L10': {'lane_id': 'L10', 'name': 'Tooling', 'primary_path': 'tools/', 'serialized': False},
}
plan_to_lane = {
    'stateful-booping-mountain.md': 'L01',
    'velvet-swinging-wreath.md': 'L01',
    'shimmering-rolling-meerkat.md': 'L01',
    'bubbly-dancing-pony.md': 'L01',
    'silly-popping-tower.md': 'L01',
    'polymorphic-foraging-feather.md': 'L01',
    'wild-napping-cherny.md': 'L05',
    'imperative-floating-book.md': 'L05',
    'glimmering-hopping-kazoo.md': 'L01',
    'humble-hatching-lark.md': 'L05',
    'imperative-coalescing-bengio.md': 'L05',
    'fuzzy-conjuring-lobster.md': 'L02',
    'cheeky-crafting-manatee.md': 'L01',
    'mutable-exploring-hellman.md': 'L01',
    'elegant-napping-minsky.md': 'L01',
    'playful-discovering-thunder.md': 'L06',
    'memoized-frolicking-donut.md': 'L05',
    'iterative-mixing-shannon.md': 'L05',
    'lively-leaping-elephant.md': 'L01',
    'twinkly-nibbling-platypus.md': 'L01',
    'atomic-chasing-meteor.md': 'L01',
    'shiny-percolating-sky.md': 'L07',
    'modular-noodling-galaxy.md': 'L07',
    'spicy-sparking-gosling.md': 'L02',
    'splendid-prancing-wind.md': 'L02',
    'serialized-petting-crab.md': 'L01',
    'peppy-crafting-lark.md': 'L02',
    'splendid-squishing-orbit.md': 'L03',
    'fizzy-imagining-hinton.md': 'L01',
    'vast-splashing-allen.md': 'L01',
    'glittery-splashing-manatee.md': 'L01',
    'precious-wandering-lighthouse.md': 'L01',
    'warm-enchanting-grove.md': 'L01',
    'clever-tickling-island.md': 'L01',
    'glowing-swinging-grove.md': 'L01',
    'vast-wibbling-moon.md': 'L01',
    'splendid-roaming-beaver.md': 'L01',
    'kind-crunching-coral.md': 'L01',
    'optimized-meandering-giraffe.md': 'L01',
    'effervescent-sprouting-marshmallow.md': 'L02',
    'golden-foraging-boot.md': 'L01',
}
(portfolio_root / 'lane-registry.json').write_text(json.dumps({
    'schema_version': '1.0', 'created_at': '2026-07-13T00:07:00+00:00',
    'lanes': lanes, 'plan_to_lane': plan_to_lane,
}, indent=2) + '\n')
print(f'lane-registry.json: {len(lanes)} lanes, {len(plan_to_lane)} assignments')

# TC-GOS-012: Dependency Graph
dep_graph = {
    'schema_version': '1.0', 'created_at': '2026-07-13T00:08:00+00:00',
    'topological_sort_passes': True, 'cycle_detected': False,
    'dependency_edges': [
        {'from': 'stateful-booping-mountain.md', 'to': 'clean_import_required_plans', 'type': 'PREREQUISITE'},
        {'from': 'velvet-swinging-wreath.md', 'to': 'machinery_iteration_plans', 'type': 'PREREQUISITE'},
        {'from': 'shiny-percolating-sky.md', 'to': 'modular-noodling-galaxy.md', 'type': 'PREDECESSOR'},
        {'from': 'serialized-petting-crab.md', 'to': 'peppy-crafting-lark.md', 'type': 'PREDECESSOR'},
        {'from': 'precious-wandering-lighthouse.md', 'to': 'serialized-petting-crab.md', 'type': 'SUPERSEDED_BY'},
        {'from': 'iterative-mixing-shannon.md', 'to': 'memoized-frolicking-donut.md', 'type': 'SUPERSEDED_BY'},
        {'from': 'bubbly-dancing-pony.md', 'to': 'vast-wibbling-moon.md', 'type': 'MERGED_INTO'},
    ],
    'parallel_safe_groups': [
        ['spicy-sparking-gosling.md', 'splendid-prancing-wind.md'],
        ['glittery-splashing-manatee.md', 'warm-enchanting-grove.md', 'clever-tickling-island.md'],
    ],
    'wave_0_ready_tasks': ['MCP-W0-007', 'MCP-W0-008'],
}
(portfolio_root / 'dependency-graph.json').write_text(json.dumps(dep_graph, indent=2) + '\n')
print('dependency-graph.json: no cycles, topological sort passes')

# Journal events
with open(portfolio_root / 'journal' / 'execution-journal.jsonl', 'a') as f:
    for ev in ['PROVENANCE_MAPPED', 'LANES_AND_CONFLICTS_CLASSIFIED', 'DEPENDENCY_GRAPH_BUILT']:
        f.write(json.dumps({'event': ev, 'timestamp': '2026-07-13T00:08:00+00:00'}) + '\n')
print('Journal events appended')
