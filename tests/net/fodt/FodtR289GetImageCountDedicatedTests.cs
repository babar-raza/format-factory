// Tests for FodtDocument.GetImageCount dedicated coverage.
// Sprint: ff-sprint-s274-dotnet-deepening-20260630
// Ledger: PC-FODT-R289

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R289: Dedicated tests for FodtDocument.GetImageCount().
/// New document returns non-negative count.
/// Returns integer >= 0.
/// Count does not decrease after reading.
/// ParagraphCount unchanged after GetImageCount.
/// TableCount unchanged after GetImageCount.
/// Called twice returns same result.
/// Dogfood: new document image count stable across calls.
/// Dogfood: image count consistent with document state.
/// </summary>
public class FodtR289GetImageCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetImageCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetImageCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetImageCount_ReturnsInteger()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetImageCount();
        Assert.IsType<int>(count);
    }

    [Fact]
    public void GetImageCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello");
        int paraBefore = doc.ParagraphCount;
        _ = doc.GetImageCount();
        Assert.Equal(paraBefore, doc.ParagraphCount);
    }

    [Fact]
    public void GetImageCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        int tablesBefore = doc.TableCount;
        _ = doc.GetImageCount();
        Assert.Equal(tablesBefore, doc.TableCount);
    }

    [Fact]
    public void GetImageCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetImageCount();
        int second = doc.GetImageCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetImageCount_WithParagraphsAndTables_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        doc.AddTable(2, 3);
        doc.AddParagraph("Para 2");
        int count = doc.GetImageCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetImageCount_DoesNotModifyDocument()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Content");
        int paraBefore = doc.ParagraphCount;
        int tableBefore = doc.TableCount;
        _ = doc.GetImageCount();
        Assert.Equal(paraBefore, doc.ParagraphCount);
        Assert.Equal(tableBefore, doc.TableCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_NewDoc_ImageCountStableAcrossCalls()
    {
        var doc = FodtDocument.CreateNew();
        int c1 = doc.GetImageCount();
        int c2 = doc.GetImageCount();
        int c3 = doc.GetImageCount();
        Assert.Equal(c1, c2);
        Assert.Equal(c2, c3);
    }

    [Fact]
    public void DogfoodPipeline_AddParagraphsThenGetImageCount_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("First paragraph.");
        doc.AddParagraph("Second paragraph.");
        doc.AddParagraph("Third paragraph.");
        int count = doc.GetImageCount();
        Assert.True(count >= 0);
    }
}
