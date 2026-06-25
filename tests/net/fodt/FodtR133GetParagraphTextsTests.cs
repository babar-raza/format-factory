// Tests for FodtDocument.GetParagraphTexts() — ordered list of all paragraph texts.
// Sprint: FORMAT-FACTORY-FODT-PARAGRAPHTEXTS-R133-20260626
// Ledger: R133-GOVERNED-DOTNET-FODT-PARAGRAPHTEXTS-001

using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R133: FodtDocument.GetParagraphTexts() returns an ordered IReadOnlyList of all
/// paragraph texts (both body paragraphs and headings). Count matches ParagraphCount.
/// Each element matches GetParagraphText(i). Mutations (AppendParagraph, RemoveParagraph)
/// are reflected immediately in the returned list on next call.
/// </summary>
public class FodtR133GetParagraphTextsTests
{
    // ---- Empty document ----

    [Fact]
    public void GetParagraphTexts_EmptyDocument_ReturnsEmptyList()
    {
        var doc = FodtDocument.CreateEmpty();
        var texts = doc.GetParagraphTexts();
        Assert.Empty(texts);
    }

    // ---- Count matches ParagraphCount ----

    [Fact]
    public void GetParagraphTexts_SingleParagraph_CountIsOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Only paragraph");
        Assert.Single(doc.GetParagraphTexts());
    }

    [Fact]
    public void GetParagraphTexts_ThreeParagraphs_CountIsThree()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        doc.AppendParagraph("Third");
        Assert.Equal(3, doc.GetParagraphTexts().Count);
    }

    [Fact]
    public void GetParagraphTexts_CountMatchesParagraphCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha");
        doc.AppendHeading("Beta", level: 2);
        doc.AppendParagraph("Gamma");
        Assert.Equal(doc.ParagraphCount, doc.GetParagraphTexts().Count);
    }

    // ---- Content matches individual GetParagraphText ----

    [Fact]
    public void GetParagraphTexts_EachElement_MatchesGetParagraphText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Line One");
        doc.AppendParagraph("Line Two");
        doc.AppendParagraph("Line Three");

        var texts = doc.GetParagraphTexts();
        for (int i = 0; i < texts.Count; i++)
        {
            Assert.Equal(doc.GetParagraphText(i), texts[i]);
        }
    }

    // ---- Headings included ----

    [Fact]
    public void GetParagraphTexts_HeadingsIncluded_AllTextsPresent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Main Title",   level: 1);
        doc.AppendParagraph("Body paragraph.");
        doc.AppendHeading("Sub-Section",  level: 2);
        doc.AppendParagraph("More body.");

        var texts = doc.GetParagraphTexts();
        Assert.Equal(4, texts.Count);
        Assert.Contains("Main Title",      texts);
        Assert.Contains("Body paragraph.", texts);
        Assert.Contains("Sub-Section",     texts);
        Assert.Contains("More body.",      texts);
    }

    // ---- Order preserved ----

    [Fact]
    public void GetParagraphTexts_Order_PreservedAsAppended()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta");
        doc.AppendParagraph("Gamma");

        var texts = doc.GetParagraphTexts();
        Assert.Equal("Alpha", texts[0]);
        Assert.Equal("Beta",  texts[1]);
        Assert.Equal("Gamma", texts[2]);
    }

    // ---- Mutations reflected ----

    [Fact]
    public void GetParagraphTexts_AfterAppend_ListGrowsByOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        var before = doc.GetParagraphTexts().Count;

        doc.AppendParagraph("Second");
        var after = doc.GetParagraphTexts().Count;

        Assert.Equal(before + 1, after);
    }

    [Fact]
    public void GetParagraphTexts_AfterRemove_ListShrinksAndContentUpdated()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Keep");
        doc.AppendParagraph("Remove me");
        doc.RemoveParagraph(1);

        var texts = doc.GetParagraphTexts();
        Assert.Single(texts);
        Assert.Equal("Keep", texts[0]);
    }

    // ---- Dogfood: technical document pipeline ----

    [Fact]
    public void DogfoodPipeline_TechnicalDocument_AllTextsVerified()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Overview",         level: 1);
        doc.AppendParagraph("This document describes the system architecture.");
        doc.AppendHeading("Components",       level: 2);
        doc.AppendParagraph("The system consists of three components.");
        doc.AppendHeading("Component A",      level: 3);
        doc.AppendParagraph("Component A handles input processing.");
        doc.AppendHeading("Component B",      level: 3);
        doc.AppendParagraph("Component B handles output rendering.");
        doc.AppendHeading("Summary",          level: 2);
        doc.AppendParagraph("All components are tested and verified.");

        var texts = doc.GetParagraphTexts();

        // Verify count
        Assert.Equal(10, texts.Count);
        Assert.Equal(doc.ParagraphCount, texts.Count);

        // Verify specific content
        Assert.Equal("Overview",    texts[0]);
        Assert.Equal("Components",  texts[2]);
        Assert.Equal("Component A", texts[4]);
        Assert.Equal("Summary",     texts[8]);

        // Verify body paragraphs
        Assert.Contains("system architecture", texts[1]);
        Assert.Contains("three components",    texts[3]);
        Assert.Contains("verified",            texts[9]);
    }
}
