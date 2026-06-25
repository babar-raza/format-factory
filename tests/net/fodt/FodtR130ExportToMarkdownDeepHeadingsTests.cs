// Tests for FodtDocument.ExportToMarkdown() with deep heading levels H4-H6.
// Sprint: FORMAT-FACTORY-FODT-MARKDOWN-DEEP-HEADINGS-20260626
// Ledger: R130-GOVERNED-DOTNET-FODT-MARKDOWN-DEEP-HEADINGS-001

using System;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R130: FodtDocument.ExportToMarkdown() maps deep heading levels to ATX syntax:
/// H4 → "#### ", H5 → "##### ", H6 → "###### ". Heading content is present.
/// Mixed shallow+deep documents render all levels correctly in order.
/// </summary>
public class FodtR130ExportToMarkdownDeepHeadingsTests
{
    // ---- H4 → "####" ----

    [Fact]
    public void ExportToMarkdown_H4Heading_ProducesFourHashes()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Chapter Sub-Section", level: 4);

        var md = doc.ExportToMarkdown();
        Assert.Contains("#### ", md);
    }

    [Fact]
    public void ExportToMarkdown_H4Heading_ContentPresent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Deep Level Four", level: 4);

        var md = doc.ExportToMarkdown();
        Assert.Contains("Deep Level Four", md);
    }

    // ---- H5 → "#####" ----

    [Fact]
    public void ExportToMarkdown_H5Heading_ProducesFiveHashes()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Fifth Level Header", level: 5);

        var md = doc.ExportToMarkdown();
        Assert.Contains("##### ", md);
    }

    [Fact]
    public void ExportToMarkdown_H5Heading_ContentPresent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Sub-Sub-Section Title", level: 5);

        var md = doc.ExportToMarkdown();
        Assert.Contains("Sub-Sub-Section Title", md);
    }

    // ---- H6 → "######" ----

    [Fact]
    public void ExportToMarkdown_H6Heading_ProducesSixHashes()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Deepest Heading Level", level: 6);

        var md = doc.ExportToMarkdown();
        Assert.Contains("###### ", md);
    }

    [Fact]
    public void ExportToMarkdown_H6Heading_ContentPresent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Very Deep Section", level: 6);

        var md = doc.ExportToMarkdown();
        Assert.Contains("Very Deep Section", md);
    }

    // ---- H4/H5/H6 do not use shallow hashes ----

    [Fact]
    public void ExportToMarkdown_H4Only_DoesNotProduceH1()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Not Top Level", level: 4);

        var md = doc.ExportToMarkdown();
        // Should not start with a single # (which would be H1)
        Assert.DoesNotContain("\n# Not Top Level", md);
        Assert.DoesNotContain("## Not Top Level", md);
        Assert.DoesNotContain("### Not Top Level", md);
    }

    // ---- Mixed shallow + deep heading document ----

    [Fact]
    public void ExportToMarkdown_AllSixLevels_AllPresentInOutput()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", level: 1);
        doc.AppendHeading("Chapter", level: 2);
        doc.AppendHeading("Section", level: 3);
        doc.AppendHeading("Subsection", level: 4);
        doc.AppendHeading("Paragraph", level: 5);
        doc.AppendHeading("Clause", level: 6);

        var md = doc.ExportToMarkdown();

        Assert.Contains("# Title", md);
        Assert.Contains("## Chapter", md);
        Assert.Contains("### Section", md);
        Assert.Contains("#### Subsection", md);
        Assert.Contains("##### Paragraph", md);
        Assert.Contains("###### Clause", md);
    }

    [Fact]
    public void ExportToMarkdown_DeepHeadingOrder_PreservedInOutput()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Alpha H4", level: 4);
        doc.AppendHeading("Beta H5", level: 5);
        doc.AppendHeading("Gamma H6", level: 6);

        var md = doc.ExportToMarkdown();

        var posAlpha = md.IndexOf("Alpha H4", StringComparison.Ordinal);
        var posBeta  = md.IndexOf("Beta H5",  StringComparison.Ordinal);
        var posGamma = md.IndexOf("Gamma H6", StringComparison.Ordinal);

        Assert.True(posAlpha >= 0);
        Assert.True(posBeta  >= 0);
        Assert.True(posGamma >= 0);
        Assert.True(posAlpha < posBeta,  "H4 Alpha should appear before H5 Beta");
        Assert.True(posBeta  < posGamma, "H5 Beta should appear before H6 Gamma");
    }

    // ---- Dogfood: full document with body and deep headings ----

    [Fact]
    public void DogfoodPipeline_DeepHeadingsAndBody_AllContentCorrect()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Document Root", level: 1);
        doc.AppendParagraph("Introduction text.");
        doc.AppendHeading("Major Section", level: 2);
        doc.AppendParagraph("Section body.");
        doc.AppendHeading("Sub-Section Detail", level: 4);
        doc.AppendParagraph("Detail text.");
        doc.AppendHeading("Fine-Grained Point", level: 6);
        doc.AppendParagraph("Granular content.");

        var md = doc.ExportToMarkdown();

        // Structural markers
        Assert.Contains("# Document Root", md);
        Assert.Contains("## Major Section", md);
        Assert.Contains("#### Sub-Section Detail", md);
        Assert.Contains("###### Fine-Grained Point", md);

        // Body content
        Assert.Contains("Introduction text.", md);
        Assert.Contains("Section body.", md);
        Assert.Contains("Detail text.", md);
        Assert.Contains("Granular content.", md);
    }
}
