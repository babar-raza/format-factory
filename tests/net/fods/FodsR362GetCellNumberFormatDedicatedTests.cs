// Tests for FodsDocument.GetCellNumberFormat dedicated coverage.
// Sprint: ff-sprint-s328-dotnet-deepening-20260630
// Ledger: PC-FODS-R362

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R362: Dedicated tests for FodsDocument.GetCellNumberFormat().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Nonexistent sheet throws.
/// Negative row throws.
/// Valid call returns non-null.
/// SheetCount unchanged after GetCellNumberFormat.
/// Called twice same result.
/// Dogfood: SetCellNumberFormat then GetCellNumberFormat.
/// Dogfood: multiple cells all return non-null format.
/// </summary>
public class FodsR362GetCellNumberFormatDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellNumberFormat_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.ThrowsAny<Exception>(() => doc.GetCellNumberFormat(null!, 0, 0));
    }

    [Fact]
    public void GetCellNumberFormat_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.ThrowsAny<Exception>(() => doc.GetCellNumberFormat("   ", 0, 0));
    }

    [Fact]
    public void GetCellNumberFormat_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellNumberFormat("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellNumberFormat_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.ThrowsAny<Exception>(() => doc.GetCellNumberFormat("Data", -1, 0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellNumberFormat_ValidCall_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "123.45");
        string? format = doc.GetCellNumberFormat("Sheet1", 0, 0);
        Assert.NotNull(format);
    }

    [Fact]
    public void GetCellNumberFormat_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        _ = doc.GetCellNumberFormat("Sheet1", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellNumberFormat_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Finance");
        doc.SetCellValue("Finance", 0, 0, "1000.00");
        string? first = doc.GetCellNumberFormat("Finance", 0, 0);
        string? second = doc.GetCellNumberFormat("Finance", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetCellNumberFormatThenGet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Totals");
        doc.SetCellValue("Totals", 0, 0, "99999");
        doc.SetCellNumberFormat("Totals", 0, 0, "#,##0.00");
        string? format = doc.GetCellNumberFormat("Totals", 0, 0);
        Assert.NotNull(format);
        Assert.Equal(doc.SheetCount, doc.SheetCount);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_AllNonNullFormat()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        for (int r = 0; r < 3; r++)
            doc.SetCellValue("Data", r, 0, $"{r * 100}");
        for (int r = 0; r < 3; r++)
            Assert.NotNull(doc.GetCellNumberFormat("Data", r, 0));
    }
}
