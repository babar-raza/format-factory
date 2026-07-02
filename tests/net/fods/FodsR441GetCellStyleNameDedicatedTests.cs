// Tests for FodsDocument.GetCellStyleName dedicated coverage.
// Sprint: ff-sprint-s392-dotnet-deepening-20260701
// Ledger: PC-FODS-R441

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R441: Dedicated tests for FodsDocument.GetCellStyleName().
/// Null/whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-null.
/// SheetCount unchanged after GetCellStyleName.
/// Idempotent (called twice same result).
/// Is string type.
/// Dogfood: SetCellValue then GetCellStyleName non-null.
/// Dogfood: multiple cells return non-null style names.
/// </summary>
public class FodsR441GetCellStyleNameDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellStyleName_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellStyleName(null!, 0, 0));
    }

    [Fact]
    public void GetCellStyleName_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellStyleName("   ", 0, 0));
    }

    [Fact]
    public void GetCellStyleName_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellStyleName("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellStyleName_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        Assert.ThrowsAny<Exception>(() => doc.GetCellStyleName(sheetName, -1, 0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellStyleName_ValidCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        doc.SetCellValue(sheetName, 0, 0, "Styled");
        string style = doc.GetCellStyleName(sheetName, 0, 0);
        Assert.NotNull(style);
    }

    [Fact]
    public void GetCellStyleName_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetName(0);
        doc.SetCellValue(sheetName, 0, 0, "Value");
        _ = doc.GetCellStyleName(sheetName, 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellStyleName_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        doc.SetCellValue(sheetName, 0, 0, "Data");
        string first = doc.GetCellStyleName(sheetName, 0, 0);
        string second = doc.GetCellStyleName(sheetName, 0, 0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCellStyleName_IsString()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        doc.SetCellValue(sheetName, 0, 0, "Item");
        string style = doc.GetCellStyleName(sheetName, 0, 0);
        Assert.IsType<string>(style);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetCellValue_GetStyleName_NonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        doc.SetCellValue(sheetName, 0, 0, "Header");
        string style = doc.GetCellStyleName(sheetName, 0, 0);
        Assert.NotNull(style);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_AllNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        doc.SetCellValue(sheetName, 0, 0, "Row1");
        doc.SetCellValue(sheetName, 1, 0, "Row2");
        doc.SetCellValue(sheetName, 2, 0, "Row3");
        Assert.NotNull(doc.GetCellStyleName(sheetName, 0, 0));
        Assert.NotNull(doc.GetCellStyleName(sheetName, 1, 0));
        Assert.NotNull(doc.GetCellStyleName(sheetName, 2, 0));
    }
}
