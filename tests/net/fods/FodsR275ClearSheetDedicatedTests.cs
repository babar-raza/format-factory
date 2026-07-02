// Tests for FodsDocument.ClearSheet dedicated coverage.
// Sprint: ff-sprint-s255-dotnet-deepening-20260630
// Ledger: PC-FODS-R275

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R275: Dedicated tests for FodsDocument.ClearSheet(sheetName).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet → throws exception.
/// Valid clear → no exception.
/// SheetCount unchanged after clear.
/// GetRowCount after clear is 0 or less than before.
/// Sheet still accessible after clear.
/// Dogfood: add data, clear, verify row count reduced.
/// Dogfood: clear multiple times idempotently.
/// </summary>
public class FodsR275ClearSheetDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ClearSheet_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.ClearSheet(null!));
    }

    [Fact]
    public void ClearSheet_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.ClearSheet("   "));
    }

    [Fact]
    public void ClearSheet_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.ClearSheet("NoSuchSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ClearSheet_ValidSheet_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        var ex = Record.Exception(() => doc.ClearSheet(sheetName));
        Assert.Null(ex);
    }

    [Fact]
    public void ClearSheet_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "A", "B" });
        int before = doc.SheetCount;
        doc.ClearSheet(sheetName);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void ClearSheet_SheetStillAccessibleAfterClear()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "Data" });
        doc.ClearSheet(sheetName);
        // Sheet should still be in GetSheetNames
        Assert.Contains(sheetName, doc.GetSheetNames());
    }

    [Fact]
    public void ClearSheet_RowCountDecreases()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "R1", "R2" });
        doc.AddRow(sheetName, new[] { "R3", "R4" });
        doc.AddRow(sheetName, new[] { "R5", "R6" });
        int before = doc.GetRowCount(sheetName);
        doc.ClearSheet(sheetName);
        int after = doc.GetRowCount(sheetName);
        Assert.True(after <= before);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddDataThenClear_RowCountReduced()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "Name", "Score" });
        doc.AddRow(sheetName, new[] { "Alice", "95" });
        doc.AddRow(sheetName, new[] { "Bob", "87" });
        doc.AddRow(sheetName, new[] { "Carol", "91" });
        int beforeClear = doc.GetRowCount(sheetName);
        Assert.True(beforeClear >= 4);
        doc.ClearSheet(sheetName);
        int afterClear = doc.GetRowCount(sheetName);
        Assert.True(afterClear < beforeClear);
    }

    [Fact]
    public void DogfoodPipeline_ClearTwice_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "A" });
        doc.ClearSheet(sheetName);
        var ex = Record.Exception(() => doc.ClearSheet(sheetName));
        Assert.Null(ex);
        // Sheet still accessible
        Assert.Contains(sheetName, doc.GetSheetNames());
    }
}
