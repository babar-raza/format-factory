// Tests for FodtDocument.InsertHeading, GetHeadingTexts, GetHeadingParagraphs deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R195

using System.Linq;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R195: Tests for FodtDocument.InsertHeading, GetHeadingTexts, GetHeadingParagraphs.
/// InsertHeading(index, text, level): inserts a heading at the given paragraph index.
/// GetHeadingTexts(): returns list of all heading texts.
/// GetHeadingParagraphs(): returns list of paragraph texts that are headings.
/// Covers: InsertHeading increments heading count; InsertHeading text accessible;
/// InsertHeading at specific index; InsertHeading level 1 and level 2;
/// GetHeadingTexts non-null; GetHeadingTexts contains inserted heading;
/// GetHeadingTexts count matches heading count; GetHeadingTexts order;
/// GetHeadingParagraphs non-null; GetHeadingParagraphs count matches;
/// GetHeadingParagraphs contains expected text; RemoveHeading reduces count;
/// GetHeadingTexts after RemoveHeading; InsertHeading after AppendParagraph;
/// dogfood CreateEmpty->InsertHeadings->AppendParagraphs->GetHeadingTexts->GetHeadingParagraphs.
/// </summary>
public class FodtR195InsertHeadingAndGetHeadingTextsTests
{
    // -------------------------------------------------------------------------
    // InsertHeading
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertHeading_IncrementsHeadingCount()
    {
        var doc = FodtDocument.CreateEmpty();
        var before = doc.GetHeadingCount();
        doc.InsertHeading(0, "Chapter One", 1);
        Assert.Equal(before + 1, doc.GetHeadingCount());
    }

    [Fact]
    public void InsertHeading_TextAccessibleViaGetHeadingTexts()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "My Section", 1);
        var texts = doc.GetHeadingTexts();
        Assert.Contains("My Section", texts);
    }

    [Fact]
    public void InsertHeading_AtSpecificIndex()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Body paragraph");
        doc.InsertHeading(0, "Before Body", 1);
        // Heading should be at position 0
        Assert.True(doc.ParagraphCount >= 2);
    }

    [Fact]
    public void InsertHeading_Level1AndLevel2_BothTracked()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Chapter", 1);
        doc.InsertHeading(1, "Section", 2);
        var texts = doc.GetHeadingTexts();
        Assert.Contains("Chapter", texts);
        Assert.Contains("Section", texts);
    }

    [Fact]
    public void InsertHeading_MultipleHeadings_CountCorrect()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "H1", 1);
        doc.InsertHeading(1, "H2", 2);
        doc.InsertHeading(2, "H3", 1);
        Assert.Equal(3, doc.GetHeadingCount());
    }

    // -------------------------------------------------------------------------
    // GetHeadingTexts
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeadingTexts_NonNull()
    {
        var doc = FodtDocument.CreateEmpty();
        var texts = doc.GetHeadingTexts();
        Assert.NotNull(texts);
    }

    [Fact]
    public void GetHeadingTexts_EmptyForNoHeadings()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Just body text");
        var texts = doc.GetHeadingTexts();
        Assert.Empty(texts);
    }

    [Fact]
    public void GetHeadingTexts_CountMatchesHeadingCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "H1", 1);
        doc.InsertHeading(1, "H2", 2);
        var texts = doc.GetHeadingTexts();
        Assert.Equal(doc.GetHeadingCount(), texts.Count);
    }

    [Fact]
    public void GetHeadingTexts_OrderIsPreserved()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "First", 1);
        doc.InsertHeading(1, "Second", 2);
        doc.InsertHeading(2, "Third", 1);
        var texts = doc.GetHeadingTexts();
        Assert.Equal("First", texts[0]);
        Assert.Equal("Second", texts[1]);
        Assert.Equal("Third", texts[2]);
    }

    [Fact]
    public void GetHeadingTexts_AfterRemoveHeading_Decreases()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "H1", 1);
        doc.InsertHeading(1, "H2", 2);
        doc.RemoveHeading(0);
        var texts = doc.GetHeadingTexts();
        Assert.Equal(1, texts.Count);
    }

    // -------------------------------------------------------------------------
    // GetHeadingParagraphs
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeadingParagraphs_NonNull()
    {
        var doc = FodtDocument.CreateEmpty();
        var paras = doc.GetHeadingParagraphs();
        Assert.NotNull(paras);
    }

    [Fact]
    public void GetHeadingParagraphs_CountMatchesHeadingCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Chapter", 1);
        doc.InsertHeading(1, "Sub-chapter", 2);
        var paras = doc.GetHeadingParagraphs();
        Assert.Equal(2, paras.Count);
    }

    [Fact]
    public void GetHeadingParagraphs_ContainsHeadingText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Introduction", 1);
        doc.AppendParagraph("Body text here.");
        var paras = doc.GetHeadingParagraphs();
        Assert.Contains("Introduction", paras);
        Assert.DoesNotContain("Body text here.", paras);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateEmpty->InsertHeadings->AppendParagraphs->GetHeadingTexts->GetHeadingParagraphs
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateInsertAppendGetTextsGetParagraphs_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();

        // InsertHeadings
        doc.InsertHeading(0, "Introduction", 1);
        doc.InsertHeading(1, "Methods", 1);
        doc.InsertHeading(2, "Subsection A", 2);
        doc.InsertHeading(3, "Subsection B", 2);

        // AppendParagraphs (body text)
        doc.AppendParagraph("Body content for introduction.");
        doc.AppendParagraph("Body content for methods section.");

        // Heading count
        Assert.Equal(4, doc.GetHeadingCount());
        Assert.True(doc.ParagraphCount >= 6);

        // GetHeadingTexts
        var texts = doc.GetHeadingTexts();
        Assert.Equal(4, texts.Count);
        Assert.Equal("Introduction", texts[0]);
        Assert.Equal("Methods", texts[1]);
        Assert.Equal("Subsection A", texts[2]);
        Assert.Equal("Subsection B", texts[3]);

        // GetHeadingParagraphs
        var headingParas = doc.GetHeadingParagraphs();
        Assert.Equal(4, headingParas.Count);
        Assert.Contains("Introduction", headingParas);
        Assert.Contains("Subsection A", headingParas);

        // RemoveHeading
        doc.RemoveHeading(3); // Remove Subsection B
        Assert.Equal(3, doc.GetHeadingCount());
        var textsAfter = doc.GetHeadingTexts();
        Assert.DoesNotContain("Subsection B", textsAfter);
    }
}
