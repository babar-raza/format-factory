# R75 Package Artifact Replay

**sprint_id:** FORMAT-FACTORY-R75-FINAL-ARTIFACT-AUTHORITY-REPAIR-RC-SEAL-PRODUCT-ADVANCEMENT-MEGA-TRAIN-001
**date:** 2026-05-29
**train:** F

## Package Matrix (Inherited from R74)

10 packages confirmed from R74 metadata directory:

| Package | Type | Status |
|---|---|---|
| aspose_format_factory_fods-0.1.0.dev0 | whl + sdist | R74 PASS |
| aspose_format_factory_fodt-0.1.0.dev0 | whl + sdist | R74 PASS |
| aspose_format_factory_zst-0.1.0.dev0 | whl + sdist | R74 PASS |
| aspose_format_factory_abw-0.1.0.dev0 | whl + sdist | R74 PASS |
| aspose_format_factory_fodp-0.1.0.dev0 | whl + sdist | R74 PASS |
| aspose_format_factory_fodg-0.1.0.dev0 | whl + sdist | R74 PASS |
| aspose_format_factory_gnumeric-0.1.0.dev0 | whl + sdist | R74 PASS |
| aspose_format_factory_pgm-0.1.0.dev0 | whl + sdist | R74 PASS |
| aspose_format_factory_pbm-0.1.0.dev0 | whl + sdist | R74 PASS |
| aspose_format_factory_sylk-0.1.0.dev0 | whl + sdist | R74 PASS |

## R75 Source Hygiene

FODS and FODT neutral_model.py updated with 2 new APIs each (Train G).
All new APIs have unit tests (31 new passing tests).
__init__.py exports updated for both packages.

Packages will be rebuilt as part of Train K bundle build using
existing build-local-packages.py infrastructure.

## Installed API Smoke

R74 smoke venv at .local/r74-smoke-venv confirmed FODS 17→23 APIs accessible.
R75 smoke verification will use .local/r75-smoke-venv during Train K.

## PACKAGE_REPLAY_STATUS: INHERITED_FROM_R74_WITH_R75_SOURCE_UPDATES
