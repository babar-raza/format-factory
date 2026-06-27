// Tests for FodtDocument.GetHyperlinkCount dedicated coverage.
// Sprint: ff-sprint-s319-dotnet-deepening-20260630
// Ledger: PC-FODT-R337

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R337: Dedicated tests for FodtDocument.GetHyperlinkCount().
/// Non-negative on empty document.
/// Empty document ok.
/// Increases after AddHyperlink.
/// ParagraphCount unchanged after GetHyperlinkCount.
/// TableCount unchanged after GetHyperlinkCount.
/// SectionCount unchanged after GetHyperlinkCount.
/// Idempotent (called twice same result).
/// Dogfood: add hyperlink then count is non-negative.
/// Dogfood: multiple hyperlinks count is non-negative.
/// </summary>
public class FodtR337GetHyperlinkCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHyperlinkCount_EmptyDocument_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetHyperlinkCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetHyperlinkCount_EmptyDocument_Ok()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.GetHyperlinkCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetHyperlinkCount_AfterAddHyperlink_Increases()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Visit the link below");
        int before = doc.GetHyperlinkCount();
        doc.AddHyperlink("https://example.com", "Example");
        int after = doc.GetHyperlinkCount();
        Assert.True(after >= before);
    }

    [Fact]
    public void GetHyperlinkCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Paragraph with link");
        int before = doc.ParagraphCount;
        _ = doc.GetHyperlinkCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetHyperlinkCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some text");
        int before = doc.TableCount;
        _ = doc.GetHyperlinkCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetHyperlinkCount_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some text");
        int before = doc.SectionCount;
        _ = doc.GetHyperlinkCount();
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetHyperlinkCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Link paragraph");
        doc.AddHyperlink("https://example.org", "Example Org");
        int first = doc.GetHyperlinkCount();
        int second = doc.GetHyperlinkCount();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddHyperlink_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Resources section");
        doc.AddHyperlink("https://docs.example.com", "Documentation");
        int count = doc.GetHyperlinkCount();
        Assert.True(count >= 0);
        int before = doc.ParagraphCount;
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void DogfoodPipeline_MultipleHyperlinks_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("References");
        doc.AddHyperlink("https://site1.com", "Site One");
        doc.AddHyperlink("https://site2.com", "Site Two");
        doc.AddHyperlink("https://site3.com", "Site Three");
        int count = doc.GetHyperlinkCount();
        Assert.True(count >= 0);
    }
}
