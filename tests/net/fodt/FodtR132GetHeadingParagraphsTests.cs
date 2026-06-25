// Tests for FodtDocument.GetHeadingParagraphs() returning FodtParagraph objects.
// Sprint: FORMAT-FACTORY-FODT-GET-HEADING-PARAGRAPHS-20260626
// Ledger: R132-GOVERNED-DOTNET-FODT-GET-HEADING-PARAGRAPHS-001

using System;
using System.Linq;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R132: FodtDocument.GetHeadingParagraphs() returns only heading paragraphs as
/// FodtParagraph objects. Each returned paragraph has IsHeading=true, non-null Text,
/// and OutlineLevel matching the heading level used when appended. Body paragraphs
/// are excluded. The count matches the number of AppendHeading calls.
/// </summary>
public class FodtR132GetHeadingParagraphsTests
{
    // ---- Empty document ----

    [Fact]
    public void GetHeadingParagraphs_EmptyDoc_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Empty(doc.GetHeadingParagraphs());
    }

    // ---- Body-only document ----

    [Fact]
    public void GetHeadingParagraphs_BodyOnlyDoc_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Just a body paragraph.");
        doc.AppendParagraph("Another body paragraph.");

        Assert.Empty(doc.GetHeadingParagraphs());
    }

    // ---- All paragraphs are headings ----

    [Fact]
    public void GetHeadingParagraphs_AllHeadings_CountMatchesAppendHeadingCalls()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", level: 1);
        doc.AppendHeading("Chapter", level: 2);
        doc.AppendHeading("Section", level: 3);

        Assert.Equal(3, doc.GetHeadingParagraphs().Count);
    }

    [Fact]
    public void GetHeadingParagraphs_AllReturn_IsHeadingTrue()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("H1", level: 1);
        doc.AppendHeading("H2", level: 2);

        var headings = doc.GetHeadingParagraphs();
        Assert.All(headings, h => Assert.True(h.IsHeading));
    }

    // ---- Mixed document: headings and body ----

    [Fact]
    public void GetHeadingParagraphs_MixedDoc_ExcludesBodyParagraphs()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", level: 1);
        doc.AppendParagraph("Intro body text.");
        doc.AppendHeading("Section", level: 2);
        doc.AppendParagraph("Section body text.");

        var headings = doc.GetHeadingParagraphs();
        Assert.Equal(2, headings.Count);
    }

    [Fact]
    public void GetHeadingParagraphs_MixedDoc_TextsMatchHeadingContent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Document Title", level: 1);
        doc.AppendParagraph("Body text goes here.");
        doc.AppendHeading("Conclusion", level: 2);

        var headings = doc.GetHeadingParagraphs();
        var texts = headings.Select(h => h.Text).ToList();

        Assert.Contains("Document Title", texts);
        Assert.Contains("Conclusion", texts);
    }

    // ---- OutlineLevel reflects heading level ----

    [Fact]
    public void GetHeadingParagraphs_H1_OutlineLevelIsOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Top Level", level: 1);

        var headings = doc.GetHeadingParagraphs();
        Assert.Equal(1, headings[0].OutlineLevel);
    }

    [Fact]
    public void GetHeadingParagraphs_H2_OutlineLevelIsTwo()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Second Level", level: 2);

        var headings = doc.GetHeadingParagraphs();
        Assert.Equal(2, headings[0].OutlineLevel);
    }

    [Fact]
    public void GetHeadingParagraphs_H3_OutlineLevelIsThree()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Third Level", level: 3);

        var headings = doc.GetHeadingParagraphs();
        Assert.Equal(3, headings[0].OutlineLevel);
    }

    // ---- Consistency with GetHeadingTexts ----

    [Fact]
    public void GetHeadingParagraphs_TextsMatchGetHeadingTexts()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Alpha", level: 1);
        doc.AppendParagraph("Body.");
        doc.AppendHeading("Beta", level: 2);

        var paragraphTexts = doc.GetHeadingParagraphs().Select(h => h.Text).ToList();
        var headingTexts   = doc.GetHeadingTexts().ToList();

        Assert.Equal(headingTexts, paragraphTexts);
    }

    // ---- Dogfood: full mixed document ----

    [Fact]
    public void DogfoodPipeline_MixedDocument_AllHeadingPropertiesCorrect()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Introduction", level: 1);
        doc.AppendParagraph("Intro body.");
        doc.AppendHeading("Methods", level: 2);
        doc.AppendParagraph("Methods body.");
        doc.AppendHeading("Results", level: 2);
        doc.AppendParagraph("Results body.");
        doc.AppendHeading("Conclusion", level: 3);

        var headings = doc.GetHeadingParagraphs();

        Assert.Equal(4, headings.Count);
        Assert.All(headings, h => Assert.True(h.IsHeading));
        Assert.All(headings, h => Assert.False(string.IsNullOrEmpty(h.Text)));
        Assert.Equal(1, headings[0].OutlineLevel); // Introduction
        Assert.Equal(2, headings[1].OutlineLevel); // Methods
        Assert.Equal(2, headings[2].OutlineLevel); // Results
        Assert.Equal(3, headings[3].OutlineLevel); // Conclusion
    }
}
