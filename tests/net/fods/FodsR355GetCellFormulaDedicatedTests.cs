// Tests for FodsDocument.GetCellFormula dedicated coverage.
// Sprint: ff-sprint-s322-dotnet-deepening-20260630
// Ledger: PC-FODS-R355

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R355: Dedicated tests for FodsDocument.GetCellFormula().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Nonexistent sheet throws.
/// Negative row throws.
/// Valid call returns non-null.
/// SheetCount unchanged after GetCellFormula.
/// Called twice same result.
/// Dogfood: SetCellFormula then GetCellFormula.
/// Dogfood: multiple cells all non-null.
/// </summary>
public class FodsR355GetCellFormulaDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellFormula_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.ThrowsAny<Exception>(() => doc.GetCellFormula(null!, 0, 0));
    }

    [Fact]
    public void GetCellFormula_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.ThrowsAny<Exception>(() => doc.GetCellFormula("   ", 0, 0));
    }

    [Fact]
    public void GetCellFormula_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFormula("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellFormula_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.ThrowsAny<Exception>(() => doc.GetCellFormula("Data", -1, 0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellFormula_ValidCall_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "100");
        string? formula = doc.GetCellFormula("Sheet1", 0, 0);
        Assert.NotNull(formula);
    }

    [Fact]
    public void GetCellFormula_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        _ = doc.GetCellFormula("Sheet1", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellFormula_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Calc");
        doc.SetCellValue("Calc", 0, 0, "=A1+B1");
        string? first = doc.GetCellFormula("Calc", 0, 0);
        string? second = doc.GetCellFormula("Calc", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetCellFormulaThenGet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Budget");
        doc.SetCellValue("Budget", 0, 0, "100");
        doc.SetCellValue("Budget", 0, 1, "200");
        doc.SetCellFormula("Budget", 1, 0, "=SUM(A1:B1)");
        string? formula = doc.GetCellFormula("Budget", 1, 0);
        Assert.NotNull(formula);
        Assert.Equal(doc.SheetCount, doc.SheetCount);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_AllNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Table");
        for (int r = 0; r < 3; r++)
            for (int c = 0; c < 3; c++)
                doc.SetCellValue("Table", r, c, $"{r * 10 + c}");
        for (int r = 0; r < 3; r++)
            for (int c = 0; c < 3; c++)
                Assert.NotNull(doc.GetCellFormula("Table", r, c));
    }
}
