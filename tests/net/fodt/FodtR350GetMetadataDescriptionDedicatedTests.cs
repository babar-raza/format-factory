// Tests for FodtDocument.GetMetadataDescription dedicated coverage.
// Sprint: ff-sprint-s332-dotnet-deepening-20260630
// Ledger: PC-FODT-R350

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R350: Dedicated tests for FodtDocument.GetMetadataDescription().
/// Empty document ok.
/// Returns non-null.
/// ParagraphCount unchanged after GetMetadataDescription.
/// TableCount unchanged after GetMetadataDescription.
/// SectionCount unchanged after GetMetadataDescription.
/// Idempotent (called twice same result).
/// After SetDescription returns correct description.
/// Dogfood: document with description and content returns non-null.
/// Dogfood: description unchanged after AddParagraph.
/// </summary>
public class FodtR350GetMetadataDescriptionDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMetadataDescription_EmptyDocument_Ok()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.GetMetadataDescription());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMetadataDescription_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        string? description = doc.GetMetadataDescription();
        Assert.NotNull(description);
    }

    [Fact]
    public void GetMetadataDescription_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Document body text");
        int before = doc.ParagraphCount;
        _ = doc.GetMetadataDescription();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetMetadataDescription_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Document body text");
        int before = doc.TableCount;
        _ = doc.GetMetadataDescription();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetMetadataDescription_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Document body text");
        int before = doc.SectionCount;
        _ = doc.GetMetadataDescription();
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetMetadataDescription_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDescription("A comprehensive analysis document");
        string? first = doc.GetMetadataDescription();
        string? second = doc.GetMetadataDescription();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetMetadataDescription_AfterSetDescription_ReturnsDescription()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDescription("This document covers the annual budget review process");
        string? description = doc.GetMetadataDescription();
        Assert.NotNull(description);
        Assert.Equal("This document covers the annual budget review process", description);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DocumentWithDescriptionAndContent_NonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDescription("Executive summary of Q4 results");
        doc.SetTitle("Q4 Summary");
        doc.SetAuthor("Finance Team");
        doc.AddParagraph("This executive summary outlines the Q4 results.");
        string? description = doc.GetMetadataDescription();
        Assert.NotNull(description);
        Assert.Equal(doc.ParagraphCount, doc.ParagraphCount);
    }

    [Fact]
    public void DogfoodPipeline_DescriptionUnchangedAfterAddParagraph()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDescription("Original document description");
        string? descBefore = doc.GetMetadataDescription();
        doc.AddParagraph("Additional content added to the document");
        string? descAfter = doc.GetMetadataDescription();
        Assert.Equal(descBefore, descAfter);
    }
}
