// R110 Wave 4: FODT InsertHeading tests
// Ledger: R110-GOVERNED-DOTNET-FODT-INSERTHEADING-001

using System;
using System.IO;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR110InsertHeadingTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    [Fact]
    public void InsertHeading_AtStart_CreatesHeading()
    {
        var doc = FodtDocument.Load(MinimalPath);
        int before = doc.GetParagraphCount();
        var heading = doc.InsertHeading(0, "Test Heading R110", 1);
        Assert.NotNull(heading);
        Assert.True(heading.IsHeading);
        Assert.Equal("Test Heading R110", heading.Text);
        Assert.Equal(before + 1, doc.GetParagraphCount());
    }

    [Fact]
    public void InsertHeading_AtEnd_AppendsHeading()
    {
        var doc = FodtDocument.Load(MinimalPath);
        int count = doc.GetParagraphCount();
        doc.InsertHeading(count, "End Heading R110", 2);
        Assert.Equal(count + 1, doc.GetParagraphCount());
        var last = doc.GetParagraphText(doc.GetParagraphCount() - 1);
        Assert.Equal("End Heading R110", last);
    }

    [Fact]
    public void InsertHeading_Level3_HasCorrectLevel()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var heading = doc.InsertHeading(0, "Level 3 Heading", 3);
        Assert.True(heading.IsHeading);
        Assert.Equal(3, heading.OutlineLevel);
    }

    [Fact]
    public void InsertHeading_AllLevels_1Through6()
    {
        var doc = FodtDocument.Load(MinimalPath);
        for (int level = 1; level <= 6; level++)
        {
            var h = doc.InsertHeading(0, $"Level {level}", level);
            Assert.True(h.IsHeading);
            Assert.Equal(level, h.OutlineLevel);
        }
    }

    [Fact]
    public void InsertHeading_Level0_Throws()
    {
        var doc = FodtDocument.Load(MinimalPath);
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            doc.InsertHeading(0, "Bad Level", 0));
    }

    [Fact]
    public void InsertHeading_Level7_Throws()
    {
        var doc = FodtDocument.Load(MinimalPath);
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            doc.InsertHeading(0, "Bad Level", 7));
    }

    [Fact]
    public void InsertHeading_NegativeIndex_Throws()
    {
        var doc = FodtDocument.Load(MinimalPath);
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            doc.InsertHeading(-1, "Bad", 1));
    }

    [Fact]
    public void InsertHeading_IndexBeyondCount_Throws()
    {
        var doc = FodtDocument.Load(MinimalPath);
        int count = doc.GetParagraphCount();
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            doc.InsertHeading(count + 1, "Bad", 1));
    }

    [Fact]
    public void InsertHeading_IncrementsHeadingCount()
    {
        var doc = FodtDocument.Load(MinimalPath);
        int headingsBefore = doc.GetHeadingCount();
        doc.InsertHeading(0, "New Heading R110", 1);
        Assert.Equal(headingsBefore + 1, doc.GetHeadingCount());
    }

    [Fact]
    public void InsertHeading_AppearsInExportToHtml()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.InsertHeading(0, "HTML Heading R110", 2);
        var html = doc.ExportToHtml();
        Assert.Contains("<h2>HTML Heading R110</h2>", html);
    }
}
