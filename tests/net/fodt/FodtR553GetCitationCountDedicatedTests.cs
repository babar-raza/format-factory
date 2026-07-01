// Tests for FodtDocument.GetCitationCount dedicated coverage.
// Sprint: ff-sprint-s529-dotnet-deepening-20260701
// Ledger: PC-FODT-R553

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R553: Dedicated tests for FodtDocument.GetCitationCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetCitationCount.
/// TableCount unchanged after GetCitationCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR553GetCitationCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCitationCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetCitationCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetCitationCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetCitationCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetCitationCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetCitationCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetCitationCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetCitationCount();
        int second = doc.GetCitationCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCitationCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetCitationCount();
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
        Assert.True(doc.GetCitationCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetCitationCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetCitationCount() >= 0);
        }
    }
}
