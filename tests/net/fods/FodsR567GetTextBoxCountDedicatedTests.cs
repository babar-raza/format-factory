// Tests for FodsDocument.GetTextBoxCount dedicated coverage.
// Sprint: ff-sprint-s518-dotnet-deepening-20260701
// Ledger: PC-FODS-R567

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R567: Dedicated tests for FodsDocument.GetTextBoxCount().
/// New document returns non-negative count.
/// SheetCount unchanged after GetTextBoxCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: default document non-negative.
/// Dogfood: after adding sheet non-negative.
/// Dogfood: multiple documents all non-negative.
/// </summary>
public class FodsR567GetTextBoxCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTextBoxCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        int count = doc.GetTextBoxCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetTextBoxCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetTextBoxCount();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetTextBoxCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        int first = doc.GetTextBoxCount();
        int second = doc.GetTextBoxCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetTextBoxCount_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        object result = doc.GetTextBoxCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultDocument_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        Assert.True(doc.GetTextBoxCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterAddingSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("TextBoxes");
        Assert.True(doc.GetTextBoxCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodsDocument.CreateNew();
            doc.AddSheet($"Sheet{i}");
            Assert.True(doc.GetTextBoxCount() >= 0);
        }
    }
}
