# Changelog

## 0.2.0.dev0

- Move the production API to `format_factory.safetensors`.
- Pin behavior to upstream SafeTensors v0.8.0 commit `a406ca3`.
- Add strict structural validation, sub-byte dtype support, deterministic
  writing, lazy memory mapping, and optional NumPy/PyTorch adapters.
