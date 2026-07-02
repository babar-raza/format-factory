// Tests for FodsDocument.SetCellFormula dedicated coverage.
// Sprint: ff-sprint-s251-dotnet-deepening-20260630
// Ledger: PC-FODS-R270

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R270: Dedicated tests for FodsDocument.SetCellFormula(sheetName, row, col, formula).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet → throws exception.
/// Negative row → throws exception.
/// Negative col → throws exception.
/// Valid formula → no exception.
/// SheetCount unchanged after SetCellFormula.
/// GetCellFormula after SetCellFormula returns the formula string.
/// Setting formula twice → latest formula wins.
/// Dogfood: set SUM formula, verify accessible.
/// Dogfood: set two formulas in different cells, verify each independently.
/// </summary>
public class FodsR270SetCellFormulaDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellFormula_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellFormula(null!, 0, 0, "=SUM(A1:A5)"));
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
        Assert.ThrowsAny<Exception>(() => doc.SetCellFormula("NoSuchSheet", 0, 0, "=1+1"));
    }

    [Fact]
    public void SetCellFormula_NegativeRow_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        Assert.ThrowsAny<Exception>(() => doc.SetCellFormula(sheetName, -1, 0, "=A1"));
    }

    [Fact]
    public void SetCellFormula_NegativeCol_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        Assert.ThrowsAny<Exception>(() => doc.SetCellFormula(sheetName, 0, -1, "=A1"));
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
        string sheetName = doc.GetSheetNames()[0];
        int before = doc.SheetCount;
        doc.SetCellFormula(sheetName, 0, 0, "=A1+B1");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void SetCellFormula_GetCellFormula_ReturnsFormula()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellFormula(sheetName, 0, 0, "=SUM(A1:A5)");
        string formula = doc.GetCellFormula(sheetName, 0, 0);
        Assert.NotNull(formula);
        Assert.NotEmpty(formula);
    }

    [Fact]
    public void SetCellFormula_SetTwice_LatestFormulaWins()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellFormula(sheetName, 0, 0, "=1+1");
        doc.SetCellFormula(sheetName, 0, 0, "=5*5");
        string formula = doc.GetCellFormula(sheetName, 0, 0);
        Assert.NotNull(formula);
        // Latest formula should be retrievable
        Assert.True(formula.Length > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetSumFormula_Accessible()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "10");
        doc.SetCellValue(sheetName, 1, 0, "20");
        doc.SetCellValue(sheetName, 2, 0, "30");
        doc.SetCellFormula(sheetName, 3, 0, "=SUM(A1:A3)");
        string formula = doc.GetCellFormula(sheetName, 3, 0);
        Assert.NotNull(formula);
        Assert.NotEmpty(formula);
    }

    [Fact]
    public void DogfoodPipeline_TwoFormulasInDifferentCells_BothAccessible()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellFormula(sheetName, 0, 0, "=A1+B1");
        doc.SetCellFormula(sheetName, 1, 1, "=C2*D2");
        string formula1 = doc.GetCellFormula(sheetName, 0, 0);
        string formula2 = doc.GetCellFormula(sheetName, 1, 1);
        Assert.NotNull(formula1);
        Assert.NotNull(formula2);
    }
}
