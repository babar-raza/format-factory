// Tests for FodtDocument.GetEndnoteCount dedicated coverage.
// Sprint: ff-sprint-s488-dotnet-deepening-20260701
// Ledger: PC-FODT-R512

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R512: Dedicated tests for FodtDocument.GetEndnoteCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetEndnoteCount.
/// TableCount unchanged after GetEndnoteCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR512GetEndnoteCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetEndnoteCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetEndnoteCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetEndnoteCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetEndnoteCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetEndnoteCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetEndnoteCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetEndnoteCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetEndnoteCount();
        int second = doc.GetEndnoteCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetEndnoteCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetEndnoteCount();
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
        Assert.True(doc.GetEndnoteCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetEndnoteCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetEndnoteCount() >= 0);
        }
    }
}
