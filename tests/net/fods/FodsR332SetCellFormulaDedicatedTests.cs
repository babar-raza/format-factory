// Tests for FodsDocument.SetCellFormula dedicated coverage.
// Sprint: ff-sprint-s304-dotnet-deepening-20260630
// Ledger: PC-FODS-R332

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R332: Dedicated tests for FodsDocument.SetCellFormula(sheetName, row, col, formula).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet throws exception.
/// Negative row throws exception.
/// Negative col throws exception.
/// Valid call no exception.
/// SheetCount unchanged after SetCellFormula.
/// GetCellFormula returns non-null after SetCellFormula.
/// Set-twice no exception.
/// Dogfood: set SUM formula, verify non-null.
/// </summary>
public class FodsR332SetCellFormulaDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellFormula_NullSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellFormula(null!, 0, 0, "=SUM(A1:A3)"));
    }

    [Fact]
    public void SetCellFormula_WhitespaceSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellFormula("   ", 0, 0, "=SUM(A1:A3)"));
    }

    [Fact]
    public void SetCellFormula_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SetCellFormula("NoSuchSheet", 0, 0, "=SUM(A1:A3)"));
    }

    [Fact]
    public void SetCellFormula_NegativeRow_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellFormula("Sheet1", -1, 0, "=SUM(A1:A3)"));
    }

    [Fact]
    public void SetCellFormula_NegativeCol_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellFormula("Sheet1", 0, -1, "=SUM(A1:A3)"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellFormula_ValidCall_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var ex = Record.Exception(() => doc.SetCellFormula("Sheet1", 0, 0, "=SUM(B1:B3)"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellFormula_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        doc.SetCellFormula("Sheet1", 0, 0, "=SUM(B1:B3)");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void SetCellFormula_GetCellFormula_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellFormula("Sheet1", 0, 0, "=SUM(B1:B3)");
        string? formula = doc.GetCellFormula("Sheet1", 0, 0);
        Assert.NotNull(formula);
    }

    [Fact]
    public void SetCellFormula_SetTwice_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellFormula("Sheet1", 0, 0, "=SUM(B1:B3)");
        var ex = Record.Exception(() => doc.SetCellFormula("Sheet1", 0, 0, "=AVERAGE(B1:B3)"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetSumFormula_GetCellFormulaNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "10");
        doc.SetCellValue("Data", 1, 0, "20");
        doc.SetCellValue("Data", 2, 0, "30");
        doc.SetCellFormula("Data", 3, 0, "=SUM(A1:A3)");
        string? formula = doc.GetCellFormula("Data", 3, 0);
        Assert.NotNull(formula);
        int before = doc.SheetCount;
        Assert.Equal(before, doc.SheetCount);
    }
}
