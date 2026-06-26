// Tests for FodtDocument.MaxFileSizeBytes and FodtDocument.GetHeadingTexts.
// Sprint: ff-sprint-s140-dotnet-deepening-20260627
// Ledger: PC-FODT-R153

using System;
using System.Linq;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R153: Tests for FodtDocument.MaxFileSizeBytes and FodtDocument.GetHeadingTexts.
/// MaxFileSizeBytes is an init-only property defaulting to 50 MB (52,428,800 bytes).
/// GetHeadingTexts returns the text of all heading paragraphs in insertion order.
/// Covers: MaxFileSizeBytes default is 50 MB; MaxFileSizeBytes is positive; can be overridden;
/// overridden value is stored; GetHeadingTexts empty doc returns empty collection;
/// single heading returns one entry; multiple headings returns all; non-headings excluded;
/// mixed headings and paragraphs returns headings only;
/// dogfood AppendHeading×2+AppendParagraph->GetHeadingTexts contains heading texts only.
/// </summary>
public class FodtR153MaxFileSizeBytesAndHeadingTextsTests
{
    // -------------------------------------------------------------------------
    // MaxFileSizeBytes tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FodtDocument_MaxFileSizeBytes_DefaultIs50MB()
    {
        var parser = new FodtParser();
        const long expected = 50L * 1024 * 1024;
        Assert.Equal(expected, parser.MaxFileSizeBytes);
    }

    [Fact]
    public void FodtDocument_MaxFileSizeBytes_IsPositive()
    {
        var parser = new FodtParser();
        Assert.True(parser.MaxFileSizeBytes > 0);
    }

    [Fact]
    public void FodtDocument_MaxFileSizeBytes_CanBeOverridden()
    {
        const long custom = 10L * 1024 * 1024;
        var parser = new FodtParser { MaxFileSizeBytes = custom };
        Assert.Equal(custom, parser.MaxFileSizeBytes);
    }

    [Fact]
    public void FodtDocument_MaxFileSizeBytes_OverriddenValueIsStored()
    {
        const long custom = 100L * 1024 * 1024;
        var parser = new FodtParser { MaxFileSizeBytes = custom };
        Assert.Equal(custom, parser.MaxFileSizeBytes);
        Assert.NotEqual(50L * 1024 * 1024, parser.MaxFileSizeBytes);
    }

    // -------------------------------------------------------------------------
    // GetHeadingTexts tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeadingTexts_EmptyDocument_ReturnsEmptyCollection()
    {
        var doc = FodtDocument.CreateEmpty();
        var headings = doc.GetHeadingTexts();
        Assert.NotNull(headings);
        Assert.Empty(headings);
    }

    [Fact]
    public void GetHeadingTexts_SingleHeading_ReturnsOneEntry()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Introduction", 1);
        var headings = doc.GetHeadingTexts();
        Assert.Single(headings);
        Assert.Equal("Introduction", headings.First());
    }

    [Fact]
    public void GetHeadingTexts_MultipleHeadings_ReturnsAll()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Chapter 1", 1);
        doc.AppendHeading("Chapter 2", 1);
        doc.AppendHeading("Chapter 3", 1);
        var headings = doc.GetHeadingTexts().ToList();
        Assert.Equal(3, headings.Count);
        Assert.Contains("Chapter 1", headings);
        Assert.Contains("Chapter 2", headings);
        Assert.Contains("Chapter 3", headings);
    }

    [Fact]
    public void GetHeadingTexts_OnlyParagraphs_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("This is not a heading.");
        doc.AppendParagraph("Neither is this.");
        var headings = doc.GetHeadingTexts();
        Assert.Empty(headings);
    }

    [Fact]
    public void GetHeadingTexts_MixedContent_ReturnsHeadingsOnly()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1);
        doc.AppendParagraph("Body text here.");
        doc.AppendHeading("Section", 2);
        doc.AppendParagraph("More body text.");
        var headings = doc.GetHeadingTexts().ToList();
        Assert.Equal(2, headings.Count);
        Assert.Contains("Title", headings);
        Assert.Contains("Section", headings);
        Assert.DoesNotContain("Body text here.", headings);
        Assert.DoesNotContain("More body text.", headings);
    }

    // -------------------------------------------------------------------------
    // Dogfood: AppendHeading×2 + AppendParagraph -> GetHeadingTexts
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AppendHeadingsAndParagraphs_GetHeadingTexts_ContainsOnlyHeadings()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Executive Summary", 1);
        doc.AppendParagraph("This report covers Q3 results.");
        doc.AppendHeading("Financial Overview", 2);
        doc.AppendParagraph("Revenue increased by 12%.");

        var headings = doc.GetHeadingTexts().ToList();

        Assert.Equal(2, headings.Count);
        Assert.Equal("Executive Summary", headings[0]);
        Assert.Equal("Financial Overview", headings[1]);
    }
}
