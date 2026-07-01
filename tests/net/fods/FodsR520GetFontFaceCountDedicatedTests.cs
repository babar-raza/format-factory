// Tests for FodsDocument.GetFontFaceCount dedicated coverage.
// Sprint: ff-sprint-s471-dotnet-deepening-20260701
// Ledger: PC-FODS-R520

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R520: Dedicated tests for FodsDocument.GetFontFaceCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetFontFaceCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR520GetFontFaceCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFontFaceCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetFontFaceCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetFontFaceCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetFontFaceCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetFontFaceCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetFontFaceCount();
        int second = doc.GetFontFaceCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetFontFaceCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetFontFaceCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetFontFaceCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetFontFaceCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetFontFaceCount() >= 0);
        }
    }
}
