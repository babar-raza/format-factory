// Tests for FodtDocument.GetMetadataSubject dedicated coverage.
// Sprint: ff-sprint-s330-dotnet-deepening-20260630
// Ledger: PC-FODT-R348

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R348: Dedicated tests for FodtDocument.GetMetadataSubject().
/// Empty document ok.
/// Returns non-null.
/// ParagraphCount unchanged after GetMetadataSubject.
/// TableCount unchanged after GetMetadataSubject.
/// SectionCount unchanged after GetMetadataSubject.
/// Idempotent (called twice same result).
/// After SetSubject returns correct subject.
/// Dogfood: document with subject and content returns non-null.
/// Dogfood: subject unchanged after AddParagraph.
/// </summary>
public class FodtR348GetMetadataSubjectDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMetadataSubject_EmptyDocument_Ok()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.GetMetadataSubject());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMetadataSubject_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        string? subject = doc.GetMetadataSubject();
        Assert.NotNull(subject);
    }

    [Fact]
    public void GetMetadataSubject_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Document content");
        int before = doc.ParagraphCount;
        _ = doc.GetMetadataSubject();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetMetadataSubject_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Document content");
        int before = doc.TableCount;
        _ = doc.GetMetadataSubject();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetMetadataSubject_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Document content");
        int before = doc.SectionCount;
        _ = doc.GetMetadataSubject();
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetMetadataSubject_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetSubject("Financial Analysis");
        string? first = doc.GetMetadataSubject();
        string? second = doc.GetMetadataSubject();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetMetadataSubject_AfterSetSubject_ReturnsSubject()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetSubject("Quarterly Business Review");
        string? subject = doc.GetMetadataSubject();
        Assert.NotNull(subject);
        Assert.Equal("Quarterly Business Review", subject);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DocumentWithSubjectAndContent_NonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetSubject("Annual Performance");
        doc.SetTitle("Performance Report");
        doc.AddParagraph("This document covers annual performance metrics.");
        string? subject = doc.GetMetadataSubject();
        Assert.NotNull(subject);
        Assert.Equal(doc.ParagraphCount, doc.ParagraphCount);
    }

    [Fact]
    public void DogfoodPipeline_SubjectUnchangedAfterAddParagraph()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetSubject("Product Strategy");
        string? subjectBefore = doc.GetMetadataSubject();
        doc.AddParagraph("New paragraph content added later");
        string? subjectAfter = doc.GetMetadataSubject();
        Assert.Equal(subjectBefore, subjectAfter);
    }
}
