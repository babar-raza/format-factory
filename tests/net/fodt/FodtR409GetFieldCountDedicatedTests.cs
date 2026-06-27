// Tests for FodtDocument.GetFieldCount dedicated coverage.
// Sprint: ff-sprint-s391-dotnet-deepening-20260630
// Ledger: PC-FODT-R409

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R409: Dedicated tests for FodtDocument.FieldCount (or GetFieldCount()).
/// New document returns non-negative.
/// ParagraphCount unchanged after checking FieldCount.
/// TableCount unchanged after checking FieldCount.
/// TextFrameCount unchanged after checking FieldCount.
/// Idempotent (read twice same result).
/// Is integer type.
/// Dogfood: FieldCount non-negative after paragraphs.
/// Dogfood: FieldCount non-negative after mixed content.
/// Dogfood: FieldCount never negative in loop.
/// </summary>
public class FodtR409GetFieldCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FieldCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        Assert.True(doc.FieldCount >= 0);
    }

    [Fact]
    public void FieldCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.ParagraphCount;
        _ = doc.FieldCount;
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void FieldCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.TableCount;
        _ = doc.FieldCount;
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void FieldCount_TextFrameCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.TextFrameCount;
        _ = doc.FieldCount;
        Assert.Equal(before, doc.TextFrameCount);
    }

    [Fact]
    public void FieldCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Text");
        int first = doc.FieldCount;
        int second = doc.FieldCount;
        Assert.Equal(first, second);
    }

    [Fact]
    public void FieldCount_IsInteger()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.FieldCount;
        Assert.IsType<int>(count);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterParagraphs_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Field reference A");
        doc.AddParagraph("Field reference B");
        Assert.True(doc.FieldCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Document header");
        doc.AddTable(2, 2);
        doc.AddParagraph("Footer field");
        Assert.True(doc.FieldCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_NeverNegativeInLoop()
    {
        var doc = FodtDocument.CreateNew();
        for (int i = 0; i < 5; i++)
        {
            doc.AddParagraph($"Paragraph with field {i}");
            Assert.True(doc.FieldCount >= 0);
        }
    }
}
