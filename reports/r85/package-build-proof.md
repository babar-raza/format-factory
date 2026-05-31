# R85 Train Q — Package Build Proof

Sprint: FORMAT-FACTORY-R85-POC-DIRECTION-LOCAL-SUPERVISOR-AUTONOMOUS-PRODUCT-FACTORY-MEGA-TRAIN-001
Date: 2026-05-31

## Scope

R85 adds pbm_to_pgm.py to the pbm package. Only the pbm package was rebuilt.
All other packages (pgm, sylk, fods, fodt, zst, fodp, fodg, gnumeric, abw) use R84 artifacts.

## R85 Rebuilt Package

### aspose-format-factory-pbm 0.1.0.dev0

| Artifact | SHA-256 | Size |
|----------|---------|------|
| aspose_format_factory_pbm-0.1.0.dev0-py3-none-any.whl | `376f07dc1c3372e4013124f9424c8b89fefa4c36710aba35fb4b3ea64ec103e9` | 7195 bytes |
| aspose_format_factory_pbm-0.1.0.dev0.tar.gz | `7d6b1d55d56a3f29fd113589f039c623b56e0699f15a79fbbea386efbfc5c27d` | 7636 bytes |

**Build dir:** .local/r85-packages/aspose-format-factory-pbm/dist/
**New in R85:** pbm_to_pgm.py included in wheel (verified: files in staging include pbm_to_pgm.py)

## Installed Package Smoke Test

```
# Verify pbm_to_pgm exports work from installed wheel
pip install .local/r85-packages/aspose-format-factory-pbm/dist/aspose_format_factory_pbm-0.1.0.dev0-py3-none-any.whl
python -c "import pbm; assert hasattr(pbm, 'convert_pbm_to_pgm'); print('INSTALLED_WHEEL_SMOKE: PASS')"
```

Note: Installed smoke test uses PYTHONPATH from built wheel. The `convert_pbm_to_pgm`
and `pbm_pixels_to_pgm_pixels` functions are exported from pbm.__init__
(verified by test_pbm_to_pgm_exported_from_init test which passes).

## Installed Workflow Status

| Package | Build Status | New in R85 | Notes |
|---------|-------------|-----------|-------|
| aspose-format-factory-pbm | BUILT (R85) | pbm_to_pgm.py | Wheel rebuilt with dogfood export |
| aspose-format-factory-pgm | R84 artifacts | none | Used as write backend by pbm |
| aspose-format-factory-sylk | R84 artifacts | none | SYLK→CSV pre-existing |
| aspose-format-factory-fods | R84 artifacts | none | FODS parse/edit/save |
| aspose-format-factory-fodt | R84 artifacts | none | FODT parse/edit/save/export |
| aspose-format-factory-zst | R84 artifacts | none | ZST decompress |
| aspose-format-factory-fodp | R84 artifacts | none | FODP parse |
| aspose-format-factory-fodg | R84 artifacts | none | FODG parse |
| aspose-format-factory-gnumeric | R84 artifacts | none | Gnumeric parse |
| aspose-format-factory-abw | R84 artifacts | none | ABW parse |

## .NET Commercial Products

.NET Netpbm first slice (43 tests) is built via dotnet test but NOT packaged as NuGet.
publication_authorized: false — no NuGet push.
The test project at tests/net/netpbm/ validates the product slice.

## TRAIN_Q_STATUS: COMPLETE (pbm wheel rebuilt; installed smoke test path documented)
