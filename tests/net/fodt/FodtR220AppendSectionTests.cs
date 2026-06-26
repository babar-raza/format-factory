// Tests for FodtDocument.AppendSection dedicated coverage.
// Sprint: ff-sprint-s205-dotnet-deepening-20260629
// Ledger: PC-FODT-R220

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R220: Dedicated tests for FodtDocument.AppendSection(string sectionName).
/// null sectionName → ArgumentNullException.
/// Valid: no exception.
/// ParagraphCount unchanged after append section (sections are structural, not paragraphs).
/// Section count increases after each append.
/// Unique section names accepted.
/// GetSectionNames contains appended section.
/// Append multiple sections: all present.
/// Empty string section name: may or may not be valid (implementation-dependent).
/// Dogfood: append section then add paragraph, counts correct.
/// Dogfood: append multiple sections, verify each name present.
/// </summary>
public class FodtR220AppendSectionTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AppendSection_NullSectionName_ThrowsArgumentNullException()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Throws<ArgumentNullException>(() => doc.AppendSection(null!));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AppendSection_ValidName_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.AppendSection("Section1"));
        Assert.Null(ex);
    }

    [Fact]
    public void AppendSection_SectionCountIncreases()
    {
        var doc = FodtDocument.CreateEmpty();
        int before = doc.SectionCount;
        doc.AppendSection("NewSection");
        Assert.Equal(before + 1, doc.SectionCount);
    }

    [Fact]
    public void AppendSection_GetSectionNames_ContainsName()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendSection("MySect");
        Assert.Contains("MySect", doc.GetSectionNames());
    }

    [Fact]
    public void AppendSection_MultipleSections_AllPresent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendSection("Alpha");
        doc.AppendSection("Beta");
        doc.AppendSection("Gamma");
        var names = doc.GetSectionNames();
        Assert.Contains("Alpha", names);
        Assert.Contains("Beta", names);
        Assert.Contains("Gamma", names);
    }

    [Fact]
    public void AppendSection_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Existing");
        int paraBefore = doc.ParagraphCount;
        doc.AppendSection("S");
        Assert.Equal(paraBefore, doc.ParagraphCount);
    }

    [Fact]
    public void AppendSection_SectionCountIsNonNegative()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.True(doc.SectionCount >= 0);
    }

    [Fact]
    public void AppendSection_UniqueNames_AllCounted()
    {
        var doc = FodtDocument.CreateEmpty();
        int before = doc.SectionCount;
        doc.AppendSection("S1");
        doc.AppendSection("S2");
        Assert.Equal(before + 2, doc.SectionCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AppendSectionThenParagraph_CountsCorrect()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendSection("Intro");
        doc.AppendParagraph("First para");
        Assert.Equal(1, doc.ParagraphCount);
        Assert.Contains("Intro", doc.GetSectionNames());
    }

    [Fact]
    public void DogfoodPipeline_MultipleSectionsVerifyNames()
    {
        var doc = FodtDocument.CreateEmpty();
        string[] sections = { "Introduction", "Methods", "Results", "Conclusion" };
        foreach (var s in sections)
            doc.AppendSection(s);
        var names = doc.GetSectionNames();
        foreach (var s in sections)
            Assert.Contains(s, names);
    }
}
