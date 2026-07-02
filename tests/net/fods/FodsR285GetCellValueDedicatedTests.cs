// Tests for FodsDocument.GetCellValue dedicated coverage.
// Sprint: ff-sprint-s262-dotnet-deepening-20260630
// Ledger: PC-FODS-R285

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R285: Dedicated tests for FodsDocument.GetCellValue(sheetName, row, col).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet name → throws exception.
/// Negative row → throws exception.
/// Negative col → throws exception.
/// Valid cell → returns non-null string.
/// Empty cell → returns empty string or null (not throws).
/// After SetCellValue, returns the set value.
/// SheetCount unchanged after call.
/// Dogfood: set cell value and retrieve it.
/// Dogfood: multiple cells with different values, each retrievable.
/// </summary>
public class FodsR285GetCellValueDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellValue_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellValue(null!, 0, 0));
    }

    [Fact]
    public void GetCellValue_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellValue("   ", 0, 0));
    }

    [Fact]
    public void GetCellValue_NonexistentSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellValue("NoSheet", 0, 0));
    }

    [Fact]
    public void GetCellValue_NegativeRow_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellValue("Sheet1", -1, 0));
    }

    [Fact]
    public void GetCellValue_NegativeCol_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellValue("Sheet1", 0, -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellValue_AfterSetCellValue_ReturnsSetValue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "TestValue");
        string value = doc.GetCellValue("Sheet1", 0, 0);
        Assert.Equal("TestValue", value);
    }

    [Fact]
    public void GetCellValue_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "data");
        int before = doc.SheetCount;
        doc.GetCellValue("Sheet1", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellValue_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 1, 2, "consistent");
        string first = doc.GetCellValue("Sheet1", 1, 2);
        string second = doc.GetCellValue("Sheet1", 1, 2);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetAndRetrieve_ValueRoundTrips()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 2, 3, "ImportantData");
        string result = doc.GetCellValue("Data", 2, 3);
        Assert.Equal("ImportantData", result);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_EachReturnsCorrectValue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "Alpha");
        doc.SetCellValue("Sheet1", 0, 1, "Beta");
        doc.SetCellValue("Sheet1", 1, 0, "Gamma");
        Assert.Equal("Alpha", doc.GetCellValue("Sheet1", 0, 0));
        Assert.Equal("Beta", doc.GetCellValue("Sheet1", 0, 1));
        Assert.Equal("Gamma", doc.GetCellValue("Sheet1", 1, 0));
    }
}
