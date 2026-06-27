// Tests for FodsDocument.GetCellFormulaType dedicated coverage.
// Sprint: ff-sprint-s355-dotnet-deepening-20260630
// Ledger: PC-FODS-R394

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R394: Dedicated tests for FodsDocument.GetCellFormulaType().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-null.
/// SheetCount unchanged after GetCellFormulaType.
/// Idempotent (called twice same result).
/// Dogfood: SetCellFormula then GetCellFormulaType returns non-null.
/// Dogfood: plain value cell returns non-null type.
/// </summary>
public class FodsR394GetCellFormulaTypeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellFormulaType_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFormulaType(null!, 0, 0));
    }

    [Fact]
    public void GetCellFormulaType_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFormulaType("   ", 0, 0));
    }

    [Fact]
    public void GetCellFormulaType_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFormulaType("Missing", 0, 0));
    }

    [Fact]
    public void GetCellFormulaType_NegativeRowIndex_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Formulas");
        Assert.ThrowsAny<Exception>(() => doc.GetCellFormulaType("Formulas", -1, 0));
    }

    [Fact]
    public void GetCellFormulaType_ValidCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        string? type = doc.GetCellFormulaType("Data", 0, 0);
        Assert.NotNull(type);
    }

    [Fact]
    public void GetCellFormulaType_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Check");
        int before = doc.SheetCount;
        _ = doc.GetCellFormulaType("Check", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellFormulaType_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        string? first = doc.GetCellFormulaType("Stable", 0, 0);
        string? second = doc.GetCellFormulaType("Stable", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterSetFormula_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Calc");
        doc.SetCellFormula("Calc", 0, 0, "=SUM(A2:A10)");
        string? type = doc.GetCellFormulaType("Calc", 0, 0);
        Assert.NotNull(type);
    }

    [Fact]
    public void DogfoodPipeline_PlainValueCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Values");
        doc.SetCellValue("Values", 0, 0, "Static Value");
        string? type = doc.GetCellFormulaType("Values", 0, 0);
        Assert.NotNull(type);
    }
}
