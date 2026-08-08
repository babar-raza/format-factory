# Changelog

## 0.2.0.dev0

- Move the production API to `format_factory.safetensors`.
- Pin behavior to upstream SafeTensors v0.8.0 commit `a406ca3`.
- Add strict structural validation, sub-byte dtype support, deterministic
  writing, lazy memory mapping, and optional NumPy/PyTorch adapters.
- Add lazy, zero-copy header/region reading (`read_header`, `safe_open`) that
  never maps or copies the payload up front, and rule-specific `validate()`
  diagnostic codes.
- Add a full in-memory load/write API (`load`, `loads`, `dump`, `dumps`) that
  re-derives tensor offsets deterministically on write, distinct from the
  lazy `read_header`/`safe_open` path.
- Add a sharded model index lifecycle (`load_index`, `dump_index`,
  `loads_index`, `dumps_index`, `SafeTensorsShardIndex.resolve_shard`) that
  rejects duplicate JSON keys and unsafe shard references.
- Add optional framework adapters (`to_numpy`, `to_torch`) that are never
  imported unless explicitly used.
