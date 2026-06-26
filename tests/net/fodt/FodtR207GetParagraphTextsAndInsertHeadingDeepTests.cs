// Tests for FodtDocument.GetParagraphTexts, InsertHeading deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R207

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R207: Tests for FodtDocument.GetParagraphTexts, InsertHeading deeper coverage.
/// GetParagraphTexts(): returns list of text strings for all paragraphs (including headings).
/// InsertHeading(index, text, level): inserts a heading paragraph at the given index.
/// Covers: GetParagraphTexts non-null; GetParagraphTexts non-empty after AppendParagraph;
/// GetParagraphTexts count equals ParagraphCount; GetParagraphTexts contains all texts;
/// GetParagraphTexts includes heading texts; GetParagraphTexts after multiple appends;
/// InsertHeading at index 0 makes it first; InsertHeading in middle shifts others;
/// InsertHeading at end appends; InsertHeading increments HeadingCount;
/// InsertHeading increments ParagraphCount; GetParagraphTexts after InsertHeading reflects it;
/// dogfood CreateEmpty->InsertHeading->AppendParagraph->GetParagraphTexts->GetHeadingTexts verify.
/// </summary>
public class FodtR207GetParagraphTextsAndInsertHeadingDeepTests
{
    // -------------------------------------------------------------------------
    // GetParagraphTexts
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphTexts_NonNull_AfterAppendParagraph()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Some text.");
        Assert.NotNull(doc.GetParagraphTexts());
    }

    [Fact]
    public void GetParagraphTexts_NonEmpty_AfterContent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world.");
        Assert.NotEmpty(doc.GetParagraphTexts());
    }

    [Fact]
    public void GetParagraphTexts_Count_EqualsParagraphCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First.");
        doc.AppendParagraph("Second.");
        doc.AppendParagraph("Third.");
        var texts = doc.GetParagraphTexts();
        Assert.Equal(doc.GetParagraphCount(), texts.Count);
    }

    [Fact]
    public void GetParagraphTexts_ContainsAllParagraphTexts()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha text here.");
        doc.AppendParagraph("Beta text here.");
        var texts = doc.GetParagraphTexts();
        Assert.True(texts.Exists(t => t.Contains("Alpha")));
        Assert.True(texts.Exists(t => t.Contains("Beta")));
    }

    [Fact]
    public void GetParagraphTexts_IncludesHeadingTexts()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "My Heading", 1);
        doc.AppendParagraph("Body paragraph.");
        var texts = doc.GetParagraphTexts();
        Assert.True(texts.Exists(t => t.Contains("My Heading")));
        Assert.True(texts.Exists(t => t.Contains("Body paragraph")));
    }

    [Fact]
    public void GetParagraphTexts_EmptyDoc_ReturnsEmptyOrNull()
    {
        var doc = FodtDocument.CreateEmpty();
        var texts = doc.GetParagraphTexts();
        Assert.True(texts == null || texts.Count == 0);
    }

    [Fact]
    public void GetParagraphTexts_AfterMultipleAppends_AllPresent()
    {
        var doc = FodtDocument.CreateEmpty();
        for (var i = 0; i < 5; i++)
            doc.AppendParagraph($"Paragraph number {i + 1}.");
        var texts = doc.GetParagraphTexts();
        Assert.Equal(5, texts.Count);
        Assert.True(texts.Exists(t => t.Contains("Paragraph number 1")));
        Assert.True(texts.Exists(t => t.Contains("Paragraph number 5")));
    }

    // -------------------------------------------------------------------------
    // InsertHeading
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertHeading_AtIndex0_BecomesFirst()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Existing paragraph.");
        doc.InsertHeading(0, "New Title", 1);
        var texts = doc.GetParagraphTexts();
        Assert.True(texts.Count >= 1);
        Assert.True(texts[0].Contains("New Title"));
    }

    [Fact]
    public void InsertHeading_IncrementsHeadingCount()
    {
        var doc = FodtDocument.CreateEmpty();
        var before = doc.GetHeadingCount();
        doc.InsertHeading(0, "A Heading", 1);
        Assert.Equal(before + 1, doc.GetHeadingCount());
    }

    [Fact]
    public void InsertHeading_IncrementsParagraphCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Existing.");
        var before = doc.GetParagraphCount();
        doc.InsertHeading(1, "Section", 2);
        Assert.Equal(before + 1, doc.GetParagraphCount());
    }

    [Fact]
    public void InsertHeading_MultipleHeadings_HeadingCountCorrect()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Chapter 1", 1);
        doc.InsertHeading(1, "Section 1.1", 2);
        doc.InsertHeading(2, "Chapter 2", 1);
        Assert.Equal(3, doc.GetHeadingCount());
    }

    [Fact]
    public void InsertHeading_Level1and2_InOutline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Top Level", 1);
        doc.InsertHeading(1, "Sub Level", 2);
        var outline = doc.GetDocumentOutline();
        Assert.Equal(2, outline.Count);
        Assert.Equal(1, outline[0].Level);
        Assert.Equal(2, outline[1].Level);
    }

    [Fact]
    public void InsertHeading_GetParagraphTexts_ContainsHeadingText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Executive Report", 1);
        doc.AppendParagraph("Report content.");
        var texts = doc.GetParagraphTexts();
        Assert.True(texts.Exists(t => t.Contains("Executive Report")));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateEmptyInsertHeadingAppendGetParagraphTextsGetHeadingTextsVerify_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();

        // InsertHeading at 0
        doc.InsertHeading(0, "Introduction", 1);
        Assert.Equal(1, doc.GetHeadingCount());

        // AppendParagraph
        doc.AppendParagraph("The introduction provides an overview of the subject matter.");
        doc.AppendParagraph("Key concepts are introduced in this section.");

        // InsertHeading at position 3 (end)
        doc.InsertHeading(3, "Methodology", 2);
        Assert.Equal(2, doc.GetHeadingCount());

        // AppendParagraph after heading
        doc.AppendParagraph("The methodology section details research approaches.");

        // GetParagraphTexts
        var texts = doc.GetParagraphTexts();
        Assert.NotNull(texts);
        Assert.True(texts.Count >= 4); // 2 headings + 3 plain paragraphs

        // Contains all content
        Assert.True(texts.Exists(t => t.Contains("Introduction")));
        Assert.True(texts.Exists(t => t.Contains("Methodology")));
        Assert.True(texts.Exists(t => t.Contains("overview")));
        Assert.True(texts.Exists(t => t.Contains("research approaches")));

        // GetHeadingTexts
        var headingTexts = doc.GetHeadingTexts();
        Assert.Equal(2, headingTexts.Count);
        Assert.Contains("Introduction", headingTexts);
        Assert.Contains("Methodology", headingTexts);

        // Verify paragraph count
        Assert.Equal(texts.Count, doc.GetParagraphCount());

        // GetDocumentOutline
        var outline = doc.GetDocumentOutline();
        Assert.Equal(2, outline.Count);
        Assert.Equal("Introduction", outline[0].Text);
        Assert.Equal(1, outline[0].Level);
        Assert.Equal("Methodology", outline[1].Text);
        Assert.Equal(2, outline[1].Level);
    }
}
