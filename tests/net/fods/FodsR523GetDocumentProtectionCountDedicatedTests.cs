// Tests for FodsDocument.GetDocumentProtectionCount dedicated coverage.
// Sprint: ff-sprint-s474-dotnet-deepening-20260701
// Ledger: PC-FODS-R523

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R523: Dedicated tests for FodsDocument.GetDocumentProtectionCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetDocumentProtectionCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR523GetDocumentProtectionCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentProtectionCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetDocumentProtectionCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetDocumentProtectionCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetDocumentProtectionCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetDocumentProtectionCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetDocumentProtectionCount();
        int second = doc.GetDocumentProtectionCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetDocumentProtectionCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetDocumentProtectionCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetDocumentProtectionCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.True(doc.GetDocumentProtectionCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            Assert.True(doc.GetDocumentProtectionCount() >= 0);
        }
    }
}
