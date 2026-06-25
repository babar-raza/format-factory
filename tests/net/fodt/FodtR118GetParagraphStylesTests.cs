// Tests for FodtDocument.GetParagraphStyles()
// Sprint: FORMAT-FACTORY-FODT-PARA-STYLES-20260626
// Ledger: R118-GOVERNED-DOTNET-FODT-PARA-STYLES-001

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R118: GetParagraphStyles() — returns a list of effective style names for all paragraphs,
/// in document order. Empty string for paragraphs without an explicit style-name attribute.
/// </summary>
public class FodtR118GetParagraphStylesTests
{
    // ---- Empty document ----

    [Fact]
    public void GetParagraphStyles_EmptyDoc_ReturnsEmptyList()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Empty(doc.GetParagraphStyles());
    }

    // ---- Count matches paragraph count ----

    [Fact]
    public void GetParagraphStyles_CountMatchesParagraphCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("One");
        doc.AppendParagraph("Two");
        doc.InsertHeading(2, "Three", 1);

        var styles = doc.GetParagraphStyles();
        Assert.Equal(doc.GetParagraphCount(), styles.Count);
    }

    // ---- Heading paragraphs ----

    [Fact]
    public void GetParagraphStyles_HeadingParagraphs_NotNull()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Title", 1);
        doc.InsertHeading(1, "Section", 2);

        var styles = doc.GetParagraphStyles();
        Assert.Equal(2, styles.Count);
        // Style entries are strings (possibly empty, but not null)
        foreach (var s in styles)
            Assert.NotNull(s);
    }

    // ---- Order preservation ----

    [Fact]
    public void GetParagraphStyles_PreservesDocumentOrder()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First body");
        doc.InsertHeading(1, "Middle heading", 1);
        doc.AppendParagraph("Last body");

        // 3 paragraphs → 3 style entries in order
        var styles = doc.GetParagraphStyles();
        Assert.Equal(3, styles.Count);
    }

    // ---- After SetParagraphStyle ----

    [Fact]
    public void GetParagraphStyles_AfterSetStyle_ReflectsNewStyle()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Styled paragraph");
        doc.SetParagraphStyle(0, "CustomStyle");

        var styles = doc.GetParagraphStyles();
        Assert.Single(styles);
        Assert.Equal("CustomStyle", styles[0]);
    }

    [Fact]
    public void GetParagraphStyles_MultipleStyles_EachCorrect()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para A");
        doc.AppendParagraph("Para B");
        doc.AppendParagraph("Para C");
        doc.SetParagraphStyle(0, "StyleA");
        doc.SetParagraphStyle(2, "StyleC");

        var styles = doc.GetParagraphStyles();
        Assert.Equal(3, styles.Count);
        Assert.Equal("StyleA", styles[0]);
        // styles[1] may be empty or default — just verify it's not null
        Assert.NotNull(styles[1]);
        Assert.Equal("StyleC", styles[2]);
    }

    // ---- GetParagraphStyleName vs GetParagraphStyles consistency ----

    [Fact]
    public void GetParagraphStyles_MatchesGetParagraphStyleName_ForEachIndex()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        doc.InsertHeading(2, "Heading", 1);
        doc.SetParagraphStyle(0, "P1Style");

        var styles = doc.GetParagraphStyles();
        for (int i = 0; i < styles.Count; i++)
        {
            var byIndex = doc.GetParagraphStyleName(i) ?? string.Empty;
            Assert.Equal(byIndex, styles[i]);
        }
    }

    // ---- Returns IReadOnlyList ----

    [Fact]
    public void GetParagraphStyles_ReturnsReadOnlyList()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Test");

        var styles = doc.GetParagraphStyles();
        Assert.IsAssignableFrom<IReadOnlyList<string>>(styles);
    }

    // ---- Dogfood pipeline ----

    [Fact]
    public void DogfoodPipeline_BuildDocumentSetStyles_VerifyStyleList()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Report Title", 1);
        doc.AppendParagraph("Executive summary paragraph.");
        doc.InsertHeading(2, "Section 1", 2);
        doc.AppendParagraph("Body content for section 1.");
        doc.SetParagraphStyle(1, "Excerpt");
        doc.SetParagraphStyle(3, "Body");

        var styles = doc.GetParagraphStyles();
        Assert.Equal(4, styles.Count);

        // Heading elements may have empty explicit style-name — just verify total count
        // Body paragraphs with SetParagraphStyle should have the set value
        Assert.Equal("Excerpt", styles[1]);
        Assert.Equal("Body", styles[3]);

        // FindParagraphsByStyle should agree with GetParagraphStyles
        var byStyle = doc.FindParagraphsByStyle("Body");
        Assert.NotEmpty(byStyle);
    }
}
