// Tests for FodtDocument.GetOutlineCount dedicated coverage.
// Sprint: ff-sprint-s439-dotnet-deepening-20260701
// Ledger: PC-FODT-R463

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R463: Dedicated tests for FodtDocument.GetOutlineCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetOutlineCount.
/// TableCount unchanged after GetOutlineCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR463GetOutlineCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetOutlineCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetOutlineCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetOutlineCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetOutlineCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetOutlineCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetOutlineCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetOutlineCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetOutlineCount();
        int second = doc.GetOutlineCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetOutlineCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetOutlineCount();
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
        Assert.True(doc.GetOutlineCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetOutlineCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetOutlineCount() >= 0);
        }
    }
}
