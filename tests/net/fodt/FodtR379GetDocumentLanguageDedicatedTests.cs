// Tests for FodtDocument.GetDocumentLanguage dedicated coverage.
// Sprint: ff-sprint-s361-dotnet-deepening-20260630
// Ledger: PC-FODT-R379

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R379: Dedicated tests for FodtDocument.GetDocumentLanguage().
/// Valid document returns non-null.
/// ParagraphCount unchanged after GetDocumentLanguage.
/// TableCount unchanged after GetDocumentLanguage.
/// SectionCount unchanged after GetDocumentLanguage.
/// Idempotent (called twice same result).
/// Returns non-empty string.
/// After SetDocumentLanguage returns expected.
/// Dogfood: English language non-null.
/// Dogfood: French language non-null.
/// </summary>
public class FodtR379GetDocumentLanguageDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentLanguage_ValidDocument_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        string? lang = doc.GetDocumentLanguage();
        Assert.NotNull(lang);
    }

    [Fact]
    public void GetDocumentLanguage_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Sample text");
        int before = doc.ParagraphCount;
        _ = doc.GetDocumentLanguage();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetDocumentLanguage_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3, "Stats");
        int before = doc.TableCount;
        _ = doc.GetDocumentLanguage();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetDocumentLanguage_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Chapter 1");
        int before = doc.SectionCount;
        _ = doc.GetDocumentLanguage();
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetDocumentLanguage_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        string? first = doc.GetDocumentLanguage();
        string? second = doc.GetDocumentLanguage();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetDocumentLanguage_ReturnsNonEmptyString()
    {
        var doc = FodtDocument.CreateNew();
        string? lang = doc.GetDocumentLanguage();
        Assert.NotNull(lang);
        Assert.True(lang.Length > 0);
    }

    [Fact]
    public void GetDocumentLanguage_AfterSetDocumentLanguage_ReturnsExpected()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDocumentLanguage("en-US");
        string? lang = doc.GetDocumentLanguage();
        Assert.NotNull(lang);
        Assert.Equal("en-US", lang);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_EnglishLanguage_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDocumentLanguage("en-US");
        doc.AddParagraph("This document is in English.");
        doc.AddTable(2, 4, "EnglishTable");
        string? lang = doc.GetDocumentLanguage();
        Assert.NotNull(lang);
    }

    [Fact]
    public void DogfoodPipeline_FrenchLanguage_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDocumentLanguage("fr-FR");
        string? lang = doc.GetDocumentLanguage();
        Assert.NotNull(lang);
    }
}
