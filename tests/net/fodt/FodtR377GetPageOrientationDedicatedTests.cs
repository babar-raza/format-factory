// Tests for FodtDocument.GetPageOrientation dedicated coverage.
// Sprint: ff-sprint-s359-dotnet-deepening-20260630
// Ledger: PC-FODT-R377

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R377: Dedicated tests for FodtDocument.GetPageOrientation().
/// Valid document returns non-null.
/// ParagraphCount unchanged after GetPageOrientation.
/// TableCount unchanged after GetPageOrientation.
/// SectionCount unchanged after GetPageOrientation.
/// Idempotent (called twice same result).
/// Returns non-empty string.
/// After SetPageOrientation "landscape" returns expected.
/// Dogfood: portrait orientation non-null.
/// Dogfood: landscape orientation non-null.
/// </summary>
public class FodtR377GetPageOrientationDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPageOrientation_ValidDocument_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        string? orientation = doc.GetPageOrientation();
        Assert.NotNull(orientation);
    }

    [Fact]
    public void GetPageOrientation_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Body text paragraph");
        int before = doc.ParagraphCount;
        _ = doc.GetPageOrientation();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetPageOrientation_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 4, "LayoutTable");
        int before = doc.TableCount;
        _ = doc.GetPageOrientation();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetPageOrientation_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Introduction");
        int before = doc.SectionCount;
        _ = doc.GetPageOrientation();
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetPageOrientation_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        string? first = doc.GetPageOrientation();
        string? second = doc.GetPageOrientation();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetPageOrientation_ReturnsNonEmptyString()
    {
        var doc = FodtDocument.CreateNew();
        string? orientation = doc.GetPageOrientation();
        Assert.NotNull(orientation);
        Assert.True(orientation.Length > 0);
    }

    [Fact]
    public void GetPageOrientation_AfterSetLandscape_ReturnsExpected()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetPageOrientation("landscape");
        string? orientation = doc.GetPageOrientation();
        Assert.NotNull(orientation);
        Assert.Equal("landscape", orientation);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PortraitOrientation_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetPageOrientation("portrait");
        doc.AddParagraph("Annual Report Cover");
        doc.AddTable(2, 3, "Summary");
        string? orientation = doc.GetPageOrientation();
        Assert.NotNull(orientation);
    }

    [Fact]
    public void DogfoodPipeline_LandscapeOrientation_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetPageOrientation("landscape");
        string? orientation = doc.GetPageOrientation();
        Assert.NotNull(orientation);
    }
}
