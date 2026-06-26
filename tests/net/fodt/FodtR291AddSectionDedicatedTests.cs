// Tests for FodtDocument.AddSection dedicated coverage.
// Sprint: ff-sprint-s276-dotnet-deepening-20260630
// Ledger: PC-FODT-R291

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R291: Dedicated tests for FodtDocument.AddSection(sectionName).
/// Valid section name no exception.
/// Empty string no exception.
/// SectionCount increases after AddSection (or non-negative result).
/// TableCount unchanged after AddSection.
/// ParagraphCount unchanged after AddSection.
/// Called twice SectionCount increases by 2 (or stays non-negative).
/// Dogfood: add section then add paragraph no exception.
/// Dogfood: add multiple sections no exception.
/// </summary>
public class FodtR291AddSectionDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AddSection_ValidName_NoException()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.AddSection("Introduction"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddSection_EmptyName_NoException()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.AddSection(""));
        Assert.Null(ex);
    }

    [Fact]
    public void AddSection_SectionCountNonNegativeAfter()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Section1");
        Assert.True(doc.GetSectionCount() >= 0);
    }

    [Fact]
    public void AddSection_SectionCountIncreases()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.GetSectionCount();
        doc.AddSection("NewSection");
        Assert.True(doc.GetSectionCount() > before);
    }

    [Fact]
    public void AddSection_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int tablesBefore = doc.TableCount;
        doc.AddSection("Intro");
        Assert.Equal(tablesBefore, doc.TableCount);
    }

    [Fact]
    public void AddSection_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int paraBefore = doc.ParagraphCount;
        doc.AddSection("Body");
        Assert.Equal(paraBefore, doc.ParagraphCount);
    }

    [Fact]
    public void AddSection_CalledTwice_SectionCountIncreases()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.GetSectionCount();
        doc.AddSection("Sec1");
        doc.AddSection("Sec2");
        Assert.True(doc.GetSectionCount() >= before + 2);
    }

    [Fact]
    public void AddSection_LongName_NoException()
    {
        var doc = FodtDocument.CreateNew();
        string longName = new string('A', 200);
        var ex = Record.Exception(() => doc.AddSection(longName));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddSectionThenParagraph_NoException()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() =>
        {
            doc.AddSection("Chapter 1");
            doc.AddParagraph("The first chapter content.");
        });
        Assert.Null(ex);
    }

    [Fact]
    public void DogfoodPipeline_AddMultipleSections_NoException()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() =>
        {
            doc.AddSection("Chapter 1");
            doc.AddSection("Chapter 2");
            doc.AddSection("Chapter 3");
        });
        Assert.Null(ex);
        Assert.True(doc.GetSectionCount() >= 3);
    }
}
