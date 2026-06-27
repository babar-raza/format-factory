// Tests for FodtDocument.GetParagraphSpacing dedicated coverage.
// Sprint: ff-sprint-s374-dotnet-deepening-20260630
// Ledger: PC-FODT-R392

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R392: Dedicated tests for FodtDocument.GetParagraphSpacing().
/// Negative index throws.
/// Out-of-range index throws.
/// Empty document throws.
/// Valid index returns non-negative.
/// ParagraphCount unchanged after GetParagraphSpacing.
/// TableCount unchanged after GetParagraphSpacing.
/// Idempotent (called twice same result).
/// Dogfood: SetSpacing 1.5 then Get=1.5.
/// Dogfood: multiple paragraphs each returns non-negative.
/// </summary>
public class FodtR392GetParagraphSpacingDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphSpacing_NegativeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello");
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphSpacing(-1));
    }

    [Fact]
    public void GetParagraphSpacing_OutOfRangeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello");
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphSpacing(doc.ParagraphCount));
    }

    [Fact]
    public void GetParagraphSpacing_EmptyDocument_Throws()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphSpacing(0));
    }

    [Fact]
    public void GetParagraphSpacing_ValidIndex_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Paragraph A");
        double spacing = doc.GetParagraphSpacing(0);
        Assert.True(spacing >= 0.0);
    }

    [Fact]
    public void GetParagraphSpacing_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.ParagraphCount;
        _ = doc.GetParagraphSpacing(0);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetParagraphSpacing_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.TableCount;
        _ = doc.GetParagraphSpacing(0);
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetParagraphSpacing_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Stable text");
        double first = doc.GetParagraphSpacing(0);
        double second = doc.GetParagraphSpacing(0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetSpacingThenGet_ReturnsSpacing()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Spaced paragraph");
        doc.SetParagraphSpacing(0, 1.5);
        double spacing = doc.GetParagraphSpacing(0);
        Assert.Equal(1.5, spacing, 6);
    }

    [Fact]
    public void DogfoodPipeline_MultipleParagraphs_EachNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Introduction");
        doc.AddParagraph("Body");
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetParagraphSpacing(0) >= 0.0);
        Assert.True(doc.GetParagraphSpacing(1) >= 0.0);
        Assert.True(doc.GetParagraphSpacing(2) >= 0.0);
    }
}
