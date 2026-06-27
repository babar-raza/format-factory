// Tests for FodtDocument.GetParagraphAlignment dedicated coverage.
// Sprint: ff-sprint-s372-dotnet-deepening-20260630
// Ledger: PC-FODT-R390

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R390: Dedicated tests for FodtDocument.GetParagraphAlignment().
/// Negative index throws.
/// Out-of-range index throws.
/// Empty document throws.
/// Valid index returns non-null.
/// ParagraphCount unchanged after GetParagraphAlignment.
/// TableCount unchanged after GetParagraphAlignment.
/// Idempotent (called twice same result).
/// Dogfood: SetAlignment left+Get.
/// Dogfood: multiple paragraphs each returns non-null.
/// </summary>
public class FodtR390GetParagraphAlignmentDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphAlignment_NegativeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello");
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphAlignment(-1));
    }

    [Fact]
    public void GetParagraphAlignment_OutOfRangeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello");
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphAlignment(doc.ParagraphCount));
    }

    [Fact]
    public void GetParagraphAlignment_EmptyDocument_Throws()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphAlignment(0));
    }

    [Fact]
    public void GetParagraphAlignment_ValidIndex_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Paragraph A");
        string alignment = doc.GetParagraphAlignment(0);
        Assert.NotNull(alignment);
    }

    [Fact]
    public void GetParagraphAlignment_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.ParagraphCount;
        _ = doc.GetParagraphAlignment(0);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetParagraphAlignment_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.TableCount;
        _ = doc.GetParagraphAlignment(0);
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetParagraphAlignment_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Stable text");
        string first = doc.GetParagraphAlignment(0);
        string second = doc.GetParagraphAlignment(0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetAlignmentLeftThenGet()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Summary text");
        doc.SetParagraphAlignment(0, "left");
        string alignment = doc.GetParagraphAlignment(0);
        Assert.Equal("left", alignment);
    }

    [Fact]
    public void DogfoodPipeline_MultipleParagraphs_EachNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Introduction");
        doc.AddParagraph("Body");
        doc.AddParagraph("Conclusion");
        Assert.NotNull(doc.GetParagraphAlignment(0));
        Assert.NotNull(doc.GetParagraphAlignment(1));
        Assert.NotNull(doc.GetParagraphAlignment(2));
    }
}
