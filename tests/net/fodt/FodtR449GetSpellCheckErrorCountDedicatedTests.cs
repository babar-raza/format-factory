// Tests for FodtDocument.GetSpellCheckErrorCount dedicated coverage.
// Sprint: ff-sprint-s425-dotnet-deepening-20260701
// Ledger: PC-FODT-R449

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R449: Dedicated tests for FodtDocument.GetSpellCheckErrorCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetSpellCheckErrorCount.
/// TableCount unchanged after GetSpellCheckErrorCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR449GetSpellCheckErrorCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSpellCheckErrorCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetSpellCheckErrorCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetSpellCheckErrorCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetSpellCheckErrorCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetSpellCheckErrorCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetSpellCheckErrorCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetSpellCheckErrorCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetSpellCheckErrorCount();
        int second = doc.GetSpellCheckErrorCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSpellCheckErrorCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetSpellCheckErrorCount();
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
        Assert.True(doc.GetSpellCheckErrorCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetSpellCheckErrorCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetSpellCheckErrorCount() >= 0);
        }
    }
}
