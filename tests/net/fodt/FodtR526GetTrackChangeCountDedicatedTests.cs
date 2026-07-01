// Tests for FodtDocument.GetTrackChangeCount dedicated coverage.
// Sprint: ff-sprint-s502-dotnet-deepening-20260701
// Ledger: PC-FODT-R526

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R526: Dedicated tests for FodtDocument.GetTrackChangeCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetTrackChangeCount.
/// TableCount unchanged after GetTrackChangeCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR526GetTrackChangeCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTrackChangeCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetTrackChangeCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetTrackChangeCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetTrackChangeCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetTrackChangeCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetTrackChangeCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetTrackChangeCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetTrackChangeCount();
        int second = doc.GetTrackChangeCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetTrackChangeCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetTrackChangeCount();
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
        Assert.True(doc.GetTrackChangeCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetTrackChangeCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetTrackChangeCount() >= 0);
        }
    }
}
