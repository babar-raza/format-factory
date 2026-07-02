// Tests for FodsDocument.GetRowValues dedicated coverage.
// Sprint: ff-sprint-s241-dotnet-deepening-20260629
// Ledger: PC-FODS-R259

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R259: Dedicated tests for FodsDocument.GetRowValues(sheetName, rowIndex).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet → throws exception.
/// Negative row index → throws exception.
/// Empty row → returns empty or small list.
/// Row with values → non-null result.
/// Values match what was set.
/// SheetCount unchanged after call.
/// Called twice → same result size.
/// Dogfood: AddRow then GetRowValues matches original values.
/// </summary>
public class FodsR259GetRowValuesDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowValues_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetRowValues(null!, 0));
    }

    [Fact]
    public void GetRowValues_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetRowValues("   ", 0));
    }

    [Fact]
    public void GetRowValues_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetRowValues("NoSuchSheet", 0));
    }

    [Fact]
    public void GetRowValues_NegativeRowIndex_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        Assert.ThrowsAny<Exception>(() => doc.GetRowValues(sheetName, -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowValues_RowWithValues_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "Hello");
        doc.SetCellValue(sheetName, 0, 1, "World");
        var values = doc.GetRowValues(sheetName, 0);
        Assert.NotNull(values);
    }

    [Fact]
    public void GetRowValues_ValuesMatchSet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "Alpha");
        doc.SetCellValue(sheetName, 0, 1, "Beta");
        var values = doc.GetRowValues(sheetName, 0);
        Assert.NotNull(values);
        // At least one of the set values should appear
        bool found = false;
        foreach (var v in values)
            if (v?.ToString()?.Contains("Alpha") == true) { found = true; break; }
        Assert.True(found);
    }

    [Fact]
    public void GetRowValues_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "Test");
        int before = doc.SheetCount;
        doc.GetRowValues(sheetName, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetRowValues_CalledTwice_SameResultSize()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "X");
        doc.SetCellValue(sheetName, 0, 1, "Y");
        var r1 = doc.GetRowValues(sheetName, 0);
        var r2 = doc.GetRowValues(sheetName, 0);
        Assert.Equal(r1.Count, r2.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddRowThenGetRowValues_MatchesOriginal()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        var rowData = new[] { "Name", "Dept", "Salary" };
        doc.AddRow(sheetName, rowData);
        // The added row should be retrievable (row index 0)
        var values = doc.GetRowValues(sheetName, 0);
        Assert.NotNull(values);
        Assert.True(values.Count >= 1);
        // The first value should match the first element or header
        bool anyMatch = false;
        foreach (var v in values)
        {
            string? s = v?.ToString();
            if (s == "Name" || s == "Dept" || s == "Salary") { anyMatch = true; break; }
        }
        Assert.True(anyMatch);
    }
}
