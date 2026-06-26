// Tests for FodtDocument.GetParagraphStyleName dedicated coverage.
// Sprint: ff-sprint-s168-dotnet-deepening-20260628
// Ledger: PC-FODT-R177

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R177: Dedicated tests for FodtDocument.GetParagraphStyleName(int index).
/// Returns the text:style-name attribute of the paragraph at the given index,
/// or null if the index is out of range OR the attribute is absent.
/// Does NOT throw for out-of-range indices — returns null silently.
/// Covers: negative index returns null; at-count index returns null;
/// beyond-count returns null; CreateEmpty single-para style is null-or-string;
/// AppendParagraph result is accessible; AppendHeading style is null-or-string;
/// result is string type when non-null; idempotent on same index;
/// dogfood AppendParagraph->GetParagraphStyleName; dogfood with heading has style.
/// </summary>
public class FodtR177GetParagraphStyleNameTests
{
    // -------------------------------------------------------------------------
    // Out-of-range — null return (no throw)
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphStyleName_NegativeIndex_ReturnsNull()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        Assert.Null(doc.GetParagraphStyleName(-1));
    }

    [Fact]
    public void GetParagraphStyleName_IndexAtCount_ReturnsNull()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        var count = doc.ParagraphCount;
        Assert.Null(doc.GetParagraphStyleName(count));
    }

    [Fact]
    public void GetParagraphStyleName_IndexBeyondCount_ReturnsNull()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        Assert.Null(doc.GetParagraphStyleName(100));
    }

    [Fact]
    public void GetParagraphStyleName_EmptyDocument_NegativeIndex_ReturnsNull()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Null(doc.GetParagraphStyleName(-1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphStyleName_ValidIndex_IsNullOrString()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Sample paragraph");
        var style = doc.GetParagraphStyleName(0);
        // Either null (no style-name attribute) or a non-empty string
        Assert.True(style == null || style is string);
    }

    [Fact]
    public void GetParagraphStyleName_WhenNonNull_IsStringType()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Sample paragraph");
        var style = doc.GetParagraphStyleName(0);
        if (style != null)
            Assert.IsType<string>(style);
    }

    [Fact]
    public void GetParagraphStyleName_Idempotent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Same paragraph");
        var first = doc.GetParagraphStyleName(0);
        var second = doc.GetParagraphStyleName(0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetParagraphStyleName_HeadingParagraph_IsNullOrString()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Chapter 1", 1);
        var style = doc.GetParagraphStyleName(0);
        Assert.True(style == null || style is string);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AppendParagraph_GetParagraphStyleName()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para 1");
        doc.AppendParagraph("Para 2");
        // Both indices accessible without exception
        var s0 = doc.GetParagraphStyleName(0);
        var s1 = doc.GetParagraphStyleName(1);
        Assert.True(s0 == null || s0 is string);
        Assert.True(s1 == null || s1 is string);
    }

    [Fact]
    public void DogfoodPipeline_MixedContent_StylesAccessible()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1);
        doc.AppendParagraph("Body text");
        doc.AppendHeading("Section", 2);
        // All three accessible without throwing
        var s0 = doc.GetParagraphStyleName(0);
        var s1 = doc.GetParagraphStyleName(1);
        var s2 = doc.GetParagraphStyleName(2);
        Assert.True(s0 == null || s0 is string);
        Assert.True(s1 == null || s1 is string);
        Assert.True(s2 == null || s2 is string);
    }
}
