// Tests for FodtDocument.GetStyleNameCount dedicated coverage.
// Sprint: ff-sprint-s405-dotnet-deepening-20260701
// Ledger: PC-FODT-R429

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R429: Dedicated tests for FodtDocument.GetStyleNameCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetStyleNameCount.
/// TableCount unchanged after GetStyleNameCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR429GetStyleNameCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetStyleNameCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetStyleNameCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetStyleNameCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetStyleNameCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetStyleNameCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetStyleNameCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetStyleNameCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetStyleNameCount();
        int second = doc.GetStyleNameCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetStyleNameCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetStyleNameCount();
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
        Assert.True(doc.GetStyleNameCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetStyleNameCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetStyleNameCount() >= 0);
        }
    }
}
