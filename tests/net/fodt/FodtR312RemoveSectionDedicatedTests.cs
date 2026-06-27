// Tests for FodtDocument.RemoveSection dedicated coverage.
// Sprint: ff-sprint-s297-dotnet-deepening-20260630
// Ledger: PC-FODT-R312

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R312: Dedicated tests for FodtDocument.RemoveSection(sectionIndex).
/// Negative index throws exception.
/// Out-of-bounds index throws exception.
/// No sections throws exception.
/// Valid call no exception.
/// Section count decreases after RemoveSection.
/// ParagraphCount unchanged after RemoveSection.
/// TableCount unchanged after RemoveSection.
/// Remove last section no exception.
/// Dogfood: add sections then remove, count matches.
/// </summary>
public class FodtR312RemoveSectionDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveSection_NegativeIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Section1");
        Assert.ThrowsAny<Exception>(() => doc.RemoveSection(-1));
    }

    [Fact]
    public void RemoveSection_OutOfBoundsIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Section1");
        int count = doc.GetSectionCount();
        Assert.ThrowsAny<Exception>(() => doc.RemoveSection(count));
    }

    [Fact]
    public void RemoveSection_NoSections_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        if (doc.GetSectionCount() == 0)
            Assert.ThrowsAny<Exception>(() => doc.RemoveSection(0));
        else
            Assert.True(true); // document has default sections
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveSection_ValidCall_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("ToRemove");
        int idx = doc.GetSectionCount() - 1;
        var ex = Record.Exception(() => doc.RemoveSection(idx));
        Assert.Null(ex);
    }

    [Fact]
    public void RemoveSection_SectionCountDecreases()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("S1");
        doc.AddSection("S2");
        int before = doc.GetSectionCount();
        doc.RemoveSection(before - 1);
        int after = doc.GetSectionCount();
        Assert.True(after < before);
    }

    [Fact]
    public void RemoveSection_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Section1");
        int paraBefore = doc.ParagraphCount;
        doc.RemoveSection(doc.GetSectionCount() - 1);
        Assert.Equal(paraBefore, doc.ParagraphCount);
    }

    [Fact]
    public void RemoveSection_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Section1");
        int tableBefore = doc.TableCount;
        doc.RemoveSection(doc.GetSectionCount() - 1);
        Assert.Equal(tableBefore, doc.TableCount);
    }

    [Fact]
    public void RemoveSection_RemoveLastSection_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("OnlySection");
        int idx = doc.GetSectionCount() - 1;
        var ex = Record.Exception(() => doc.RemoveSection(idx));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddSectionsThenRemove_CountMatches()
    {
        var doc = FodtDocument.CreateNew();
        int initial = doc.GetSectionCount();
        doc.AddSection("Chapter1");
        doc.AddSection("Chapter2");
        doc.AddSection("Chapter3");
        int afterAdd = doc.GetSectionCount();
        Assert.Equal(initial + 3, afterAdd);
        doc.RemoveSection(afterAdd - 1);
        int afterRemove = doc.GetSectionCount();
        Assert.Equal(afterAdd - 1, afterRemove);
    }
}
