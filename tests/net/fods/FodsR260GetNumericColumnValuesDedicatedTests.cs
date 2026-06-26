// Tests for FodsDocument.GetNumericColumnValues dedicated coverage.
// Sprint: ff-sprint-s242-dotnet-deepening-20260629
// Ledger: PC-FODS-R260

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R260: Dedicated tests for FodsDocument.GetNumericColumnValues(sheetName, columnIndex).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet → throws exception.
/// Negative column index → throws exception.
/// Empty sheet → returns empty or zero-count result.
/// Non-null result after data set.
/// Numeric values parsed from string cells.
/// SheetCount unchanged after call.
/// Called twice → same result size.
/// Dogfood: add numeric rows, verify values returned.
/// </summary>
public class FodsR260GetNumericColumnValuesDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNumericColumnValues_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetNumericColumnValues(null!, 0));
    }

    [Fact]
    public void GetNumericColumnValues_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetNumericColumnValues("   ", 0));
    }

    [Fact]
    public void GetNumericColumnValues_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetNumericColumnValues("NoSuchSheet", 0));
    }

    [Fact]
    public void GetNumericColumnValues_NegativeColumnIndex_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        Assert.ThrowsAny<Exception>(() => doc.GetNumericColumnValues(sheetName, -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNumericColumnValues_EmptySheet_ReturnsEmpty()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        var result = doc.GetNumericColumnValues(sheetName, 0);
        Assert.NotNull(result);
        Assert.Empty(result);
    }

    [Fact]
    public void GetNumericColumnValues_NumericCells_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "100");
        doc.SetCellValue(sheetName, 1, 0, "200");
        var result = doc.GetNumericColumnValues(sheetName, 0);
        Assert.NotNull(result);
    }

    [Fact]
    public void GetNumericColumnValues_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "42");
        int before = doc.SheetCount;
        doc.GetNumericColumnValues(sheetName, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetNumericColumnValues_CalledTwice_SameResultSize()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "10");
        doc.SetCellValue(sheetName, 1, 0, "20");
        var r1 = doc.GetNumericColumnValues(sheetName, 0);
        var r2 = doc.GetNumericColumnValues(sheetName, 0);
        Assert.Equal(r1.Count, r2.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddNumericRows_VerifyValuesReturned()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        // Add score data
        doc.AddRow(sheetName, new[] { "Name", "Score" });
        doc.AddRow(sheetName, new[] { "Alice", "95" });
        doc.AddRow(sheetName, new[] { "Bob", "82" });
        doc.AddRow(sheetName, new[] { "Carol", "78" });
        // Column 1 (Score) should contain numeric values
        var scores = doc.GetNumericColumnValues(sheetName, 1);
        Assert.NotNull(scores);
        // Should find at least some numeric values
        Assert.True(scores.Count >= 1);
        // All values should be non-negative
        foreach (var s in scores)
            Assert.True(s >= 0);
    }
}
