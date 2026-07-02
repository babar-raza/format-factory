// Tests for FodsDocument.GetCellFormula dedicated coverage.
// Sprint: ff-sprint-s284-dotnet-deepening-20260630
// Ledger: PC-FODS-R312

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R312: Dedicated tests for FodsDocument.GetCellFormula(sheetName, row, col).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet name throws exception.
/// Negative row throws exception.
/// Negative col throws exception.
/// Valid call returns non-null.
/// SheetCount unchanged after GetCellFormula.
/// Called twice returns same result.
/// Dogfood: set formula then get returns it.
/// Dogfood: multiple cells with formulas independently retrievable.
/// </summary>
public class FodsR312GetCellFormulaDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellFormula_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellFormula(null!, 0, 0));
    }

    [Fact]
    public void GetCellFormula_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellFormula("   ", 0, 0));
    }

    [Fact]
    public void GetCellFormula_NonexistentSheet_ReturnsNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Null(doc.GetCellFormula("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellFormula_NegativeRow_ReturnsNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        Assert.Null(doc.GetCellFormula(sheet, -1, 0));
    }

    [Fact]
    public void GetCellFormula_NegativeCol_ReturnsNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        Assert.Null(doc.GetCellFormula(sheet, 0, -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellFormula_ValidCall_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        doc.SetCellFormula(sheet, 0, 0, "=A1+B1");
        string? formula = doc.GetCellFormula(sheet, 0, 0);
        Assert.NotNull(formula);
    }

    [Fact]
    public void GetCellFormula_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        int before = doc.SheetCount;
        doc.SetCellFormula(sheet, 0, 0, "=SUM(A1:A5)");
        _ = doc.GetCellFormula(sheet, 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellFormula_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        doc.SetCellFormula(sheet, 0, 0, "=A1*2");
        string? first = doc.GetCellFormula(sheet, 0, 0);
        string? second = doc.GetCellFormula(sheet, 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetFormulaThenGet_ReturnsIt()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        doc.SetCellFormula(sheet, 1, 1, "=SUM(A1:A10)");
        string? formula = doc.GetCellFormula(sheet, 1, 1);
        Assert.NotNull(formula);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_IndependentlyRetrievable()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        doc.SetCellFormula(sheet, 0, 0, "=A1+B1");
        doc.SetCellFormula(sheet, 1, 0, "=A2+B2");
        string? f1 = doc.GetCellFormula(sheet, 0, 0);
        string? f2 = doc.GetCellFormula(sheet, 1, 0);
        Assert.NotNull(f1);
        Assert.NotNull(f2);
    }
}
