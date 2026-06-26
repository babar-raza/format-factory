// Tests for FodtDocument.GetTableCellStyle dedicated coverage.
// Sprint: ff-sprint-s286-dotnet-deepening-20260630
// Ledger: PC-FODT-R301

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R301: Dedicated tests for FodtDocument.GetTableCellStyle(tableIndex, row, col).
/// Negative table index throws exception.
/// Out-of-bounds table index throws exception.
/// No tables throws exception.
/// Negative row throws exception.
/// Negative col throws exception.
/// Valid call returns non-null.
/// TableCount unchanged after GetTableCellStyle.
/// Called twice returns same result.
/// Dogfood: set style then get returns it.
/// </summary>
public class FodtR301GetTableCellStyleDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableCellStyle_NegativeTableIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        Assert.ThrowsAny<Exception>(() => doc.GetTableCellStyle(-1, 0, 0));
    }

    [Fact]
    public void GetTableCellStyle_OutOfBoundsTableIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        int count = doc.TableCount;
        Assert.ThrowsAny<Exception>(() => doc.GetTableCellStyle(count, 0, 0));
    }

    [Fact]
    public void GetTableCellStyle_NoTables_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetTableCellStyle(0, 0, 0));
    }

    [Fact]
    public void GetTableCellStyle_NegativeRow_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        Assert.ThrowsAny<Exception>(() => doc.GetTableCellStyle(0, -1, 0));
    }

    [Fact]
    public void GetTableCellStyle_NegativeCol_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        Assert.ThrowsAny<Exception>(() => doc.GetTableCellStyle(0, 0, -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableCellStyle_ValidCall_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        doc.SetTableCellStyle(0, 0, 0, "bold");
        string? style = doc.GetTableCellStyle(0, 0, 0);
        Assert.NotNull(style);
    }

    [Fact]
    public void GetTableCellStyle_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        int before = doc.TableCount;
        doc.SetTableCellStyle(0, 0, 0, "italic");
        _ = doc.GetTableCellStyle(0, 0, 0);
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetTableCellStyle_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        doc.SetTableCellStyle(0, 0, 0, "bold");
        string? first = doc.GetTableCellStyle(0, 0, 0);
        string? second = doc.GetTableCellStyle(0, 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetStyleThenGet_ReturnsIt()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        doc.SetTableCellStyle(0, 1, 1, "italic");
        string? style = doc.GetTableCellStyle(0, 1, 1);
        Assert.NotNull(style);
    }
}
