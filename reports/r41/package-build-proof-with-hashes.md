# R41 Lane D+G-J: Package Build Proof with Hashes

**Sprint:** R41
**Date:** 2026-05-21

## Python FOSS Packages

### FODS Wheel
- File: `aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl`
- Size: 10,696 bytes
- SHA-256: `0d9e6826515d849052bcda7f8546515063e51ab93d23e7183715c96b45c26014`

### FODS Sdist
- File: `aspose_format_factory_fods-0.1.0.dev0.tar.gz`
- Size: 9,525 bytes
- SHA-256: `2eac310d1844593d4e251de5eac8cf8d451407aa0f4790767d7cce4502a5f02c`

### FODT Wheel
- File: `aspose_format_factory_fodt-0.1.0.dev0-py3-none-any.whl`
- Size: 12,290 bytes
- SHA-256: `513e84aaa5b29c90128d11d4c80f3ce2c451cc0d5d9c8801b044b7b49ca391a5`

### FODT Sdist
- File: `aspose_format_factory_fodt-0.1.0.dev0.tar.gz`
- Size: 10,589 bytes
- SHA-256: `be1083ee18edc93e2ec24ba4b04c78709573b8f9c4d3d83223705f0d816f3b62`

**PYTHON_PACKAGE_BUILD: PASS**

---

## .NET NuGet Packages

### FODS NuGet
- File: `FormatFactory.Fods.0.1.0-tier0.nupkg`
- Size: 13,063 bytes
- SHA-256: `b10bbd4f2cbb219fd214d6c73aab0296408234dec4d06885b0254d3779bbc6de`
- DLL (`lib/net10.0/FormatFactory.Fods.dll`): 25,600 bytes

### FODT NuGet
- File: `FormatFactory.Fodt.0.1.0-tier0.nupkg`
- Size: 12,106 bytes
- SHA-256: `2bdf2da57bae0a96f9b094e639c02bb8a9efa43ac8b63d93b5babc37d2eb3a89`
- DLL (`lib/net10.0/FormatFactory.Fodt.dll`): 23,552 bytes

**NUGET_PACKAGE_BUILD: PASS**

---

## Python Test Coverage (R41)

| Suite | Result |
|-------|--------|
| tests/python/fods/ | 181 passed, 4 skipped |
| tests/python/fodt/ | 181 passed, 4 skipped |

## .NET Test Coverage (R41)

| Suite | Result |
|-------|--------|
| tests/net/fods/ | 157 passed |
| tests/net/fodt/ | 145 passed |

---

## Notes

- Build artifacts in `.local/package-builds/` (gitignored)
- publication_authorized: false — packages are local-only, NOT published
- commercial_product_ready: false — Gate 11 G11-G not yet approved by Babar Raza
- All hashes computed from on-disk artifacts at time of R41 sprint
