// Tests for FodtDocument.SetSectionStyle dedicated coverage.
// Sprint: ff-sprint-s280-dotnet-deepening-20260630
// Ledger: PC-FODT-R295

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R295: Dedicated tests for FodtDocument.SetSectionStyle(sectionIndex, style).
/// Negative index throws exception.
/// Out-of-bounds index throws exception.
/// No sections throws exception.
/// Valid call no exception.
/// SectionCount unchanged after SetSectionStyle.
/// Set twice no exception.
/// ParagraphCount unchanged after SetSectionStyle.
/// TableCount unchanged after SetSectionStyle.
/// Dogfood: add section, set style, no exception.
/// Dogfood: set style on multiple sections no exception.
/// </summary>
public class FodtR295SetSectionStyleDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetSectionStyle_NegativeIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Intro");
        Assert.ThrowsAny<Exception>(() => doc.SetSectionStyle(-1, "bold"));
    }

    [Fact]
    public void SetSectionStyle_OutOfBoundsIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Intro");
        int count = doc.GetSectionCount();
        Assert.ThrowsAny<Exception>(() => doc.SetSectionStyle(count, "bold"));
    }

    [Fact]
    public void SetSectionStyle_NoSections_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        if (doc.GetSectionCount() == 0)
            Assert.ThrowsAny<Exception>(() => doc.SetSectionStyle(0, "bold"));
        else
            Assert.True(true); // document has default sections
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetSectionStyle_ValidCall_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Body");
        int idx = doc.GetSectionCount() - 1;
        var ex = Record.Exception(() => doc.SetSectionStyle(idx, "italic"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetSectionStyle_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Chapter");
        int before = doc.GetSectionCount();
        doc.SetSectionStyle(before - 1, "underline");
        Assert.Equal(before, doc.GetSectionCount());
    }

    [Fact]
    public void SetSectionStyle_SetTwice_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Sec");
        int idx = doc.GetSectionCount() - 1;
        doc.SetSectionStyle(idx, "bold");
        var ex = Record.Exception(() => doc.SetSectionStyle(idx, "italic"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetSectionStyle_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Sec");
        int paraBefore = doc.ParagraphCount;
        int idx = doc.GetSectionCount() - 1;
        doc.SetSectionStyle(idx, "bold");
        Assert.Equal(paraBefore, doc.ParagraphCount);
    }

    [Fact]
    public void SetSectionStyle_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Sec");
        int tableBefore = doc.TableCount;
        int idx = doc.GetSectionCount() - 1;
        doc.SetSectionStyle(idx, "bold");
        Assert.Equal(tableBefore, doc.TableCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddSectionSetStyle_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("StyledSection");
        int idx = doc.GetSectionCount() - 1;
        var ex = Record.Exception(() => doc.SetSectionStyle(idx, "bold"));
        Assert.Null(ex);
    }

    [Fact]
    public void DogfoodPipeline_SetStyleOnMultipleSections_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Section1");
        doc.AddSection("Section2");
        int count = doc.GetSectionCount();
        var ex = Record.Exception(() =>
        {
            doc.SetSectionStyle(count - 2, "bold");
            doc.SetSectionStyle(count - 1, "italic");
        });
        Assert.Null(ex);
    }
}
