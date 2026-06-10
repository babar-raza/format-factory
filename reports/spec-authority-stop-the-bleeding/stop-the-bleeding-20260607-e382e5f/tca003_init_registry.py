"""TCA-003: Initialize .local/spec-source-registry/sources.jsonl"""
import subprocess, json, os, yaml

# Dynamic REPO_ROOT
repo_root = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True).strip()
if repo_root.startswith('/c/'):
    repo_root = 'C:/' + repo_root[3:]

cache_root = os.path.join(repo_root, '.local', 'spec-cache')
registry_path = os.path.join(repo_root, '.local', 'spec-source-registry', 'sources.jsonl')

# Find all spec-index.yaml files
index_files = []
for dirpath, dirnames, filenames in os.walk(cache_root):
    if 'spec-index.yaml' in filenames:
        index_files.append(os.path.join(dirpath, 'spec-index.yaml'))

index_files.sort()
print(f"Found {len(index_files)} spec-index.yaml files")

entries = []
for idx_path in index_files:
    with open(idx_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    format_id = data.get('format_id', '')
    version = str(data.get('version', ''))
    spec_name = data.get('spec_name', '')

    # Extract SHA-256 — try multiple field names
    sha256_raw = data.get('sha256') or data.get('content_hash') or ''
    if isinstance(sha256_raw, str) and sha256_raw.startswith('sha256:'):
        sha256_val = sha256_raw[7:]
    else:
        sha256_val = sha256_raw if sha256_raw else None

    # Extract cached/fetched date
    cached_at = (
        data.get('fetched_at') or
        data.get('download_date') or
        data.get('access_date') or
        'unknown'
    )

    # Local path relative to repo root (forward slashes)
    rel = os.path.relpath(os.path.dirname(idx_path), repo_root)
    local_path = rel.replace('\\', '/')

    spec_id_ver = version.replace('.', '_').replace(' ', '_').upper()
    spec_id = f"SPEC-{format_id.upper()}-{spec_id_ver}"

    retrieval_status = data.get('retrieval_status', 'cached') or 'cached'

    entry = {
        "format_id": format_id,
        "spec_id": spec_id,
        "version": version,
        "spec_name": spec_name,
        "source_sha256": sha256_val,
        "cached_at": str(cached_at),
        "local_path": local_path,
        "retrieval_status": retrieval_status,
    }
    entries.append(entry)
    print(f"  {format_id} v{version} -> {spec_id}  sha256={'present' if sha256_val else 'absent'}")

# Write JSONL
with open(registry_path, 'w', encoding='utf-8') as f:
    for e in entries:
        f.write(json.dumps(e) + '\n')

print(f"\nWrote {len(entries)} entries to {registry_path}")

# Verify
with open(registry_path, 'r', encoding='utf-8') as f:
    lines = [json.loads(l) for l in f if l.strip()]
print(f"Verified: {len(lines)} valid JSONL lines")
fods_present = any(l['format_id'] == 'fods' for l in lines)
print(f"FODS_PRESENT: {fods_present}")
print("PASS" if fods_present and len(lines) >= 1 else "FAIL")
