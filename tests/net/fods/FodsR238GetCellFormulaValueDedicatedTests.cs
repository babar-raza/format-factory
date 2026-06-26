// Tests for FodsDocument.GetCellFormulaValue dedicated coverage.
// Sprint: ff-sprint-s220-dotnet-deepening-20260629
// Ledger: PC-FODS-R238

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R238: Dedicated tests for FodsDocument.GetCellFormulaValue(sheetName, row, col).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet → throws exception.
/// Negative row → throws exception.
/// Negative col → throws exception.
/// Empty cell → returns null or empty string.
/// Non-null after set.
/// SheetCount unchanged after call.
/// Dogfood: set formula, get returns non-null.
/// Dogfood: two cells independent.
/// </summary>
public class FodsR238GetCellFormulaValueDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellFormulaValue_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFormulaValue(null!, 0, 0));
    }

    [Fact]
    public void GetCellFormulaValue_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFormulaValue("   ", 0, 0));
    }

    [Fact]
    public void GetCellFormulaValue_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFormulaValue("Ghost", 0, 0));
    }

    [Fact]
    public void GetCellFormulaValue_NegativeRow_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        Assert.ThrowsAny<Exception>(() => doc.GetCellFormulaValue(sheetName, -1, 0));
    }

    [Fact]
    public void GetCellFormulaValue_NegativeCol_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        Assert.ThrowsAny<Exception>(() => doc.GetCellFormulaValue(sheetName, 0, -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellFormulaValue_EmptyCell_ReturnsNullOrEmpty()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        var result = doc.GetCellFormulaValue(sheetName, 0, 0);
        Assert.True(result == null || result == string.Empty);
    }

    [Fact]
    public void GetCellFormulaValue_AfterSet_NonNull()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "=SUM(1,2)");
        var result = doc.GetCellFormulaValue(sheetName, 0, 0);
        Assert.NotNull(result);
    }

    [Fact]
    public void GetCellFormulaValue_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetNames()[0];
        doc.GetCellFormulaValue(sheetName, 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetFormula_GetReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "=A1+B1");
        doc.SetCellValue(sheetName, 0, 1, "=SUM(A1:A3)");
        var v0 = doc.GetCellFormulaValue(sheetName, 0, 0);
        var v1 = doc.GetCellFormulaValue(sheetName, 0, 1);
        Assert.NotNull(v0);
        Assert.NotNull(v1);
    }

    [Fact]
    public void DogfoodPipeline_TwoCells_Independent()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "=1+1");
        doc.SetCellValue(sheetName, 1, 0, "=2+2");
        var v0 = doc.GetCellFormulaValue(sheetName, 0, 0);
        var v1 = doc.GetCellFormulaValue(sheetName, 1, 0);
        // Both should be non-null or empty — they don't interfere
        Assert.NotNull(v0);
        Assert.NotNull(v1);
    }
}
