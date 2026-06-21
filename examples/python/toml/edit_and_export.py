"""
TOML example: Edit configuration values and export to JSON.

Demonstrates: Load a TOML config, modify values with set_value, export as JSON.

Usage:
    python edit_and_export.py [path/to/config.toml]

If no path is given, creates a minimal in-memory example.
"""
import sys
import tempfile
import os
import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "toml"))

from toml_codec import (
    load_toml,
    set_value,
    get_value,
    to_json_str,
    list_sections,
    roundtrip,
)

# --- Create or use sample ---
if len(sys.argv) > 1:
    sample_path = sys.argv[1]
    cleanup = False
else:
    sample_path = tempfile.mktemp(suffix=".toml")
    cleanup = True
    content = """\
[app]
name = "MyService"
version = "1.0.0"
environment = "development"

[database]
host = "localhost"
port = 5432
pool_size = 5

[features]
enable_cache = false
enable_metrics = false
max_retries = 3
"""
    with open(sample_path, "w", encoding="utf-8") as f:
        f.write(content)

try:
    print(f"Source config: {sample_path}")

    # --- Load original ---
    result = load_toml(sample_path)
    data = result["data"]
    print(f"\nOriginal values:")
    print(f"  app.environment  = {get_value(sample_path, 'app.environment')!r}")
    print(f"  database.pool_size = {get_value(sample_path, 'database.pool_size')}")
    print(f"  features.enable_cache    = {get_value(sample_path, 'features.enable_cache')}")
    print(f"  features.enable_metrics  = {get_value(sample_path, 'features.enable_metrics')}")

    # --- Apply production overrides ---
    data = set_value(data, "app.environment", "production")
    data = set_value(data, "database.pool_size", 20)
    data = set_value(data, "features.enable_cache", True)
    data = set_value(data, "features.enable_metrics", True)
    data = set_value(data, "features.max_retries", 5)

    print(f"\nAfter production overrides:")
    print(f"  app.environment         = {data['app']['environment']!r}")
    print(f"  database.pool_size      = {data['database']['pool_size']}")
    print(f"  features.enable_cache   = {data['features']['enable_cache']}")
    print(f"  features.enable_metrics = {data['features']['enable_metrics']}")
    print(f"  features.max_retries    = {data['features']['max_retries']}")

    # --- Export to JSON ---
    json_out = to_json_str(sample_path)
    parsed_json = json.loads(json_out)
    print(f"\nOriginal config as JSON:")
    print(json.dumps(parsed_json, indent=2))

    # --- Roundtrip verification (original file) ---
    import tempfile as _tf
    rt_dest = _tf.mktemp(suffix=".toml")
    try:
        rt_result = roundtrip(sample_path, rt_dest)
        print(f"\nRoundtrip verification: {rt_result.get('ok')} "
              f"(keys preserved: {rt_result.get('key_count', 'N/A')})")
    finally:
        if os.path.exists(rt_dest):
            os.unlink(rt_dest)

    # --- Sections summary ---
    sections = list_sections(sample_path)
    print(f"\nConfig sections: {sections}")

finally:
    if cleanup and os.path.exists(sample_path):
        os.unlink(sample_path)
