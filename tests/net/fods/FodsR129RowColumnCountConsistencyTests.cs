// Tests for FodsDocument.GetRowCount/GetColumnCount consistency after mutations.
// Sprint: FORMAT-FACTORY-FODS-ROW-COL-COUNT-CONSISTENCY-20260626
// Ledger: R129-GOVERNED-DOTNET-FODS-ROW-COL-COUNT-CONSISTENCY-001

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R129: FodsDocument.GetRowCount(sheetName) and GetColumnCount(sheetName) stay
/// consistent with FodsSheet.Rows.Count and actual data after InsertRow, DeleteRows,
/// InsertRowWithValues, and ClearSheet mutations.
/// </summary>
public class FodsR129RowColumnCountConsistencyTests
{
    // ---- GetRowCount: basic ----

    [Fact]
    public void GetRowCount_EmptySheet_IsZero()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Equal(0, doc.GetRowCount("Sheet1"));
    }

    [Fact]
    public void GetRowCount_AfterInsertRowWithValues_Increases()
    {
        var doc = FodsDocument.CreateNew();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "a", "b", "c" });
        doc.InsertRowWithValues("Sheet1", 1, new[] { "d", "e", "f" });

        Assert.Equal(2, doc.GetRowCount("Sheet1"));
    }

    [Fact]
    public void GetRowCount_MatchesSheetRowsCount()
    {
        var doc = FodsDocument.CreateNew();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "row1c1", "row1c2" });
        doc.InsertRowWithValues("Sheet1", 1, new[] { "row2c1", "row2c2" });
        doc.InsertRowWithValues("Sheet1", 2, new[] { "row3c1", "row3c2" });

        var sheet = doc.GetSheetByName("Sheet1")!;
        Assert.Equal(doc.GetRowCount("Sheet1"), sheet.Rows.Count);
    }

    // ---- GetRowCount: after DeleteRows ----

    [Fact]
    public void GetRowCount_AfterDeleteRows_Decreases()
    {
        var doc = FodsDocument.CreateNew();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "a" });
        doc.InsertRowWithValues("Sheet1", 1, new[] { "b" });
        doc.InsertRowWithValues("Sheet1", 2, new[] { "c" });

        doc.DeleteRows("Sheet1", 0, 1); // delete 1 row at index 0

        Assert.Equal(2, doc.GetRowCount("Sheet1"));
    }

    // ---- GetRowCount: after ClearSheet ----

    [Fact]
    public void GetRowCount_AfterClearSheet_IsZero()
    {
        var doc = FodsDocument.CreateNew();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "x", "y" });
        doc.InsertRowWithValues("Sheet1", 1, new[] { "z", "w" });

        doc.ClearSheet("Sheet1");

        Assert.Equal(0, doc.GetRowCount("Sheet1"));
    }

    // ---- GetColumnCount: basic ----

    [Fact]
    public void GetColumnCount_EmptySheet_IsZero()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Equal(0, doc.GetColumnCount("Sheet1"));
    }

    [Fact]
    public void GetColumnCount_SingleRowThreeCols_IsThree()
    {
        var doc = FodsDocument.CreateNew();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "A", "B", "C" });

        Assert.Equal(3, doc.GetColumnCount("Sheet1"));
    }

    // ---- GetColumnCount: after ClearSheet ----

    [Fact]
    public void GetColumnCount_AfterClearSheet_IsZero()
    {
        var doc = FodsDocument.CreateNew();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "X", "Y", "Z" });

        doc.ClearSheet("Sheet1");

        Assert.Equal(0, doc.GetColumnCount("Sheet1"));
    }

    // ---- Consistency between GetRowCount and InsertRow ----

    [Fact]
    public void GetRowCount_AfterInsertRow_Increases()
    {
        var doc = FodsDocument.CreateNew();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "a" });
        var beforeCount = doc.GetRowCount("Sheet1");

        doc.InsertRow("Sheet1", 1);
        Assert.Equal(beforeCount + 1, doc.GetRowCount("Sheet1"));
    }

    // ---- Dogfood: sequence of mutations stays consistent ----

    [Fact]
    public void DogfoodPipeline_MutationSequence_CountsStayConsistent()
    {
        var doc = FodsDocument.CreateNew();

        // Add 3 rows
        doc.InsertRowWithValues("Sheet1", 0, new[] { "r1", "c1", "d1" });
        doc.InsertRowWithValues("Sheet1", 1, new[] { "r2", "c2", "d2" });
        doc.InsertRowWithValues("Sheet1", 2, new[] { "r3", "c3", "d3" });
        Assert.Equal(3, doc.GetRowCount("Sheet1"));
        Assert.Equal(3, doc.GetColumnCount("Sheet1"));

        // Delete one row
        doc.DeleteRows("Sheet1", 0, 1);
        Assert.Equal(2, doc.GetRowCount("Sheet1"));

        // Clear and verify both are zero
        doc.ClearSheet("Sheet1");
        Assert.Equal(0, doc.GetRowCount("Sheet1"));
        Assert.Equal(0, doc.GetColumnCount("Sheet1"));
    }
}
