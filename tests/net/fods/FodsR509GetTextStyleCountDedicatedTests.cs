// Tests for FodsDocument.GetTextStyleCount dedicated coverage.
// Sprint: ff-sprint-s460-dotnet-deepening-20260701
// Ledger: PC-FODS-R509

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R509: Dedicated tests for FodsDocument.GetTextStyleCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetTextStyleCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR509GetTextStyleCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTextStyleCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetTextStyleCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetTextStyleCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetTextStyleCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetTextStyleCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetTextStyleCount();
        int second = doc.GetTextStyleCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetTextStyleCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetTextStyleCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetTextStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetTextStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetTextStyleCount() >= 0);
        }
    }
}
