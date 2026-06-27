// Tests for FodtDocument.GetTableRowHeight dedicated coverage.
// Sprint: ff-sprint-s347-dotnet-deepening-20260630
// Ledger: PC-FODT-R365

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R365: Dedicated tests for FodtDocument.GetTableRowHeight().
/// Negative table index throws.
/// Out-of-range table index throws.
/// Negative row index throws.
/// Out-of-range row index throws.
/// Valid row returns non-negative value.
/// ParagraphCount unchanged after GetTableRowHeight.
/// TableCount unchanged after GetTableRowHeight.
/// Idempotent (called twice same result).
/// Dogfood: table with set row height returns value.
/// </summary>
public class FodtR365GetTableRowHeightDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableRowHeight_NegativeTableIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 4, "Grid");
        Assert.ThrowsAny<Exception>(() => doc.GetTableRowHeight(-1, 0));
    }

    [Fact]
    public void GetTableRowHeight_OutOfRangeTableIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 4, "Grid");
        Assert.ThrowsAny<Exception>(() => doc.GetTableRowHeight(99, 0));
    }

    [Fact]
    public void GetTableRowHeight_NegativeRowIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 4, "Grid");
        Assert.ThrowsAny<Exception>(() => doc.GetTableRowHeight(0, -1));
    }

    [Fact]
    public void GetTableRowHeight_OutOfRangeRowIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 4, "Grid");
        Assert.ThrowsAny<Exception>(() => doc.GetTableRowHeight(0, 99));
    }

    [Fact]
    public void GetTableRowHeight_ValidRow_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(4, 3, "Report");
        double height = doc.GetTableRowHeight(0, 0);
        Assert.True(height >= 0.0);
    }

    [Fact]
    public void GetTableRowHeight_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Section title");
        doc.AddTable(2, 3, "Data");
        int before = doc.ParagraphCount;
        _ = doc.GetTableRowHeight(0, 0);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetTableRowHeight_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3, "Summary");
        int before = doc.TableCount;
        _ = doc.GetTableRowHeight(0, 0);
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetTableRowHeight_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 5, "Stable");
        double first = doc.GetTableRowHeight(0, 0);
        double second = doc.GetTableRowHeight(0, 0);
        Assert.Equal(first, second, precision: 10);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetRowHeightThenGet_ReturnsValue()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(4, 3, "Layout");
        doc.SetTableRowHeight(0, 0, 1.2);
        double height = doc.GetTableRowHeight(0, 0);
        Assert.True(height >= 0.0);
    }
}
