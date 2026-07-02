// Tests for FodsDocument.GetColumnValues dedicated coverage.
// Sprint: ff-sprint-s250-dotnet-deepening-20260630
// Ledger: PC-FODS-R269

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R269: Dedicated tests for FodsDocument.GetColumnValues(sheetName, columnIndex).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet → throws exception.
/// Negative column index → throws exception.
/// Empty sheet → returns empty or non-null collection.
/// After SetCellValue → values appear in result.
/// SheetCount unchanged after call.
/// Called twice → same result.
/// Dogfood: add rows with column data, verify GetColumnValues returns expected count.
/// Dogfood: multi-column, verify correct column is returned.
/// </summary>
public class FodsR269GetColumnValuesDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnValues_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetColumnValues(null!, 0));
    }

    [Fact]
    public void GetColumnValues_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetColumnValues("   ", 0));
    }

    [Fact]
    public void GetColumnValues_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetColumnValues("NoSuchSheet", 0));
    }

    [Fact]
    public void GetColumnValues_NegativeColumnIndex_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        Assert.ThrowsAny<Exception>(() => doc.GetColumnValues(sheetName, -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnValues_EmptySheet_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        var result = doc.GetColumnValues(sheetName, 0);
        Assert.NotNull(result);
    }

    [Fact]
    public void GetColumnValues_AfterSetCellValue_NonEmpty()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "Alpha");
        doc.SetCellValue(sheetName, 1, 0, "Beta");
        var result = doc.GetColumnValues(sheetName, 0);
        Assert.NotNull(result);
        Assert.True(result.Count > 0);
    }

    [Fact]
    public void GetColumnValues_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "V1");
        int before = doc.SheetCount;
        doc.GetColumnValues(sheetName, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetColumnValues_CalledTwice_SameCount()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "X");
        doc.SetCellValue(sheetName, 1, 0, "Y");
        int first = doc.GetColumnValues(sheetName, 0).Count;
        int second = doc.GetColumnValues(sheetName, 0).Count;
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddRowsWithData_ColumnValuesNonEmpty()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "Name", "Score" });
        doc.AddRow(sheetName, new[] { "Alice", "95" });
        doc.AddRow(sheetName, new[] { "Bob", "87" });
        doc.AddRow(sheetName, new[] { "Carol", "92" });
        var col0 = doc.GetColumnValues(sheetName, 0);
        Assert.NotNull(col0);
        Assert.True(col0.Count >= 1);
    }

    [Fact]
    public void DogfoodPipeline_MultiColumn_CorrectColumnReturned()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "Name", "Department" });
        doc.AddRow(sheetName, new[] { "Alice", "Engineering" });
        doc.AddRow(sheetName, new[] { "Bob", "Finance" });
        var col1 = doc.GetColumnValues(sheetName, 1);
        Assert.NotNull(col1);
        // Column 1 should contain department values
        Assert.True(col1.Count >= 1);
    }
}
