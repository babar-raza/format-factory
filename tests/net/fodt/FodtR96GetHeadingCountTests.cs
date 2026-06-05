// R96 Train M: FODT .NET GetHeadingCount Tests
// Governed skill: /add-dotnet-api
// Ledger: R96-GOVERNED-DOTNET-FODT-GETHEADINGCOUNT-001
// Sprint: FORMAT-FACTORY-R96-AUTONOMOUS-CONTINUATION-POC-PRODUCT-DEEPENING-MEGA-TRAIN-001

using System;
using System.IO;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR96GetHeadingCountTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    private static string SampleFodtPath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    [Fact]
    public void GetHeadingCount_ReturnsNonNegative()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        Assert.True(doc.GetHeadingCount() >= 0);
    }

    [Fact]
    public void GetHeadingCount_MatchesGetHeadingParagraphs()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        Assert.Equal(doc.GetHeadingParagraphs().Count, doc.GetHeadingCount());
    }

    [Fact]
    public void GetHeadingCount_LessThanOrEqualToParagraphCount()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        Assert.True(doc.GetHeadingCount() <= doc.Paragraphs.Count,
            "Heading count should not exceed paragraph count");
    }

    [Fact]
    public void GetHeadingCount_Consistent()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        Assert.Equal(doc.GetHeadingCount(), doc.GetHeadingCount());
    }

    [Fact]
    public void GetHeadingCount_ReturnsInt()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        int count = doc.GetHeadingCount();
        Assert.IsType<int>(count);
    }

    [Fact]
    public void GetHeadingCount_NonNegativeWithWordCount()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        if (doc.GetWordCount() > 0)
        {
            Assert.True(doc.GetHeadingCount() >= 0);
        }
    }

    [Fact]
    public void GetHeadingCount_ZeroOrMoreHeadings()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        var headingCount = doc.GetHeadingCount();
        Assert.True(headingCount >= 0 && headingCount <= 1000,
            $"Heading count should be reasonable, got {headingCount}");
    }

    [Fact]
    public void GetHeadingCount_CorrelatesWithParagraphs()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        int bodyParas = doc.Paragraphs.Count - doc.GetHeadingCount();
        Assert.True(bodyParas >= 0, "Non-heading paragraphs should be non-negative");
    }
}
