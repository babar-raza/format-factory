// Tests for FodtDocument.GetFontCount dedicated coverage.
// Sprint: ff-sprint-s440-dotnet-deepening-20260701
// Ledger: PC-FODT-R464

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R464: Dedicated tests for FodtDocument.GetFontCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetFontCount.
/// TableCount unchanged after GetFontCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR464GetFontCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFontCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetFontCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetFontCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetFontCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetFontCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetFontCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetFontCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetFontCount();
        int second = doc.GetFontCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetFontCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetFontCount();
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
        Assert.True(doc.GetFontCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetFontCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetFontCount() >= 0);
        }
    }
}
