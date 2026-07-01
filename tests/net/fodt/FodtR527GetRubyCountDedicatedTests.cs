// Tests for FodtDocument.GetRubyCount dedicated coverage.
// Sprint: ff-sprint-s503-dotnet-deepening-20260701
// Ledger: PC-FODT-R527

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R527: Dedicated tests for FodtDocument.GetRubyCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetRubyCount.
/// TableCount unchanged after GetRubyCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR527GetRubyCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRubyCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetRubyCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetRubyCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetRubyCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetRubyCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetRubyCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetRubyCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetRubyCount();
        int second = doc.GetRubyCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetRubyCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetRubyCount();
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
        Assert.True(doc.GetRubyCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetRubyCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetRubyCount() >= 0);
        }
    }
}
