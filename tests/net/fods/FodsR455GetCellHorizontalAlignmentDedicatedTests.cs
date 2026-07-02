// Tests for FodsDocument.GetCellHorizontalAlignment dedicated coverage.
// Sprint: ff-sprint-s406-dotnet-deepening-20260701
// Ledger: PC-FODS-R455

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R455: Dedicated tests for FodsDocument.GetCellHorizontalAlignment().
/// Null/whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-null.
/// SheetCount unchanged after GetCellHorizontalAlignment.
/// Idempotent (called twice same result).
/// Is string type.
/// SetHorizontalAlignment+Get round-trips.
/// Dogfood: default cell alignment non-null.
/// Dogfood: multiple cells all non-null.
/// </summary>
public class FodsR455GetCellHorizontalAlignmentDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellHorizontalAlignment_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellHorizontalAlignment(null!, 0, 0));
    }

    [Fact]
    public void GetCellHorizontalAlignment_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellHorizontalAlignment("   ", 0, 0));
    }

    [Fact]
    public void GetCellHorizontalAlignment_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellHorizontalAlignment("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellHorizontalAlignment_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        Assert.ThrowsAny<Exception>(() => doc.GetCellHorizontalAlignment(sheetName, -1, 0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellHorizontalAlignment_ValidCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        string alignment = doc.GetCellHorizontalAlignment(sheetName, 0, 0);
        Assert.NotNull(alignment);
    }

    [Fact]
    public void GetCellHorizontalAlignment_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetName(0);
        _ = doc.GetCellHorizontalAlignment(sheetName, 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellHorizontalAlignment_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        string first = doc.GetCellHorizontalAlignment(sheetName, 0, 0);
        string second = doc.GetCellHorizontalAlignment(sheetName, 0, 0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCellHorizontalAlignment_IsString()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        object alignment = doc.GetCellHorizontalAlignment(sheetName, 0, 0);
        Assert.IsType<string>(alignment);
    }

    [Fact]
    public void GetCellHorizontalAlignment_AfterSet_RoundTrips()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        doc.SetCellHorizontalAlignment(sheetName, 0, 0, "center");
        string alignment = doc.GetCellHorizontalAlignment(sheetName, 0, 0);
        Assert.Equal("center", alignment);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultCell_AlignmentNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        string alignment = doc.GetCellHorizontalAlignment(sheetName, 0, 0);
        Assert.NotNull(alignment);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_AllNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        for (int row = 0; row < 3; row++)
        {
            for (int col = 0; col < 3; col++)
            {
                Assert.NotNull(doc.GetCellHorizontalAlignment(sheetName, row, col));
            }
        }
    }

    // -------------------------------------------------------------------------
    // Type 3 — ODF semantic (fixture-based) — GI-FODS-NET-001 Phase 4c
    // -------------------------------------------------------------------------

    private static readonly string FixturesPath =
        System.IO.Path.GetFullPath(System.IO.Path.Combine(AppContext.BaseDirectory, "../../../../../../tests/net/fods/Fixtures"));

    [Fact]
    public void GetCellHorizontalAlignment_FromFixture_ReturnsCenter_WhenStyleCe1Applied()
    {
        // fods-cell-styles.fods: Sheet1 row0 col0 has style ce1 with fo:text-align="center"
        var doc = FodsDocument.Load(System.IO.Path.Combine(FixturesPath, "fods-cell-styles.fods"));
        Assert.Equal("center", doc.GetCellHorizontalAlignment("Sheet1", 0, 0));
    }

    [Fact]
    public void GetCellHorizontalAlignment_FromFixture_ReturnsEnd_WhenStyleCe2Applied()
    {
        // fods-cell-styles.fods: Sheet1 row1 col0 has style ce2 with fo:text-align="end"
        var doc = FodsDocument.Load(System.IO.Path.Combine(FixturesPath, "fods-cell-styles.fods"));
        Assert.Equal("end", doc.GetCellHorizontalAlignment("Sheet1", 1, 0));
    }

    [Fact]
    public void GetCellHorizontalAlignment_FromFixture_ReturnsStart_WhenNoStyleApplied()
    {
        // fods-cell-styles.fods: Sheet1 row0 col1 has no explicit style → default "start"
        var doc = FodsDocument.Load(System.IO.Path.Combine(FixturesPath, "fods-cell-styles.fods"));
        Assert.Equal("start", doc.GetCellHorizontalAlignment("Sheet1", 0, 1));
    }
}
