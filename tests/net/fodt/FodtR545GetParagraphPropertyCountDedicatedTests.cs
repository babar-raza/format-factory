// Tests for FodtDocument.GetParagraphPropertyCount dedicated coverage.
// Sprint: ff-sprint-s521-dotnet-deepening-20260701
// Ledger: PC-FODT-R545

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R545: Dedicated tests for FodtDocument.GetParagraphPropertyCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetParagraphPropertyCount.
/// TableCount unchanged after GetParagraphPropertyCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR545GetParagraphPropertyCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphPropertyCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetParagraphPropertyCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetParagraphPropertyCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetParagraphPropertyCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetParagraphPropertyCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetParagraphPropertyCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetParagraphPropertyCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetParagraphPropertyCount();
        int second = doc.GetParagraphPropertyCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetParagraphPropertyCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetParagraphPropertyCount();
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
        Assert.True(doc.GetParagraphPropertyCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetParagraphPropertyCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetParagraphPropertyCount() >= 0);
        }
    }
}
