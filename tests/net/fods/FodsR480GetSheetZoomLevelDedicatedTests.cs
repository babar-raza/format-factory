// Tests for FodsDocument.GetSheetZoomLevel dedicated coverage.
// Sprint: ff-sprint-s431-dotnet-deepening-20260701
// Ledger: PC-FODS-R480

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R480: Dedicated tests for FodsDocument.GetSheetZoomLevel(string sheetName).
/// Null/whitespace/nonexistent sheet name throws.
/// Valid sheet returns non-negative int.
/// SheetCount unchanged after call.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default sheet and multiple sheets both return non-negative.
/// </summary>
public class FodsR480GetSheetZoomLevelDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard clause tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetZoomLevel_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetZoomLevel(null!));
    }

    [Fact]
    public void GetSheetZoomLevel_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetZoomLevel("   "));
    }

    [Fact]
    public void GetSheetZoomLevel_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetZoomLevel("NoSuchSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetZoomLevel_ValidSheet_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames()[0];
        int val = doc.GetSheetZoomLevel(sheet);
        Assert.True(val >= 0);
    }

    [Fact]
    public void GetSheetZoomLevel_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        string sheet = doc.GetSheetNames()[0];
        _ = doc.GetSheetZoomLevel(sheet);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetZoomLevel_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames()[0];
        int first = doc.GetSheetZoomLevel(sheet);
        int second = doc.GetSheetZoomLevel(sheet);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSheetZoomLevel_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames()[0];
        object result = doc.GetSheetZoomLevel(sheet);
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
        Assert.True(doc.GetSheetZoomLevel(sheet) >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSheets_AllNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        foreach (string sheet in doc.GetSheetNames())
        {
            Assert.True(doc.GetSheetZoomLevel(sheet) >= 0);
        }
    }
}
