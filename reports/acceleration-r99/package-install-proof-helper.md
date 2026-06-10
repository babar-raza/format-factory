# Package Install Proof Helper — Train H

Sprint: FORMAT-FACTORY-ACCELERATION-R99-PRODUCT-FACTORY-ACCELERATION-LAYER-PARALLEL-MEGA-TRAIN-001

## Tool Created

`tools/supervisor/package_install_proof.py`

## Capabilities

- **Auto-detect**: Detects which product source directories have uncommitted changes
- **Import proof**: Runs `import <package>` for detected or specified formats
- **Log capture**: Writes per-format install proof logs to `--log-dir`
- **JSON output**: `--json` flag for machine-readable results

## CLI Interface

```bash
# Auto-detect changed products
python tools/supervisor/package_install_proof.py

# Test specific formats
python tools/supervisor/package_install_proof.py --format fods fodt pbm

# JSON output
python tools/supervisor/package_install_proof.py --format fods --json
```

## Supported Formats

| Format | Package | Import Name |
|--------|---------|-------------|
| fods | format-factory-fods | fods |
| fodt | format-factory-fodt | fodt |
| pbm | format-factory-pbm | pbm |
| pgm | format-factory-pgm | pgm |
| ppm | format-factory-ppm | ppm |
| sylk | format-factory-sylk | sylk |
| dif | format-factory-dif | dif |
| zst | format-factory-zst | zst |
| qoi | format-factory-qoi | qoi |

## Exit Codes

- 0: All proofs passed
- 1: One or more proofs failed
- 2: No changed products detected

## Test Results

- 5 tests in `test_package_install_proof.py`, all pass
