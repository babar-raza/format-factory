// Tests for FodsDocument.GetSheetMaxColumn dedicated coverage.
// Sprint: ff-sprint-s428-dotnet-deepening-20260701
// Ledger: PC-FODS-R477

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R477: Dedicated tests for FodsDocument.GetSheetMaxColumn(string sheetName).
/// Null/whitespace/nonexistent sheet name throws.
/// Valid sheet returns non-negative int.
/// SheetCount unchanged after call.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default sheet and multiple sheets both return non-negative.
/// </summary>
public class FodsR477GetSheetMaxColumnDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard clause tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetMaxColumn_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetMaxColumn(null!));
    }

    [Fact]
    public void GetSheetMaxColumn_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetMaxColumn("   "));
    }

    [Fact]
    public void GetSheetMaxColumn_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetMaxColumn("NoSuchSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetMaxColumn_ValidSheet_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames()[0];
        int val = doc.GetSheetMaxColumn(sheet);
        Assert.True(val >= 0);
    }

    [Fact]
    public void GetSheetMaxColumn_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        string sheet = doc.GetSheetNames()[0];
        _ = doc.GetSheetMaxColumn(sheet);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetMaxColumn_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames()[0];
        int first = doc.GetSheetMaxColumn(sheet);
        int second = doc.GetSheetMaxColumn(sheet);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSheetMaxColumn_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames()[0];
        object result = doc.GetSheetMaxColumn(sheet);
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames()[0];
        Assert.True(doc.GetSheetMaxColumn(sheet) >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSheets_AllNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        foreach (string sheet in doc.GetSheetNames())
        {
            Assert.True(doc.GetSheetMaxColumn(sheet) >= 0);
        }
    }
}
