// Tests for FodtDocument.GetPageSize dedicated coverage.
// Sprint: ff-sprint-s358-dotnet-deepening-20260630
// Ledger: PC-FODT-R376

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R376: Dedicated tests for FodtDocument.GetPageSize().
/// Valid document returns non-null.
/// ParagraphCount unchanged after GetPageSize.
/// TableCount unchanged after GetPageSize.
/// SectionCount unchanged after GetPageSize.
/// Idempotent (called twice same result).
/// Returns non-empty string.
/// After SetPageSize returns expected format.
/// Dogfood: A4 page size non-null.
/// Dogfood: Letter page size non-null.
/// </summary>
public class FodtR376GetPageSizeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPageSize_ValidDocument_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        string? size = doc.GetPageSize();
        Assert.NotNull(size);
    }

    [Fact]
    public void GetPageSize_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Content paragraph");
        int before = doc.ParagraphCount;
        _ = doc.GetPageSize();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetPageSize_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3, "DataTable");
        int before = doc.TableCount;
        _ = doc.GetPageSize();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetPageSize_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Section A");
        int before = doc.SectionCount;
        _ = doc.GetPageSize();
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetPageSize_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        string? first = doc.GetPageSize();
        string? second = doc.GetPageSize();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetPageSize_ReturnsNonEmptyString()
    {
        var doc = FodtDocument.CreateNew();
        string? size = doc.GetPageSize();
        Assert.NotNull(size);
        Assert.True(size.Length > 0);
    }

    [Fact]
    public void GetPageSize_AfterSetPageSize_ReturnsExpected()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetPageSize("A4");
        string? size = doc.GetPageSize();
        Assert.NotNull(size);
        Assert.Equal("A4", size);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_A4PageSize_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetPageSize("A4");
        doc.AddParagraph("Annual Report 2026");
        doc.AddTable(3, 4, "Results");
        string? size = doc.GetPageSize();
        Assert.NotNull(size);
    }

    [Fact]
    public void DogfoodPipeline_LetterPageSize_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetPageSize("Letter");
        string? size = doc.GetPageSize();
        Assert.NotNull(size);
    }
}
