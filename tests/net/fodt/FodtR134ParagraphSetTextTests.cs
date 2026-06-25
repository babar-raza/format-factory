// Tests for FodtParagraph.SetText() — live DOM write-through mutation on paragraph objects.
// Sprint: FORMAT-FACTORY-FODT-SETTEXT-R134-20260626
// Ledger: R134-GOVERNED-DOTNET-FODT-PARAGRAPHSETTEXT-001

using System;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R134: FodtParagraph.SetText(value) mutates the underlying DOM in-place.
/// After SetText, FodtParagraph.Text reflects the new value. The change is visible
/// through FodtDocument.GetParagraphText(index) and FodtDocument.GetParagraphTexts().
/// IsHeading and OutlineLevel are preserved after SetText on a heading paragraph.
/// </summary>
public class FodtR134ParagraphSetTextTests
{
    // ---- Basic SetText + Text readback ----

    [Fact]
    public void SetText_BodyParagraph_TextReflectsNewValue()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Original text");
        var para = doc.Paragraphs[0];

        para.SetText("Updated text");

        Assert.Equal("Updated text", para.Text);
    }

    [Fact]
    public void SetText_HeadingParagraph_TextReflectsNewValue()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Original Title", level: 1);
        var para = doc.Paragraphs[0];

        para.SetText("New Title");

        Assert.Equal("New Title", para.Text);
    }

    // ---- Live DOM: document-level methods reflect SetText change ----

    [Fact]
    public void SetText_DocumentGetParagraphText_AlsoUpdated()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Before");
        var para = doc.Paragraphs[0];

        para.SetText("After");

        Assert.Equal("After", doc.GetParagraphText(0));
    }

    [Fact]
    public void SetText_GetParagraphTexts_ReflectsChange()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Initial");
        doc.AppendParagraph("Second");
        var para = doc.Paragraphs[0];

        para.SetText("Modified");

        var texts = doc.GetParagraphTexts();
        Assert.Equal("Modified", texts[0]);
        Assert.Equal("Second",   texts[1]);
    }

    // ---- IsHeading preserved after SetText ----

    [Fact]
    public void SetText_OnHeading_IsHeadingStillTrue()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Section", level: 2);
        var para = doc.Paragraphs[0];

        para.SetText("Renamed Section");

        Assert.True(para.IsHeading);
    }

    [Fact]
    public void SetText_OnHeading_OutlineLevelPreserved()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("H3 Heading", level: 3);
        var para = doc.Paragraphs[0];

        para.SetText("Updated H3");

        Assert.Equal(3, para.OutlineLevel);
    }

    // ---- IsHeading=false preserved for body paragraphs ----

    [Fact]
    public void SetText_OnBodyParagraph_IsHeadingStillFalse()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Body");
        var para = doc.Paragraphs[0];

        para.SetText("Updated Body");

        Assert.False(para.IsHeading);
    }

    // ---- SetText with empty string ----

    [Fact]
    public void SetText_EmptyString_TextBecomesEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Content");
        var para = doc.Paragraphs[0];

        para.SetText(string.Empty);

        Assert.Equal(string.Empty, para.Text);
    }

    // ---- Multiple SetText calls ----

    [Fact]
    public void SetText_CalledTwice_LastValueWins()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        var para = doc.Paragraphs[0];

        para.SetText("Second");
        para.SetText("Third");

        Assert.Equal("Third", para.Text);
    }

    // ---- ExportToMarkdown reflects SetText change ----

    [Fact]
    public void SetText_Heading_ExportToMarkdownShowsUpdatedText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Old Title", level: 1);
        var para = doc.Paragraphs[0];

        para.SetText("New Title");

        var md = doc.ExportToMarkdown();
        Assert.Contains("New Title", md);
        Assert.DoesNotContain("Old Title", md);
    }

    // ---- Dogfood: template fill pipeline ----

    [Fact]
    public void DogfoodPipeline_TemplateFill_AllPlaceholdersReplaced()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("{{REPORT_TITLE}}",    level: 1);
        doc.AppendParagraph("Author: {{AUTHOR}}");
        doc.AppendHeading("{{SECTION_1}}",       level: 2);
        doc.AppendParagraph("{{BODY_TEXT}}");
        doc.AppendHeading("Conclusion",           level: 2);
        doc.AppendParagraph("{{CONCLUSION}}");

        // Fill in template
        doc.Paragraphs[0].SetText("Monthly Sales Report — June 2026");
        doc.Paragraphs[1].SetText("Author: Alice Johnson");
        doc.Paragraphs[2].SetText("Executive Summary");
        doc.Paragraphs[3].SetText("Sales increased by 12% compared to May 2026.");
        doc.Paragraphs[5].SetText("All targets exceeded. Q3 outlook is positive.");

        var texts = doc.GetParagraphTexts();

        Assert.Equal("Monthly Sales Report — June 2026",         texts[0]);
        Assert.Equal("Author: Alice Johnson",                     texts[1]);
        Assert.Equal("Executive Summary",                         texts[2]);
        Assert.Contains("12%",                                    texts[3]);
        Assert.Equal("Conclusion",                                 texts[4]);
        Assert.Contains("Q3 outlook",                             texts[5]);

        // Headings still headings
        Assert.True(doc.Paragraphs[0].IsHeading);
        Assert.True(doc.Paragraphs[2].IsHeading);
        Assert.Equal(1, doc.Paragraphs[0].OutlineLevel);
        Assert.Equal(2, doc.Paragraphs[2].OutlineLevel);
    }
}
