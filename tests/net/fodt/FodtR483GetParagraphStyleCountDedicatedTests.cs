// Tests for FodtDocument.GetParagraphStyleCount dedicated coverage.
// Sprint: ff-sprint-s459-dotnet-deepening-20260701
// Ledger: PC-FODT-R483

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R483: Dedicated tests for FodtDocument.GetParagraphStyleCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetParagraphStyleCount.
/// TableCount unchanged after GetParagraphStyleCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR483GetParagraphStyleCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphStyleCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetParagraphStyleCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetParagraphStyleCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetParagraphStyleCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetParagraphStyleCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetParagraphStyleCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetParagraphStyleCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetParagraphStyleCount();
        int second = doc.GetParagraphStyleCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetParagraphStyleCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetParagraphStyleCount();
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
        Assert.True(doc.GetParagraphStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetParagraphStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetParagraphStyleCount() >= 0);
        }
    }
}
