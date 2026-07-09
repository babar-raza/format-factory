// Type 4 persistence roundtrip tests for Category C sheet-config properties
// GI-FODS-NET-001 Phase 5 — validates that sheet-config setters write to ODF XML
// (office:settings config:config-item hierarchy) so values survive ToFodsXml → LoadFromXml roundtrip.
//
// Each test: CreateNew → AddSheet → Set[Property] → roundtrip → Get[Property]

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// GI-FODS-NET-001 Phase 5 Type 4 tests: Category C sheet-config property persistence
/// through ODF XML roundtrip (ToFodsXml → LoadFromXml).
/// Proves that SetSheetConfigItem writes correct ODF XML so values survive save/reload.
/// </summary>
public class FodsGI001CategoryCSheetConfigTests
{
    private static FodsDocument CreateDocWithSheet(string sheetName = "Sheet1")
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet(sheetName);
        return doc;
    }

    private static FodsDocument Roundtrip(FodsDocument doc)
    {
        string xml = doc.ToFodsXml();
        return FodsDocument.LoadFromXml(xml);
    }

    [Fact]
    public void RT5_C01_SetSheetFreezeRows_Roundtrips()
    {
        var doc = CreateDocWithSheet();
        const string sheetName = "Sheet1";
        doc.SetSheetFreezeRows(sheetName, 3);
        var reloaded = Roundtrip(doc);
        Assert.Equal(3, reloaded.GetSheetFreezeRows(sheetName));
    }

    [Fact]
    public void RT5_C02_SetSheetFreezeColumns_Roundtrips()
    {
        var doc = CreateDocWithSheet();
        const string sheetName = "Sheet1";
        doc.SetSheetFreezeColumns(sheetName, 2);
        var reloaded = Roundtrip(doc);
        Assert.Equal(2, reloaded.GetSheetFreezeColumns(sheetName));
    }

    [Fact]
    public void RT5_C03_SetSheetZoomLevel_Roundtrips()
    {
        var doc = CreateDocWithSheet();
        const string sheetName = "Sheet1";
        doc.SetSheetZoomLevel(sheetName, 150);
        var reloaded = Roundtrip(doc);
        Assert.Equal(150, reloaded.GetSheetZoomLevel(sheetName));
    }

    [Fact]
    public void RT5_C04_SetSheetPrintArea_Roundtrips()
    {
        var doc = CreateDocWithSheet();
        const string sheetName = "Sheet1";
        doc.SetSheetPrintArea(sheetName, "A1:D10");
        var reloaded = Roundtrip(doc);
        Assert.Equal("A1:D10", reloaded.GetSheetPrintArea(sheetName));
    }

    [Fact]
    public void RT5_C05_SetSheetFreezeRows_Zero_ClearsFreeze()
    {
        // Edge case: setting freeze rows to 0 should remove or zero the freeze
        var doc = CreateDocWithSheet();
        const string sheetName = "Sheet1";
        doc.SetSheetFreezeRows(sheetName, 3);
        doc.SetSheetFreezeRows(sheetName, 0);
        var reloaded = Roundtrip(doc);
        Assert.Equal(0, reloaded.GetSheetFreezeRows(sheetName));
    }
}
