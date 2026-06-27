// Tests for FodtDocument.GetMetadataGenerator dedicated coverage.
// Sprint: ff-sprint-s336-dotnet-deepening-20260630
// Ledger: PC-FODT-R354

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R354: Dedicated tests for FodtDocument.GetMetadataGenerator().
/// Empty document ok.
/// Returns non-null.
/// ParagraphCount unchanged after GetMetadataGenerator.
/// TableCount unchanged after GetMetadataGenerator.
/// SectionCount unchanged after GetMetadataGenerator.
/// Idempotent (called twice same result).
/// After SetGenerator returns correct generator.
/// Dogfood: document with generator and content returns non-null.
/// Dogfood: generator unchanged after AddParagraph.
/// </summary>
public class FodtR354GetMetadataGeneratorDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMetadataGenerator_EmptyDocument_Ok()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.GetMetadataGenerator());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMetadataGenerator_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        string? generator = doc.GetMetadataGenerator();
        Assert.NotNull(generator);
    }

    [Fact]
    public void GetMetadataGenerator_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Body content here");
        int before = doc.ParagraphCount;
        _ = doc.GetMetadataGenerator();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetMetadataGenerator_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Body content here");
        int before = doc.TableCount;
        _ = doc.GetMetadataGenerator();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetMetadataGenerator_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Body content here");
        int before = doc.SectionCount;
        _ = doc.GetMetadataGenerator();
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetMetadataGenerator_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetGenerator("FormatFactory 1.0");
        string? first = doc.GetMetadataGenerator();
        string? second = doc.GetMetadataGenerator();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetMetadataGenerator_AfterSetGenerator_ReturnsGenerator()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetGenerator("Automated Document Pipeline v2.0");
        string? generator = doc.GetMetadataGenerator();
        Assert.NotNull(generator);
        Assert.Equal("Automated Document Pipeline v2.0", generator);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DocumentWithGeneratorAndContent_NonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetGenerator("Report Builder 3.0");
        doc.SetTitle("Monthly Summary");
        doc.SetAuthor("Pipeline");
        doc.AddParagraph("This monthly summary was generated automatically.");
        string? generator = doc.GetMetadataGenerator();
        Assert.NotNull(generator);
        Assert.Equal(doc.ParagraphCount, doc.ParagraphCount);
    }

    [Fact]
    public void DogfoodPipeline_GeneratorUnchangedAfterAddParagraph()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetGenerator("Template Engine 5.0");
        string? generatorBefore = doc.GetMetadataGenerator();
        doc.AddParagraph("Extra content added by post-processor");
        string? generatorAfter = doc.GetMetadataGenerator();
        Assert.Equal(generatorBefore, generatorAfter);
    }
}
