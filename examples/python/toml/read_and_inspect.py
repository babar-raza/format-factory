"""
TOML example: Read and inspect TOML configuration files.

Usage:
    python read_and_inspect.py [path/to/config.toml]

If no path is given, creates a minimal in-memory example.
"""
import sys
import tempfile
import os
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]

try:
    from toml import (  # installed: format-factory-toml
        load_toml, probe_toml, list_sections, get_value,
        get_all_keys, get_keys, has_key, has_section, to_json_str, count_keys,
    )
except ImportError:
    sys.path.insert(0, str(_REPO / "src" / "python" / "toml"))
    from toml_codec import (  # type: ignore  # dev fallback
        load_toml, probe_toml, list_sections, get_value,
        get_all_keys, get_keys, has_key, has_section, to_json_str, count_keys,
    )

# --- Create or use sample ---
if len(sys.argv) > 1:
    sample_path = sys.argv[1]
    cleanup = False
else:
    sample_path = tempfile.mktemp(suffix=".toml")
    cleanup = True
    content = """\
[database]
host = "localhost"
port = 5432
name = "mydb"
pool_size = 10

[server]
host = "0.0.0.0"
port = 8080
debug = true
workers = 4

[logging]
level = "INFO"
file = "/var/log/app.log"
max_size_mb = 100
"""
    with open(sample_path, "w", encoding="utf-8") as f:
        f.write(content)

try:
    # --- Probe ---
    probe = probe_toml(sample_path)
    print(f"File: {sample_path}")
    print(f"  Format: {probe.get('format')}")
    print(f"  Exists: {probe.get('exists')}")
    print(f"  Size: {probe.get('size_bytes')} bytes")
    print(f"  Top-level keys: {probe.get('top_level_keys')}")
    print(f"  Section count: {probe.get('section_count')}")

    # --- Load ---
    result = load_toml(sample_path)
    data = result["data"]
    print(f"\n  Sections loaded: {list(data.keys())}")

    # --- Section enumeration ---
    sections = list_sections(sample_path)
    print(f"\n  Sections: {sections}")

    # --- Key access ---
    db_host = get_value(sample_path, "database.host")
    db_port = get_value(sample_path, "database.port")
    srv_debug = get_value(sample_path, "server.debug")
    log_level = get_value(sample_path, "logging.level")
    print(f"\n  database.host = {db_host!r}")
    print(f"  database.port = {db_port}")
    print(f"  server.debug  = {srv_debug}")
    print(f"  logging.level = {log_level!r}")

    # --- Key inventory ---
    all_keys = get_all_keys(sample_path)
    print(f"\n  All keys ({len(all_keys)}):")
    for k in sorted(all_keys):
        print(f"    {k}")

    # --- Existence checks ---
    print(f"\n  has_section('database'): {has_section(sample_path, 'database')}")
    print(f"  has_section('cache'): {has_section(sample_path, 'cache')}")
    print(f"  has_key('server.workers'): {has_key(sample_path, 'server.workers')}")
    print(f"  has_key('server.timeout'): {has_key(sample_path, 'server.timeout')}")

    # --- Key count ---
    total = count_keys(sample_path)
    print(f"\n  Total leaf keys: {total}")

    # --- JSON export ---
    json_out = to_json_str(sample_path)
    print(f"\n  JSON representation:\n{json_out}")

finally:
    if cleanup and os.path.exists(sample_path):
        os.unlink(sample_path)
