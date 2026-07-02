// Tests for FodsDocument.GetCellIndent dedicated coverage.
// Sprint: ff-sprint-s399-dotnet-deepening-20260701
// Ledger: PC-FODS-R448

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R448: Dedicated tests for FodsDocument.GetCellIndent().
/// Null/whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-negative indent.
/// SheetCount unchanged after GetCellIndent.
/// Idempotent (called twice same result).
/// SetCellIndent + GetCellIndent round-trips.
/// Dogfood: default cell indent non-negative.
/// Dogfood: multiple cells all non-negative indents.
/// </summary>
public class FodsR448GetCellIndentDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellIndent_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellIndent(null!, 0, 0));
    }

    [Fact]
    public void GetCellIndent_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellIndent("   ", 0, 0));
    }

    [Fact]
    public void GetCellIndent_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellIndent("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellIndent_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        Assert.ThrowsAny<Exception>(() => doc.GetCellIndent(sheetName, -1, 0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellIndent_ValidCell_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        int indent = doc.GetCellIndent(sheetName, 0, 0);
        Assert.True(indent >= 0);
    }

    [Fact]
    public void GetCellIndent_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetName(0);
        _ = doc.GetCellIndent(sheetName, 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellIndent_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        int first = doc.GetCellIndent(sheetName, 0, 0);
        int second = doc.GetCellIndent(sheetName, 0, 0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCellIndent_SetIndent_RoundTrips()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        doc.SetCellIndent(sheetName, 0, 0, 3);
        int indent = doc.GetCellIndent(sheetName, 0, 0);
        Assert.Equal(3, indent);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultCell_IndentNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        int indent = doc.GetCellIndent(sheetName, 0, 0);
        Assert.True(indent >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_AllNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        for (int col = 0; col < 4; col++)
        {
            Assert.True(doc.GetCellIndent(sheetName, 0, col) >= 0);
        }
    }
}
