// Type 4 persistence roundtrip tests for Category B properties
// GI-FODS-NET-001 Phase 4c — validates that Category B setters write to ODF XML
// so values survive ToFodsXml() → LoadFromXml() roundtrip.
//
// Each test: CreateNew → AddSheet → SetCellValue → Set[Property] → roundtrip → Get[Property]

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// GI-FODS-NET-001 Phase 4c Type 4 tests: Category B cell-property persistence
/// through ODF XML roundtrip (ToFodsXml → LoadFromXml).
/// Proves that FodsStyleEditor writes correct ODF XML so values survive save/reload.
/// </summary>
public class FodsGI001CategoryBRoundtripTests
{
    private static FodsDocument CreateDocWithCell(string sheetName = "Sheet1")
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet(sheetName);
        doc.SetCellValue(sheetName, 0, 0, "test");
        return doc;
    }

    private static FodsDocument Roundtrip(FodsDocument doc)
    {
        string xml = doc.ToFodsXml();
        return FodsDocument.LoadFromXml(xml);
    }

    // -------------------------------------------------------------------------
    // RT4-B01: GetCellHorizontalAlignment
    // -------------------------------------------------------------------------

    [Fact]
    public void RT4_B01_SetCellHorizontalAlignment_Roundtrips()
    {
        var doc = CreateDocWithCell();
        doc.SetCellHorizontalAlignment("Sheet1", 0, 0, "center");
        var r = Roundtrip(doc);
        Assert.Equal("center", r.GetCellHorizontalAlignment("Sheet1", 0, 0));
    }

    [Fact]
    public void RT4_B01_SetCellHorizontalAlignment_End_Roundtrips()
    {
        var doc = CreateDocWithCell();
        doc.SetCellHorizontalAlignment("Sheet1", 0, 0, "end");
        var r = Roundtrip(doc);
        Assert.Equal("end", r.GetCellHorizontalAlignment("Sheet1", 0, 0));
    }

    // -------------------------------------------------------------------------
    // RT4-B02: GetCellVerticalAlignment
    // -------------------------------------------------------------------------

    [Fact]
    public void RT4_B02_SetCellVerticalAlignment_Roundtrips()
    {
        var doc = CreateDocWithCell();
        doc.SetCellVerticalAlignment("Sheet1", 0, 0, "middle");
        var r = Roundtrip(doc);
        Assert.Equal("middle", r.GetCellVerticalAlignment("Sheet1", 0, 0));
    }

    // -------------------------------------------------------------------------
    // RT4-B03: GetCellFontColor (via FodsStyleEditor)
    // -------------------------------------------------------------------------

    [Fact]
    public void RT4_B03_SetCellFontColor_Roundtrips()
    {
        var doc = CreateDocWithCell();
        doc.SetCellFontColor("Sheet1", 0, 0, "#0000FF");
        var r = Roundtrip(doc);
        Assert.Equal("#0000FF", r.GetCellFontColor("Sheet1", 0, 0));
    }

    // -------------------------------------------------------------------------
    // RT4-B04: GetCellUnderline
    // -------------------------------------------------------------------------

    [Fact]
    public void RT4_B04_SetCellUnderline_Roundtrips()
    {
        var doc = CreateDocWithCell();
        doc.SetCellUnderline("Sheet1", 0, 0, "solid");
        var r = Roundtrip(doc);
        Assert.Equal("solid", r.GetCellUnderline("Sheet1", 0, 0));
    }

    // -------------------------------------------------------------------------
    // RT4-B05: GetCellShrinkToFit
    // -------------------------------------------------------------------------

    [Fact]
    public void RT4_B05_SetCellShrinkToFit_Roundtrips()
    {
        var doc = CreateDocWithCell();
        doc.SetCellShrinkToFit("Sheet1", 0, 0, true);
        var r = Roundtrip(doc);
        Assert.True(r.GetCellShrinkToFit("Sheet1", 0, 0));
    }

    // -------------------------------------------------------------------------
    // RT4-B06: GetCellRotationAngle
    // -------------------------------------------------------------------------

    [Fact]
    public void RT4_B06_SetCellRotationAngle_Roundtrips()
    {
        var doc = CreateDocWithCell();
        doc.SetCellRotationAngle("Sheet1", 0, 0, 90);
        var r = Roundtrip(doc);
        Assert.Equal(90, r.GetCellRotationAngle("Sheet1", 0, 0));
    }

    // -------------------------------------------------------------------------
    // RT4-B07: GetCellStrikethrough
    // -------------------------------------------------------------------------

    [Fact]
    public void RT4_B07_SetCellStrikethrough_Roundtrips()
    {
        var doc = CreateDocWithCell();
        doc.SetCellStrikethrough("Sheet1", 0, 0, true);
        var r = Roundtrip(doc);
        Assert.True(r.GetCellStrikethrough("Sheet1", 0, 0));
    }

    // -------------------------------------------------------------------------
    // RT4-B08: GetCellBorderStyle
    // -------------------------------------------------------------------------

    [Fact]
    public void RT4_B08_SetCellBorderStyle_Roundtrips()
    {
        var doc = CreateDocWithCell();
        doc.SetCellBorderStyle("Sheet1", 0, 0, "0.05pt solid #000000");
        var r = Roundtrip(doc);
        Assert.Equal("0.05pt solid #000000", r.GetCellBorderStyle("Sheet1", 0, 0));
    }

    // -------------------------------------------------------------------------
    // RT4-B09: GetCellIndentLevel
    // -------------------------------------------------------------------------

    [Fact]
    public void RT4_B09_SetCellIndentLevel_Roundtrips()
    {
        var doc = CreateDocWithCell();
        doc.SetCellIndentLevel("Sheet1", 0, 0, 2);
        var r = Roundtrip(doc);
        Assert.Equal(2, r.GetCellIndentLevel("Sheet1", 0, 0));
    }

    // -------------------------------------------------------------------------
    // RT4-B10: Compound — multiple properties on same cell survive roundtrip
    // -------------------------------------------------------------------------

    [Fact]
    public void RT4_B10_MultipleProperties_SameCell_AllRoundtrip()
    {
        var doc = CreateDocWithCell();
        doc.SetCellHorizontalAlignment("Sheet1", 0, 0, "center");
        doc.SetCellVerticalAlignment("Sheet1", 0, 0, "middle");
        doc.SetCellFontColor("Sheet1", 0, 0, "#FF0000");
        doc.SetCellUnderline("Sheet1", 0, 0, "solid");

        var r = Roundtrip(doc);

        Assert.Equal("center", r.GetCellHorizontalAlignment("Sheet1", 0, 0));
        Assert.Equal("middle", r.GetCellVerticalAlignment("Sheet1", 0, 0));
        Assert.Equal("#FF0000", r.GetCellFontColor("Sheet1", 0, 0));
        Assert.Equal("solid", r.GetCellUnderline("Sheet1", 0, 0));
    }
}
