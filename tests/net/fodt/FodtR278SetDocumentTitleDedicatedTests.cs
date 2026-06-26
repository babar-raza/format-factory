// Tests for FodtDocument.SetDocumentTitle dedicated coverage.
// Sprint: ff-sprint-s263-dotnet-deepening-20260630
// Ledger: PC-FODT-R278

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R278: Dedicated tests for FodtDocument.SetDocumentTitle(title) and GetDocumentTitle().
/// Valid title → no exception.
/// GetDocumentTitle returns the set title.
/// Set twice → second title wins.
/// ParagraphCount unchanged after set.
/// TableCount unchanged after set.
/// GetDocumentTitle called twice → same result.
/// Empty string title → no exception.
/// Dogfood: set title and retrieve it.
/// Dogfood: overwrite title, new title retrieved.
/// </summary>
public class FodtR278SetDocumentTitleDedicatedTests
{
    // -------------------------------------------------------------------------
    // Basic behavioral tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetDocumentTitle_ValidTitle_NoException()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.SetDocumentTitle("My Document"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetDocumentTitle_EmptyString_NoException()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.SetDocumentTitle(""));
        Assert.Null(ex);
    }

    [Fact]
    public void SetDocumentTitle_GetDocumentTitle_ReturnsSetTitle()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDocumentTitle("Test Title");
        string title = doc.GetDocumentTitle();
        Assert.Equal("Test Title", title);
    }

    [Fact]
    public void SetDocumentTitle_SetTwice_SecondTitleWins()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDocumentTitle("First");
        doc.SetDocumentTitle("Second");
        string title = doc.GetDocumentTitle();
        Assert.Equal("Second", title);
    }

    // -------------------------------------------------------------------------
    // Preservation tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetDocumentTitle_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some content");
        int before = doc.ParagraphCount;
        doc.SetDocumentTitle("New Title");
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void SetDocumentTitle_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        int before = doc.TableCount;
        doc.SetDocumentTitle("Doc Title");
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetDocumentTitle_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDocumentTitle("Stable Title");
        string first = doc.GetDocumentTitle();
        string second = doc.GetDocumentTitle();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetAndRetrieve_TitleMatches()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDocumentTitle("Annual Report 2026");
        string retrieved = doc.GetDocumentTitle();
        Assert.Equal("Annual Report 2026", retrieved);
    }

    [Fact]
    public void DogfoodPipeline_OverwriteTitle_NewTitleRetrieved()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDocumentTitle("Draft Title");
        doc.SetDocumentTitle("Final Title");
        string result = doc.GetDocumentTitle();
        Assert.Equal("Final Title", result);
    }
}
