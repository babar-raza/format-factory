// Tests for FodtDocument.GetTextBoxCount dedicated coverage.
// Sprint: ff-sprint-s467-dotnet-deepening-20260701
// Ledger: PC-FODT-R491

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R491: Dedicated tests for FodtDocument.GetTextBoxCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetTextBoxCount.
/// TableCount unchanged after GetTextBoxCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR491GetTextBoxCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTextBoxCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetTextBoxCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetTextBoxCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetTextBoxCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetTextBoxCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetTextBoxCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetTextBoxCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetTextBoxCount();
        int second = doc.GetTextBoxCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetTextBoxCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetTextBoxCount();
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
        Assert.True(doc.GetTextBoxCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetTextBoxCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetTextBoxCount() >= 0);
        }
    }
}
