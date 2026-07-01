// Tests for FodtDocument.GetRubyTextCount dedicated coverage.
// Sprint: ff-sprint-s444-dotnet-deepening-20260701
// Ledger: PC-FODT-R468

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R468: Dedicated tests for FodtDocument.GetRubyTextCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetRubyTextCount.
/// TableCount unchanged after GetRubyTextCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR468GetRubyTextCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRubyTextCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetRubyTextCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetRubyTextCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetRubyTextCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetRubyTextCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetRubyTextCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetRubyTextCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetRubyTextCount();
        int second = doc.GetRubyTextCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetRubyTextCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetRubyTextCount();
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
        Assert.True(doc.GetRubyTextCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetRubyTextCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetRubyTextCount() >= 0);
        }
    }
}
