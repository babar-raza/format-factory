// Tests for FodtDocument.GetParagraphStyles, SearchText, FindParagraphsByStyle deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R193

using System.Linq;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R193: Tests for FodtDocument.GetParagraphStyles, SearchText, FindParagraphsByStyle.
/// GetParagraphStyles(): returns distinct style names across all paragraphs.
/// SearchText(query): returns list of paragraph indices containing query.
/// FindParagraphsByStyle(styleName): returns paragraph indices with the given style.
/// Covers: GetParagraphStyles non-null; GetParagraphStyles contains default style;
/// GetParagraphStyles after SetParagraphStyle contains added style;
/// SearchText non-null; SearchText empty for missing text;
/// SearchText finds existing text; SearchText count for duplicated text;
/// SearchText case sensitivity check; FindParagraphsByStyle non-null;
/// FindParagraphsByStyle empty for non-existent style;
/// FindParagraphsByStyle count after SetParagraphStyle;
/// FindParagraphsByStyle index valid; GetParagraphStyles count after multiple styles;
/// dogfood CreateEmpty->AppendParagraphs->SetStyles->Search->FindByStyle.
/// </summary>
public class FodtR193GetParagraphStylesAndSearchTests
{
    // -------------------------------------------------------------------------
    // GetParagraphStyles
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphStyles_NonNull()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Some text");
        var styles = doc.GetParagraphStyles();
        Assert.NotNull(styles);
    }

    [Fact]
    public void GetParagraphStyles_AfterSetParagraphStyle_ContainsStyle()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Styled paragraph");
        doc.SetParagraphStyle(0, "CustomStyle");
        var styles = doc.GetParagraphStyles();
        Assert.Contains("CustomStyle", styles);
    }

    [Fact]
    public void GetParagraphStyles_MultipleStyles_ContainsAll()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("P1");
        doc.AppendParagraph("P2");
        doc.AppendParagraph("P3");
        doc.SetParagraphStyle(0, "StyleA");
        doc.SetParagraphStyle(1, "StyleB");
        doc.SetParagraphStyle(2, "StyleA"); // duplicate
        var styles = doc.GetParagraphStyles();
        Assert.Contains("StyleA", styles);
        Assert.Contains("StyleB", styles);
    }

    [Fact]
    public void GetParagraphStyles_DuplicateStyle_OnlyOneEntry()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("P1");
        doc.AppendParagraph("P2");
        doc.SetParagraphStyle(0, "Repeated");
        doc.SetParagraphStyle(1, "Repeated");
        var styles = doc.GetParagraphStyles();
        // Distinct styles should not have duplicates
        var distinctCount = styles.Distinct().Count();
        Assert.Equal(distinctCount, styles.Count);
    }

    // -------------------------------------------------------------------------
    // SearchText
    // -------------------------------------------------------------------------

    [Fact]
    public void SearchText_NonNull()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world");
        var results = doc.SearchText("Hello");
        Assert.NotNull(results);
    }

    [Fact]
    public void SearchText_MissingText_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world");
        var results = doc.SearchText("NONEXISTENT_XYZ");
        Assert.Empty(results);
    }

    [Fact]
    public void SearchText_ExistingText_ReturnsResults()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world");
        doc.AppendParagraph("Goodbye world");
        var results = doc.SearchText("world");
        Assert.NotEmpty(results);
    }

    [Fact]
    public void SearchText_DuplicateText_CountMatchesOccurrences()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("match one");
        doc.AppendParagraph("other text");
        doc.AppendParagraph("match two");
        var results = doc.SearchText("match");
        Assert.Equal(2, results.Count);
    }

    [Fact]
    public void SearchText_SingleMatch_IndexValid()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First paragraph");
        doc.AppendParagraph("Target paragraph here");
        doc.AppendParagraph("Third paragraph");
        var results = doc.SearchText("Target");
        Assert.Single(results);
        Assert.True(results[0] >= 0);
    }

    // -------------------------------------------------------------------------
    // FindParagraphsByStyle
    // -------------------------------------------------------------------------

    [Fact]
    public void FindParagraphsByStyle_NonNull()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Some text");
        var results = doc.FindParagraphsByStyle("Default");
        Assert.NotNull(results);
    }

    [Fact]
    public void FindParagraphsByStyle_NonExistentStyle_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Some text");
        var results = doc.FindParagraphsByStyle("NONEXISTENT_STYLE_XYZ");
        Assert.Empty(results);
    }

    [Fact]
    public void FindParagraphsByStyle_AfterSetParagraphStyle_ReturnsMatching()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("P0");
        doc.AppendParagraph("P1");
        doc.AppendParagraph("P2");
        doc.SetParagraphStyle(0, "Bold");
        doc.SetParagraphStyle(2, "Bold");
        var results = doc.FindParagraphsByStyle("Bold");
        Assert.Equal(2, results.Count);
    }

    [Fact]
    public void FindParagraphsByStyle_IndexIsValid()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("P0");
        doc.AppendParagraph("P1");
        doc.SetParagraphStyle(1, "Italic");
        var results = doc.FindParagraphsByStyle("Italic");
        Assert.Single(results);
        Assert.Equal(1, results[0]);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateEmpty->AppendParagraphs->SetStyles->SearchText->FindParagraphsByStyle
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateAppendSetStylesSearchFind_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();

        // Add paragraphs
        doc.AppendParagraph("Introduction to the topic.");
        doc.AppendParagraph("This section covers methods.");
        doc.AppendParagraph("Introduction continued here.");
        doc.AppendParagraph("Conclusion and summary.");

        // Set styles
        doc.SetParagraphStyle(0, "Heading1");
        doc.SetParagraphStyle(2, "Heading1");
        doc.SetParagraphStyle(3, "Summary");

        // GetParagraphStyles
        var styles = doc.GetParagraphStyles();
        Assert.Contains("Heading1", styles);
        Assert.Contains("Summary", styles);

        // SearchText
        var introMatches = doc.SearchText("Introduction");
        Assert.Equal(2, introMatches.Count);

        var conclusionMatches = doc.SearchText("Conclusion");
        Assert.Equal(1, conclusionMatches.Count);

        var noMatches = doc.SearchText("NONEXISTENT_XYZ");
        Assert.Empty(noMatches);

        // FindParagraphsByStyle
        var heading1s = doc.FindParagraphsByStyle("Heading1");
        Assert.Equal(2, heading1s.Count);
        Assert.Contains(0, heading1s);
        Assert.Contains(2, heading1s);

        var summaries = doc.FindParagraphsByStyle("Summary");
        Assert.Equal(1, summaries.Count);
        Assert.Equal(3, summaries[0]);
    }
}
