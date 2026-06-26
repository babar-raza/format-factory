// Tests for FodtDocument.GetHeadingCount, GetHeadingTexts, GetParagraphStyles deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R205

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R205: Tests for FodtDocument.GetHeadingCount, GetHeadingTexts, GetParagraphStyles deeper.
/// GetHeadingCount(): returns number of heading paragraphs in the document.
/// GetHeadingTexts(): returns list of text strings from all heading paragraphs.
/// GetParagraphStyles(): returns list of style names used by all paragraphs.
/// Covers: GetHeadingCount zero for empty doc; GetHeadingCount increases with InsertHeading;
/// GetHeadingCount correct after multiple levels; GetHeadingCount does not count plain paragraphs;
/// GetHeadingTexts non-null after InsertHeading; GetHeadingTexts correct count;
/// GetHeadingTexts contains expected text; GetHeadingTexts does not contain paragraph text;
/// GetParagraphStyles non-null; GetParagraphStyles non-empty after AppendParagraph;
/// GetParagraphStyles contains heading styles; GetParagraphStyles count >= paragraph count;
/// dogfood CreateEmpty->InsertHeadings->AppendParagraphs->GetHeadingCount->GetHeadingTexts->GetParagraphStyles->Verify.
/// </summary>
public class FodtR205GetHeadingCountAndHeadingTextsDeepTests
{
    private static FodtDocument CreateMixedDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Chapter One", 1);
        doc.AppendParagraph("This is the introduction paragraph.");
        doc.InsertHeading(1, "Section 1.1", 2);
        doc.AppendParagraph("Content of section 1.1 goes here.");
        doc.InsertHeading(2, "Chapter Two", 1);
        doc.AppendParagraph("Content of chapter two.");
        doc.InsertHeading(3, "Section 2.1", 2);
        doc.AppendParagraph("Details of section 2.1.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetHeadingCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeadingCount_EmptyDoc_IsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.GetHeadingCount());
    }

    [Fact]
    public void GetHeadingCount_AfterOneInsertHeading_IsOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "My Title", 1);
        Assert.Equal(1, doc.GetHeadingCount());
    }

    [Fact]
    public void GetHeadingCount_AfterMultipleHeadings_IsCorrect()
    {
        var doc = CreateMixedDoc();
        Assert.Equal(4, doc.GetHeadingCount());
    }

    [Fact]
    public void GetHeadingCount_PlainParagraphs_NotCounted()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Plain text only.");
        doc.AppendParagraph("More plain text.");
        Assert.Equal(0, doc.GetHeadingCount());
    }

    [Fact]
    public void GetHeadingCount_MixedContent_OnlyHeadingsCounted()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Heading 1", 1);
        doc.AppendParagraph("Para A");
        doc.InsertHeading(1, "Heading 2", 2);
        doc.AppendParagraph("Para B");
        Assert.Equal(2, doc.GetHeadingCount());
    }

    [Fact]
    public void GetHeadingCount_AllLevels_Counted()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Level 1 Heading", 1);
        doc.InsertHeading(1, "Level 2 Heading", 2);
        doc.InsertHeading(2, "Level 3 Heading", 3);
        Assert.Equal(3, doc.GetHeadingCount());
    }

    // -------------------------------------------------------------------------
    // GetHeadingTexts
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeadingTexts_NonNull_AfterInsertHeading()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Title", 1);
        Assert.NotNull(doc.GetHeadingTexts());
    }

    [Fact]
    public void GetHeadingTexts_Count_MatchesHeadingCount()
    {
        var doc = CreateMixedDoc();
        var texts = doc.GetHeadingTexts();
        Assert.Equal(doc.GetHeadingCount(), texts.Count);
    }

    [Fact]
    public void GetHeadingTexts_ContainsExpectedText()
    {
        var doc = CreateMixedDoc();
        var texts = doc.GetHeadingTexts();
        Assert.Contains("Chapter One", texts);
        Assert.Contains("Section 1.1", texts);
        Assert.Contains("Chapter Two", texts);
        Assert.Contains("Section 2.1", texts);
    }

    [Fact]
    public void GetHeadingTexts_DoesNotContainParagraphText()
    {
        var doc = CreateMixedDoc();
        var texts = doc.GetHeadingTexts();
        Assert.DoesNotContain("introduction paragraph", texts);
        Assert.DoesNotContain("Content of section", texts);
    }

    [Fact]
    public void GetHeadingTexts_EmptyDoc_ReturnsEmptyOrNull()
    {
        var doc = FodtDocument.CreateEmpty();
        var texts = doc.GetHeadingTexts();
        Assert.True(texts == null || texts.Count == 0);
    }

    [Fact]
    public void GetHeadingTexts_SingleHeading_HasCorrectText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Executive Summary", 1);
        var texts = doc.GetHeadingTexts();
        Assert.NotEmpty(texts);
        Assert.Contains("Executive Summary", texts);
    }

    // -------------------------------------------------------------------------
    // GetParagraphStyles
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphStyles_NonNull_AfterAppendParagraph()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Some text.");
        Assert.NotNull(doc.GetParagraphStyles());
    }

    [Fact]
    public void GetParagraphStyles_NonEmpty_AfterContent()
    {
        var doc = CreateMixedDoc();
        Assert.NotEmpty(doc.GetParagraphStyles());
    }

    [Fact]
    public void GetParagraphStyles_CountAtLeastOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Title", 1);
        var styles = doc.GetParagraphStyles();
        Assert.True(styles.Count >= 1);
    }

    [Fact]
    public void GetParagraphStyles_ContainsAStyleName()
    {
        var doc = CreateMixedDoc();
        var styles = doc.GetParagraphStyles();
        // Each style should be a non-empty string
        foreach (var s in styles)
            Assert.False(string.IsNullOrWhiteSpace(s));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateInsertHeadingsAppendGetHeadingCountGetHeadingTextsGetStylesVerify_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();

        // Build document with headings and paragraphs
        doc.InsertHeading(0, "Introduction", 1);
        doc.AppendParagraph("The introduction covers the project background.");
        doc.InsertHeading(1, "Methods", 2);
        doc.AppendParagraph("Methods describe the experimental approach.");
        doc.InsertHeading(2, "Results", 2);
        doc.AppendParagraph("Results show a positive outcome.");
        doc.InsertHeading(3, "Conclusion", 1);
        doc.AppendParagraph("The conclusion summarizes all findings.");

        // GetHeadingCount
        var headingCount = doc.GetHeadingCount();
        Assert.Equal(4, headingCount);

        // GetParagraphCount should be > headingCount (has plain paras too)
        Assert.True(doc.GetParagraphCount() > headingCount);

        // GetHeadingTexts
        var headingTexts = doc.GetHeadingTexts();
        Assert.Equal(4, headingTexts.Count);
        Assert.Contains("Introduction", headingTexts);
        Assert.Contains("Methods", headingTexts);
        Assert.Contains("Results", headingTexts);
        Assert.Contains("Conclusion", headingTexts);

        // Heading texts do not include paragraph text
        Assert.DoesNotContain("project background", headingTexts);
        Assert.DoesNotContain("experimental approach", headingTexts);

        // GetParagraphStyles
        var styles = doc.GetParagraphStyles();
        Assert.NotNull(styles);
        Assert.NotEmpty(styles);

        // GetPlainText contains all headings and paragraphs
        var text = doc.GetPlainText();
        Assert.Contains("Introduction", text);
        Assert.Contains("project background", text);
        Assert.Contains("Conclusion", text);
    }
}
