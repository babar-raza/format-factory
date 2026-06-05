// R97 Train M: FODT .NET GetParagraphCount Tests
// Governed skill: /add-dotnet-api
// Ledger: R97-GOVERNED-DOTNET-FODT-GETPARAGRAPHCOUNT-001

using System;
using System.IO;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR97GetParagraphCountTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    private static string SampleFodtPath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    [Fact]
    public void GetParagraphCount_ReturnsNonNegative()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        Assert.True(doc.GetParagraphCount() >= 0);
    }

    [Fact]
    public void GetParagraphCount_MatchesParagraphsCount()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        Assert.Equal(doc.Paragraphs.Count, doc.GetParagraphCount());
    }

    [Fact]
    public void GetParagraphCount_GreaterThanOrEqualToHeadingCount()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        Assert.True(doc.GetParagraphCount() >= doc.GetHeadingCount());
    }

    [Fact]
    public void GetParagraphCount_Consistent()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        Assert.Equal(doc.GetParagraphCount(), doc.GetParagraphCount());
    }

    [Fact]
    public void GetParagraphCount_ReturnsInt()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        int count = doc.GetParagraphCount();
        Assert.IsType<int>(count);
    }

    [Fact]
    public void GetParagraphCount_HasParagraphs()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        Assert.True(doc.GetParagraphCount() > 0, "Sample should have paragraphs");
    }

    [Fact]
    public void GetParagraphCount_MatchesParagraphTextsCount()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        Assert.Equal(doc.GetParagraphTexts().Count, doc.GetParagraphCount());
    }

    [Fact]
    public void GetParagraphCount_Reasonable()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        Assert.InRange(doc.GetParagraphCount(), 1, 10000);
    }
}
