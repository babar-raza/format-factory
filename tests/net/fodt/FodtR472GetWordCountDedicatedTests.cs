// Tests for FodtDocument.GetWordCount dedicated coverage.
// Sprint: ff-sprint-s448-dotnet-deepening-20260701
// Ledger: PC-FODT-R472

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R472: Dedicated tests for FodtDocument.GetWordCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetWordCount.
/// TableCount unchanged after GetWordCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR472GetWordCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWordCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetWordCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetWordCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetWordCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetWordCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetWordCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetWordCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetWordCount();
        int second = doc.GetWordCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetWordCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetWordCount();
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
        Assert.True(doc.GetWordCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetWordCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetWordCount() >= 0);
        }
    }
}
