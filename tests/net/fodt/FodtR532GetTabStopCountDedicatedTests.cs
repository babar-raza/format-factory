// Tests for FodtDocument.GetTabStopCount dedicated coverage.
// Sprint: ff-sprint-s508-dotnet-deepening-20260701
// Ledger: PC-FODT-R532

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R532: Dedicated tests for FodtDocument.GetTabStopCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetTabStopCount.
/// TableCount unchanged after GetTabStopCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR532GetTabStopCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTabStopCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetTabStopCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetTabStopCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetTabStopCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetTabStopCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetTabStopCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetTabStopCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetTabStopCount();
        int second = doc.GetTabStopCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetTabStopCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetTabStopCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterParagraphs_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("First paragraph");
        doc.AddParagraph("Second paragraph");
        Assert.True(doc.GetTabStopCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetTabStopCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetTabStopCount() >= 0);
        }
    }
}
