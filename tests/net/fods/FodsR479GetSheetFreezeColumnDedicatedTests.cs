// Tests for FodsDocument.GetSheetFreezeColumn dedicated coverage.
// Sprint: ff-sprint-s430-dotnet-deepening-20260701
// Ledger: PC-FODS-R479

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R479: Dedicated tests for FodsDocument.GetSheetFreezeColumn(string sheetName).
/// Null/whitespace/nonexistent sheet name throws.
/// Valid sheet returns non-negative int.
/// SheetCount unchanged after call.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default sheet and multiple sheets both return non-negative.
/// </summary>
public class FodsR479GetSheetFreezeColumnDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard clause tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetFreezeColumn_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetSheetFreezeColumn(null!));
    }

    [Fact]
    public void GetSheetFreezeColumn_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetSheetFreezeColumn("   "));
    }

    [Fact]
    public void GetSheetFreezeColumn_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetSheetFreezeColumn("NoSuchSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetFreezeColumn_ValidSheet_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames()[0];
        int val = doc.GetSheetFreezeColumn(sheet);
        Assert.True(val >= 0);
    }

    [Fact]
    public void GetSheetFreezeColumn_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        string sheet = doc.GetSheetNames()[0];
        _ = doc.GetSheetFreezeColumn(sheet);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetFreezeColumn_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames()[0];
        int first = doc.GetSheetFreezeColumn(sheet);
        int second = doc.GetSheetFreezeColumn(sheet);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSheetFreezeColumn_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames()[0];
        object result = doc.GetSheetFreezeColumn(sheet);
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames()[0];
        Assert.True(doc.GetSheetFreezeColumn(sheet) >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSheets_AllNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Extra");
        foreach (string sheet in doc.GetSheetNames())
        {
            Assert.True(doc.GetSheetFreezeColumn(sheet) >= 0);
        }
    }
}
