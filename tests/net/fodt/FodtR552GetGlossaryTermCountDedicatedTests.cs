// Tests for FodtDocument.GetGlossaryTermCount dedicated coverage.
// Sprint: ff-sprint-s528-dotnet-deepening-20260701
// Ledger: PC-FODT-R552

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R552: Dedicated tests for FodtDocument.GetGlossaryTermCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetGlossaryTermCount.
/// TableCount unchanged after GetGlossaryTermCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR552GetGlossaryTermCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetGlossaryTermCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetGlossaryTermCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetGlossaryTermCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetGlossaryTermCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetGlossaryTermCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetGlossaryTermCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetGlossaryTermCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetGlossaryTermCount();
        int second = doc.GetGlossaryTermCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetGlossaryTermCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetGlossaryTermCount();
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
        Assert.True(doc.GetGlossaryTermCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetGlossaryTermCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetGlossaryTermCount() >= 0);
        }
    }
}
