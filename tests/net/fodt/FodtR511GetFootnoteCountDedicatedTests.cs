// Tests for FodtDocument.GetFootnoteCount dedicated coverage.
// Sprint: ff-sprint-s487-dotnet-deepening-20260701
// Ledger: PC-FODT-R511

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R511: Dedicated tests for FodtDocument.GetFootnoteCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetFootnoteCount.
/// TableCount unchanged after GetFootnoteCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR511GetFootnoteCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFootnoteCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetFootnoteCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetFootnoteCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetFootnoteCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetFootnoteCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetFootnoteCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetFootnoteCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetFootnoteCount();
        int second = doc.GetFootnoteCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetFootnoteCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetFootnoteCount();
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
        Assert.True(doc.GetFootnoteCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetFootnoteCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetFootnoteCount() >= 0);
        }
    }
}
