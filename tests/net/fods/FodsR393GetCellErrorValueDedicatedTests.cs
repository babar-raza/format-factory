// Tests for FodsDocument.GetCellErrorValue dedicated coverage.
// Sprint: ff-sprint-s354-dotnet-deepening-20260630
// Ledger: PC-FODS-R393

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R393: Dedicated tests for FodsDocument.GetCellErrorValue().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-null.
/// SheetCount unchanged after GetCellErrorValue.
/// Idempotent (called twice same result).
/// Dogfood: cell with no error returns non-null (empty or none).
/// Dogfood: SetCellError then Get returns expected error string.
/// </summary>
public class FodsR393GetCellErrorValueDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellErrorValue_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellErrorValue(null!, 0, 0));
    }

    [Fact]
    public void GetCellErrorValue_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellErrorValue("   ", 0, 0));
    }

    [Fact]
    public void GetCellErrorValue_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellErrorValue("Phantom", 0, 0));
    }

    [Fact]
    public void GetCellErrorValue_NegativeRowIndex_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Errors");
        Assert.ThrowsAny<Exception>(() => doc.GetCellErrorValue("Errors", -1, 0));
    }

    [Fact]
    public void GetCellErrorValue_ValidCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        string? error = doc.GetCellErrorValue("Data", 0, 0);
        Assert.NotNull(error);
    }

    [Fact]
    public void GetCellErrorValue_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Check");
        int before = doc.SheetCount;
        _ = doc.GetCellErrorValue("Check", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellErrorValue_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        string? first = doc.GetCellErrorValue("Stable", 0, 0);
        string? second = doc.GetCellErrorValue("Stable", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CellWithNoError_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Clean");
        doc.SetCellValue("Clean", 0, 0, "Normal value");
        string? error = doc.GetCellErrorValue("Clean", 0, 0);
        Assert.NotNull(error);
    }

    [Fact]
    public void DogfoodPipeline_SetCellError_ReturnsExpected()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Formulas");
        doc.SetCellError("Formulas", 0, 0, "#DIV/0!");
        string? error = doc.GetCellErrorValue("Formulas", 0, 0);
        Assert.NotNull(error);
        Assert.Equal("#DIV/0!", error);
    }
}
