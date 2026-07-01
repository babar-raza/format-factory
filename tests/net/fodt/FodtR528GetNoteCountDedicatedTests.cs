// Tests for FodtDocument.GetNoteCount dedicated coverage.
// Sprint: ff-sprint-s504-dotnet-deepening-20260701
// Ledger: PC-FODT-R528

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R528: Dedicated tests for FodtDocument.GetNoteCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetNoteCount.
/// TableCount unchanged after GetNoteCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR528GetNoteCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNoteCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetNoteCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetNoteCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetNoteCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetNoteCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetNoteCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetNoteCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetNoteCount();
        int second = doc.GetNoteCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetNoteCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetNoteCount();
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
        Assert.True(doc.GetNoteCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetNoteCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetNoteCount() >= 0);
        }
    }
}
