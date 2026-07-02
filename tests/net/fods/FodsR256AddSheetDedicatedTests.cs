// Tests for FodsDocument.AddSheet dedicated coverage.
// Sprint: ff-sprint-s238-dotnet-deepening-20260629
// Ledger: PC-FODS-R256

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R256: Dedicated tests for FodsDocument.AddSheet(sheetName).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Valid sheet → no exception.
/// SheetCount increases after AddSheet.
/// New sheet accessible via GetSheetNames.
/// New sheet accessible via GetRowCount.
/// Add two sheets → SheetCount increases by 2.
/// Added sheet name appears in GetSheetNames.
/// Called twice with different names → both accessible.
/// Dogfood: add sheet, add data, verify data isolated.
/// </summary>
public class FodsR256AddSheetDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AddSheet_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.AddSheet(null!));
    }

    [Fact]
    public void AddSheet_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.AddSheet("   "));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AddSheet_ValidName_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var ex = Record.Exception(() => doc.AddSheet("NewSheet"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddSheet_SheetCountIncreases()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        doc.AddSheet("ExtraSheet");
        Assert.True(doc.SheetCount > before);
    }

    [Fact]
    public void AddSheet_NewSheetAccessibleViaGetSheetNames()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("MyNewSheet");
        var names = doc.GetSheetNames();
        Assert.Contains("MyNewSheet", names);
    }

    [Fact]
    public void AddSheet_NewSheetAccessibleViaGetRowCount()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("DataSheet");
        var ex = Record.Exception(() => doc.GetRowCount("DataSheet"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddSheet_TwoSheets_SheetCountIncreasedByTwo()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        doc.AddSheet("SheetAlpha");
        doc.AddSheet("SheetBeta");
        Assert.True(doc.SheetCount >= before + 2);
    }

    [Fact]
    public void AddSheet_BothNamesInGetSheetNames()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("FirstNew");
        doc.AddSheet("SecondNew");
        var names = doc.GetSheetNames();
        Assert.Contains("FirstNew", names);
        Assert.Contains("SecondNew", names);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddSheet_DataIsolatedFromOriginal()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string original = doc.GetSheetNames()[0];
        doc.AddRow(original, new[] { "OriginalData" });
        doc.AddSheet("IsolatedSheet");
        int originalRows = doc.GetRowCount(original);
        int newRows = doc.GetRowCount("IsolatedSheet");
        Assert.True(originalRows > 0);
        Assert.Equal(0, newRows);
    }
}
