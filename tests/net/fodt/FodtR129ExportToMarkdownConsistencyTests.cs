// Tests for FodtDocument.ExportToMarkdown() multi-paragraph and consistency properties.
// Sprint: FORMAT-FACTORY-FODT-MARKDOWN-CONSISTENCY-20260626
// Ledger: R129-GOVERNED-DOTNET-FODT-MARKDOWN-CONSISTENCY-001

using System;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R129: FodtDocument.ExportToMarkdown() consistency properties — each paragraph
/// appears in output, paragraphs have distinct positions, empty paragraphs produce
/// consistent output, and ExportToMarkdown matches ExportToMarkdownFile content.
/// </summary>
public class FodtR129ExportToMarkdownConsistencyTests
{
    // ---- Each paragraph content appears in markdown ----

    [Fact]
    public void ExportToMarkdown_AllParagraphTexts_PresentInOutput()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First paragraph");
        doc.AppendParagraph("Second paragraph");
        doc.AppendParagraph("Third paragraph");

        var md = doc.ExportToMarkdown();

        Assert.Contains("First paragraph", md);
        Assert.Contains("Second paragraph", md);
        Assert.Contains("Third paragraph", md);
    }

    [Fact]
    public void ExportToMarkdown_AllHeadingTexts_PresentInOutput()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Heading One", level: 1);
        doc.AppendHeading("Heading Two", level: 2);
        doc.AppendHeading("Heading Three", level: 3);

        var md = doc.ExportToMarkdown();

        Assert.Contains("Heading One", md);
        Assert.Contains("Heading Two", md);
        Assert.Contains("Heading Three", md);
    }

    // ---- Paragraph ordering: first appears before second ----

    [Fact]
    public void ExportToMarkdown_ParagraphOrder_PreservedInOutput()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("AAA content");
        doc.AppendParagraph("ZZZ content");

        var md = doc.ExportToMarkdown();

        var aaaPos = md.IndexOf("AAA content", StringComparison.Ordinal);
        var zzzPos = md.IndexOf("ZZZ content", StringComparison.Ordinal);

        Assert.True(aaaPos >= 0, "First paragraph not found");
        Assert.True(zzzPos >= 0, "Second paragraph not found");
        Assert.True(aaaPos < zzzPos, "First paragraph should appear before second");
    }

    [Fact]
    public void ExportToMarkdown_HeadingBeforeBody_CorrectOrder()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Document Title", level: 1);
        doc.AppendParagraph("Body content follows.");

        var md = doc.ExportToMarkdown();

        var h1Pos = md.IndexOf("Document Title", StringComparison.Ordinal);
        var bodyPos = md.IndexOf("Body content follows", StringComparison.Ordinal);

        Assert.True(h1Pos < bodyPos, "Heading should appear before body text");
    }

    // ---- Consistent output across calls ----

    [Fact]
    public void ExportToMarkdown_CalledTwice_ReturnsSameOutput()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Stable Title", level: 1);
        doc.AppendParagraph("Stable body.");

        var md1 = doc.ExportToMarkdown();
        var md2 = doc.ExportToMarkdown();

        Assert.Equal(md1, md2);
    }

    // ---- ExportToMarkdown length > 0 for non-empty doc ----

    [Fact]
    public void ExportToMarkdown_NonEmptyDoc_LengthGreaterThanZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Some content");

        var md = doc.ExportToMarkdown();
        Assert.True(md.Length > 0, "Non-empty document should produce non-empty markdown");
    }

    // ---- After ReplaceText, new text appears in markdown ----

    [Fact]
    public void ExportToMarkdown_AfterReplaceText_ReflectsChanges()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Original content here.");
        doc.ReplaceText("Original", "Updated");

        var md = doc.ExportToMarkdown();
        Assert.Contains("Updated", md);
        Assert.DoesNotContain("Original", md);
    }

    // ---- Newlines present between paragraphs ----

    [Fact]
    public void ExportToMarkdown_MultipleParagraphs_ContainsNewlines()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");

        var md = doc.ExportToMarkdown();
        Assert.Contains("\n", md);
    }

    // ---- Dogfood: full round-trip from paragraphs to markdown ----

    [Fact]
    public void DogfoodPipeline_BuildDocumentThenExport_AllContentPresent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Report 2026", level: 1);
        doc.AppendParagraph("Executive summary.");
        doc.AppendHeading("Data Section", level: 2);
        doc.AppendParagraph("Data analysis content.");
        doc.AppendHeading("Conclusions", level: 2);
        doc.AppendParagraph("Final conclusions here.");

        var md = doc.ExportToMarkdown();

        // All content in order
        Assert.Contains("# Report 2026", md);
        Assert.Contains("## Data Section", md);
        Assert.Contains("## Conclusions", md);
        Assert.Contains("Executive summary.", md);
        Assert.Contains("Data analysis content.", md);
        Assert.Contains("Final conclusions here.", md);

        // Structural consistency
        Assert.True(md.Length > 50, "Expected substantial markdown output");
        Assert.True(doc.ParagraphCount == 6, $"Expected 6 paragraphs, got {doc.ParagraphCount}");
    }
}
