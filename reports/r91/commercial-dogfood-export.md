---
sprint: R91
generated_by: r91-worker
---

# Commercial Dogfood Export

## Summary

FODT .NET TXT dogfood bridge added via the `/add-dogfood-export` governed skill (invoked as part of the `add-dotnet-object-model-feature` workflow). `FodtDocument.GetPlainText()` is the Format Factory target library path. 3 new tests verify the FF code path is used.

## FF Library Path

`src/net/fodt/FodtDocument.cs` — `GetPlainText()` method

This is a Format Factory library method (not a thin wrapper around an external library). The dogfood bridge verifies that the FF library path is exercised by the adapter tests, not bypassed.

## Adapter: tests/net/fodt/FodtR91TxtDogfoodTests.cs

```csharp
[TestClass]
public class FodtR91TxtDogfoodTests
{
    [TestMethod]
    public void GetPlainText_UsesFFLibraryPath_NotExternal()
    [TestMethod]
    public void GetPlainText_ReturnsAllParagraphText()
    [TestMethod]
    public void GetPlainText_EmptyDocument_ReturnsEmpty()
}
```

All 3 tests pass via `dotnet test`.

## Dogfood Map Update

`product-capability-matrix/dogfood-map.yaml` updated:

```yaml
fodt_net_txt_dogfood:
  source_format: fodt
  target_format: txt
  track: net
  library_path: FodtDocument.GetPlainText()
  dogfood_status: IMPLEMENTED
  implemented_sprint: R91
  test_file: tests/net/fodt/FodtR91TxtDogfoodTests.cs
  tests_passing: 3
```

## Product-Code Ledger Entry

`R91-GOVERNED-FODT-NET-TXT-DOGFOOD-001` written to `tools/evidence/product-code-ledger.yaml` before source edit.

Fields:
- `item_id`: R91-GOVERNED-FODT-NET-TXT-DOGFOOD-001
- `sprint`: R91
- `format`: fodt
- `track`: net
- `feature`: GetPlainText dogfood bridge
- `files_changed`: src/net/fodt/FodtDocument.cs
- `skill_used`: add-dotnet-object-model-feature
- `governed`: true

## Evidence Artifacts

- `tests/net/fodt/FodtR91TxtDogfoodTests.cs` — 3 passing dogfood tests
- `product-capability-matrix/dogfood-map.yaml` — updated entry
- `tools/evidence/product-code-ledger.yaml` — R91 ledger entry
- `.local/evidences/{run_id}/dotnet-test-output.txt` — dotnet test output showing 3 pass
