// Tests for FodtDocument.GetMetadataTitle dedicated coverage.
// Sprint: ff-sprint-s328-dotnet-deepening-20260630
// Ledger: PC-FODT-R346

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R346: Dedicated tests for FodtDocument.GetMetadataTitle().
/// Empty document ok.
/// Returns non-null.
/// ParagraphCount unchanged after GetMetadataTitle.
/// TableCount unchanged after GetMetadataTitle.
/// SectionCount unchanged after GetMetadataTitle.
/// Idempotent (called twice same result).
/// After SetTitle returns correct title.
/// Dogfood: document with title and content returns non-null.
/// Dogfood: document title unchanged after AddParagraph.
/// </summary>
public class FodtR346GetMetadataTitleDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMetadataTitle_EmptyDocument_Ok()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.GetMetadataTitle());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMetadataTitle_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        string? title = doc.GetMetadataTitle();
        Assert.NotNull(title);
    }

    [Fact]
    public void GetMetadataTitle_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Body content");
        int before = doc.ParagraphCount;
        _ = doc.GetMetadataTitle();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetMetadataTitle_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Body content");
        int before = doc.TableCount;
        _ = doc.GetMetadataTitle();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetMetadataTitle_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Body content");
        int before = doc.SectionCount;
        _ = doc.GetMetadataTitle();
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetMetadataTitle_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetTitle("My Document");
        string? first = doc.GetMetadataTitle();
        string? second = doc.GetMetadataTitle();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetMetadataTitle_AfterSetTitle_ReturnsTitle()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetTitle("Project Report 2026");
        string? title = doc.GetMetadataTitle();
        Assert.NotNull(title);
        Assert.Equal("Project Report 2026", title);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DocumentWithTitleAndContent_NonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetTitle("Annual Summary");
        doc.AddParagraph("This document summarizes the annual results.");
        string? title = doc.GetMetadataTitle();
        Assert.NotNull(title);
        Assert.Equal(doc.ParagraphCount, doc.ParagraphCount);
    }

    [Fact]
    public void DogfoodPipeline_TitleUnchangedAfterAddParagraph()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetTitle("Static Title");
        string? titleBefore = doc.GetMetadataTitle();
        doc.AddParagraph("New content added after title was set");
        string? titleAfter = doc.GetMetadataTitle();
        Assert.Equal(titleBefore, titleAfter);
    }
}
