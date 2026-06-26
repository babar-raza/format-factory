// Tests for FodtDocument.GetLanguage / SetLanguage dedicated coverage.
// Sprint: ff-sprint-s211-dotnet-deepening-20260629
// Ledger: PC-FODT-R226

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R226: Dedicated tests for FodtDocument.GetLanguage / SetLanguage.
/// Empty document: GetLanguage returns null or non-null default.
/// No exception on empty doc.
/// SetLanguage then Get: returns set value.
/// Returns string type.
/// ParagraphCount unchanged after get.
/// Called twice: returns same value.
/// Set twice: latest value returned.
/// Paragraphs added after set: language unchanged.
/// Dogfood: set language, add paragraphs, verify stable.
/// Dogfood: exact value round-trip.
/// </summary>
public class FodtR226GetLanguageTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetLanguage_EmptyDoc_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.GetLanguage());
        Assert.Null(ex);
    }

    [Fact]
    public void GetLanguage_EmptyDoc_ReturnsStringOrNull()
    {
        var doc = FodtDocument.CreateEmpty();
        var lang = doc.GetLanguage();
        Assert.True(lang == null || lang is string);
    }

    [Fact]
    public void GetLanguage_AfterSet_ReturnsValue()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetLanguage("en-US");
        Assert.Equal("en-US", doc.GetLanguage());
    }

    [Fact]
    public void GetLanguage_ReturnsString()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetLanguage("fr-FR");
        Assert.IsAssignableFrom<string>(doc.GetLanguage());
    }

    [Fact]
    public void GetLanguage_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta");
        int before = doc.ParagraphCount;
        doc.GetLanguage();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetLanguage_CalledTwice_SameValue()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetLanguage("de-DE");
        Assert.Equal(doc.GetLanguage(), doc.GetLanguage());
    }

    [Fact]
    public void GetLanguage_SetTwice_ReturnsLatest()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetLanguage("en-US");
        doc.SetLanguage("es-ES");
        Assert.Equal("es-ES", doc.GetLanguage());
    }

    [Fact]
    public void GetLanguage_AfterParagraphsAdded_LanguageUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetLanguage("en-GB");
        doc.AppendParagraph("Para 1");
        doc.AppendHeading("Heading", 1);
        Assert.Equal("en-GB", doc.GetLanguage());
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_LanguageWithParagraphs_LanguageStable()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetLanguage("ja-JP");
        for (int i = 0; i < 5; i++)
            doc.AppendParagraph($"Content {i}");
        Assert.Equal("ja-JP", doc.GetLanguage());
    }

    [Fact]
    public void DogfoodPipeline_ExactValueRoundTrip()
    {
        var doc = FodtDocument.CreateEmpty();
        string expected = "zh-CN";
        doc.SetLanguage(expected);
        Assert.Equal(expected, doc.GetLanguage());
    }
}
