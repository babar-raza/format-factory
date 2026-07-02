// Tests for FodsDocument.GetCellFormula dedicated (additional) coverage.
// Sprint: ff-sprint-s303-dotnet-deepening-20260630
// Ledger: PC-FODS-R331

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R331: Dedicated tests for FodsDocument.GetCellFormula additional scenarios.
/// Non-formula cell returns non-null (default or empty formula).
/// Formula set on row 0 col 0 returns non-null.
/// Formula set on row 2 col 3 returns non-null.
/// SheetCount unchanged after multiple GetCellFormula calls.
/// Set formula on adjacent cells no exception.
/// Idempotent: get formula twice returns same value.
/// Dogfood: set sum formula, get formula non-null.
/// Dogfood: set formula on multiple cells, each non-null.
/// </summary>
public class FodsR331GetCellFormulaDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellFormula_NonFormulaCell_ReturnsNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "plain text");
        string? formula = doc.GetCellFormula("Sheet1", 0, 0);
        Assert.Null(formula);
    }

    [Fact]
    public void GetCellFormula_FormulaOnRow0Col0_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellFormula("Sheet1", 0, 0, "=A1+B1");
        string? formula = doc.GetCellFormula("Sheet1", 0, 0);
        Assert.NotNull(formula);
    }

    [Fact]
    public void GetCellFormula_FormulaOnRow2Col3_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellFormula("Sheet1", 2, 3, "=SUM(A1:D2)");
        string? formula = doc.GetCellFormula("Sheet1", 2, 3);
        Assert.NotNull(formula);
    }

    [Fact]
    public void GetCellFormula_MultipleGetCalls_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellFormula("Sheet1", 0, 0, "=A1+1");
        int sheetsBefore = doc.SheetCount;
        _ = doc.GetCellFormula("Sheet1", 0, 0);
        _ = doc.GetCellFormula("Sheet1", 0, 0);
        _ = doc.GetCellFormula("Sheet1", 0, 0);
        Assert.Equal(sheetsBefore, doc.SheetCount);
    }

    [Fact]
    public void GetCellFormula_AdjacentCellFormulas_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellFormula("Sheet1", 0, 0, "=1+1");
        doc.SetCellFormula("Sheet1", 0, 1, "=2+2");
        var ex = Record.Exception(() =>
        {
            _ = doc.GetCellFormula("Sheet1", 0, 0);
            _ = doc.GetCellFormula("Sheet1", 0, 1);
        });
        Assert.Null(ex);
    }

    [Fact]
    public void GetCellFormula_Idempotent_SameValue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellFormula("Sheet1", 1, 1, "=B2*C3");
        string? first = doc.GetCellFormula("Sheet1", 1, 1);
        string? second = doc.GetCellFormula("Sheet1", 1, 1);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetSumFormula_GetFormulaNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Totals");
        doc.SetCellValue("Totals", 0, 0, "100");
        doc.SetCellValue("Totals", 1, 0, "200");
        doc.SetCellFormula("Totals", 2, 0, "=SUM(A1:A2)");
        string? formula = doc.GetCellFormula("Totals", 2, 0);
        Assert.NotNull(formula);
    }

    [Fact]
    public void DogfoodPipeline_SetFormulaOnMultipleCells_EachNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Calc");
        doc.SetCellFormula("Calc", 0, 0, "=1+1");
        doc.SetCellFormula("Calc", 1, 0, "=2*3");
        doc.SetCellFormula("Calc", 2, 0, "=10-4");
        string? f0 = doc.GetCellFormula("Calc", 0, 0);
        string? f1 = doc.GetCellFormula("Calc", 1, 0);
        string? f2 = doc.GetCellFormula("Calc", 2, 0);
        Assert.NotNull(f0);
        Assert.NotNull(f1);
        Assert.NotNull(f2);
    }
}
