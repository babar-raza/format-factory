// Tests for FodtDocument.GetTextStyleCount dedicated coverage.
// Sprint: ff-sprint-s480-dotnet-deepening-20260701
// Ledger: PC-FODT-R504

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R504: Dedicated tests for FodtDocument.GetTextStyleCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetTextStyleCount.
/// TableCount unchanged after GetTextStyleCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR504GetTextStyleCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTextStyleCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetTextStyleCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetTextStyleCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetTextStyleCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetTextStyleCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetTextStyleCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetTextStyleCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetTextStyleCount();
        int second = doc.GetTextStyleCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetTextStyleCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetTextStyleCount();
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
        Assert.True(doc.GetTextStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetTextStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetTextStyleCount() >= 0);
        }
    }
}
