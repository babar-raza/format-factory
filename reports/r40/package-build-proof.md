# R40 Lane E+F: Package Build Proof

**Sprint:** R40
**Date:** 2026-05-21

## Python FOSS Packages (Lane E)

### Build Results

| Package | Wheel | Sdist | Status |
|---------|-------|-------|--------|
| aspose-format-factory-fods | aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl (10,696B) | aspose_format_factory_fods-0.1.0.dev0.tar.gz (9,525B) | built |
| aspose-format-factory-fodt | aspose_format_factory_fodt-0.1.0.dev0-py3-none-any.whl (12,290B) | aspose_format_factory_fodt-0.1.0.dev0.tar.gz (10,589B) | built |

Build path: `.local/package-builds/python-foss/`

### Smoke Test Results

Both wheels installed in a clean temp venv (`python -m venv`) and imported:

```
INSTALLED: aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl
SMOKE_PASS: fods version=0.1.0
C:\...\site-packages\fods\__init__.py

INSTALLED: aspose_format_factory_fodt-0.1.0.dev0-py3-none-any.whl
SMOKE_PASS: fodt version=0.1.0
C:\...\site-packages\fodt\__init__.py
```

**PYTHON_PACKAGE_BUILD: PASS**

---

## .NET NuGet Packages (Lane F)

### Build Results

| Package | File | DLL Size | Status |
|---------|------|----------|--------|
| FormatFactory.Fods | FormatFactory.Fods.0.1.0-tier0.nupkg (13,063B) | lib/net10.0/FormatFactory.Fods.dll (25,600B) | built |
| FormatFactory.Fodt | FormatFactory.Fodt.0.1.0-tier0.nupkg (12,106B) | lib/net10.0/FormatFactory.Fodt.dll (23,552B) | built |

Build path: `.local/package-builds/dotnet/`
Method: `dotnet build --configuration Release` + `dotnet pack --configuration Release`

### Consumer Smoke Test Results

Temp consumer projects created for each package with local nuget.config feed:

```
FormatFactory.Fods package loaded
caught: FodsDocumentException
SMOKE_OK

FormatFactory.Fodt package loaded
caught: FodtDocumentException
SMOKE_OK
```

Both packages: resolved from local feed, compiled, ran, returned expected exception on missing file.

**NUGET_PACKAGE_BUILD: PASS**

---

## Notes

- `publication_authorized: false` — packages are local-only, NOT published
- `commercial_product_ready: false` — Gate 11 G11-G not yet approved by Babar Raza
- Previous R39 `--no-build` error: stale 11,776B DLL lacked FodsDocument class in binary; R40 rebuild produces correct 25,600B DLL
