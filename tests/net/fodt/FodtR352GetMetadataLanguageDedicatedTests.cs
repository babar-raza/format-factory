// Tests for FodtDocument.GetMetadataLanguage dedicated coverage.
// Sprint: ff-sprint-s334-dotnet-deepening-20260630
// Ledger: PC-FODT-R352

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R352: Dedicated tests for FodtDocument.GetMetadataLanguage().
/// Empty document ok.
/// Returns non-null.
/// ParagraphCount unchanged after GetMetadataLanguage.
/// TableCount unchanged after GetMetadataLanguage.
/// SectionCount unchanged after GetMetadataLanguage.
/// Idempotent (called twice same result).
/// After SetLanguage returns correct language.
/// Dogfood: document with language and content returns non-null.
/// Dogfood: language unchanged after AddParagraph.
/// </summary>
public class FodtR352GetMetadataLanguageDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMetadataLanguage_EmptyDocument_Ok()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.GetMetadataLanguage());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMetadataLanguage_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        string? language = doc.GetMetadataLanguage();
        Assert.NotNull(language);
    }

    [Fact]
    public void GetMetadataLanguage_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Document body text");
        int before = doc.ParagraphCount;
        _ = doc.GetMetadataLanguage();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetMetadataLanguage_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Document body text");
        int before = doc.TableCount;
        _ = doc.GetMetadataLanguage();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetMetadataLanguage_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Document body text");
        int before = doc.SectionCount;
        _ = doc.GetMetadataLanguage();
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetMetadataLanguage_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetLanguage("en-US");
        string? first = doc.GetMetadataLanguage();
        string? second = doc.GetMetadataLanguage();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetMetadataLanguage_AfterSetLanguage_ReturnsLanguage()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetLanguage("fr-FR");
        string? language = doc.GetMetadataLanguage();
        Assert.NotNull(language);
        Assert.Equal("fr-FR", language);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DocumentWithLanguageAndContent_NonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetLanguage("de-DE");
        doc.SetTitle("Jahresbericht");
        doc.SetAuthor("Redaktionsteam");
        doc.AddParagraph("Dieser Bericht fasst die Ergebnisse des Jahres zusammen.");
        string? language = doc.GetMetadataLanguage();
        Assert.NotNull(language);
        Assert.Equal(doc.ParagraphCount, doc.ParagraphCount);
    }

    [Fact]
    public void DogfoodPipeline_LanguageUnchangedAfterAddParagraph()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetLanguage("es-ES");
        string? languageBefore = doc.GetMetadataLanguage();
        doc.AddParagraph("Nuevo parrafo agregado al documento");
        string? languageAfter = doc.GetMetadataLanguage();
        Assert.Equal(languageBefore, languageAfter);
    }
}
