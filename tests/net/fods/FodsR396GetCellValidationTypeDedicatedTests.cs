// Tests for FodsDocument.GetCellValidationType dedicated coverage.
// Sprint: ff-sprint-s356-dotnet-deepening-20260630
// Ledger: PC-FODS-R396

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R396: Dedicated tests for FodsDocument.GetCellValidationType().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-null.
/// SheetCount unchanged after GetCellValidationType.
/// Idempotent (called twice same result).
/// Dogfood: SetCellValidation then GetCellValidationType returns non-null.
/// Dogfood: plain cell without validation returns non-null.
/// </summary>
public class FodsR396GetCellValidationTypeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellValidationType_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellValidationType(null!, 0, 0));
    }

    [Fact]
    public void GetCellValidationType_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellValidationType("   ", 0, 0));
    }

    [Fact]
    public void GetCellValidationType_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellValidationType("Ghost", 0, 0));
    }

    [Fact]
    public void GetCellValidationType_NegativeRowIndex_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Validate");
        Assert.ThrowsAny<Exception>(() => doc.GetCellValidationType("Validate", -1, 0));
    }

    [Fact]
    public void GetCellValidationType_ValidCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        string? type = doc.GetCellValidationType("Data", 0, 0);
        Assert.NotNull(type);
    }

    [Fact]
    public void GetCellValidationType_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Check");
        int before = doc.SheetCount;
        _ = doc.GetCellValidationType("Check", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellValidationType_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        string? first = doc.GetCellValidationType("Stable", 0, 0);
        string? second = doc.GetCellValidationType("Stable", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterSetValidation_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Input");
        doc.SetCellValidation("Input", 0, 0, "list", "A;B;C");
        string? type = doc.GetCellValidationType("Input", 0, 0);
        Assert.NotNull(type);
    }

    [Fact]
    public void DogfoodPipeline_PlainCellWithNoValidation_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Plain");
        doc.SetCellValue("Plain", 0, 0, "Just a value");
        string? type = doc.GetCellValidationType("Plain", 0, 0);
        Assert.NotNull(type);
    }
}
