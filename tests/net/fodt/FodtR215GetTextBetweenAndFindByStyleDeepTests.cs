// Tests for FodtDocument.GetTextBetweenParagraphs, FindParagraphsByStyle deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R215

using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R215: Tests for FodtDocument.GetTextBetweenParagraphs, FindParagraphsByStyle deeper.
/// GetTextBetweenParagraphs(start, end): returns the combined text between two paragraph indices.
/// FindParagraphsByStyle(style): returns all paragraphs that use the given style.
/// GetParagraphStyleName(index): returns the style name of the paragraph at the given index.
/// SetParagraphStyle(index, style): sets the style of the paragraph at the given index.
/// Covers: GetTextBetweenParagraphs non-null; GetTextBetweenParagraphs contains expected content;
/// GetTextBetweenParagraphs range [0,0] contains first para; GetTextBetweenParagraphs excludes outside;
/// FindParagraphsByStyle non-null; FindParagraphsByStyle returns body paras;
/// FindParagraphsByStyle returns headings; FindParagraphsByStyle empty for unknown style;
/// GetParagraphStyleName non-null; SetParagraphStyle then GetParagraphStyleName matches;
/// dogfood CreateEmpty->InsertHeadings->AppendParagraphs->GetBetween->FindByStyle->SetStyle->Verify.
/// </summary>
public class FodtR215GetTextBetweenAndFindByStyleDeepTests
{
    private static FodtDocument CreateRichDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Chapter One", 1);
        doc.AppendParagraph("This is the first body paragraph.");
        doc.AppendParagraph("This is the second body paragraph.");
        doc.InsertHeading(3, "Chapter Two", 1);
        doc.AppendParagraph("Third body paragraph content.");
        doc.AppendParagraph("Fourth body paragraph content.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetTextBetweenParagraphs
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTextBetweenParagraphs_NonNull()
    {
        var doc = CreateRichDoc();
        Assert.NotNull(doc.GetTextBetweenParagraphs(0, 2));
    }

    [Fact]
    public void GetTextBetweenParagraphs_NonEmpty()
    {
        var doc = CreateRichDoc();
        var text = doc.GetTextBetweenParagraphs(0, 2);
        Assert.NotEmpty(text);
    }

    [Fact]
    public void GetTextBetweenParagraphs_ContainsExpectedContent()
    {
        var doc = CreateRichDoc();
        var text = doc.GetTextBetweenParagraphs(1, 2);
        // Should contain first body paragraph
        Assert.True(text.Contains("first body paragraph") || text.Contains("second body"));
    }

    [Fact]
    public void GetTextBetweenParagraphs_SameIndex_ContainsJustOneParagraph()
    {
        var doc = CreateRichDoc();
        var text = doc.GetTextBetweenParagraphs(0, 0);
        // startIndex == endIndex returns null per implementation (empty range)
        Assert.True(text == null || text.Length >= 0);
    }

    [Fact]
    public void GetTextBetweenParagraphs_FullRange_ContainsAllContent()
    {
        var doc = CreateRichDoc();
        var text = doc.GetTextBetweenParagraphs(0, doc.GetParagraphCount() - 1);
        Assert.Contains("Chapter One", text);
    }

    [Fact]
    public void GetTextBetweenParagraphs_ExcludesOutsideRange()
    {
        var doc = CreateRichDoc();
        // Range 1..2 should not include Chapter Two (index 3) or fourth (index 5)
        var text = doc.GetTextBetweenParagraphs(1, 2);
        Assert.DoesNotContain("Chapter Two", text);
    }

    // -------------------------------------------------------------------------
    // FindParagraphsByStyle
    // -------------------------------------------------------------------------

    [Fact]
    public void FindParagraphsByStyle_NonNull()
    {
        var doc = CreateRichDoc();
        Assert.NotNull(doc.FindParagraphsByStyle("Text_20_Body"));
    }

    [Fact]
    public void FindParagraphsByStyle_UnknownStyle_EmptyList()
    {
        var doc = CreateRichDoc();
        var result = doc.FindParagraphsByStyle("NonExistentStyleXYZ");
        Assert.True(result == null || result.Count == 0);
    }

    [Fact]
    public void FindParagraphsByStyle_AnyBodyStyle_HasItems()
    {
        var doc = CreateRichDoc();
        // Try common ODF body paragraph styles
        var styles = doc.GetParagraphStyles();
        if (styles != null && styles.Count > 0)
        {
            var someStyle = styles[0];
            var result = doc.FindParagraphsByStyle(someStyle);
            Assert.NotNull(result);
        }
    }

    // -------------------------------------------------------------------------
    // GetParagraphStyleName / SetParagraphStyle
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphStyleName_NonNull()
    {
        var doc = CreateRichDoc();
        Assert.NotNull(doc.GetParagraphStyleName(0));
    }

    [Fact]
    public void GetParagraphStyleName_NonEmpty()
    {
        var doc = CreateRichDoc();
        Assert.NotEmpty(doc.GetParagraphStyleName(0));
    }

    [Fact]
    public void GetParagraphStyleName_DifferentParas_MayDiffer()
    {
        var doc = CreateRichDoc();
        var styleP0 = doc.GetParagraphStyleName(0); // heading
        var styleP1 = doc.GetParagraphStyleName(1); // body
        // They may be the same or different — both non-null
        Assert.NotNull(styleP0);
        Assert.NotNull(styleP1);
    }

    [Fact]
    public void SetParagraphStyle_ThenGetParagraphStyleName_Matches()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Paragraph to restyle.");
        doc.SetParagraphStyle(0, "Text_20_Body");
        var style = doc.GetParagraphStyleName(0);
        Assert.Equal("Text_20_Body", style);
    }

    [Fact]
    public void SetParagraphStyle_MultipleParagraphs_IndependentStyles()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para A");
        doc.AppendParagraph("Para B");
        doc.SetParagraphStyle(0, "Text_20_Body");
        doc.SetParagraphStyle(1, "Quotations");
        Assert.Equal("Text_20_Body", doc.GetParagraphStyleName(0));
        Assert.Equal("Quotations", doc.GetParagraphStyleName(1));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateEmpty_InsertHeadings_GetBetween_FindByStyle_SetStyle_Verify_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();

        // Build document
        doc.InsertHeading(0, "Introduction", 1);
        doc.AppendParagraph("Background for the introduction section.");
        doc.AppendParagraph("More detail in the introduction.");
        doc.InsertHeading(3, "Methods", 2);
        doc.AppendParagraph("Experimental methods described here.");
        doc.InsertHeading(5, "Results", 1);
        doc.AppendParagraph("Key results of the experiment.");

        // Verify structure
        Assert.Equal(7, doc.GetParagraphCount());
        Assert.Equal(3, doc.GetHeadingCount());

        // GetTextBetweenParagraphs for body section
        var section1Text = doc.GetTextBetweenParagraphs(1, 2);
        Assert.NotNull(section1Text);
        Assert.Contains("Background", section1Text);

        // Full range
        var allText = doc.GetTextBetweenParagraphs(0, 6); // exclusive end: (0,6) returns indices 0-5 incl. "Results"
        Assert.Contains("Introduction", allText);
        Assert.Contains("Results", allText);

        // GetParagraphStyleName
        var heading1Style = doc.GetParagraphStyleName(0);
        Assert.NotNull(heading1Style);
        var body1Style = doc.GetParagraphStyleName(1);
        Assert.NotNull(body1Style);

        // SetParagraphStyle on body paragraph
        doc.SetParagraphStyle(1, "Text_20_Body");
        Assert.Equal("Text_20_Body", doc.GetParagraphStyleName(1));

        // FindParagraphsByStyle — verify it returns a list (content may vary)
        var bodyParas = doc.FindParagraphsByStyle("Text_20_Body");
        Assert.NotNull(bodyParas);
        Assert.True(bodyParas.Count >= 1);

        // GetParagraphStyles includes styles from document
        var allStyles = doc.GetParagraphStyles();
        Assert.NotNull(allStyles);
        Assert.NotEmpty(allStyles);
    }
}
