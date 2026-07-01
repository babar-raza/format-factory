// Tests for FodtDocument.GetLineCount dedicated coverage.
// Sprint: ff-sprint-s447-dotnet-deepening-20260701
// Ledger: PC-FODT-R471

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R471: Dedicated tests for FodtDocument.GetLineCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetLineCount.
/// TableCount unchanged after GetLineCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR471GetLineCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetLineCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetLineCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetLineCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetLineCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetLineCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetLineCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetLineCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetLineCount();
        int second = doc.GetLineCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetLineCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetLineCount();
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
        Assert.True(doc.GetLineCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetLineCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetLineCount() >= 0);
        }
    }
}
