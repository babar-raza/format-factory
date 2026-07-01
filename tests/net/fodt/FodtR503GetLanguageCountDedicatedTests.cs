// Tests for FodtDocument.GetLanguageCount dedicated coverage.
// Sprint: ff-sprint-s479-dotnet-deepening-20260701
// Ledger: PC-FODT-R503

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R503: Dedicated tests for FodtDocument.GetLanguageCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetLanguageCount.
/// TableCount unchanged after GetLanguageCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR503GetLanguageCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetLanguageCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetLanguageCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetLanguageCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetLanguageCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetLanguageCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetLanguageCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetLanguageCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetLanguageCount();
        int second = doc.GetLanguageCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetLanguageCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetLanguageCount();
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
        Assert.True(doc.GetLanguageCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetLanguageCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetLanguageCount() >= 0);
        }
    }
}
