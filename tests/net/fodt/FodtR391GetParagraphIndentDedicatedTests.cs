// Tests for FodtDocument.GetParagraphIndent dedicated coverage.
// Sprint: ff-sprint-s373-dotnet-deepening-20260630
// Ledger: PC-FODT-R391

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R391: Dedicated tests for FodtDocument.GetParagraphIndent().
/// Negative index throws.
/// Out-of-range index throws.
/// Empty document throws.
/// Valid index returns non-negative.
/// ParagraphCount unchanged after GetParagraphIndent.
/// TableCount unchanged after GetParagraphIndent.
/// Idempotent (called twice same result).
/// Dogfood: SetIndent 2.0cm then Get=2.0.
/// Dogfood: multiple paragraphs each returns non-negative.
/// </summary>
public class FodtR391GetParagraphIndentDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphIndent_NegativeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello");
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphIndent(-1));
    }

    [Fact]
    public void GetParagraphIndent_OutOfRangeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello");
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphIndent(doc.ParagraphCount));
    }

    [Fact]
    public void GetParagraphIndent_EmptyDocument_Throws()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphIndent(0));
    }

    [Fact]
    public void GetParagraphIndent_ValidIndex_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Paragraph A");
        double indent = doc.GetParagraphIndent(0);
        Assert.True(indent >= 0.0);
    }

    [Fact]
    public void GetParagraphIndent_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.ParagraphCount;
        _ = doc.GetParagraphIndent(0);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetParagraphIndent_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.TableCount;
        _ = doc.GetParagraphIndent(0);
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetParagraphIndent_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Stable text");
        double first = doc.GetParagraphIndent(0);
        double second = doc.GetParagraphIndent(0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetIndentThenGet_ReturnsIndent()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Indented paragraph");
        doc.SetParagraphIndent(0, 2.0);
        double indent = doc.GetParagraphIndent(0);
        Assert.Equal(2.0, indent, 6);
    }

    [Fact]
    public void DogfoodPipeline_MultipleParagraphs_EachNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Introduction");
        doc.AddParagraph("Body");
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetParagraphIndent(0) >= 0.0);
        Assert.True(doc.GetParagraphIndent(1) >= 0.0);
        Assert.True(doc.GetParagraphIndent(2) >= 0.0);
    }
}
