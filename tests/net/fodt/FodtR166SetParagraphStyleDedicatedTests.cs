// Tests for FodtDocument.SetParagraphStyle dedicated coverage.
// Sprint: ff-sprint-s157-dotnet-deepening-20260628
// Ledger: PC-FODT-R166

using System;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R166: Dedicated tests for FodtDocument.SetParagraphStyle(int index, string styleName).
/// SetParagraphStyle assigns a named style to the paragraph at the given zero-based index.
/// Throws ArgumentNullException if styleName is null.
/// Throws ArgumentOutOfRangeException for negative index or index >= ParagraphCount.
/// Covers: null styleName throws ArgumentNullException; negative index throws ArgumentOutOfRangeException;
/// index at ParagraphCount throws ArgumentOutOfRangeException; index beyond count throws;
/// valid call does not throw; paragraph count unchanged after set;
/// paragraph text unchanged after set; dogfood AppendParagraph->SetParagraphStyle pipeline;
/// dogfood set style on multiple paragraphs; dogfood empty style name does not throw.
/// </summary>
public class FodtR166SetParagraphStyleDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetParagraphStyle_NullStyleName_ThrowsArgumentNullException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Test");
        Assert.Throws<ArgumentNullException>(() => doc.SetParagraphStyle(0, null!));
    }

    [Fact]
    public void SetParagraphStyle_NegativeIndex_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Test");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SetParagraphStyle(-1, "BoldStyle"));
    }

    [Fact]
    public void SetParagraphStyle_IndexAtParagraphCount_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Only paragraph");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SetParagraphStyle(1, "BoldStyle"));
    }

    [Fact]
    public void SetParagraphStyle_IndexBeyondCount_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para 0");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SetParagraphStyle(10, "BoldStyle"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetParagraphStyle_ValidCall_DoesNotThrow()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Styled paragraph");
        // Should not throw
        doc.SetParagraphStyle(0, "Heading1");
        Assert.Equal(1, doc.ParagraphCount);
    }

    [Fact]
    public void SetParagraphStyle_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para 0");
        doc.AppendParagraph("Para 1");
        var before = doc.ParagraphCount;
        doc.SetParagraphStyle(0, "CustomStyle");
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void SetParagraphStyle_ParagraphTextUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Important text");
        doc.SetParagraphStyle(0, "Important");
        Assert.Equal("Important text", doc.GetParagraphText(0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AppendParagraph_SetParagraphStyle()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Content");
        doc.SetParagraphStyle(0, "BodyText");
        // After styling, paragraph still accessible
        Assert.Equal(1, doc.ParagraphCount);
        Assert.Equal("Content", doc.GetParagraphText(0));
    }

    [Fact]
    public void DogfoodPipeline_SetStyle_OnMultipleParagraphs()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para A");
        doc.AppendParagraph("Para B");
        doc.AppendParagraph("Para C");
        doc.SetParagraphStyle(0, "StyleA");
        doc.SetParagraphStyle(1, "StyleB");
        doc.SetParagraphStyle(2, "StyleC");
        // All should work without throwing
        Assert.Equal(3, doc.ParagraphCount);
    }

    [Fact]
    public void DogfoodPipeline_EmptyStyleName_DoesNotThrow()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para");
        // Empty string is a valid (though unusual) style name
        doc.SetParagraphStyle(0, string.Empty);
        Assert.Equal(1, doc.ParagraphCount);
    }
}
