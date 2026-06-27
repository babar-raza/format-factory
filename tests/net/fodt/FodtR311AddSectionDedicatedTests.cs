// Tests for FodtDocument.AddSection dedicated coverage.
// Sprint: ff-sprint-s296-dotnet-deepening-20260630
// Ledger: PC-FODT-R311

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R311: Dedicated tests for FodtDocument.AddSection(name).
/// Valid call no exception.
/// Section count increases after AddSection.
/// ParagraphCount unchanged after AddSection.
/// TableCount unchanged after AddSection.
/// Called twice no exception.
/// Added section with empty string no exception.
/// Section count increases after each AddSection.
/// Dogfood: add multiple sections, count matches.
/// Dogfood: add section with name, GetSectionCount reflects addition.
/// </summary>
public class FodtR311AddSectionDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AddSection_ValidCall_NoException()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.AddSection("Introduction"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddSection_SectionCountIncreases()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.GetSectionCount();
        doc.AddSection("Introduction");
        int after = doc.GetSectionCount();
        Assert.True(after > before);
    }

    [Fact]
    public void AddSection_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int paraBefore = doc.ParagraphCount;
        doc.AddSection("Section1");
        Assert.Equal(paraBefore, doc.ParagraphCount);
    }

    [Fact]
    public void AddSection_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int tableBefore = doc.TableCount;
        doc.AddSection("Section1");
        Assert.Equal(tableBefore, doc.TableCount);
    }

    [Fact]
    public void AddSection_CalledTwice_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("First");
        var ex = Record.Exception(() => doc.AddSection("Second"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddSection_EmptyName_NoException()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.AddSection(string.Empty));
        Assert.Null(ex);
    }

    [Fact]
    public void AddSection_EachCall_IncreasesCount()
    {
        var doc = FodtDocument.CreateNew();
        int count0 = doc.GetSectionCount();
        doc.AddSection("S1");
        int count1 = doc.GetSectionCount();
        doc.AddSection("S2");
        int count2 = doc.GetSectionCount();
        Assert.True(count1 > count0);
        Assert.True(count2 > count1);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddMultipleSections_CountMatches()
    {
        var doc = FodtDocument.CreateNew();
        int initial = doc.GetSectionCount();
        doc.AddSection("Chapter1");
        doc.AddSection("Chapter2");
        doc.AddSection("Chapter3");
        int final = doc.GetSectionCount();
        Assert.Equal(initial + 3, final);
    }

    [Fact]
    public void DogfoodPipeline_AddSectionWithName_GetSectionCountReflects()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.GetSectionCount();
        doc.AddSection("Appendix");
        Assert.Equal(before + 1, doc.GetSectionCount());
    }
}
