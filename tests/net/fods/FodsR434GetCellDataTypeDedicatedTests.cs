// Tests for FodsDocument.GetCellDataType dedicated coverage.
// Sprint: ff-sprint-s390-dotnet-deepening-20260630
// Ledger: PC-FODS-R434

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R434: Dedicated tests for FodsDocument.GetCellDataType().
/// Null/whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-null.
/// SheetCount unchanged after GetCellDataType.
/// Idempotent (called twice same result).
/// Is string type.
/// Dogfood: SetCellValue then GetCellDataType non-null.
/// Dogfood: multiple cells return non-null.
/// </summary>
public class FodsR434GetCellDataTypeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellDataType_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellDataType(null!, 0, 0));
    }

    [Fact]
    public void GetCellDataType_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellDataType("   ", 0, 0));
    }

    [Fact]
    public void GetCellDataType_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellDataType("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellDataType_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        Assert.ThrowsAny<Exception>(() => doc.GetCellDataType(sheetName, -1, 0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellDataType_ValidCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        doc.SetCellValue(sheetName, 0, 0, "Hello");
        string dataType = doc.GetCellDataType(sheetName, 0, 0);
        Assert.NotNull(dataType);
    }

    [Fact]
    public void GetCellDataType_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetName(0);
        doc.SetCellValue(sheetName, 0, 0, "Test");
        _ = doc.GetCellDataType(sheetName, 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellDataType_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        doc.SetCellValue(sheetName, 0, 0, "Data");
        string first = doc.GetCellDataType(sheetName, 0, 0);
        string second = doc.GetCellDataType(sheetName, 0, 0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCellDataType_IsString()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        doc.SetCellValue(sheetName, 0, 0, "Value");
        string dataType = doc.GetCellDataType(sheetName, 0, 0);
        Assert.IsType<string>(dataType);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetCellValue_GetDataType_NonNull()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        doc.SetCellValue(sheetName, 0, 0, "Report");
        string dataType = doc.GetCellDataType(sheetName, 0, 0);
        Assert.NotNull(dataType);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_AllNonNull()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        doc.SetCellValue(sheetName, 0, 0, "Alpha");
        doc.SetCellValue(sheetName, 1, 0, "Beta");
        doc.SetCellValue(sheetName, 2, 0, "Gamma");
        Assert.NotNull(doc.GetCellDataType(sheetName, 0, 0));
        Assert.NotNull(doc.GetCellDataType(sheetName, 1, 0));
        Assert.NotNull(doc.GetCellDataType(sheetName, 2, 0));
    }
}
