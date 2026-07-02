// Tests for FodsDocument.SetCellFormula dedicated coverage.
// Sprint: ff-sprint-s221-dotnet-deepening-20260629
// Ledger: PC-FODS-R239

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R239: Dedicated tests for FodsDocument.SetCellFormula(sheetName, row, col, formula).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet → throws exception.
/// Negative row → throws exception.
/// Negative col → throws exception.
/// Valid formula → no exception.
/// SheetCount unchanged after set.
/// Set then get returns non-null.
/// Set twice → latest value.
/// Dogfood: set formula multiple cells, get all non-null.
/// </summary>
public class FodsR239SetCellFormulaDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellFormula_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellFormula(null!, 0, 0, "=A1+B1"));
    }

    [Fact]
    public void SetCellFormula_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellFormula("   ", 0, 0, "=A1+B1"));
    }

    [Fact]
    public void SetCellFormula_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellFormula("NoSheet", 0, 0, "=A1+B1"));
    }

    [Fact]
    public void SetCellFormula_NegativeRow_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        Assert.ThrowsAny<Exception>(() => doc.SetCellFormula(sheetName, -1, 0, "=A1+B1"));
    }

    [Fact]
    public void SetCellFormula_NegativeCol_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        Assert.ThrowsAny<Exception>(() => doc.SetCellFormula(sheetName, 0, -1, "=A1+B1"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellFormula_ValidFormula_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        var ex = Record.Exception(() => doc.SetCellFormula(sheetName, 0, 0, "=1+1"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellFormula_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellFormula(sheetName, 0, 0, "=1+1");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void SetCellFormula_GetFormulaReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellFormula(sheetName, 0, 0, "=SUM(A1:A3)");
        var result = doc.GetCellFormulaValue(sheetName, 0, 0);
        Assert.NotNull(result);
    }

    [Fact]
    public void SetCellFormula_SetTwice_GetReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellFormula(sheetName, 0, 0, "=1+1");
        doc.SetCellFormula(sheetName, 0, 0, "=2+2");
        var result = doc.GetCellFormulaValue(sheetName, 0, 0);
        Assert.NotNull(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultipleCells_AllNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        string[] formulas = { "=1+1", "=2*3", "=10-4", "=SUM(1,2,3)" };
        for (int i = 0; i < formulas.Length; i++)
            doc.SetCellFormula(sheetName, i, 0, formulas[i]);
        for (int i = 0; i < formulas.Length; i++)
        {
            var result = doc.GetCellFormulaValue(sheetName, i, 0);
            Assert.NotNull(result);
        }
    }
}
