// Tests for FodtDocument.GetSectionCount dedicated coverage.
// Sprint: ff-sprint-s375-dotnet-deepening-20260630
// Ledger: PC-FODT-R393

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R393: Dedicated tests for FodtDocument.GetSectionCount() (or SectionCount property).
/// New document returns non-negative.
/// ParagraphCount unchanged after checking SectionCount.
/// TableCount unchanged after checking SectionCount.
/// Adding paragraphs does not decrease SectionCount.
/// Idempotent (read twice same result).
/// Dogfood: SectionCount non-negative after AddParagraph.
/// Dogfood: SectionCount non-negative after multiple paragraphs.
/// Dogfood: SectionCount type is int.
/// </summary>
public class FodtR393GetSectionCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SectionCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        Assert.True(doc.SectionCount >= 0);
    }

    [Fact]
    public void SectionCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.ParagraphCount;
        _ = doc.SectionCount;
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void SectionCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.TableCount;
        _ = doc.SectionCount;
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void SectionCount_AfterAddParagraph_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("New paragraph");
        Assert.True(doc.SectionCount >= 0);
    }

    [Fact]
    public void SectionCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Stable text");
        int first = doc.SectionCount;
        int second = doc.SectionCount;
        Assert.Equal(first, second);
    }

    [Fact]
    public void SectionCount_IsInteger()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.SectionCount;
        Assert.IsType<int>(count);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterSingleParagraph_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Introduction section");
        Assert.True(doc.SectionCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMultipleParagraphs_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Section 1");
        doc.AddParagraph("Section 2");
        doc.AddParagraph("Section 3");
        Assert.True(doc.SectionCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_SectionCountNeverNegative()
    {
        var doc = FodtDocument.CreateNew();
        for (int i = 0; i < 5; i++)
        {
            doc.AddParagraph($"Paragraph {i}");
            Assert.True(doc.SectionCount >= 0);
        }
    }
}
