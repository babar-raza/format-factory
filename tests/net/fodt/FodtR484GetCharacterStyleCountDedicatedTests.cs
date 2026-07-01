// Tests for FodtDocument.GetCharacterStyleCount dedicated coverage.
// Sprint: ff-sprint-s460-dotnet-deepening-20260701
// Ledger: PC-FODT-R484

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R484: Dedicated tests for FodtDocument.GetCharacterStyleCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetCharacterStyleCount.
/// TableCount unchanged after GetCharacterStyleCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR484GetCharacterStyleCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCharacterStyleCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetCharacterStyleCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetCharacterStyleCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetCharacterStyleCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetCharacterStyleCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetCharacterStyleCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetCharacterStyleCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetCharacterStyleCount();
        int second = doc.GetCharacterStyleCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCharacterStyleCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetCharacterStyleCount();
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
        Assert.True(doc.GetCharacterStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetCharacterStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetCharacterStyleCount() >= 0);
        }
    }
}
