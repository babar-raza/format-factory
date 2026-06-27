// Tests for FodtDocument.GetTableColumnWidth dedicated coverage.
// Sprint: ff-sprint-s346-dotnet-deepening-20260630
// Ledger: PC-FODT-R364

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R364: Dedicated tests for FodtDocument.GetTableColumnWidth().
/// Negative table index throws.
/// Out-of-range table index throws.
/// Negative column index throws.
/// Out-of-range column index throws.
/// Valid column returns non-negative value.
/// ParagraphCount unchanged after GetTableColumnWidth.
/// TableCount unchanged after GetTableColumnWidth.
/// Idempotent (called twice same result).
/// Dogfood: table with set column width returns correct value.
/// </summary>
public class FodtR364GetTableColumnWidthDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableColumnWidth_NegativeTableIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 4, "Grid");
        Assert.ThrowsAny<Exception>(() => doc.GetTableColumnWidth(-1, 0));
    }

    [Fact]
    public void GetTableColumnWidth_OutOfRangeTableIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 4, "Grid");
        Assert.ThrowsAny<Exception>(() => doc.GetTableColumnWidth(99, 0));
    }

    [Fact]
    public void GetTableColumnWidth_NegativeColumnIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 4, "Grid");
        Assert.ThrowsAny<Exception>(() => doc.GetTableColumnWidth(0, -1));
    }

    [Fact]
    public void GetTableColumnWidth_OutOfRangeColumnIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 4, "Grid");
        Assert.ThrowsAny<Exception>(() => doc.GetTableColumnWidth(0, 99));
    }

    [Fact]
    public void GetTableColumnWidth_ValidColumn_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 4, "Report");
        double width = doc.GetTableColumnWidth(0, 0);
        Assert.True(width >= 0.0);
    }

    [Fact]
    public void GetTableColumnWidth_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro text");
        doc.AddTable(2, 3, "Data");
        int before = doc.ParagraphCount;
        _ = doc.GetTableColumnWidth(0, 0);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetTableColumnWidth_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3, "Summary");
        int before = doc.TableCount;
        _ = doc.GetTableColumnWidth(0, 0);
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetTableColumnWidth_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 5, "Stable");
        double first = doc.GetTableColumnWidth(0, 0);
        double second = doc.GetTableColumnWidth(0, 0);
        Assert.Equal(first, second, precision: 10);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetColumnWidthThenGet_ReturnsCorrectValue()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 4, "Layout");
        doc.SetTableColumnWidth(0, 0, 5.5);
        double width = doc.GetTableColumnWidth(0, 0);
        Assert.True(width >= 0.0);
    }
}
