// Tests for FodsDocument.GetCellNumberFormat dedicated coverage.
// Sprint: ff-sprint-s349-dotnet-deepening-20260630
// Ledger: PC-FODS-R387

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R387: Dedicated tests for FodsDocument.GetCellNumberFormat().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-null.
/// SheetCount unchanged after GetCellNumberFormat.
/// Idempotent (called twice same result).
/// Dogfood: SetCellNumberFormat then Get returns expected format.
/// Dogfood: multiple cells with different formats each non-null.
/// </summary>
public class FodsR387GetCellNumberFormatDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellNumberFormat_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellNumberFormat(null!, 0, 0));
    }

    [Fact]
    public void GetCellNumberFormat_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellNumberFormat("  ", 0, 0));
    }

    [Fact]
    public void GetCellNumberFormat_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellNumberFormat("Unknown", 0, 0));
    }

    [Fact]
    public void GetCellNumberFormat_NegativeRowIndex_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Numbers");
        Assert.ThrowsAny<Exception>(() => doc.GetCellNumberFormat("Numbers", -1, 0));
    }

    [Fact]
    public void GetCellNumberFormat_ValidCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        string? format = doc.GetCellNumberFormat("Data", 0, 0);
        Assert.NotNull(format);
    }

    [Fact]
    public void GetCellNumberFormat_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Formats");
        int before = doc.SheetCount;
        _ = doc.GetCellNumberFormat("Formats", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellNumberFormat_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        string? first = doc.GetCellNumberFormat("Stable", 0, 0);
        string? second = doc.GetCellNumberFormat("Stable", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterSetCellNumberFormat_ReturnsExpected()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Finance");
        doc.SetCellNumberFormat("Finance", 0, 0, "#,##0.00");
        string? format = doc.GetCellNumberFormat("Finance", 0, 0);
        Assert.NotNull(format);
        Assert.Equal("#,##0.00", format);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_DifferentFormats()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        doc.SetCellNumberFormat("Report", 0, 0, "0.00%");
        doc.SetCellNumberFormat("Report", 1, 0, "yyyy-MM-dd");
        doc.SetCellNumberFormat("Report", 2, 0, "$#,##0");
        Assert.NotNull(doc.GetCellNumberFormat("Report", 0, 0));
        Assert.NotNull(doc.GetCellNumberFormat("Report", 1, 0));
        Assert.NotNull(doc.GetCellNumberFormat("Report", 2, 0));
    }
}
