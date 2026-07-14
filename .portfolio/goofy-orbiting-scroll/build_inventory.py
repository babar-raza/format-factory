"""TC-GOS-002: Build source-inventory.json for all 41 plan files."""
import hashlib, json, datetime
from pathlib import Path

now = datetime.datetime.now(datetime.timezone.utc).isoformat()
portfolio_id = 'GOS-72E1DF137383C56F'

supplied = [
    ('s001', r'C:\Users\prora\.claude\plans\shiny-percolating-sky.md'),
    ('s002', r'C:\Users\prora\.claude\plans\glimmering-hopping-kazoo.md'),
    ('s003', r'C:\Users\prora\.claude\plans\polymorphic-foraging-feather.md'),
    ('s004', r'C:\Users\prora\.claude\plans\iterative-mixing-shannon.md'),
    ('s005', r'C:\Users\prora\.claude\plans\memoized-frolicking-donut.md'),
    ('s006', r'C:\Users\prora\.claude\plans\bubbly-dancing-pony.md'),
    ('s007', r'C:\Users\prora\.claude\plans\mutable-exploring-hellman.md'),
    ('s008', r'C:\Users\prora\.claude\plans\elegant-napping-minsky.md'),
    ('s009', r'C:\Users\prora\.claude\plans\stateful-booping-mountain.md'),
    ('s010', r'C:\Users\prora\.claude\plans\splendid-prancing-wind.md'),
    ('s011', r'C:\Users\prora\.claude\plans\splendid-squishing-orbit.md'),
    ('s012', r'C:\Users\prora\.claude\plans\twinkly-nibbling-platypus.md'),
    ('s013', r'C:\Users\prora\.claude\plans\vast-wibbling-moon.md'),
    ('s014', r'C:\Users\prora\.claude\plans\clever-tickling-island.md'),
    ('s015', r'C:\Users\prora\.claude\plans\warm-enchanting-grove.md'),
    ('s016', r'C:\Users\prora\.claude\plans\glowing-swinging-grove.md'),
    ('s017', r'C:\Users\prora\.claude\plans\vast-splashing-allen.md'),
    ('s018', r'C:\Users\prora\.claude\plans\kind-crunching-coral.md'),
    ('s019', r'C:\Users\prora\.claude\plans\humble-hatching-lark.md'),
    ('s020', r'C:\Users\prora\.claude\plans\atomic-chasing-meteor.md'),
    ('s021', r'C:\Users\prora\.claude\plans\spicy-sparking-gosling.md'),
    ('s022', r'C:\Users\prora\.claude\plans\playful-discovering-thunder.md'),
    ('s023', r'C:\Users\prora\.claude\plans\precious-wandering-lighthouse.md'),
    ('s024', r'C:\Users\prora\.claude\plans\serialized-petting-crab.md'),
    ('s025', r'C:\Users\prora\.claude\plans\glittery-splashing-manatee.md'),
    ('s026', r'C:\Users\prora\.claude\plans\imperative-coalescing-bengio.md'),
    ('s027', r'C:\Users\prora\.claude\plans\silly-popping-tower.md'),
    ('s028', r'C:\Users\prora\.claude\plans\peppy-crafting-lark.md'),
    ('s029', r'C:\Users\prora\.claude\plans\fizzy-imagining-hinton.md'),
    ('s030', r'C:\Users\prora\.claude\plans\shimmering-rolling-meerkat.md'),
    ('s031', r'C:\Users\prora\.claude\plans\modular-noodling-galaxy.md'),
    ('s032', r'C:\Users\prora\.claude\plans\imperative-floating-book.md'),
    ('s033', r'C:\Users\prora\.claude\plans\optimized-meandering-giraffe.md'),
    ('s034', r'C:\Users\prora\.claude\plans\splendid-roaming-beaver.md'),
    ('s035', r'C:\Users\prora\.claude\plans\wild-napping-cherny.md'),
    ('s036', r'C:\Users\prora\.claude\plans\cheeky-crafting-manatee.md'),
    ('s037', r'C:\Users\prora\.claude\plans\velvet-swinging-wreath.md'),
    ('s038', r'C:\Users\prora\.claude\plans\golden-foraging-boot.md'),
    ('s039', r'C:\Users\prora\.claude\plans\effervescent-sprouting-marshmallow.md'),
    ('s040', r'C:\Users\prora\.claude\plans\fuzzy-conjuring-lobster'),
    ('s041', r'C:\Users\prora\.claude\plans\lively-leaping-elephant.md'),
]

records = []
hashes_seen = {}
resolved = readable = hashed = failed = 0
duplicate_content = []

for source_id, literal_path in supplied:
    p = Path(literal_path)
    base_name = p.stem
    record = {
        'source_id': source_id,
        'literal_path': literal_path,
        'normalized_path': str(p),
        'relative_path': None,
        'base_name': base_name,
        'file_type': 'markdown',
        'encoding': 'utf-8',
        'title': None,
        'source_hash': None,
        'byte_size': None,
        'original_plan_ids': [],
        'original_task_ids': [],
        'declared_revision': None,
        'declared_status': None,
        'registered_plan_id': source_id,
        'duplicate_content_of': None,
        'possible_revision_of': None,
        'readable': False,
        'fully_ingested': False,
        'source_copy_or_reference': 'external',
        'parser_version': '1.0',
        'ingestion_errors': [],
        'status': 'PENDING'
    }

    resolved += 1

    if p.exists():
        try:
            content = p.read_bytes()
            record['readable'] = True
            record['byte_size'] = len(content)
            readable += 1

            h = hashlib.sha256(content).hexdigest()
            record['source_hash'] = h
            hashed += 1

            text = content.decode('utf-8', errors='replace')
            for line in text.splitlines():
                line = line.strip()
                if line.startswith('# '):
                    record['title'] = line[2:].strip()
                    break

            if h in hashes_seen:
                record['duplicate_content_of'] = hashes_seen[h]
                duplicate_content.append(source_id)
            else:
                hashes_seen[h] = source_id

            record['status'] = 'RESOLVED'
        except Exception as e:
            record['ingestion_errors'].append(str(e))
            failed += 1
            record['status'] = 'FAILED'
    else:
        record['ingestion_errors'].append('File not found at normalized path')
        failed += 1
        record['status'] = 'FAILED'

    records.append(record)

inventory = {
    'schema_version': '1.0',
    'portfolio_id': portfolio_id,
    'generated_at': now,
    'counters': {
        'SUPPLIED_PLAN_PATHS': 41,
        'RESOLVED_PLAN_PATHS': resolved,
        'READABLE_PLAN_FILES': readable,
        'FULLY_HASHED_PLAN_FILES': hashed,
        'FULLY_INGESTED_PLAN_FILES': 0,
        'REGISTERED_PLAN_FILES': len(records),
        'EXACT_DUPLICATE_PLAN_FILES': len(duplicate_content),
        'REVISION_CANDIDATE_PLAN_FILES': 0,
        'FAILED_PLAN_FILES': failed
    },
    'duplicate_groups': duplicate_content,
    'sources': records
}

out = Path('.portfolio/goofy-orbiting-scroll/source-inventory.json')
out.write_text(json.dumps(inventory, indent=2))

print(f'SUPPLIED: 41')
print(f'RESOLVED: {resolved}')
print(f'READABLE: {readable}')
print(f'HASHED:   {hashed}')
print(f'FAILED:   {failed}')
print(f'DUPLICATES: {len(duplicate_content)} -> {duplicate_content}')

for r in records:
    if r['status'] == 'FAILED':
        print(f'  FAILED: {r["source_id"]} {r["base_name"]} -> {r["ingestion_errors"]}')

# Print titles for reference
print('\nTitles extracted:')
for r in records:
    print(f'  {r["source_id"]} {r["base_name"]}: {r["title"]}')
