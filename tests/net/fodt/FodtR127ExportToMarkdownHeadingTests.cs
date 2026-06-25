// Tests for FodtDocument.ExportToMarkdown() heading level hierarchy.
// Sprint: FORMAT-FACTORY-FODT-EXPORT-MARKDOWN-HEADINGS-20260626
// Ledger: R127-GOVERNED-DOTNET-FODT-EXPORT-MARKDOWN-HEADINGS-001

using System;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R127: FodtDocument.ExportToMarkdown() — converts headings to ATX markdown syntax.
/// H1 → "# text", H2 → "## text", H3 → "### text". Body paragraphs appear as plain
/// text without hash prefix. Empty document produces valid non-empty string.
/// </summary>
public class FodtR127ExportToMarkdownHeadingTests
{
    // ---- Empty document ----

    [Fact]
    public void ExportToMarkdown_EmptyDoc_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateEmpty();
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
    }

    // ---- H1 heading → "# " ----

    [Fact]
    public void ExportToMarkdown_H1Heading_ContainsHashPrefix()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Document Title", level: 1);

        var md = doc.ExportToMarkdown();
        Assert.Contains("# Document Title", md);
    }

    [Fact]
    public void ExportToMarkdown_H1Heading_ContentPresent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("My Report", level: 1);

        var md = doc.ExportToMarkdown();
        Assert.Contains("My Report", md);
    }

    // ---- H2 heading → "## " ----

    [Fact]
    public void ExportToMarkdown_H2Heading_ContainsDoubleHashPrefix()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Section One", level: 2);

        var md = doc.ExportToMarkdown();
        Assert.Contains("## Section One", md);
    }

    // ---- H3 heading → "### " ----

    [Fact]
    public void ExportToMarkdown_H3Heading_ContainsTripleHashPrefix()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Subsection", level: 3);

        var md = doc.ExportToMarkdown();
        Assert.Contains("### Subsection", md);
    }

    // ---- Body paragraph: no hash prefix ----

    [Fact]
    public void ExportToMarkdown_BodyParagraph_DoesNotContainHashPrefix()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Plain body text here.");

        var md = doc.ExportToMarkdown();
        // Should not start with a hash
        Assert.DoesNotContain("# Plain body text", md);
        Assert.Contains("Plain body text", md);
    }

    [Fact]
    public void ExportToMarkdown_BodyParagraph_ContentPresent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Introduction paragraph content.");

        var md = doc.ExportToMarkdown();
        Assert.Contains("Introduction paragraph content.", md);
    }

    // ---- Heading level ordering is preserved ----

    [Fact]
    public void ExportToMarkdown_H1BeforeH2_CorrectOrderInOutput()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Top Level", level: 1);
        doc.AppendHeading("Sub Level", level: 2);

        var md = doc.ExportToMarkdown();
        var h1Pos = md.IndexOf("# Top Level", StringComparison.Ordinal);
        var h2Pos = md.IndexOf("## Sub Level", StringComparison.Ordinal);

        Assert.True(h1Pos >= 0, "H1 heading not found in output");
        Assert.True(h2Pos >= 0, "H2 heading not found in output");
        Assert.True(h1Pos < h2Pos, "H1 should appear before H2 in output");
    }

    // ---- Dogfood: full document structure in markdown ----

    [Fact]
    public void DogfoodPipeline_FullDocumentStructure_AllLevelsPresent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Report Title", level: 1);
        doc.AppendParagraph("Executive summary goes here.");
        doc.AppendHeading("Section One", level: 2);
        doc.AppendParagraph("First section body.");
        doc.AppendHeading("Background", level: 3);
        doc.AppendParagraph("Background details.");

        var md = doc.ExportToMarkdown();

        Assert.Contains("# Report Title", md);
        Assert.Contains("## Section One", md);
        Assert.Contains("### Background", md);
        Assert.Contains("Executive summary", md);
        Assert.Contains("First section body.", md);
        Assert.Contains("Background details.", md);
    }
}
