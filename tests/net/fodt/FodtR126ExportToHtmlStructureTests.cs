// Tests for FodtDocument.ExportToHtml() structural output.
// Sprint: FORMAT-FACTORY-FODT-EXPORT-HTML-STRUCTURE-20260626
// Ledger: R126-GOVERNED-DOTNET-FODT-EXPORT-HTML-STRUCTURE-001

using System;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R126: FodtDocument.ExportToHtml() — converts paragraphs to HTML. Headings map to
/// &lt;h1&gt;/&lt;h2&gt;/etc., body paragraphs map to &lt;p&gt; tags. Result is a
/// non-null, non-empty string for any document state. Special characters are escaped.
/// </summary>
public class FodtR126ExportToHtmlStructureTests
{
    // ---- Empty document: produces valid non-empty HTML ----

    [Fact]
    public void ExportToHtml_EmptyDoc_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateEmpty();
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
    }

    [Fact]
    public void ExportToHtml_EmptyDoc_ReturnsNonEmptyString()
    {
        var doc = FodtDocument.CreateEmpty();
        var html = doc.ExportToHtml();
        Assert.False(string.IsNullOrWhiteSpace(html),
            "ExportToHtml on empty doc should return valid HTML skeleton, not empty");
    }

    // ---- Body paragraph → <p> ----

    [Fact]
    public void ExportToHtml_BodyParagraph_ProducesPTag()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello World");

        var html = doc.ExportToHtml();
        Assert.Contains("<p>", html, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void ExportToHtml_BodyParagraph_ContentInPTag()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Sample body text");

        var html = doc.ExportToHtml();
        Assert.Contains("Sample body text", html);
    }

    // ---- Heading → <h1> ----

    [Fact]
    public void ExportToHtml_H1Heading_ProducesH1Tag()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Document Title", level: 1);

        var html = doc.ExportToHtml();
        Assert.Contains("<h1>", html, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void ExportToHtml_H1Heading_ContentInH1Tag()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("My Title", level: 1);

        var html = doc.ExportToHtml();
        Assert.Contains("My Title", html);
    }

    // ---- Heading level 2 → <h2> ----

    [Fact]
    public void ExportToHtml_H2Heading_ProducesH2Tag()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Section Header", level: 2);

        var html = doc.ExportToHtml();
        Assert.Contains("<h2>", html, StringComparison.OrdinalIgnoreCase);
    }

    // ---- Special characters are escaped ----

    [Fact]
    public void ExportToHtml_AmpersandInParagraph_IsEscaped()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Tom & Jerry");

        var html = doc.ExportToHtml();
        Assert.Contains("&amp;", html);
        Assert.DoesNotContain(" & ", html);
    }

    [Fact]
    public void ExportToHtml_AngleBracketsInParagraph_AreEscaped()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("<bold>");

        var html = doc.ExportToHtml();
        Assert.Contains("&lt;", html);
        Assert.DoesNotContain("<bold>", html);
    }

    // ---- Dogfood: mixed heading+body pipeline ----

    [Fact]
    public void DogfoodPipeline_HeadingAndBody_CorrectStructure()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Report Title", level: 1);
        doc.AppendParagraph("Introduction paragraph.");
        doc.AppendHeading("Section One", level: 2);
        doc.AppendParagraph("Section body content.");

        var html = doc.ExportToHtml();

        // All structural elements present
        Assert.Contains("<h1>", html, StringComparison.OrdinalIgnoreCase);
        Assert.Contains("<h2>", html, StringComparison.OrdinalIgnoreCase);
        Assert.Contains("<p>", html, StringComparison.OrdinalIgnoreCase);
        // All content present
        Assert.Contains("Report Title", html);
        Assert.Contains("Introduction paragraph.", html);
        Assert.Contains("Section One", html);
        Assert.Contains("Section body content.", html);
    }
}
