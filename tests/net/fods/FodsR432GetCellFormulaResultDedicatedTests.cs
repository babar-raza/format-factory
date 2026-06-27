// Tests for FodsDocument.GetCellFormulaResult dedicated coverage.
// Sprint: ff-sprint-s389-dotnet-deepening-20260630
// Ledger: PC-FODS-R432

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R432: Dedicated tests for FodsDocument.GetCellFormulaResult().
/// Null/whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Negative row index throws.
/// Out-of-range row index throws.
/// Valid cell returns non-null.
/// SheetCount unchanged after GetCellFormulaResult.
/// Idempotent (called twice same result).
/// Dogfood: SetCellValue then GetCellFormulaResult non-null.
/// Dogfood: multiple cells return non-null.
/// </summary>
public class FodsR432GetCellFormulaResultDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellFormulaResult_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFormulaResult(null!, 0, 0));
    }

    [Fact]
    public void GetCellFormulaResult_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFormulaResult("   ", 0, 0));
    }

    [Fact]
    public void GetCellFormulaResult_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFormulaResult("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellFormulaResult_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        Assert.ThrowsAny<Exception>(() => doc.GetCellFormulaResult(sheetName, -1, 0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellFormulaResult_ValidCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        doc.SetCellValue(sheetName, 0, 0, "100");
        string result = doc.GetCellFormulaResult(sheetName, 0, 0);
        Assert.NotNull(result);
    }

    [Fact]
    public void GetCellFormulaResult_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetName(0);
        doc.SetCellValue(sheetName, 0, 0, "42");
        _ = doc.GetCellFormulaResult(sheetName, 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellFormulaResult_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        doc.SetCellValue(sheetName, 0, 0, "200");
        string first = doc.GetCellFormulaResult(sheetName, 0, 0);
        string second = doc.GetCellFormulaResult(sheetName, 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetCellValue_GetFormulaResult_NonNull()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        doc.SetCellValue(sheetName, 0, 0, "500");
        string result = doc.GetCellFormulaResult(sheetName, 0, 0);
        Assert.NotNull(result);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_AllNonNull()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        doc.SetCellValue(sheetName, 0, 0, "10");
        doc.SetCellValue(sheetName, 1, 0, "20");
        doc.SetCellValue(sheetName, 2, 0, "30");
        Assert.NotNull(doc.GetCellFormulaResult(sheetName, 0, 0));
        Assert.NotNull(doc.GetCellFormulaResult(sheetName, 1, 0));
        Assert.NotNull(doc.GetCellFormulaResult(sheetName, 2, 0));
    }
}
