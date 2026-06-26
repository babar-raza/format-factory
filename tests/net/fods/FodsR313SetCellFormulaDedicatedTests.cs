// Tests for FodsDocument.SetCellFormula dedicated coverage.
// Sprint: ff-sprint-s285-dotnet-deepening-20260630
// Ledger: PC-FODS-R313

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R313: Dedicated tests for FodsDocument.SetCellFormula(sheetName, row, col, formula).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet name throws exception.
/// Negative row throws exception.
/// Negative col throws exception.
/// Valid call no exception.
/// SheetCount unchanged after SetCellFormula.
/// Set twice no exception.
/// Dogfood: set formula, no exception.
/// Dogfood: set formula on multiple cells no exception.
/// </summary>
public class FodsR313SetCellFormulaDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellFormula_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SetCellFormula(null!, 0, 0, "=A1+B1"));
    }

    [Fact]
    public void SetCellFormula_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SetCellFormula("   ", 0, 0, "=A1+B1"));
    }

    [Fact]
    public void SetCellFormula_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SetCellFormula("NoSuchSheet", 0, 0, "=A1+B1"));
    }

    [Fact]
    public void SetCellFormula_NegativeRow_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames().First();
        Assert.ThrowsAny<Exception>(() => doc.SetCellFormula(sheet, -1, 0, "=A1+B1"));
    }

    [Fact]
    public void SetCellFormula_NegativeCol_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames().First();
        Assert.ThrowsAny<Exception>(() => doc.SetCellFormula(sheet, 0, -1, "=A1+B1"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellFormula_ValidCall_NoException()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames().First();
        var ex = Record.Exception(() => doc.SetCellFormula(sheet, 0, 0, "=SUM(A1:A5)"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellFormula_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames().First();
        int before = doc.SheetCount;
        doc.SetCellFormula(sheet, 0, 0, "=A1*2");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void SetCellFormula_SetTwice_NoException()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames().First();
        doc.SetCellFormula(sheet, 0, 0, "=A1+B1");
        var ex = Record.Exception(() => doc.SetCellFormula(sheet, 0, 0, "=A1-B1"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetFormula_NoException()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames().First();
        doc.SetCellValue(sheet, 0, 0, "10");
        doc.SetCellValue(sheet, 0, 1, "20");
        var ex = Record.Exception(() => doc.SetCellFormula(sheet, 0, 2, "=SUM(A1:B1)"));
        Assert.Null(ex);
    }

    [Fact]
    public void DogfoodPipeline_SetFormulaMultipleCells_NoException()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames().First();
        var ex = Record.Exception(() =>
        {
            doc.SetCellFormula(sheet, 0, 0, "=A1+B1");
            doc.SetCellFormula(sheet, 1, 0, "=A2*2");
            doc.SetCellFormula(sheet, 2, 0, "=SUM(A1:A2)");
        });
        Assert.Null(ex);
    }
}
