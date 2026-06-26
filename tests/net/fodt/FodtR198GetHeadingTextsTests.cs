// Tests for FodtDocument.GetHeadingTexts dedicated coverage.
// Sprint: ff-sprint-s189-dotnet-deepening-20260628
// Ledger: PC-FODT-R198

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R198: Dedicated tests for FodtDocument.GetHeadingTexts().
/// Returns an IReadOnlyList of strings containing the text of each heading paragraph.
/// Body paragraphs (text:p) are excluded; only headings (text:h) are included.
/// Empty document returns empty list.
/// Order follows document order.
/// All heading levels included.
/// No nulls in result (empty string for empty heading).
/// Covers: empty doc returns empty; body paragraphs excluded; single heading;
/// multiple headings in order; returns IReadOnlyList<string>; no nulls;
/// all levels included; count matches GetHeadingParagraphs count;
/// dogfood three headings text; dogfood mixed content headings extracted.
/// </summary>
public class FodtR198GetHeadingTextsTests
{
    // -------------------------------------------------------------------------
    // Basic tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeadingTexts_EmptyDocument_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Empty(doc.GetHeadingTexts());
    }

    [Fact]
    public void GetHeadingTexts_OnlyBodyParagraphs_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Body 1");
        doc.AppendParagraph("Body 2");
        Assert.Empty(doc.GetHeadingTexts());
    }

    [Fact]
    public void GetHeadingTexts_SingleHeading_ReturnsOneElement()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("My Title", 1);
        var result = doc.GetHeadingTexts();
        Assert.Single(result);
        Assert.Equal("My Title", result[0]);
    }

    [Fact]
    public void GetHeadingTexts_MultipleHeadings_InDocumentOrder()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("First", 1);
        doc.AppendHeading("Second", 2);
        doc.AppendHeading("Third", 3);
        var result = doc.GetHeadingTexts();
        Assert.Equal(3, result.Count);
        Assert.Equal("First", result[0]);
        Assert.Equal("Second", result[1]);
        Assert.Equal("Third", result[2]);
    }

    [Fact]
    public void GetHeadingTexts_ReturnsIReadOnlyList()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1);
        Assert.IsAssignableFrom<System.Collections.Generic.IReadOnlyList<string>>(doc.GetHeadingTexts());
    }

    [Fact]
    public void GetHeadingTexts_NoNullsInResult()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("H1", 1);
        doc.AppendHeading("H2", 2);
        foreach (var t in doc.GetHeadingTexts())
            Assert.NotNull(t);
    }

    [Fact]
    public void GetHeadingTexts_CountMatchesGetHeadingParagraphsCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("A", 1);
        doc.AppendParagraph("Body");
        doc.AppendHeading("B", 2);
        Assert.Equal(doc.GetHeadingParagraphs().Count, doc.GetHeadingTexts().Count);
    }

    [Fact]
    public void GetHeadingTexts_AllHeadingLevelsIncluded()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("L1", 1);
        doc.AppendHeading("L2", 2);
        doc.AppendHeading("L3", 3);
        var result = doc.GetHeadingTexts();
        Assert.Contains("L1", result);
        Assert.Contains("L2", result);
        Assert.Contains("L3", result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ThreeHeadings_AllTextsPresent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Introduction", 1);
        doc.AppendHeading("Main Section", 1);
        doc.AppendHeading("Conclusion", 1);
        var result = doc.GetHeadingTexts();
        Assert.Equal(3, result.Count);
        Assert.Contains("Introduction", result);
        Assert.Contains("Main Section", result);
        Assert.Contains("Conclusion", result);
    }

    [Fact]
    public void DogfoodPipeline_MixedContent_OnlyHeadingTextsExtracted()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Intro para");
        doc.AppendHeading("Chapter One", 1);
        doc.AppendParagraph("Body text");
        doc.AppendHeading("Chapter Two", 1);
        doc.AppendParagraph("More body");
        var result = doc.GetHeadingTexts();
        Assert.Equal(2, result.Count);
        Assert.DoesNotContain("Intro para", result);
        Assert.DoesNotContain("Body text", result);
        Assert.Contains("Chapter One", result);
        Assert.Contains("Chapter Two", result);
    }
}
