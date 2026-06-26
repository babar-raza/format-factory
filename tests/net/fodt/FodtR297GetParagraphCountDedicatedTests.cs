// Tests for FodtDocument.GetParagraphCount dedicated coverage.
// Sprint: ff-sprint-s282-dotnet-deepening-20260630
// Ledger: PC-FODT-R297

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R297: Dedicated tests for FodtDocument.GetParagraphCount() / ParagraphCount property.
/// Returns non-negative int.
/// Increases after AddParagraph.
/// SectionCount unchanged after accessing ParagraphCount.
/// TableCount unchanged after accessing ParagraphCount.
/// Called twice returns same result.
/// Adding two paragraphs increases count by at least 2.
/// New document count at least zero.
/// Dogfood: add paragraph, count increases.
/// Dogfood: multiple paragraphs accumulated correctly.
/// </summary>
public class FodtR297GetParagraphCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ParagraphCount_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        Assert.True(doc.ParagraphCount >= 0);
    }

    [Fact]
    public void ParagraphCount_IncreasesAfterAddParagraph()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        doc.AddParagraph("Hello");
        int after = doc.ParagraphCount;
        Assert.True(after > before);
    }

    [Fact]
    public void ParagraphCount_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int secBefore = doc.GetSectionCount();
        _ = doc.ParagraphCount;
        Assert.Equal(secBefore, doc.GetSectionCount());
    }

    [Fact]
    public void ParagraphCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int tableBefore = doc.TableCount;
        _ = doc.ParagraphCount;
        Assert.Equal(tableBefore, doc.TableCount);
    }

    [Fact]
    public void ParagraphCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para");
        int first = doc.ParagraphCount;
        int second = doc.ParagraphCount;
        Assert.Equal(first, second);
    }

    [Fact]
    public void ParagraphCount_AddTwoParagraphs_IncreasedByAtLeastTwo()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        doc.AddParagraph("Para1");
        doc.AddParagraph("Para2");
        int after = doc.ParagraphCount;
        Assert.True(after >= before + 2);
    }

    [Fact]
    public void ParagraphCount_NewDocument_AtLeastZero()
    {
        var doc = FodtDocument.CreateNew();
        Assert.True(doc.ParagraphCount >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddParagraph_CountIncreases()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        doc.AddParagraph("Introduction paragraph.");
        Assert.True(doc.ParagraphCount > before);
    }

    [Fact]
    public void DogfoodPipeline_MultipleParagraphs_AccumulatedCorrectly()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        doc.AddParagraph("First.");
        doc.AddParagraph("Second.");
        doc.AddParagraph("Third.");
        Assert.True(doc.ParagraphCount >= before + 3);
    }
}
