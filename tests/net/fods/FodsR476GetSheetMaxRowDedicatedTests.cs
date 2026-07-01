// Tests for FodsDocument.GetSheetMaxRow dedicated coverage.
// Sprint: ff-sprint-s427-dotnet-deepening-20260701
// Ledger: PC-FODS-R476

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R476: Dedicated tests for FodsDocument.GetSheetMaxRow().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Valid sheet returns non-negative value.
/// SheetCount unchanged after GetSheetMaxRow.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default sheet max row non-negative.
/// Dogfood: multiple sheets have non-negative max row.
/// </summary>
public class FodsR476GetSheetMaxRowDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard clause tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetMaxRow_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetMaxRow(null!));
    }

    [Fact]
    public void GetSheetMaxRow_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetMaxRow("   "));
    }

    [Fact]
    public void GetSheetMaxRow_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetMaxRow("NoSuchSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetMaxRow_ValidSheet_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int maxRow = doc.GetSheetMaxRow("Sheet1");
        Assert.True(maxRow >= 0);
    }

    [Fact]
    public void GetSheetMaxRow_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        _ = doc.GetSheetMaxRow("Sheet1");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetMaxRow_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int first = doc.GetSheetMaxRow("Sheet1");
        int second = doc.GetSheetMaxRow("Sheet1");
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSheetMaxRow_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        object result = doc.GetSheetMaxRow("Sheet1");
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultSheet_MaxRowNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        int maxRow = doc.GetSheetMaxRow("Report");
        Assert.True(maxRow >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSheets_AllNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        var names = new[] { "Sheet1", "Sheet2", "Sheet3" };
        foreach (var name in names)
        {
            doc.AddSheet(name);
            Assert.True(doc.GetSheetMaxRow(name) >= 0);
        }
    }
}
