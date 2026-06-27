// Tests for FodtDocument.GetParagraphAlignment dedicated coverage.
// Sprint: ff-sprint-s349-dotnet-deepening-20260630
// Ledger: PC-FODT-R367

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R367: Dedicated tests for FodtDocument.GetParagraphAlignment().
/// Negative paragraph index throws.
/// Out-of-range paragraph index throws.
/// Empty document throws.
/// Valid paragraph returns non-null.
/// ParagraphCount unchanged after GetParagraphAlignment.
/// TableCount unchanged after GetParagraphAlignment.
/// Idempotent (called twice same result).
/// After SetParagraphAlignment returns expected value.
/// Dogfood: multiple paragraphs with different alignments.
/// </summary>
public class FodtR367GetParagraphAlignmentDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphAlignment_NegativeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Content");
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphAlignment(-1));
    }

    [Fact]
    public void GetParagraphAlignment_OutOfRangeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Content");
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphAlignment(99));
    }

    [Fact]
    public void GetParagraphAlignment_EmptyDocument_Throws()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphAlignment(0));
    }

    [Fact]
    public void GetParagraphAlignment_ValidParagraph_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Sample text");
        string? alignment = doc.GetParagraphAlignment(0);
        Assert.NotNull(alignment);
    }

    [Fact]
    public void GetParagraphAlignment_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Fixed paragraph");
        int before = doc.ParagraphCount;
        _ = doc.GetParagraphAlignment(0);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetParagraphAlignment_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Fixed paragraph");
        int before = doc.TableCount;
        _ = doc.GetParagraphAlignment(0);
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetParagraphAlignment_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Stable paragraph");
        string? first = doc.GetParagraphAlignment(0);
        string? second = doc.GetParagraphAlignment(0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetParagraphAlignment_AfterSetAlignment_ReturnsExpected()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Center aligned paragraph");
        doc.SetParagraphAlignment(0, "center");
        string? alignment = doc.GetParagraphAlignment(0);
        Assert.NotNull(alignment);
        Assert.Equal("center", alignment);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultipleParagraphs_DifferentAlignments()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Left paragraph");
        doc.AddParagraph("Center paragraph");
        doc.AddParagraph("Right paragraph");
        doc.SetParagraphAlignment(0, "left");
        doc.SetParagraphAlignment(1, "center");
        doc.SetParagraphAlignment(2, "right");
        Assert.NotNull(doc.GetParagraphAlignment(0));
        Assert.NotNull(doc.GetParagraphAlignment(1));
        Assert.NotNull(doc.GetParagraphAlignment(2));
    }
}
