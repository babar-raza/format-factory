# /add-same-format-writer-feature

Add a same-format save/write feature to a product (FODS, FODT, Netpbm .NET or Python).
Same-format save = load from file → modify → save back to same format.

## Usage

```
/add-same-format-writer-feature
```

## What This Skill Does

1. **Pre-flight**: Reads skill-registry.yaml and product-code-change-ledger.json
2. **Plan**: Identifies the target format and save-path API to implement
3. **Implement**: Adds `Save(path)` / `SaveToFile(path)` / `write_<format>` to source
4. **Round-trip test**: Creates a round-trip test (load → modify → save → reload → verify)
5. **Ledger**: Adds a `GOVERNED_PRODUCT_CHANGE` entry with pre/post SHA-256
6. **Verify**: Runs tests and confirms round-trip passes

## Constraints

- Must implement save/write that produces a valid file of the same format
- Must include at least one round-trip test (load → save → reload → compare)
- Must not silently corrupt the format on save
- Ledger entry required before any src edit

## Evidence Required

- Source file modified
- Pre/post SHA-256
- Test file with round-trip test
- Pass result
- Ledger entry ID

## Acceptance Criteria

- `Save(path)` or equivalent writes a valid file
- Reloading the saved file produces equivalent content
- At least 4 tests pass
